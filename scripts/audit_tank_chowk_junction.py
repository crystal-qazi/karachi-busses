#!/usr/bin/env python3
"""Audit the Tank Chowk junction topology from the extracted OSM road inventory.

Inspects the five road ways that meet near Tank Chowk (stops 514/515 area):
endpoint connectivity, shared junction nodes, one-way direction, missing
links and disconnected segments. Writes a JSON report for review; it does not
modify the road inventory, the database or any stop coordinate.

Usage:
    python scripts/audit_tank_chowk_junction.py            # dry run
    python scripts/audit_tank_chowk_junction.py --build    # write report
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.road_network import RoadGraph  # noqa: E402
from app.snapping import load_roads  # noqa: E402
from shapely.geometry import box  # noqa: E402

TANK_CHOWK_WAYS = [
    "545406459",  # trunk_link ramp at the junction (oneway=yes)
    "850584014",  # Jinnah Avenue carriageway (secondary)
    "522535777",  # trunk carriageway through the junction
    "883797721",  # Jinnah Avenue carriageway (secondary)
    "522375908",  # trunk carriageway through the junction
]
JUNCTION_PAD_M = 800.0


def audit_junction(roads_path: Path, output_path: Path) -> dict:
    roads = load_roads(roads_path)
    if roads.is_empty:
        raise ValueError("Road GeoJSON contains no usable road segments.")

    # Locate the five ways and derive the audit bbox from their geometry.
    way_parts: dict[str, list] = defaultdict(list)
    for wgs84_line, projected_line, props in roads.iter_parts():
        way_id = str(props.get("@id", "") or "")
        if way_id in TANK_CHOWK_WAYS:
            way_parts[way_id].append((wgs84_line, projected_line, props))
    missing = sorted(set(TANK_CHOWK_WAYS) - set(way_parts))
    if missing:
        raise ValueError(f"Ways missing from road inventory: {missing}")

    lats: list[float] = []
    lngs: list[float] = []
    for way_id, parts in way_parts.items():
        for wgs84_line, _, _ in parts:
            for lng, lat in wgs84_line.coords:
                lats.append(lat)
                lngs.append(lng)
    pad_deg = JUNCTION_PAD_M / 111_000.0
    area = box(min(lngs) - pad_deg, min(lats) - pad_deg,
               max(lngs) + pad_deg, max(lats) + pad_deg)
    parts = roads.parts_intersecting(area)
    graph = RoadGraph.from_parts(parts)
    in_degree = Counter()
    for nbrs in graph.adjacency.values():
        for nbr, _, _ in nbrs:
            in_degree[nbr] += 1

    ways_report = []
    for way_id in TANK_CHOWK_WAYS:
        ref = graph.way_ref_by_id(way_id)
        if ref is None:
            ways_report.append({"osm_way_id": way_id, "in_audit_area": False})
            continue
        way = graph.ways[ref]
        node_seqs = graph.way_parts.get(way_id, [])
        flat_nodes = [node for seq in node_seqs for node in seq]
        endpoints = []
        for node in ({flat_nodes[0], flat_nodes[-1]} if flat_nodes else {}):
            endpoints.append({
                "lng": graph.node_coords[node][0],
                "lat": graph.node_coords[node][1],
                "degree_out": len(graph.adjacency.get(node, [])),
            })
        ways_report.append({
            "osm_way_id": way_id,
            "in_audit_area": True,
            "name": way.name,
            "highway": way.highway,
            "forward_only": way.forward_only,
            "backward_only": way.backward_only,
            "part_count": len(node_seqs),
            "node_count": len(flat_nodes),
            "network_length_m": round(
                sum(
                    _part_length(graph, seq)
                    for seq in node_seqs
                ), 2),
            "endpoints": endpoints,
        })

    # Shared junction nodes among the five ways, and with the wider network.
    focus_nodes: dict[int, set[str]] = defaultdict(set)
    for way_id in TANK_CHOWK_WAYS:
        for seq in graph.way_parts.get(way_id, []):
            for node in seq:
                focus_nodes[node].add(way_id)
    shared_pairs = Counter()
    junction_nodes = []
    for node, way_ids in sorted(focus_nodes.items()):
        if len(way_ids) < 2:
            continue
        for a in way_ids:
            for b in way_ids:
                if a < b:
                    shared_pairs[f"{a}~{b}"] += 1
        # How many *distinct other* ways also pass through this node?
        other_ways = set()
        for nbr, _, ref in graph.adjacency.get(node, []):
            other_ways.add(graph.ways[ref].osm_way_id)
        other_ways.difference_update(way_ids)
        junction_nodes.append({
            "lng": graph.node_coords[node][0],
            "lat": graph.node_coords[node][1],
            "focus_ways": sorted(way_ids),
            "in_degree": in_degree[node],
            "out_degree": len(graph.adjacency.get(node, [])),
            "other_way_count": len(other_ways),
            "other_way_ids": sorted(other_ways)[:10],
        })

    # Dead ends inside the audit area (degree-1 endpoints = potential missing
    # links) among the five focus ways.
    dead_ends = []
    for way_id in TANK_CHOWK_WAYS:
        for seq in graph.way_parts.get(way_id, []):
            for node in ({seq[0], seq[-1]} if len(seq) >= 2 else []):
                degree_total = len(graph.adjacency.get(node, [])) + in_degree[node]
                if degree_total <= 1:
                    dead_ends.append({
                        "osm_way_id": way_id,
                        "lng": graph.node_coords[node][0],
                        "lat": graph.node_coords[node][1],
                        "out_degree": len(graph.adjacency.get(node, [])),
                        "in_degree": in_degree[node],
                    })

    report = {
        "status": "tank_chowk_junction_topology_audit_review_aid_only",
        "roads_source": str(roads_path),
        "audit_area_pad_m": JUNCTION_PAD_M,
        "audit_area_parts": len(parts),
        "graph_nodes": len(graph.node_coords),
        "graph_edges": graph.edge_count,
        "focus_ways": ways_report,
        "shared_node_pairs": dict(sorted(shared_pairs.items())),
        "junction_nodes": junction_nodes,
        "dead_ends": dead_ends,
        "limitations": [
            "Coordinate-equality node matching reflects the exported GeoJSON; "
            "it does not read raw OSM node ids.",
            "A missing link here is a geometric observation, not proof that a "
            "physical road connection is absent in OSM.",
            "This audit does not verify bus movements, stop placement or the "
            "historical route alignment.",
        ],
        "attribution": "© OpenStreetMap contributors",
    }
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _part_length(graph: RoadGraph, seq: list[int]) -> float:
    import math
    return sum(
        math.dist(graph.node_proj[a], graph.node_proj[b])
        for a, b in zip(seq, seq[1:])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roads", type=Path,
        default=ROOT / "data" / "osm_roads" / "karachi-osm-bus-roads.geojson")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "data" / "osm_roads" / "tank-chowk-junction-audit.json")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed; pass --build to write the audit report.")
        return 0
    report = audit_junction(args.roads, args.output)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
