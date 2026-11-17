#!/usr/bin/env python3
"""Build and validate the Karachi Division polygon from a local OSM relation extract.

Requires Osmium Tool, Shapely and pyproj. No network access or application DB
access is performed. Output is research-only and must be reviewed before use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RELATION_ID = 6080948
OSM_ATTRIBUTION = "© OpenStreetMap contributors"
OSM_LICENSE = "Open Database License 1.0 (ODbL)"
AREA_CRS = "EPSG:32642"  # WGS 84 / UTM zone 42N; Karachi lies in zone 42N.


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_relation_feature(collection: dict) -> dict:
    if collection.get("type") != "FeatureCollection":
        raise ValueError("Osmium output is not a GeoJSON FeatureCollection.")
    matches = []
    for feature in collection.get("features", []):
        props = feature.get("properties") or {}
        if str(props.get("@id", props.get("id", ""))) == str(RELATION_ID) and props.get("@type", props.get("type")) == "relation":
            matches.append(feature)
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one polygon feature for relation {RELATION_ID}; found {len(matches)}."
        )
    feature = matches[0]
    if feature.get("geometry", {}).get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Selected relation did not export as Polygon or MultiPolygon.")
    return feature


def validate_geometry(feature: dict) -> dict:
    try:
        from shapely.geometry import shape
        from shapely.validation import explain_validity
        from pyproj import Transformer
    except ImportError as exc:
        raise RuntimeError(
            "GIS dependencies missing. Install with: pip install -r requirements-gis.txt"
        ) from exc

    geometry = shape(feature["geometry"])
    if geometry.is_empty:
        raise ValueError("Boundary geometry is empty.")
    if not geometry.is_valid:
        raise ValueError(f"Invalid polygon topology: {explain_validity(geometry)}")
    if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError(f"Unexpected geometry type: {geometry.geom_type}")

    # Check longitude/latitude ranges and all polygon rings are closed.
    coords = []
    polygons = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    ring_count = 0
    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            ring_count += 1
            points = list(ring.coords)
            if len(points) < 4 or points[0] != points[-1]:
                raise ValueError("Polygon ring is not closed or has fewer than four coordinates.")
            for lon, lat in points:
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise ValueError(f"Coordinate outside EPSG:4326 range: {(lon, lat)}")
            coords.extend(points)

    transformer = Transformer.from_crs("EPSG:4326", AREA_CRS, always_xy=True)
    projected = __import__("shapely.ops", fromlist=["transform"]).transform(
        transformer.transform, geometry
    )
    if not projected.is_valid or projected.area <= 0:
        raise ValueError("Projected boundary is invalid or has non-positive area.")

    return {
        "geometry_type": geometry.geom_type,
        "polygon_count": len(polygons),
        "ring_count": ring_count,
        "coordinate_count": len(coords),
        "is_valid": True,
        "validity_reason": "Valid Geometry",
        "area_crs": AREA_CRS,
        "area_m2": round(projected.area, 2),
        "area_km2": round(projected.area / 1_000_000, 6),
        "bounds_wgs84": [round(v, 8) for v in geometry.bounds],
    }


def build_boundary(relation_xml: Path, output_dir: Path) -> dict:
    if not relation_xml.is_file():
        raise FileNotFoundError(f"Relation XML not found: {relation_xml}")
    osmium = shutil.which("osmium")
    if not osmium:
        raise FileNotFoundError("Osmium Tool is not installed or not available on PATH.")

    output_dir.mkdir(parents=True, exist_ok=True)
    intermediate = output_dir / f"osm-export-{RELATION_ID}.geojson.tmp"
    output_geojson = output_dir / f"karachi-division-{RELATION_ID}.geojson"
    command = [
        osmium, "export", "--stop-on-error", "--geometry-types=polygon",
        "--attributes=id,version,timestamp", "-o", str(intermediate),
        str(relation_xml),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        collection = json.loads(intermediate.read_text(encoding="utf-8"))
        feature = find_relation_feature(collection)
        validation = validate_geometry(feature)
        output = {
            "type": "FeatureCollection",
            "name": "Karachi Division — OSM operational study boundary",
            "features": [feature],
        }
        output_geojson.write_text(json.dumps(output, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        intermediate.unlink(missing_ok=True)

    metadata = {
        "status": "geometry_validated_research_candidate",
        "relation_id": RELATION_ID,
        "relation_xml": relation_xml.name,
        "relation_xml_sha256": sha256_file(relation_xml),
        "geojson_file": output_geojson.name,
        "geojson_sha256": sha256_file(output_geojson),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": f"https://www.openstreetmap.org/relation/{RELATION_ID}",
        "source_relation_tags": feature.get("properties", {}),
        "attribution": OSM_ATTRIBUTION,
        "license": OSM_LICENSE,
        "validation": validation,
        "limitations": [
            "OSM operational boundary, not a government legal certification.",
            "Area is a planar measurement in EPSG:32642 and must be compared with official references.",
            "District overlays are not validated by this operation.",
            "Independent visual review is required before road extraction or production use.",
        ],
    }
    (output_dir / "boundary-validation.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--relation-xml", type=Path,
                        default=Path("data/osm_boundary/osm-relation-6080948-full.osm"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_boundary"))
    parser.add_argument("--build", action="store_true",
                        help="Assemble the relation polygon, validate topology and write research GeoJSON.")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed and no GIS processing performed.")
        print(f"Relation XML: {args.relation_xml.resolve()}")
        print(f"Output: {args.output_dir.resolve()}")
        print("Run with --build after Phase 5J relation extraction and GIS dependency installation.")
        return 0
    try:
        print(json.dumps(build_boundary(args.relation_xml, args.output_dir), indent=2))
    except (OSError, subprocess.CalledProcessError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
