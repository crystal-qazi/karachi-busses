#!/usr/bin/env python3
"""Audit 572 historical node coordinates against nearby OSM bus-stop candidates.

Distance and exact-name evidence are review aids only. No object is assigned.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = ROOT / "data/research/PHASE_5_NODE_AUDIT.csv"
CANDIDATES = ROOT / "data/osm_stops/karachi-osm-bus-stop-candidates.geojson"
OUTPUT = ROOT / "data/osm_stops/PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT.csv"
REPORT = ROOT / "data/osm_stops/PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT_REPORT.json"
RADIUS_M = 250
AREA_CRS = "EPSG:32642"

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())

def classify_candidate(exact_name_count: int, nearby_count: int) -> str:
    if exact_name_count:
        return "exact_name_and_proximity_candidate"
    if nearby_count:
        return "proximity_only_candidates"
    return "no_candidate_within_250m"

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def audit(nodes_path: Path = NODES, candidates_path: Path = CANDIDATES,
          output_path: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    from pyproj import Transformer
    from shapely.geometry import Point, shape
    from shapely.ops import transform
    from shapely.strtree import STRtree

    with nodes_path.open(encoding="utf-8-sig", newline="") as f:
        nodes = list(csv.DictReader(f))
    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if not nodes:
        raise ValueError("Historical node audit is empty")
    if not features:
        raise ValueError("OSM bus stop candidate inventory is empty")

    transformer = Transformer.from_crs("EPSG:4326", AREA_CRS, always_xy=True)
    candidate_geometries = []
    candidate_metadata = []
    for feature in features:
        geometry = shape(feature["geometry"])
        if geometry.is_empty or not geometry.is_valid:
            continue
        projected = transform(transformer.transform, geometry)
        candidate_geometries.append(projected)
        candidate_metadata.append(feature.get("properties", {}))
    if not candidate_geometries:
        raise ValueError("No valid OSM candidate geometries")
    tree = STRtree(candidate_geometries)

    fields = [
        "historical_node_id", "latitude", "longitude", "historical_route_labels",
        "candidate_review_status", "nearby_candidate_count_within_250m",
        "exact_name_candidate_count_within_250m", "exact_name_candidate_osm_ids",
        "nearest_osm_type", "nearest_osm_id", "nearest_osm_name", "nearest_osm_kind",
        "nearest_candidate_distance_m",
    ]
    for i in range(1, 4):
        fields.extend([
            f"candidate_{i}_osm_type", f"candidate_{i}_osm_id",
            f"candidate_{i}_name", f"candidate_{i}_kind", f"candidate_{i}_distance_m",
        ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for node in nodes:
            point_wgs84 = Point(float(node["longitude"]), float(node["latitude"]))
            point = transform(transformer.transform, point_wgs84)
            indices = [int(i) for i in tree.query(point.buffer(RADIUS_M))]
            nearby = sorted(
                ((float(point.distance(candidate_geometries[i])), i) for i in indices),
                key=lambda item: (item[0], str(candidate_metadata[item[1]].get("osm_type")), int(candidate_metadata[item[1]].get("osm_id", 0))),
            )
            nearby = [(distance, i) for distance, i in nearby if distance <= RADIUS_M]
            if not nearby:
                nearest_index = int(tree.nearest(point))
                nearest = [(float(point.distance(candidate_geometries[nearest_index])), nearest_index)]
            else:
                nearest = nearby

            node_name = normalize(node["node_id"].replace("_", " "))
            exact = []
            for distance, index in nearby:
                props = candidate_metadata[index]
                candidate_names = {
                    normalize(str(props.get("name") or "")),
                    normalize(str(props.get("name_en") or "")),
                } - {""}
                if node_name and node_name in candidate_names:
                    exact.append((distance, index))

            status = classify_candidate(len(exact), len(nearby))
            nearest_distance, nearest_index = nearest[0]
            nearest_props = candidate_metadata[nearest_index]
            row = {
                "historical_node_id": node["node_id"],
                "latitude": node["latitude"],
                "longitude": node["longitude"],
                "historical_route_labels": node.get("historical_route_labels", ""),
                "candidate_review_status": status,
                "nearby_candidate_count_within_250m": len(nearby),
                "exact_name_candidate_count_within_250m": len(exact),
                "exact_name_candidate_osm_ids": ";".join(
                    f'{candidate_metadata[i].get("osm_type")}/{candidate_metadata[i].get("osm_id")}'
                    for _, i in exact
                ),
                "nearest_osm_type": nearest_props.get("osm_type", ""),
                "nearest_osm_id": nearest_props.get("osm_id", ""),
                "nearest_osm_name": nearest_props.get("name") or nearest_props.get("name_en") or "",
                "nearest_osm_kind": nearest_props.get("candidate_kind", ""),
                "nearest_candidate_distance_m": round(nearest_distance, 2),
            }
            for slot in range(1, 4):
                if slot <= len(nearby):
                    distance, index = nearby[slot - 1]
                    props = candidate_metadata[index]
                    row.update({
                        f"candidate_{slot}_osm_type": props.get("osm_type", ""),
                        f"candidate_{slot}_osm_id": props.get("osm_id", ""),
                        f"candidate_{slot}_name": props.get("name") or props.get("name_en") or "",
                        f"candidate_{slot}_kind": props.get("candidate_kind", ""),
                        f"candidate_{slot}_distance_m": round(distance, 2),
                    })
                else:
                    for key in ("osm_type", "osm_id", "name", "kind", "distance_m"):
                        row[f"candidate_{slot}_{key}"] = ""
            writer.writerow(row)
            counts[status] += 1
            if len(nearby) > 1:
                counts["historical_nodes_with_multiple_nearby_candidates"] += 1

    report = {
        "status": "osm_proximity_and_name_audit_not_physical_stop_verification",
        "historical_node_rows": len(nodes),
        "osm_candidate_features": len(candidate_geometries),
        "search_radius_m": RADIUS_M,
        "area_crs": AREA_CRS,
        "counts": dict(sorted(counts.items())),
        "inputs": {
            "historical_node_audit_sha256": sha256_file(nodes_path),
            "osm_candidate_inventory_sha256": sha256_file(candidates_path),
        },
        "output": {"csv": output_path.name, "sha256": sha256_file(output_path), "rows": len(nodes)},
        "limitations": [
            "Exact name and proximity matches are review candidates only, not physical-stop confirmation.",
            "Nearest OSM geometry is not assigned as a boarding coordinate.",
            "No route code is assigned to OSM objects and no historical coordinate is changed.",
            "No fuzzy name matching, geocoding, snapping, route geometry, or database write is performed.",
            "All 572 historical records remain unverified pending field/operator evidence.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed.")
        print(f"Historical nodes: {NODES}")
        print(f"OSM candidate inventory: {CANDIDATES}")
        print(f"Output: {OUTPUT}")
        return 0
    try:
        print(json.dumps(audit(), indent=2))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
