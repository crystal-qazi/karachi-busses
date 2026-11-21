#!/usr/bin/env python3
"""Analyse the CMH Malir Cantt → Tank Chowk road corridor with connected OSM paths.

Routes the DB stop sequences around the corridor using the road-network
routing engine (app.road_network): per-leg temp split-node snapping, one-way
aware Dijkstra, cost budget. Everything is preview/analysis only — the script
never writes to the database and never invents coordinates.

Historical evidence handled explicitly: the SMTA EV-01 directory lists
"Cantt Bazar" and "Checkpost 02" between CMH Malir Cantt and Tank Chowk, but
data/research/PHASE_5_STOP_NODE_CROSSWALK.csv marks them no_exact_match /
unmatched with empty coordinates, so NO leg is computed for them and no
coordinate is invented. The gap stays visible in the report.

Usage:
    python scripts/analyze_cmh_tank_chowk_corridor.py            # dry run
    python scripts/analyze_cmh_tank_chowk_corridor.py --build    # write report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shapely.geometry import box  # noqa: E402

from app import create_app  # noqa: E402
from app.road_network import RoadGraph, route_stops  # noqa: E402
from app.snapping import load_roads  # noqa: E402
from app.database.helpers import cursor_context  # noqa: E402
from config import Config  # noqa: E402

CROSSWALK_CSV = "data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"

# Corridor stop IDs, in travel order, restricted to the CMH↔Tank Chowk
# question. EV-1 (direction 94) sequences 1-4; EV-2 (direction 95) sequences
# 5-10. Stops without coordinates cannot be included — that is the point.
CORRIDOR_DIRECTIONS = [
    {
        "label": "EV-1 (direction 94)",
        "direction_id": 94,
        "corridor_stop_ids": [514, 515, 394, 516],
        "unmatched_between": {
            "from_stop_id": 514,
            "to_stop_id": 515,
            "names": ["Cantt Bazar", "Checkpost 02"],
            "crosswalk_rows": ["EV-01 seq 2 Cantt Bazar", "EV-01 seq 3 Checkpost 02"],
        },
    },
    {
        "label": "EV-2 (direction 95)",
        "direction_id": 95,
        "corridor_stop_ids": [523, 524, 515, 443, 516],
        "unmatched_between": {
            "from_stop_id": 524,
            "to_stop_id": 515,
            "names": ["Checkpost 05", "Checkpost 06"],
            "crosswalk_rows": ["EV-02 seq 5 Checkpost 05", "EV-02 seq 6 Checkpost 06"],
        },
    },
]


def fetch_direction_stops(direction_ids: list[int]) -> dict[int, list[dict]]:
    app = create_app()
    with app.app_context():
        with cursor_context() as (conn, cur):
            placeholders = ", ".join(["%s"] * len(direction_ids))
            cur.execute(
                f"""
                SELECT rs.direction_id, rs.stop_sequence, s.id AS stop_id,
                       s.stop_name, s.latitude, s.longitude, s.status
                FROM route_stops rs
                JOIN bus_stops s ON s.id = rs.stop_id
                WHERE rs.direction_id IN ({placeholders})
                ORDER BY rs.direction_id, rs.stop_sequence
                """,
                tuple(direction_ids),
            )
            rows = cur.fetchall()
    by_direction: dict[int, list[dict]] = {}
    for row in rows:
        by_direction.setdefault(int(row["direction_id"]), []).append({
            "id": int(row["stop_id"]),
            "name": str(row["stop_name"]),
            "sequence": int(row["stop_sequence"]),
            "lat": float(row["latitude"]) if row["latitude"] is not None else None,
            "lng": float(row["longitude"]) if row["longitude"] is not None else None,
            "status": str(row["status"]),
        })
    return by_direction


def corridor_subset(all_stops: list[dict], corridor_ids: list[int]) -> list[dict]:
    """Return the corridor stops in travel order with coordinates."""
    subset = []
    for stop in all_stops:
        if stop["id"] in corridor_ids:
            if stop["lat"] is None or stop["lng"] is None:
                raise ValueError(
                    f"Stop {stop['id']} ({stop['name']}) has no coordinates; "
                    "corridor routing cannot include it.")
            subset.append(stop)
    missing = set(corridor_ids) - {s["id"] for s in subset}
    if missing:
        raise ValueError(f"Corridor stops missing from direction: {sorted(missing)}")
    return subset


def analyze_corridor(roads_path: Path) -> dict:
    roads = load_roads(roads_path)
    if roads.is_empty:
        raise ValueError("Road GeoJSON contains no usable road segments.")

    by_direction = fetch_direction_stops(
        [c["direction_id"] for c in CORRIDOR_DIRECTIONS])

    # One graph over the whole corridor bbox: the corridor spans a few km,
    # and a single shared graph lets the report show continuity across legs.
    all_corridor_stops = [
        stop
        for c in CORRIDOR_DIRECTIONS
        for stop in corridor_subset(by_direction[c["direction_id"]],
                                    c["corridor_stop_ids"])
    ]
    pad_deg = Config.ROUTE_BBOX_PAD_M / 111_000.0
    lats = [s["lat"] for s in all_corridor_stops]
    lngs = [s["lng"] for s in all_corridor_stops]
    area = box(min(lngs) - pad_deg, min(lats) - pad_deg,
               max(lngs) + pad_deg, max(lats) + pad_deg)
    parts = roads.parts_intersecting(area)
    graph = RoadGraph.from_parts(parts)

    directions_report = []
    for corridor in CORRIDOR_DIRECTIONS:
        stops = corridor_subset(by_direction[corridor["direction_id"]],
                                corridor["corridor_stop_ids"])
        result = route_stops(
            graph, roads, stops,
            max_snap_distance_m=Config.ROUTE_SNAP_MAX_DISTANCE_M,
            cost_budget_factor=Config.ROUTE_COST_BUDGET_FACTOR,
            cost_budget_extra_m=Config.ROUTE_COST_BUDGET_EXTRA_M,
        )
        directions_report.append({
            "label": corridor["label"],
            "direction_id": corridor["direction_id"],
            "corridor_stop_ids": corridor["corridor_stop_ids"],
            "stops_used": [
                {"id": s["id"], "name": s["name"], "sequence": s["sequence"],
                 "lat": s["lat"], "lng": s["lng"], "status": s["status"]}
                for s in stops
            ],
            "summary": result["summary"],
            "legs": result["legs"],
            # The unmatched SMTA directory stops are reported as an evidence
            # gap: no coordinates exist, so no leg is computed for them.
            "unmatched_between_stops": corridor["unmatched_between"],
        })

    return {
        "status": "cmh_tank_chowk_corridor_analysis_review_aid_only",
        "roads_source": str(roads_path),
        "corridor_graph": {
            "parts": len(parts),
            "nodes": len(graph.node_coords),
            "edges": graph.edge_count,
            "bbox_pad_m": Config.ROUTE_BBOX_PAD_M,
        },
        "config": {
            "route_snap_max_distance_m": Config.ROUTE_SNAP_MAX_DISTANCE_M,
            "route_cost_budget_factor": Config.ROUTE_COST_BUDGET_FACTOR,
            "route_cost_budget_extra_m": Config.ROUTE_COST_BUDGET_EXTRA_M,
        },
        "historical_evidence": {
            "crosswalk_file": CROSSWALK_CSV,
            "note": (
                "The SMTA EV-01 directory lists Cantt Bazar and Checkpost 02 "
                "between CMH Malir Cantt and Tank Chowk, and EV-02 lists "
                "Checkpost 05/06 before Tank Chowk, but the crosswalk marks "
                "them no_exact_match/unmatched with empty coordinates. They "
                "stay unmatched: no coordinates are invented and no leg is "
                "computed for them."),
        },
        "directions": directions_report,
        "junction_audit_reference": {
            "file": "data/osm_roads/tank-chowk-junction-audit.json",
            "note": (
                "Ways 522535777 + 850584014 + 545406459 form a connected "
                "triangle at the junction via 3 shared nodes; the parallel "
                "carriageways 522375908 (trunk) and 883797721 (Jinnah Ave) "
                "share no nodes with that triangle inside the audit area and "
                "all five ways are oneway."),
        },
        "limitations": [
            "Routed paths are connected-road candidates derived from current "
            "OSM data; they are not proof of the historical bus alignment.",
            "Unmatched source stops (Cantt Bazar, Checkpost 02, Checkpost 05, "
            "Checkpost 06) have no coordinates and remain unmatched.",
            "The database stop sequences themselves are unverified "
            "(under_review); nothing in this analysis changes them.",
        ],
        "attribution": "© OpenStreetMap contributors",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roads", type=Path,
        default=ROOT / "data" / "osm_roads" / "karachi-osm-bus-roads.geojson")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "data" / "osm_roads" / "cmh-tank-chowk-corridor.json")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    report = analyze_corridor(args.roads)
    if not args.build:
        print("DRY RUN: no files changed; pass --build to write the report.")
        for direction in report["directions"]:
            print(direction["label"], "->", direction["summary"])
        return 0
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for direction in report["directions"]:
        print(direction["label"], "->", direction["summary"])
    print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
