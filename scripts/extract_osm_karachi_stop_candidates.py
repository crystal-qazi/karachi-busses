#!/usr/bin/env python3
"""Extract OSM bus-stop/platform candidates inside Karachi Division.

This is an OSM feature inventory only. It does not verify SMTA service, assign
historical stops, or infer boarding points and routes.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, shutil, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PARENT_RELATION_ID = 6080948

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def is_bus_stop_candidate(tags: dict[str, str]) -> bool:
    if tags.get("highway") == "bus_stop":
        return True
    if tags.get("amenity") == "bus_station":
        return True
    if tags.get("highway") == "platform" and tags.get("bus") in {"yes", "designated"}:
        return True
    if tags.get("public_transport") in {"platform", "stop_position", "station"}:
        return tags.get("bus") in {"yes", "designated"} or tags.get("route") == "bus"
    return False

def candidate_kind(tags: dict[str, str]) -> str:
    if tags.get("amenity") == "bus_station":
        return "bus_station"
    if tags.get("highway") == "bus_stop":
        return "highway_bus_stop"
    if tags.get("public_transport") == "stop_position":
        return "bus_stop_position"
    if tags.get("public_transport") == "platform" or tags.get("highway") == "platform":
        return "bus_platform"
    return "bus_transit_feature"

def clip_candidate_geometry(geometry, boundary):
    if geometry.is_empty or not geometry.is_valid:
        return None
    clipped = geometry.intersection(boundary)
    if clipped.is_empty or not clipped.is_valid:
        return None
    return clipped

def extract_candidates(input_pbf: Path, boundary_path: Path, output_dir: Path) -> dict:
    import osmium
    from shapely.geometry import Point, LineString, Polygon, shape, mapping
    input_pbf, boundary_path, output_dir = Path(input_pbf), Path(boundary_path), Path(output_dir)
    if not input_pbf.is_file():
        raise FileNotFoundError(f"OSM PBF not found: {input_pbf}")
    if not boundary_path.is_file():
        raise FileNotFoundError(f"Karachi OSM boundary not found: {boundary_path}")
    boundary_data = json.loads(boundary_path.read_text(encoding="utf-8"))
    features = [f for f in boundary_data.get("features", []) if f.get("properties", {}).get("@id") == PARENT_RELATION_ID]
    if len(features) != 1:
        raise ValueError(f"Expected exactly one Karachi Division relation {PARENT_RELATION_ID}")
    boundary = shape(features[0]["geometry"])
    if boundary.is_empty or not boundary.is_valid:
        raise ValueError("Karachi Division boundary is empty or invalid")

    output_dir.mkdir(parents=True, exist_ok=True)
    geojson_path = output_dir / "karachi-osm-bus-stop-candidates.geojson"
    compressed_path = output_dir / "karachi-osm-bus-stop-candidates.geojson.gz"
    counts = Counter()
    seen = set()
    feature_count = 0

    def write_feature(stream, osm_type, osm_id, version, timestamp, tags, geometry):
        nonlocal feature_count
        key = (osm_type, int(osm_id))
        if key in seen:
            counts["duplicate_osm_objects_skipped"] += 1
            return
        seen.add(key)
        props = {
            "osm_type": osm_type, "osm_id": int(osm_id), "version": int(version),
            "timestamp": str(timestamp), "candidate_kind": candidate_kind(tags),
            "name": tags.get("name"), "name_en": tags.get("name:en"),
            "ref": tags.get("ref"), "operator": tags.get("operator"),
            "network": tags.get("network"), "bus": tags.get("bus"),
            "public_transport": tags.get("public_transport"),
            "highway": tags.get("highway"), "amenity": tags.get("amenity"),
            "tags": tags, "geometry_clipped_to_parent_boundary": True,
            "physical_stop_verification": "unverified",
            "smta_route_assignment": "not_assigned",
        }
        feature = {"type": "Feature", "id": f"{osm_type}/{osm_id}", "properties": props, "geometry": mapping(geometry)}
        if feature_count:
            stream.write(",\n")
        stream.write(json.dumps(feature, ensure_ascii=False, separators=(",", ":")))
        feature_count += 1
        counts[f"osm_type:{osm_type}"] += 1
        counts[f"kind:{props['candidate_kind']}"] += 1
        if not props["name"]:
            counts["unnamed_candidates"] += 1

    with geojson_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write('{"type":"FeatureCollection","name":"Karachi OSM bus stop and platform candidates","features":[\n')
        class StopHandler(osmium.SimpleHandler):
            def node(self, node):
                tags = {t.k: t.v for t in node.tags}
                if not is_bus_stop_candidate(tags):
                    return
                try:
                    if not node.location.valid():
                        counts["invalid_node_location"] += 1
                        return
                    point = Point(node.location.lon, node.location.lat)
                    if not boundary.covers(point):
                        counts["outside_parent_boundary"] += 1
                        return
                    write_feature(stream, "node", node.id, node.version, node.timestamp, tags, point)
                except Exception:
                    counts["node_geometry_error"] += 1

            def way(self, way):
                tags = {t.k: t.v for t in way.tags}
                if not is_bus_stop_candidate(tags):
                    return
                try:
                    nodes = list(way.nodes)
                    coords = [(n.lon, n.lat) for n in nodes if n.location.valid()]
                    if len(coords) < 2 or len(coords) != len(nodes):
                        counts["incomplete_way_geometry"] += 1
                        return
                    if way.is_closed() and len(coords) >= 4 and tags.get("area") != "no":
                        geom = Polygon(coords)
                    else:
                        geom = LineString(coords)
                    if geom.is_empty or not geom.is_valid:
                        counts["invalid_way_geometry"] += 1
                        return
                    clipped = clip_candidate_geometry(geom, boundary)
                    if clipped is None:
                        counts["outside_or_invalid_parent_boundary"] += 1
                        return
                    write_feature(stream, "way", way.id, way.version, way.timestamp, tags, clipped)
                except Exception:
                    counts["way_geometry_error"] += 1

        handler = StopHandler()
        handler.apply_file(str(input_pbf), locations=True)
        stream.write("\n]}\n")

    with geojson_path.open("rb") as source, gzip.open(compressed_path, "wb", compresslevel=6) as target:
        shutil.copyfileobj(source, target)

    report = {
        "status": "osm_transit_feature_inventory_not_physical_stop_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_provider": "Geofabrik Pakistan regional OSM PBF",
        "source_pbf_name": input_pbf.name,
        "source_pbf_sha256": sha256_file(input_pbf),
        "boundary_source": f"OpenStreetMap relation {PARENT_RELATION_ID} (Karachi Division)",
        "boundary_sha256": sha256_file(boundary_path),
        "feature_count": feature_count,
        "counts": dict(sorted(counts.items())),
        "outputs": {
            "geojson": geojson_path.name,
            "geojson_sha256": sha256_file(geojson_path),
            "compressed_geojson": compressed_path.name,
            "compressed_size_bytes": compressed_path.stat().st_size,
        },
        "selection": {
            "included": ["highway=bus_stop", "amenity=bus_station", "bus-tagged public_transport platform/stop_position/station", "bus-tagged highway=platform"],
            "excluded": ["generic rail-only platforms/stations without bus tags", "unrelated transport features"],
            "geometry": "OSM node points and clipped way geometry; no centroid or inferred boarding point is created",
        },
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License 1.0 (ODbL)",
        "limitations": [
            "OSM features are community-mapped candidates, not SMTA-confirmed stops or proof of current bus service.",
            "No historical stop names or coordinates are joined or assigned.",
            "No boarding side, stop pole, accessibility, route direction, or live dispatch is verified.",
            "No route geometry or database write is performed.",
        ],
    }
    (output_dir / "bus-stop-candidate-extraction-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pbf", type=Path, default=Path("data/osm_source/pakistan-latest.osm.pbf"))
    parser.add_argument("--boundary", type=Path, default=Path("data/osm_boundary/karachi-division-6080948.geojson"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_stops"))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no PBF parsing or files changed.")
        print(f"Input PBF: {args.input_pbf.resolve()}")
        print(f"Boundary: {args.boundary.resolve()}")
        print(f"Output: {args.output_dir.resolve()}")
        return 0
    try:
        print(json.dumps(extract_candidates(args.input_pbf, args.boundary, args.output_dir), indent=2))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
