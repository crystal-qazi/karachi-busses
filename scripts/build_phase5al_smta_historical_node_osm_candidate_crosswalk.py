#!/usr/bin/env python3
"""Build a conservative SMTA -> historical-node -> OSM proximity crosswalk.

Historical coordinates and nearby OSM objects are evidence candidates only.
This script never verifies stops or assigns routes/boarding coordinates.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv"
ALIASES = ROOT / "data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv"
HISTORICAL = ROOT / "data/research/PHASE_5_NODE_AUDIT.csv"
OSM_AUDIT = ROOT / "data/osm_stops/PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT.csv"
OUTPUT = ROOT / "data/osm_stops/PHASE_5AL_SMTA_HISTORICAL_NODE_OSM_CANDIDATE_CROSSWALK.csv"
REPORT = ROOT / "data/osm_stops/PHASE_5AL_SMTA_HISTORICAL_NODE_OSM_CANDIDATE_CROSSWALK_REPORT.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def alias_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for row in rows:
        if row.get("name_alias_status") != "confirmed_by_user":
            continue
        source = normalize(row.get("source_stop_name", ""))
        target = normalize(row.get("historical_node_id", "").replace("_", " "))
        if not source or not target:
            continue
        for route in (part.strip() for part in row.get("route_codes", "").split(";")):
            if route:
                result[(route, source)] = target
    return result


def _candidate_rows(audit: dict[str, str]) -> list[dict[str, str]]:
    candidates = []
    for index in range(1, 4):
        osm_id = audit.get(f"candidate_{index}_osm_id", "")
        if not osm_id:
            continue
        candidates.append({
            "osm_type": audit.get(f"candidate_{index}_osm_type", ""),
            "osm_id": osm_id,
            "osm_name": audit.get(f"candidate_{index}_name", ""),
            "osm_candidate_kind": audit.get(f"candidate_{index}_kind", ""),
            "distance_m": audit.get(f"candidate_{index}_distance_m", ""),
            "osm_candidate_relation": "within_250m_proximity_only",
        })
    return candidates


def reconcile(
    sequences_path: Path = SEQUENCES,
    aliases_path: Path = ALIASES,
    historical_path: Path = HISTORICAL,
    audit_path: Path = OSM_AUDIT,
    output_path: Path = OUTPUT,
    report_path: Path = REPORT,
) -> dict:
    sequences = read_csv(sequences_path)
    aliases = read_csv(aliases_path)
    historical = read_csv(historical_path)
    audit_rows = read_csv(audit_path)
    if not sequences or not historical or not audit_rows:
        raise ValueError("One or more required input registers are empty")

    historical_index: dict[str, list[dict[str, str]]] = {}
    for node in historical:
        key = normalize(node.get("node_id", "").replace("_", " "))
        if key:
            historical_index.setdefault(key, []).append(node)
    audit_index = {row.get("historical_node_id", ""): row for row in audit_rows}
    approved_aliases = alias_index(aliases)

    fields = [
        "route_code", "official_route_label", "route_family", "official_status",
        "sequence_number", "official_entry_name", "official_source_url",
        "historical_match_type", "historical_node_id", "historical_latitude",
        "historical_longitude", "historical_route_labels",
        "historical_coordinate_verification", "historical_collision_group",
        "historical_review_note", "osm_candidates_within_250m_count",
        "osm_exact_name_candidates_within_250m_count", "osm_exact_name_candidate_ids",
        "osm_candidate_list_truncated", "osm_candidate_relation", "osm_type",
        "osm_id", "osm_name", "osm_candidate_kind", "osm_distance_m",
        "nearest_osm_name_any_distance", "nearest_osm_distance_any_m",
        "physical_stop_verification", "coordinate_assignment", "route_assignment",
    ]
    counts = Counter()
    route_counts: dict[str, Counter] = {}
    output_rows = 0
    named_entries = 0
    entry_osm_status_counts = Counter()
    entries_with_multiple_250m_candidates = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for entry in sequences:
            if entry.get("entry_type") != "operator_published_named_entry":
                counts["direction_descriptors_excluded"] += 1
                continue
            named_entries += 1
            route = entry.get("route_code", "")
            official_name = entry.get("entry_name", "")
            key = normalize(official_name)
            nodes = historical_index.get(key, []) if key else []
            match_type = "exact_historical_node_name"
            if not nodes:
                alias_key = approved_aliases.get((route, key))
                nodes = historical_index.get(alias_key, []) if alias_key else []
                match_type = "user_approved_route_scoped_alias" if nodes else "unmatched"
            if not nodes:
                nodes = [None]
                match_type = "unmatched"

            route_counter = route_counts.setdefault(route, Counter())
            route_counter[match_type] += 1
            counts[match_type] += 1

            for node in nodes:
                audit = audit_index.get(node.get("node_id", ""), {}) if node else {}
                nearby = _candidate_rows(audit) if audit else []
                total_nearby = int(audit.get("nearby_candidate_count_within_250m") or 0) if audit else 0
                if nearby:
                    candidate_rows = nearby
                elif not node:
                    candidate_rows = [{
                        "osm_type": "", "osm_id": "", "osm_name": "",
                        "osm_candidate_kind": "", "distance_m": "",
                        "osm_candidate_relation": "no_historical_node_match",
                    }]
                elif not audit:
                    candidate_rows = [{
                        "osm_type": "", "osm_id": "", "osm_name": "",
                        "osm_candidate_kind": "", "distance_m": "",
                        "osm_candidate_relation": "no_osm_audit_record",
                    }]
                elif audit.get("nearest_osm_id"):
                    candidate_rows = [{
                        "osm_type": audit.get("nearest_osm_type", ""),
                        "osm_id": audit.get("nearest_osm_id", ""),
                        "osm_name": audit.get("nearest_osm_name", ""),
                        "osm_candidate_kind": audit.get("nearest_osm_kind", ""),
                        "distance_m": audit.get("nearest_candidate_distance_m", ""),
                        "osm_candidate_relation": "nearest_outside_250m_context_only",
                    }]
                else:
                    candidate_rows = [{
                        "osm_type": "", "osm_id": "", "osm_name": "",
                        "osm_candidate_kind": "", "distance_m": "",
                        "osm_candidate_relation": "no_osm_candidate_recorded",
                    }]

                within_count_for_entry = sum(
                    candidate["osm_candidate_relation"] == "within_250m_proximity_only"
                    for candidate in candidate_rows
                )
                if within_count_for_entry > 1:
                    entries_with_multiple_250m_candidates += 1
                if within_count_for_entry:
                    entry_osm_status_counts["has_250m_proximity_candidates"] += 1
                elif any(candidate["osm_candidate_relation"] == "nearest_outside_250m_context_only" for candidate in candidate_rows):
                    entry_osm_status_counts["nearest_only_outside_250m"] += 1
                elif match_type == "unmatched":
                    entry_osm_status_counts["no_historical_node_match"] += 1
                else:
                    entry_osm_status_counts["no_osm_candidate_recorded"] += 1

                for candidate in candidate_rows:
                    writer.writerow({
                        "route_code": route,
                        "official_route_label": entry.get("official_route_label", ""),
                        "route_family": entry.get("route_family", ""),
                        "official_status": entry.get("official_status", ""),
                        "sequence_number": entry.get("sequence_number", ""),
                        "official_entry_name": official_name,
                        "official_source_url": entry.get("official_source_url", ""),
                        "historical_match_type": match_type,
                        "historical_node_id": node.get("node_id", "") if node else "",
                        "historical_latitude": node.get("latitude", "") if node else "",
                        "historical_longitude": node.get("longitude", "") if node else "",
                        "historical_route_labels": node.get("historical_route_labels", "") if node else "",
                        "historical_coordinate_verification": node.get("verification_status", "not_matched") if node else "not_matched",
                        "historical_collision_group": node.get("coordinate_collision_group", "") if node else "",
                        "historical_review_note": node.get("review_note", "") if node else "",
                        "osm_candidates_within_250m_count": total_nearby,
                        "osm_exact_name_candidates_within_250m_count": audit.get("exact_name_candidate_count_within_250m", "") if audit else "",
                        "osm_exact_name_candidate_ids": audit.get("exact_name_candidate_osm_ids", "") if audit else "",
                        "osm_candidate_list_truncated": "yes" if total_nearby > 3 else "no",
                        "osm_candidate_relation": candidate["osm_candidate_relation"],
                        "osm_type": candidate["osm_type"],
                        "osm_id": candidate["osm_id"],
                        "osm_name": candidate["osm_name"],
                        "osm_candidate_kind": candidate["osm_candidate_kind"],
                        "osm_distance_m": candidate["distance_m"],
                        "nearest_osm_name_any_distance": audit.get("nearest_osm_name", "") if audit else "",
                        "nearest_osm_distance_any_m": audit.get("nearest_candidate_distance_m", "") if audit else "",
                        "physical_stop_verification": "unverified",
                        "coordinate_assignment": "not_assigned",
                        "route_assignment": "not_assigned",
                    })
                    output_rows += 1
                    counts[candidate["osm_candidate_relation"]] += 1

    report = {
        "status": "historical_coordinate_and_osm_proximity_candidate_crosswalk_only",
        "official_named_entries": named_entries,
        "direction_descriptors_excluded": counts["direction_descriptors_excluded"],
        "output_rows": output_rows,
        "historical_name_match_counts": {
            "exact_historical_node_name": counts["exact_historical_node_name"],
            "user_approved_route_scoped_alias": counts["user_approved_route_scoped_alias"],
            "unmatched": counts["unmatched"],
        },
        "osm_candidate_relation_row_counts": {
            "within_250m_proximity_only": counts["within_250m_proximity_only"],
            "nearest_outside_250m_context_only": counts["nearest_outside_250m_context_only"],
            "no_osm_candidate_recorded": counts["no_osm_candidate_recorded"],
            "no_historical_node_match": counts["no_historical_node_match"],
            "no_osm_audit_record": counts["no_osm_audit_record"],
        },
        "unique_official_entry_osm_status_counts": dict(sorted(entry_osm_status_counts.items())),
        "official_entries_with_multiple_250m_candidates": entries_with_multiple_250m_candidates,
        "route_summary": {
            route: dict(sorted(values.items())) for route, values in sorted(route_counts.items())
        },
        "alias_policy": "Only confirmed_by_user aliases are applied, and only to route codes listed in the alias register.",
        "limitations": [
            "Historical coordinates are references from an earlier dataset, not verified passenger boarding points.",
            "OSM features within 250m are proximity candidates only; proximity does not prove identity or route use.",
            "When more than three OSM candidates are within 250m, the report retains the total count and the three nearest candidates only.",
            "Nearest OSM features beyond 250m are shown as context only, never as within-radius candidates.",
            "No fuzzy name matching, geocoding, snapping, route assignment, coordinate approval, or geometry generation is performed.",
            "All rows retain physical_stop_verification=unverified, coordinate_assignment=not_assigned, and route_assignment=not_assigned.",
            "Historical route labels are preserved as source metadata and are not treated as current SMTA route assignments.",
        ],
        "inputs": {
            "official_sequences": str(sequences_path),
            "user_confirmed_aliases": str(aliases_path),
            "historical_coordinate_register": str(historical_path),
            "phase_5aj_osm_proximity_audit": str(audit_path),
        },
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
        print(f"Sequences: {SEQUENCES}")
        print(f"Historical nodes: {HISTORICAL}")
        print(f"Phase 5AJ audit: {OSM_AUDIT}")
        print(f"Output: {OUTPUT}")
        return 0
    try:
        print(json.dumps(reconcile(), indent=2))
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
