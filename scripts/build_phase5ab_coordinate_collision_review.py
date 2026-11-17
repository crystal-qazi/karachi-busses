#!/usr/bin/env python3
"""Build a manual-review register for exact duplicate historical coordinates.

This is a diagnostic only. It does not choose a preferred node, move points,
merge names, verify a physical stop, or approve routes. Standard-library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE = Path("data/research/PHASE_5_NODE_AUDIT.csv")
OUTPUT = Path("data/research/PHASE_5AB_COORDINATE_COLLISION_REVIEW.csv")
REPORT = Path("data/research/PHASE_5AB_COORDINATE_COLLISION_REVIEW_REPORT.json")
REQUIRED = {"node_id", "latitude", "longitude", "historical_route_labels", "route_label_count", "verification_status"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(source: Path = SOURCE, output: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    missing = REQUIRED - set(fields)
    if missing:
        raise ValueError(f"Node audit missing fields: {sorted(missing)}")

    groups: dict[tuple[Decimal, Decimal], list[dict[str, str]]] = defaultdict(list)
    seen_nodes = set()
    for row in rows:
        node_id = (row.get("node_id") or "").strip()
        if not node_id or node_id in seen_nodes:
            raise ValueError(f"Blank or duplicate node_id: {node_id!r}")
        seen_nodes.add(node_id)
        try:
            coordinate = (Decimal(row["latitude"]), Decimal(row["longitude"]))
        except (InvalidOperation, KeyError) as exc:
            raise ValueError(f"Invalid coordinate for {node_id}") from exc
        if not all(value.is_finite() for value in coordinate):
            raise ValueError(f"Non-finite coordinate for {node_id}")
        groups[coordinate].append(row)

    collisions = [(coord, members) for coord, members in groups.items() if len(members) > 1]
    collisions.sort(key=lambda item: (item[0][0], item[0][1]))
    fields_out = [
        "collision_group_id", "node_id", "latitude", "longitude",
        "cluster_size", "cluster_node_ids", "node_route_labels",
        "route_labels_shared_by_all_nodes", "route_labels_union",
        "source_verification_status", "coordinate_collision_review_status",
        "review_action", "reviewer_decision", "reviewer_evidence", "reviewer_notes",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    all_members = 0
    cluster_summaries = []
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_out)
        writer.writeheader()
        for index, (coordinate, members) in enumerate(collisions, start=1):
            members = sorted(members, key=lambda row: row["node_id"])
            all_members += len(members)
            node_ids = sorted(row["node_id"] for row in members)
            route_sets = [
                {value.strip() for value in (row.get("historical_route_labels") or "").split(";") if value.strip()}
                for row in members
            ]
            shared = set.intersection(*route_sets) if route_sets else set()
            union = set.union(*route_sets) if route_sets else set()
            group_id = f"CC-{index:02d}"
            for row, route_set in zip(members, route_sets):
                writer.writerow({
                    "collision_group_id": group_id,
                    "node_id": row["node_id"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "cluster_size": len(members),
                    "cluster_node_ids": ";".join(node_ids),
                    "node_route_labels": ";".join(sorted(route_set)),
                    "route_labels_shared_by_all_nodes": ";".join(sorted(shared)),
                    "route_labels_union": ";".join(sorted(union)),
                    "source_verification_status": row.get("verification_status", ""),
                    "coordinate_collision_review_status": "exact_duplicate_coordinate_manual_review",
                    "review_action": "verify_each_named_place_and_source_coordinate_independently; do_not_merge_or_reassign",
                    "reviewer_decision": "",
                    "reviewer_evidence": "",
                    "reviewer_notes": "",
                })
            cluster_summaries.append({
                "collision_group_id": group_id,
                "latitude": str(coordinate[0]),
                "longitude": str(coordinate[1]),
                "cluster_size": len(members),
                "node_ids": node_ids,
                "shared_route_labels": sorted(shared),
                "route_label_union": sorted(union),
            })

    report = {
        "status": "exact_coordinate_collision_audit_complete_manual_review_required",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(source), "sha256": sha256(source)},
        "source_node_rows": len(rows),
        "unique_node_ids": len(seen_nodes),
        "exact_duplicate_coordinate_clusters": len(collisions),
        "nodes_in_duplicate_clusters": all_members,
        "non_collision_nodes": len(rows) - all_members,
        "clusters": cluster_summaries,
        "output": {"csv": str(output), "sha256": sha256(output), "rows": all_members},
        "interpretation": [
            "Exact coordinate equality identifies a data collision, not proof that named places are the same physical stop.",
            "Shared route labels are historical metadata and do not establish a common passenger stop.",
            "No node is preferred, merged, moved, or assigned to a route.",
            "All physical stop verification remains unverified and all route approvals remain not approved.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("pass --build to write the coordinate collision review")
    try:
        print(json.dumps(build(), indent=2))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
