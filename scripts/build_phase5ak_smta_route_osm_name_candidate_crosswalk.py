#!/usr/bin/env python3
"""Reconcile SMTA named route entries with OSM transit candidates by exact names.

All matches are candidate references only. No physical stop, route assignment,
coordinate, or boarding location is approved by this process.
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
CANDIDATES = ROOT / "data/osm_stops/karachi-osm-bus-stop-candidates.geojson"
OUTPUT = ROOT / "data/osm_stops/PHASE_5AK_SMTA_ROUTE_OSM_NAME_CANDIDATE_CROSSWALK.csv"
REPORT = ROOT / "data/osm_stops/PHASE_5AK_SMTA_ROUTE_OSM_NAME_CANDIDATE_CROSSWALK_REPORT.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def build_alias_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[str]]:
    index: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        if row.get("name_alias_status") != "confirmed_by_user":
            continue
        source = normalize(row.get("source_stop_name", ""))
        historical_id = normalize(row.get("historical_node_id", "").replace("_", " "))
        if not source or not historical_id:
            continue
        for route_code in (part.strip() for part in row.get("route_codes", "").split(";")):
            if route_code:
                index.setdefault((route_code, source), []).append(historical_id)
    return index


def reconcile(
    sequences_path: Path = SEQUENCES,
    aliases_path: Path = ALIASES,
    candidates_path: Path = CANDIDATES,
    output_path: Path = OUTPUT,
    report_path: Path = REPORT,
) -> dict:
    sequences = read_csv(sequences_path)
    aliases = read_csv(aliases_path)
    candidate_data = json.loads(candidates_path.read_text(encoding="utf-8"))
    features = candidate_data.get("features", [])
    if not sequences:
        raise ValueError("Official route sequence input is empty")
    if not features:
        raise ValueError("OSM candidate inventory is empty")

    # Index all names to all matching OSM objects; never collapse duplicates.
    name_index: dict[str, list[dict]] = {}
    for feature in features:
        props = feature.get("properties") or {}
        names = {
            normalize(str(props.get("name") or "")),
            normalize(str(props.get("name_en") or "")),
        } - {""}
        for name in names:
            name_index.setdefault(name, []).append(feature)

    alias_index = build_alias_index(aliases)
    fields = [
        "route_code", "official_route_label", "route_family", "official_status",
        "sequence_number", "official_entry_name", "official_source_url",
        "match_type", "candidate_match_key", "osm_type", "osm_id",
        "osm_candidate_kind", "osm_name", "osm_name_en", "osm_ref",
        "osm_operator", "osm_network", "osm_public_transport", "osm_highway",
        "osm_amenity", "osm_tags_json", "candidate_status",
        "physical_stop_verification", "coordinate_assignment",
        "route_assignment",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    route_counts: dict[str, Counter] = {}
    named_entries = 0
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for entry in sequences:
            if entry.get("entry_type") != "operator_published_named_entry":
                counts["direction_descriptors_excluded"] += 1
                continue
            named_entries += 1
            route = entry["route_code"]
            official_name = entry.get("entry_name", "")
            exact_key = normalize(official_name)
            exact_matches = list(name_index.get(exact_key, [])) if exact_key else []
            alias_keys = alias_index.get((route, exact_key), [])
            alias_matches = []
            for alias_key in alias_keys:
                alias_matches.extend(name_index.get(alias_key, []))

            # Exact official-name matches take precedence. Alias matching is only
            # applied when no exact match exists and only for its approved routes.
            if exact_matches:
                match_type, match_key, matches = "exact_normalized_name", exact_key, exact_matches
            elif alias_matches:
                match_type, match_key, matches = "user_approved_route_scoped_alias", ";".join(alias_keys), alias_matches
            else:
                match_type, match_key, matches = "unmatched", "", []

            # Preserve duplicate OSM objects and distinguish same object reached
            # through multiple alias keys without duplicating its row.
            unique = {}
            for feature in matches:
                props = feature.get("properties") or {}
                key = (str(props.get("osm_type", "")), str(props.get("osm_id", "")))
                unique.setdefault(key, feature)
            matches = list(unique.values())
            if not matches:
                matches = [None]

            route_counter = route_counts.setdefault(route, Counter())
            route_counter[match_type] += 1
            counts[match_type] += 1
            if len(matches) > 1:
                counts["entries_with_multiple_osm_candidates"] += 1

            for feature in matches:
                props = (feature or {}).get("properties") or {}
                writer.writerow({
                    "route_code": route,
                    "official_route_label": entry.get("official_route_label", ""),
                    "route_family": entry.get("route_family", ""),
                    "official_status": entry.get("official_status", ""),
                    "sequence_number": entry.get("sequence_number", ""),
                    "official_entry_name": official_name,
                    "official_source_url": entry.get("official_source_url", ""),
                    "match_type": match_type,
                    "candidate_match_key": match_key,
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
                    "candidate_status": "candidate_only" if feature else "no_osm_name_candidate",
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_assignment": "not_assigned",
                })

    report = {
        "status": "name_only_osm_candidate_crosswalk_not_stop_or_route_verification",
        "official_named_entries": named_entries,
        "direction_descriptors_excluded": counts["direction_descriptors_excluded"],
        "output_rows": sum(route_counts[route][kind] for route in route_counts for kind in route_counts[route]),
        "counts_by_match_type": {
            key: counts[key] for key in (
                "exact_normalized_name",
                "user_approved_route_scoped_alias",
                "unmatched",
            )
        },
        "entries_with_multiple_osm_candidates": counts["entries_with_multiple_osm_candidates"],
        "route_summary": {
            route: dict(sorted(values.items())) for route, values in sorted(route_counts.items())
        },
        "alias_policy": (
            "Only rows marked confirmed_by_user are used; each alias is restricted "
            "to the route_codes listed in the alias register."
        ),
        "limitations": [
            "OSM name matches are candidate references only, not confirmation of a passenger stop.",
            "No OSM object is assigned to an SMTA route or historical coordinate.",
            "No fuzzy matching, proximity matching, geocoding, snapping, or geometry generation is performed.",
            "All candidate rows retain physical_stop_verification=unverified, coordinate_assignment=not_assigned, and route_assignment=not_assigned.",
            "Direction descriptors are excluded from passenger-stop matching.",
            "All duplicate OSM objects matching a name are retained; ambiguity is not resolved automatically.",
        ],
        "inputs": {
            "official_sequences": str(sequences_path),
            "user_confirmed_aliases": str(aliases_path),
            "osm_candidate_inventory": str(candidates_path),
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
        print(f"Aliases: {ALIASES}")
        print(f"OSM candidates: {CANDIDATES}")
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
