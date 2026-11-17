#!/usr/bin/env python3
"""Build Karachi Division boundary from a regional OSM PBF using pip packages only."""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

RELATION_ID = 6080948
AREA_CRS = "EPSG:32642"

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def validate_relation_identity(tags):
    """Validate the administrative identity using English name when available.

    OSM's primary name tag is language-dependent; Karachi Division's primary
    name is Urdu, while name:en carries the English label.
    """
    if tags.get("boundary") != "administrative":
        raise ValueError(f"Relation is not an administrative boundary: {tags}")
    if tags.get("admin_level") != "5":
        raise ValueError(f"Unexpected Karachi Division admin_level: {tags.get('admin_level')!r}")
    english_name = tags.get("name:en")
    primary_name = tags.get("name")
    accepted_names = {"Karachi Division", "Karachi"}
    if english_name not in accepted_names and primary_name not in accepted_names:
        raise ValueError(f"Unexpected relation name; name={primary_name!r}, name:en={english_name!r}")
    return english_name or primary_name

def validate_geometry(geometry_data):
    geometry_type = geometry_data.get("type")
    if geometry_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Expected a non-empty Polygon or MultiPolygon.")
    try:
        from shapely.geometry import shape
        from shapely.validation import explain_validity
        from shapely.ops import transform
        from pyproj import Transformer
    except ImportError as exc:
        raise RuntimeError("Run: python -m pip install -r requirements-gis.txt") from exc
    geometry = shape(geometry_data)
    if geometry.is_empty or geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Expected a non-empty Polygon or MultiPolygon.")
    if not geometry.is_valid:
        raise ValueError(f"Invalid polygon topology: {explain_validity(geometry)}")
    polygons = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    rings = coordinates = 0
    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            rings += 1
            points = list(ring.coords)
            if len(points) < 4 or points[0] != points[-1]:
                raise ValueError("Polygon ring is not closed or has fewer than four coordinates.")
            coordinates += len(points)
            for lon, lat in points:
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise ValueError(f"Coordinate outside EPSG:4326: {(lon, lat)}")
    transformer = Transformer.from_crs("EPSG:4326", AREA_CRS, always_xy=True)
    projected = transform(transformer.transform, geometry)
    if not projected.is_valid or projected.area <= 0:
        raise ValueError("Projected geometry is invalid or has non-positive area.")
    return {
        "geometry_type": geometry.geom_type, "polygon_count": len(polygons),
        "ring_count": rings, "coordinate_count": coordinates,
        "is_valid": True, "validity_reason": "Valid Geometry",
        "area_crs": AREA_CRS, "area_m2": round(projected.area, 2),
        "area_km2": round(projected.area / 1_000_000, 6),
        "bounds_wgs84": [round(v, 8) for v in geometry.bounds],
    }

def build_boundary(input_pbf, output_dir):
    if not input_pbf.is_file():
        raise FileNotFoundError(f"Regional PBF not found: {input_pbf}")
    try:
        import osmium
    except ImportError as exc:
        raise RuntimeError("Install PyOsmium: pip install -r requirements-gis.txt") from exc
    class Collector(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.relation_data = None
            self.geometry = None
        def relation(self, relation):
            if relation.id == RELATION_ID:
                self.relation_data = {
                    "id": relation.id, "version": relation.version,
                    "timestamp": str(relation.timestamp),
                    "tags": {tag.k: tag.v for tag in relation.tags},
                    "members": [{"type": m.type, "ref": m.ref, "role": m.role} for m in relation.members],
                }
        def area(self, area):
            if not area.from_way() and area.orig_id() == RELATION_ID:
                self.geometry = json.loads(osmium.geom.GeoJSONFactory().create_multipolygon(area))
    handler = Collector()
    handler.apply_file(str(input_pbf))
    relation = handler.relation_data
    if relation is None:
        raise ValueError(f"Relation {RELATION_ID} not found in regional PBF.")
    tags = relation["tags"]
    english_name = validate_relation_identity(tags)
    if handler.geometry is None:
        raise ValueError("PyOsmium could not assemble the relation multipolygon.")
    validation = validate_geometry(handler.geometry)
    output_dir.mkdir(parents=True, exist_ok=True)
    geojson_path = output_dir / f"karachi-division-{RELATION_ID}.geojson"
    feature = {"type": "Feature", "properties": {
        "@type": "relation", "@id": RELATION_ID, "version": relation["version"],
        "timestamp": relation["timestamp"], "display_name_en": english_name, **tags}, "geometry": handler.geometry}
    geojson = {"type": "FeatureCollection", "name": "Karachi Division — OSM operational study boundary", "features": [feature]}
    geojson_path.write_text(json.dumps(geojson, ensure_ascii=False) + "\n", encoding="utf-8")
    metadata = {
        "status": "geometry_validated_research_candidate",
        "provider": "Geofabrik regional OSM PBF; parsed locally with PyOsmium",
        "input_pbf": input_pbf.name, "input_pbf_size_bytes": input_pbf.stat().st_size,
        "input_pbf_sha256": sha256_file(input_pbf),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "relation": relation, "relation_member_count": len(relation["members"]),
        "geojson_file": geojson_path.name, "geojson_sha256": sha256_file(geojson_path),
        "attribution": "© OpenStreetMap contributors", "license": "Open Database License 1.0 (ODbL)",
        "validation": validation,
        "limitations": ["OSM operational boundary, not government legal certification.",
            "Area is planar EPSG:32642 and must be compared with official references.",
            "District overlays are not validated.", "Independent visual review required before road extraction or production use."]
    }
    (output_dir / "boundary-validation.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pbf", type=Path, default=Path("data/osm_source/pakistan-latest.osm.pbf"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_boundary"))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed, network requests, or GIS processing.")
        print(f"Input PBF: {args.input_pbf.resolve()}"); print(f"Output: {args.output_dir.resolve()}")
        print("Install Python dependencies with pip, then pass --build.")
        return 0
    try:
        print(json.dumps(build_boundary(args.input_pbf, args.output_dir), indent=2))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
