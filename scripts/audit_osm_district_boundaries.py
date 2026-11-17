#!/usr/bin/env python3
"""Audit the seven OSM district subareas of Karachi Division; pip-only GIS."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PARENT_RELATION_ID = 6080948
EXPECTED_DISTRICTS = {
    "Karachi Central": {"karachi central", "karachi central district", "central district", "nazimabad district"},
    "Karachi East": {"karachi east", "karachi east district", "east district"},
    "Karachi South": {"karachi south", "karachi south district", "south district"},
    "Karachi West": {"karachi west", "karachi west district", "west district"},
    "Keamari": {"keamari", "keamari district", "karachi keamari", "karachi keamari district"},
    "Korangi": {"korangi", "korangi district", "karachi korangi", "karachi korangi district"},
    "Malir": {"malir", "malir district", "karachi malir", "karachi malir district"},
}
AREA_CRS = "EPSG:32642"


def normalize_name(value):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()


def classify_district(tags):
    candidates = [
        tags.get("name:en"), tags.get("official_name:en"),
        tags.get("alt_name:en"), tags.get("name"),
    ]
    normalized = {normalize_name(value) for value in candidates if value}
    for district, aliases in EXPECTED_DISTRICTS.items():
        if normalized.intersection(aliases):
            return district
    # OSM's Central district relation is currently named "Nazimabad District".
    if tags.get("wikipedia") == "en:Karachi Central District":
        return "Karachi Central"
    return None


def relation_member_ids(pbf_path):
    import osmium

    class Parent(osmium.SimpleHandler):
        members = None
        def relation(self, relation):
            if relation.id == PARENT_RELATION_ID:
                self.members = [
                    member.ref for member in relation.members
                    if member.type == "r" and member.role == "subarea"
                ]

    handler = Parent()
    handler.apply_file(str(pbf_path))
    if handler.members is None:
        raise ValueError(f"Parent relation {PARENT_RELATION_ID} not found.")
    if len(handler.members) != 7:
        raise ValueError(f"Expected 7 relation subareas, found {len(handler.members)}: {handler.members}")
    return handler.members


def audit_districts(pbf_path, output_dir):
    import osmium
    from pyproj import Geod, Transformer
    from shapely.geometry import shape, mapping
    from shapely.ops import transform, unary_union
    from shapely.validation import explain_validity

    child_ids = set(relation_member_ids(pbf_path))

    class Selected(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.relations = {}
            self.geometries = {}
        def relation(self, relation):
            if relation.id in child_ids:
                self.relations[relation.id] = {
                    "id": relation.id,
                    "version": relation.version,
                    "timestamp": str(relation.timestamp),
                    "tags": {tag.k: tag.v for tag in relation.tags},
                }
        def area(self, area):
            if not area.from_way() and area.orig_id() in child_ids:
                self.geometries[area.orig_id()] = json.loads(
                    osmium.geom.GeoJSONFactory().create_multipolygon(area)
                )

    handler = Selected()
    handler.apply_file(str(pbf_path))
    missing_relations = sorted(child_ids - set(handler.relations))
    missing_geometries = sorted(child_ids - set(handler.geometries))
    if missing_relations or missing_geometries:
        raise ValueError(
            f"Missing child relations={missing_relations}; missing assembled areas={missing_geometries}"
        )

    transformer = Transformer.from_crs("EPSG:4326", AREA_CRS, always_xy=True)
    geod = Geod(ellps="WGS84")
    features = []
    rows = []
    geometries = []
    for relation_id in sorted(child_ids):
        relation = handler.relations[relation_id]
        tags = relation["tags"]
        if tags.get("boundary") != "administrative" or tags.get("admin_level") != "6":
            raise ValueError(f"Child relation {relation_id} is not an admin_level=6 boundary: {tags}")
        geom_data = handler.geometries[relation_id]
        geom = shape(geom_data)
        if geom.is_empty or not geom.is_valid:
            raise ValueError(f"Invalid district geometry {relation_id}: {explain_validity(geom)}")
        projected = transform(transformer.transform, geom)
        geodesic_area, perimeter = geod.geometry_area_perimeter(geom)
        matched = classify_district(tags)
        properties = {
            "@type": "relation", "@id": relation_id,
            "display_name_en": tags.get("name:en") or tags.get("name"),
            "matched_official_district": matched,
            "version": relation["version"], "timestamp": relation["timestamp"],
            **tags,
        }
        features.append({"type": "Feature", "properties": properties, "geometry": mapping(geom)})
        geometries.append((relation_id, geom, projected))
        rows.append({
            "relation_id": relation_id,
            "name": tags.get("name"),
            "name_en": tags.get("name:en"),
            "admin_level": tags.get("admin_level"),
            "matched_official_district": matched,
            "area_km2_epsg32642": round(projected.area / 1_000_000, 6),
            "area_km2_geodesic": round(abs(geodesic_area) / 1_000_000, 6),
            "perimeter_km": round(perimeter / 1000, 3),
            "valid": True,
        })

    parent_handler = type("ParentGeometry", (osmium.SimpleHandler,), {
        "__init__": lambda self: (osmium.SimpleHandler.__init__(self), setattr(self, "geometry", None))[-1],
        "area": lambda self, area: setattr(
            self, "geometry",
            json.loads(osmium.geom.GeoJSONFactory().create_multipolygon(area))
        ) if not area.from_way() and area.orig_id() == PARENT_RELATION_ID else None,
    })()
    parent_handler.apply_file(str(pbf_path))
    if parent_handler.geometry is None:
        raise ValueError("Could not reassemble parent Karachi Division geometry.")
    parent = shape(parent_handler.geometry)
    parent_projected = transform(transformer.transform, parent)
    district_union = unary_union([item[1] for item in geometries])
    union_projected = transform(transformer.transform, district_union)
    gap_km2 = parent_projected.difference(union_projected).area / 1_000_000
    excess_km2 = union_projected.difference(parent_projected).area / 1_000_000
    overlap_km2 = (
        sum(item[2].area for item in geometries) - union_projected.area
    ) / 1_000_000
    matched_names = sorted({row["matched_official_district"] for row in rows if row["matched_official_district"]})
    missing_official = sorted(set(EXPECTED_DISTRICTS) - set(matched_names))
    duplicates = sorted(name for name in matched_names if sum(r["matched_official_district"] == name for r in rows) > 1)

    output_dir.mkdir(parents=True, exist_ok=True)
    districts_path = output_dir / "karachi-districts-osm-subareas.geojson"
    districts_geojson = {
        "type": "FeatureCollection",
        "name": "Karachi Division — OSM district subarea relations",
        "features": features,
    }
    districts_path.write_text(json.dumps(districts_geojson, ensure_ascii=False) + "\n", encoding="utf-8")

    parent_feature = {
        "type": "Feature",
        "properties": {"name": "Karachi Division", "@id": PARENT_RELATION_ID},
        "geometry": mapping(parent),
    }
    preview_data = json.dumps(
        {"division": {"type": "FeatureCollection", "features": [parent_feature]},
         "districts": districts_geojson},
        ensure_ascii=False,
    ).replace("</", "<\\/")
    preview_html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Karachi OSM Boundary Audit</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>html,body,#map{height:100%;margin:0}#panel{position:absolute;z-index:1000;top:12px;left:52px;background:#fff;padding:12px 15px;border-radius:8px;max-width:340px;font:14px/1.4 system-ui;box-shadow:0 1px 8px #777}#map{height:100vh}</style></head>
<body><div id="panel"><b>Karachi OSM boundary audit</b><div>Blue: Division relation 6080948</div><div>Colored lines: seven subarea relations</div><div>© OpenStreetMap contributors · ODbL</div><div>Research preview only — not legal boundary certification.</div></div><div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
const data = __DATA__;
const map=L.map('map');L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
const division=L.geoJSON(data.division,{style:{color:'#1769aa',weight:3,fillOpacity:0.04}}).addTo(map);
const districts=L.geoJSON(data.districts,{style:f=>({color:['#d94841','#2b8a3e','#7048e8','#e67700','#0b7285','#c2255c','#495057'][Math.abs(Number(f.properties['@id']))%7],weight:2,fillOpacity:0.08}),onEachFeature:(f,l)=>l.bindPopup((f.properties.display_name_en||f.properties.name||'District')+' · relation '+f.properties['@id'])}).addTo(map);
map.fitBounds(division.getBounds());L.control.layers(null,{'Division boundary':division,'District subareas':districts}).addTo(map);
</script></body></html>""".replace("__DATA__", preview_data)
    preview_path = output_dir / "karachi-boundary-preview.html"
    preview_path.write_text(preview_html, encoding="utf-8")

    report = {
        "status": "district_subarea_audit_complete",
        "parent_relation_id": PARENT_RELATION_ID,
        "child_relation_ids": sorted(child_ids),
        "expected_official_districts": sorted(EXPECTED_DISTRICTS),
        "matched_official_districts": matched_names,
        "missing_official_districts": missing_official,
        "duplicate_official_matches": duplicates,
        "district_count": len(rows),
        "districts": rows,
        "parent_area_km2_epsg32642": round(parent_projected.area / 1_000_000, 6),
        "district_union_area_km2_epsg32642": round(union_projected.area / 1_000_000, 6),
        "parent_area_not_covered_by_districts_km2": round(gap_km2, 6),
        "district_area_outside_parent_km2": round(excess_km2, 6),
        "overlap_between_districts_km2": round(overlap_km2, 6),
        "union_matches_parent_within_1_km2": abs(gap_km2) <= 1 and abs(excess_km2) <= 1,
        "official_area_references_km2": [
            {"area_km2": 3527, "source": "Commissioner Karachi — Area & Maps", "url": "https://www.commissionerkarachi.gos.pk/area-maps"},
            {"area_km2": 3640, "source": "The Urban Unit — Karachi City Climate Risk Assessment (2024)", "url": "https://urbanunit.gov.pk/Download/Project%20files/8/Deliverable%20D_CCRA_FD_17042024.pdf"},
            {"area_km2": 7134.669, "source": "Geoview OSM relation summary; secondary, non-official", "url": "https://pk.geoview.info/krachy_dwyzhn%2C6080948r"},
        ],
        "limitations": [
            "OSM subarea membership and names require comparison with official district sources.",
            "Area figures from different sources may reflect different administrative vintages or extents.",
            "Do not clip roads or publish as an authoritative boundary until gaps, overlaps and area discrepancy are resolved.",
        ],
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License 1.0 (ODbL)",
        "outputs": [districts_path.name, preview_path.name],
    }
    report_path = output_dir / "district-boundary-audit.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pbf", type=Path, default=Path("data/osm_source/pakistan-latest.osm.pbf"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_boundary"))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed, network requests, or GIS processing.")
        print(f"Input PBF: {args.input_pbf.resolve()}")
        print(f"Output: {args.output_dir.resolve()}")
        return 0
    try:
        print(json.dumps(audit_districts(args.input_pbf, args.output_dir), indent=2))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
