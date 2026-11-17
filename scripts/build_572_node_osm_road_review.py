#!/usr/bin/env python3
"""Build a read-only OSM road-proximity register for all 572 historical nodes.

No geocoding, snapping, route inference, source mutation, or database writes.
Requires the pip-installable packages in requirements-gis.txt.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

CRS = "EPSG:32642"
RADIUS_M = 250.0
BANDS = ((15, "0-15m"), (50, "15-50m"), (100, "50-100m"), (250, "100-250m"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def band(distance: float) -> str:
    for upper, label in BANDS:
        if distance <= upper:
            return label
    return ">250m"


def read_rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def build_register(nodes_path: Path, crosswalk_path: Path, roads_path: Path,
                   boundary_path: Path, output_dir: Path) -> dict:
    # Imports are intentionally local so basic CLI/help and input validation remain light.
    from pyproj import Transformer
    from shapely.geometry import Point, shape
    from shapely.ops import transform
    from shapely.strtree import STRtree

    nodes_path, crosswalk_path, roads_path, boundary_path, output_dir = map(
        Path, (nodes_path, crosswalk_path, roads_path, boundary_path, output_dir)
    )
    nodes = read_rows(nodes_path, {
        "node_id", "latitude", "longitude", "historical_route_labels",
        "route_label_count", "coordinate_collision_group",
    })
    crosswalk = read_rows(crosswalk_path, {
        "route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id",
    })
    if len(nodes) != 572:
        raise ValueError(f"Expected exactly 572 source coordinate nodes; found {len(nodes)}")

    node_by_id: dict[str, dict[str, str]] = {}
    candidate_refs: dict[str, list[str]] = defaultdict(list)
    for row in nodes:
        node_id = row["node_id"].strip()
        if not node_id or node_id in node_by_id:
            raise ValueError(f"Blank or duplicate node ID: {node_id!r}")
        lat, lon = float(row["latitude"]), float(row["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinate for {node_id}: {lat}, {lon}")
        node_by_id[node_id] = row
    for row in crosswalk:
        node_id = row["coordinate_node_id"].strip()
        if node_id:
            if node_id not in node_by_id:
                raise ValueError(f"Crosswalk references unknown node: {node_id}")
            candidate_refs[node_id].append(
                f'{row["route_code"]}#{row["source_stop_sequence"]}:{row["source_stop_name"]}'
            )

    boundary_data = json.loads(boundary_path.read_text(encoding="utf-8"))
    parents = [
        feature for feature in boundary_data.get("features", [])
        if feature.get("properties", {}).get("@id") == 6080948
    ]
    if len(parents) != 1:
        raise ValueError("Expected exactly one OSM parent relation 6080948")
    parent = shape(parents[0]["geometry"])
    if parent.is_empty or not parent.is_valid:
        raise ValueError("OSM parent boundary is invalid")

    transformer = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
    road_data = json.loads(roads_path.read_text(encoding="utf-8"))
    lines, properties = [], []
    for feature in road_data.get("features", []):
        try:
            geometry = transform(transformer.transform, shape(feature["geometry"]))
            if not geometry.is_empty and geometry.is_valid and geometry.length > 0:
                lines.append(geometry)
                properties.append(feature.get("properties", {}))
        except (KeyError, TypeError, ValueError):
            continue
    if not lines:
        raise ValueError("No valid OSM road geometries found")
    tree = STRtree(lines)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "karachi-572-node-osm-road-review.csv"
    fields = [
        "node_id", "latitude", "longitude", "historical_route_labels", "route_label_count",
        "coordinate_collision_group", "candidate_smta_stop_refs", "candidate_smta_ref_count",
        "nearest_osm_way_id", "nearest_road_name", "nearest_highway", "nearest_oneway",
        "nearest_access", "nearest_distance_m", "proximity_band",
        "candidate_roads_within_250m", "nearby_osm_candidates", "audit_status", "review_note",
    ]
    counts = Counter()
    collision_nodes = 0
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for node_id, row in node_by_id.items():
            lat, lon = float(row["latitude"]), float(row["longitude"])
            refs = candidate_refs.get(node_id, [])
            out = {
                "node_id": node_id, "latitude": lat, "longitude": lon,
                "historical_route_labels": row["historical_route_labels"],
                "route_label_count": row["route_label_count"],
                "coordinate_collision_group": row["coordinate_collision_group"],
                "candidate_smta_stop_refs": json.dumps(refs, ensure_ascii=False),
                "candidate_smta_ref_count": len(refs),
            }
            if row["coordinate_collision_group"]:
                collision_nodes += 1
            point_wgs84 = Point(lon, lat)
            if not parent.covers(point_wgs84):
                out.update({
                    "audit_status": "outside_osm_parent_boundary",
                    "review_note": "Historical source coordinate is outside OSM relation 6080948; no road candidate assigned.",
                })
                counts["outside_osm_parent_boundary"] += 1
                writer.writerow(out)
                continue

            point = transform(transformer.transform, point_wgs84)
            indexes = tree.query(point.buffer(RADIUS_M))
            candidates = []
            for index in indexes:
                i = int(index)
                distance = float(point.distance(lines[i]))
                if distance <= RADIUS_M:
                    prop = properties[i]
                    tags = prop.get("tags", {})
                    candidates.append((distance, i, prop, tags))
            candidates.sort(key=lambda item: (item[0], str(item[2].get("@id", ""))))
            unique, seen = [], set()
            for item in candidates:
                way_id = item[2].get("@id")
                if way_id in seen:
                    continue
                seen.add(way_id)
                unique.append(item)
                if len(unique) == 5:
                    break

            if unique:
                distance, _, prop, tags = unique[0]
                nearby = [{
                    "osm_way_id": item[2].get("@id"),
                    "name": item[3].get("name"),
                    "highway": item[3].get("highway"),
                    "oneway": item[3].get("oneway"),
                    "access": item[3].get("access"),
                    "distance_m": round(item[0], 2),
                } for item in unique]
                out.update({
                    "nearest_osm_way_id": prop.get("@id", ""),
                    "nearest_road_name": tags.get("name", ""),
                    "nearest_highway": tags.get("highway", ""),
                    "nearest_oneway": tags.get("oneway", ""),
                    "nearest_access": tags.get("access", ""),
                    "nearest_distance_m": round(distance, 2),
                    "proximity_band": band(distance),
                    "candidate_roads_within_250m": len(candidates),
                    "nearby_osm_candidates": json.dumps(nearby, ensure_ascii=False, separators=(",", ":")),
                    "audit_status": "proximity_only_unverified",
                    "review_note": "Geometric proximity only; does not verify stop identity, road side, platform, bus access, or route use.",
                })
                counts["proximity_only_unverified"] += 1
            else:
                nearest_index = int(tree.nearest(point))
                distance = float(point.distance(lines[nearest_index]))
                prop = properties[nearest_index]
                tags = prop.get("tags", {})
                out.update({
                    "nearest_osm_way_id": prop.get("@id", ""),
                    "nearest_road_name": tags.get("name", ""),
                    "nearest_highway": tags.get("highway", ""),
                    "nearest_oneway": tags.get("oneway", ""),
                    "nearest_access": tags.get("access", ""),
                    "nearest_distance_m": round(distance, 2),
                    "proximity_band": band(distance),
                    "candidate_roads_within_250m": 0,
                    "nearby_osm_candidates": "[]",
                    "audit_status": "nearest_road_over_250m",
                    "review_note": "Nearest road is over 250m away; geometric proximity only and not a stop verification.",
                })
                counts["nearest_road_over_250m"] += 1
            writer.writerow(out)

    report = {
        "status": "572_node_osm_road_proximity_register_complete_not_stop_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "node_source": nodes_path.name, "node_source_sha256": sha256(nodes_path),
        "crosswalk_source": crosswalk_path.name, "crosswalk_source_sha256": sha256(crosswalk_path),
        "road_source": "OpenStreetMap candidate road network clipped to relation 6080948",
        "road_geojson_sha256": sha256(roads_path),
        "boundary_source": "OpenStreetMap relation 6080948",
        "boundary_sha256": sha256(boundary_path),
        "crs_for_distance": CRS, "search_radius_m": RADIUS_M,
        "source_node_count": len(nodes), "output_node_count": sum(counts.values()),
        "candidate_smta_stop_refs": sum(len(v) for v in candidate_refs.values()),
        "distinct_nodes_with_smta_candidate_refs": len(candidate_refs),
        "coordinate_collision_node_count": collision_nodes,
        "counts": dict(sorted(counts.items())),
        "output_csv": csv_path.name, "output_csv_sha256": sha256(csv_path),
        "limitations": [
            "All 572 source points remain historical coordinate candidates, not verified passenger stops.",
            "Nearest OSM road does not establish bus service, boarding side, platform, direction, or accessibility.",
            "No snapping, geocoding, route construction, access inference, database writes, or source mutation.",
            "OSM access, one-way, bus, vehicle, and conditional restrictions need separate interpretation.",
            "Manual, operator, or field evidence is required before any stop or route can be approved.",
        ],
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License 1.0 (ODbL)",
        "database_writes": False,
        "geocoding_or_snapping": False,
    }
    (output_dir / "karachi-572-node-osm-road-review-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=Path, default=Path("data/research/PHASE_5_NODE_AUDIT.csv"))
    parser.add_argument("--crosswalk", type=Path, default=Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"))
    parser.add_argument("--roads", type=Path, required=True)
    parser.add_argument("--boundary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/phase5s"))
    args = parser.parse_args()
    report = build_register(args.nodes, args.crosswalk, args.roads, args.boundary, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
