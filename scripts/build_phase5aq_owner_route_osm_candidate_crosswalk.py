#!/usr/bin/env python3
"""Build a conservative OSM context crosswalk for owner-reviewed route stops.

Only exact historical-node matches and coordinate-review-required candidates
are joined to the Phase 5AJ OSM proximity audit. Name-only aliases, ambiguous
variants and unmatched labels are deliberately not joined.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/research/owner_route_node_candidate_crosswalk.csv"
OSM_AUDIT = ROOT / "data/osm_stops/PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT.csv"
OUTPUT = ROOT / "data/osm_stops/PHASE_5AQ_OWNER_ROUTE_OSM_CANDIDATE_CROSSWALK.csv"
REPORT = ROOT / "data/osm_stops/PHASE_5AQ_OWNER_ROUTE_OSM_CANDIDATE_CROSSWALK_REPORT.json"
JOINABLE_STATUSES = {"exact_normalized_name", "coordinate_review_required"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def placeholder(relation: str) -> dict[str, str]:
    return {
        "osm_type": "", "osm_id": "", "osm_name": "", "osm_kind": "",
        "distance_m": "", "relation": relation,
    }


def osm_candidates(audit: dict[str, str]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for index in range(1, 4):
        osm_id = audit.get(f"candidate_{index}_osm_id", "")
        if not osm_id:
            continue
        candidates.append({
            "osm_type": audit.get(f"candidate_{index}_osm_type", ""),
            "osm_id": osm_id,
            "osm_name": audit.get(f"candidate_{index}_name", ""),
            "osm_kind": audit.get(f"candidate_{index}_kind", ""),
            "distance_m": audit.get(f"candidate_{index}_distance_m", ""),
            "relation": "within_250m_proximity_only",
        })
    if candidates:
        return candidates
    if audit.get("nearest_osm_id"):
        return [{
            "osm_type": audit.get("nearest_osm_type", ""),
            "osm_id": audit.get("nearest_osm_id", ""),
            "osm_name": audit.get("nearest_osm_name", ""),
            "osm_kind": audit.get("nearest_osm_kind", ""),
            "distance_m": audit.get("nearest_candidate_distance_m", ""),
            "relation": "nearest_outside_250m_context_only",
        }]
    return [placeholder("no_osm_candidate_recorded")]


def build(input_path: Path = INPUT, audit_path: Path = OSM_AUDIT,
          output_path: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    source_rows = read_csv(input_path)
    audit_rows = read_csv(audit_path)
    if not source_rows or not audit_rows:
        raise ValueError("Owner crosswalk or Phase 5AJ OSM audit is empty")

    audit_by_node = {row.get("historical_node_id", ""): row for row in audit_rows}
    fields = [
        "route_code", "sequence", "owner_reviewed_stop_name", "match_status",
        "candidate_source_node_id", "candidate_latitude", "candidate_longitude",
        "candidate_coordinate_collision", "candidate_review_note",
        "osm_candidates_within_250m_count", "osm_exact_name_candidate_count",
        "osm_exact_name_candidate_ids", "osm_candidate_list_truncated",
        "osm_review_relation", "osm_type", "osm_id", "osm_name", "osm_kind",
        "osm_distance_m", "nearest_osm_name_any_distance",
        "nearest_osm_distance_any_m", "physical_stop_verification",
        "coordinate_assignment", "route_assignment",
    ]
    match_counts = Counter()
    relation_counts = Counter()
    unique_entry_relations = Counter()
    output_rows = 0
    entries_with_multiple_candidates = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for source in source_rows:
            status = source.get("match_status", "")
            match_counts[status] += 1
            node_id = source.get("candidate_source_node_id", "")
            audit = audit_by_node.get(node_id, {}) if status in JOINABLE_STATUSES and node_id else {}

            if status not in JOINABLE_STATUSES:
                relation = (
                    "not_joined_coordinate_not_authorized"
                    if status in {"user_confirmed_name_alias", "ambiguous_name_variant"}
                    else "no_historical_node_match"
                )
                candidates = [placeholder(relation)]
                nearby_count = 0
                exact_count = ""
                exact_ids = ""
                nearest_name = ""
                nearest_distance = ""
            elif not audit:
                candidates = [placeholder("no_osm_audit_record")]
                nearby_count = 0
                exact_count = ""
                exact_ids = ""
                nearest_name = ""
                nearest_distance = ""
            else:
                candidates = osm_candidates(audit)
                nearby_count = int(audit.get("nearby_candidate_count_within_250m") or 0)
                exact_count = audit.get("exact_name_candidate_count_within_250m", "")
                exact_ids = audit.get("exact_name_candidate_osm_ids", "")
                nearest_name = audit.get("nearest_osm_name", "")
                nearest_distance = audit.get("nearest_candidate_distance_m", "")

            if nearby_count > 1:
                entries_with_multiple_candidates += 1
            unique_entry_relations[candidates[0]["relation"]] += 1

            for candidate in candidates:
                writer.writerow({
                    "route_code": source.get("route_code", ""),
                    "sequence": source.get("sequence", ""),
                    "owner_reviewed_stop_name": source.get("owner_reviewed_stop_name", ""),
                    "match_status": status,
                    "candidate_source_node_id": node_id,
                    "candidate_latitude": source.get("candidate_latitude", ""),
                    "candidate_longitude": source.get("candidate_longitude", ""),
                    "candidate_coordinate_collision": source.get("candidate_coordinate_collision", ""),
                    "candidate_review_note": source.get("candidate_review_note", ""),
                    "osm_candidates_within_250m_count": nearby_count,
                    "osm_exact_name_candidate_count": exact_count,
                    "osm_exact_name_candidate_ids": exact_ids,
                    "osm_candidate_list_truncated": "yes" if nearby_count > 3 else "no",
                    "osm_review_relation": candidate["relation"],
                    "osm_type": candidate["osm_type"],
                    "osm_id": candidate["osm_id"],
                    "osm_name": candidate["osm_name"],
                    "osm_kind": candidate["osm_kind"],
                    "osm_distance_m": candidate["distance_m"],
                    "nearest_osm_name_any_distance": nearest_name,
                    "nearest_osm_distance_any_m": nearest_distance,
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_assignment": "not_assigned",
                })
                relation_counts[candidate["relation"]] += 1
                output_rows += 1

    report = {
        "status": "owner_route_osm_proximity_context_only_not_stop_verification",
        "input_owner_route_stop_rows": len(source_rows),
        "output_rows": output_rows,
        "match_status_counts": dict(sorted(match_counts.items())),
        "osm_review_relation_row_counts": dict(sorted(relation_counts.items())),
        "unique_route_stop_relation_counts": dict(sorted(unique_entry_relations.items())),
        "entries_with_multiple_osm_candidates_within_250m": entries_with_multiple_candidates,
        "join_policy": "Only exact_normalized_name and coordinate_review_required rows join to the historical-node OSM audit. Alias, ambiguous and unmatched rows are not joined.",
        "limitations": [
            "OSM proximity is context only and does not prove physical boarding-stop identity, route use, direction or current service.",
            "Historical coordinates are unverified source coordinates and are not approved boarding coordinates.",
            "Name-only aliases deliberately remain without coordinate or OSM candidate assignment.",
            "Ambiguous name variants and unmatched labels are not joined to OSM candidates.",
            "Coordinate-review-required rows may show OSM context but remain unassigned and unverified.",
            "No fuzzy matching, geocoding, snapping, route assignment, geometry generation or database write occurs.",
        ],
        "output": str(output_path),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed.")
        print(f"Owner crosswalk: {INPUT}")
        print(f"Phase 5AJ OSM audit: {OSM_AUDIT}")
        print(f"Output: {OUTPUT}")
        return 0
    try:
        print(json.dumps(build(), indent=2))
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
