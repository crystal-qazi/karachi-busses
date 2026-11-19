#!/usr/bin/env python3
"""Find exact OSM name candidates for owner-reviewed route entries still unmatched.

This is a name-only research crosswalk. It does not infer coordinates, join
nearby objects, assign routes, or verify physical boarding stops.
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
INPUT = ROOT / "data/research/owner_route_node_candidate_crosswalk.csv"
OSM_INVENTORY = ROOT / "data/osm_stops/karachi-osm-bus-stop-candidates.geojson"
OUTPUT = ROOT / "data/osm_stops/PHASE_5BG_OWNER_UNMATCHED_OSM_NAME_CANDIDATES.csv"
REPORT = ROOT / "data/osm_stops/PHASE_5BG_OWNER_UNMATCHED_OSM_NAME_CANDIDATES_REPORT.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def build(input_path: Path = INPUT, inventory_path: Path = OSM_INVENTORY,
          output_path: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    source_rows = [row for row in read_csv(input_path) if row.get("match_status") == "unmatched"]
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    features = inventory.get("features", [])
    if not source_rows:
        raise ValueError("No unmatched owner-route entries were found")
    if not features:
        raise ValueError("OSM bus-stop candidate inventory is empty")

    name_index: dict[str, list[dict]] = {}
    for feature in features:
        props = feature.get("properties") or {}
        for key in {normalize(str(props.get("name") or "")), normalize(str(props.get("name_en") or ""))} - {""}:
            name_index.setdefault(key, []).append(feature)

    fields = [
        "route_code", "sequence", "owner_reviewed_stop_name",
        "existing_match_status", "candidate_match_key", "osm_name_match_status",
        "osm_type", "osm_id", "osm_candidate_kind", "osm_name", "osm_name_en",
        "osm_ref", "osm_operator", "osm_network", "osm_public_transport",
        "osm_highway", "osm_amenity", "osm_tags_json",
        "physical_stop_verification", "coordinate_assignment", "route_assignment",
    ]
    output_rows = 0
    exact_entry_count = 0
    no_match_count = 0
    multiple_candidate_entries = 0
    unique_label_matches: set[str] = set()
    route_counts: dict[str, Counter] = {}
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for source in source_rows:
            label = source.get("owner_reviewed_stop_name", "")
            key = normalize(label)
            matches = name_index.get(key, []) if key else []
            # Preserve each distinct OSM object, but avoid duplicate rows if
            # name and name:en normalize to the same key for one feature.
            unique: dict[tuple[str, str], dict] = {}
            for feature in matches:
                props = feature.get("properties") or {}
                obj_key = (str(props.get("osm_type", "")), str(props.get("osm_id", "")))
                unique.setdefault(obj_key, feature)
            matches = list(unique.values())

            route_counter = route_counts.setdefault(source.get("route_code", ""), Counter())
            if matches:
                exact_entry_count += 1
                unique_label_matches.add(label)
                route_counter["exact_osm_name_candidate"] += 1
                if len(matches) > 1:
                    multiple_candidate_entries += 1
            else:
                no_match_count += 1
                route_counter["no_exact_osm_name_candidate"] += 1
                matches = [None]

            for feature in matches:
                props = (feature or {}).get("properties") or {}
                writer.writerow({
                    "route_code": source.get("route_code", ""),
                    "sequence": source.get("sequence", ""),
                    "owner_reviewed_stop_name": label,
                    "existing_match_status": "unmatched",
                    "candidate_match_key": key if feature else "",
                    "osm_name_match_status": "exact_normalized_name_candidate" if feature else "no_exact_osm_name_candidate",
                    "osm_type": props.get("osm_type", ""),
                    "osm_id": props.get("osm_id", ""),
                    "osm_candidate_kind": props.get("candidate_kind", ""),
                    "osm_name": props.get("name") or "",
                    "osm_name_en": props.get("name_en") or "",
                    "osm_ref": props.get("ref") or "",
                    "osm_operator": props.get("operator") or "",
                    "osm_network": props.get("network") or "",
                    "osm_public_transport": props.get("public_transport") or "",
                    "osm_highway": props.get("highway") or "",
                    "osm_amenity": props.get("amenity") or "",
                    "osm_tags_json": json.dumps(props.get("tags") or {}, ensure_ascii=False, sort_keys=True),
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_assignment": "not_assigned",
                })
                output_rows += 1

    report = {
        "status": "owner_unmatched_osm_exact_name_candidates_only_not_stop_verification",
        "input_unmatched_route_stop_entries": len(source_rows),
        "distinct_unmatched_owner_labels": len({row.get("owner_reviewed_stop_name", "") for row in source_rows}),
        "entries_with_exact_osm_name_candidate": exact_entry_count,
        "distinct_labels_with_exact_osm_name_candidate": len(unique_label_matches),
        "entries_without_exact_osm_name_candidate": no_match_count,
        "entries_with_multiple_exact_osm_objects": multiple_candidate_entries,
        "output_rows": output_rows,
        "route_summary": {route: dict(sorted(counts.items())) for route, counts in sorted(route_counts.items())},
        "method": "Exact normalized equality only across OSM name and name:en tags; no fuzzy matching, proximity matching or alias inference.",
        "limitations": [
            "An exact OSM name is a candidate reference only; it does not prove physical stop identity or that a bus uses the feature.",
            "No OSM coordinates or geometry are copied into the output.",
            "No route assignment, boarding-side inference, coordinate assignment, verification or geometry generation occurs.",
            "All candidates remain physical_stop_verification=unverified, coordinate_assignment=not_assigned and route_assignment=not_assigned.",
            "Unmatched labels with no exact OSM name remain unresolved; transliteration and alternate spellings are not inferred.",
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
        print(f"Owner route crosswalk: {INPUT}")
        print(f"OSM candidate inventory: {OSM_INVENTORY}")
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
