#!/usr/bin/env python3
"""Apply user-confirmed name aliases to a derived review register only.

The source crosswalk is never changed. Alias matches do not assign coordinates,
verify physical stops, confirm boarding sides, or approve route service.
Standard-library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

KEYS = ("route_code", "source_stop_sequence")
REQUIRED_CROSSWALK = set(KEYS) | {"source_stop_name", "coordinate_node_id", "latitude", "longitude"}
REQUIRED_SHORTLIST = set(KEYS) | {"source_stop_name", "candidate_node_id"}
REQUIRED_ALIASES = {"source_stop_name", "historical_node_id", "route_codes", "occurrence_count", "name_alias_status", "confirmation_basis", "physical_stop_verification", "coordinate_assignment"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path, required: set[str], label: str) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    missing = required - set(fields)
    if missing:
        raise ValueError(f"{label} missing required fields: {sorted(missing)}")
    return rows, fields


def row_key(row: dict[str, str]) -> tuple[str, str]:
    return tuple((row.get(k) or "").strip() for k in KEYS)


def build(crosswalk_path: Path, shortlist_path: Path, aliases_path: Path, output_dir: Path) -> dict:
    crosswalk, crosswalk_fields = read_csv(crosswalk_path, REQUIRED_CROSSWALK, "Crosswalk")
    shortlist, _ = read_csv(shortlist_path, REQUIRED_SHORTLIST, "Alias shortlist")
    aliases, _ = read_csv(aliases_path, REQUIRED_ALIASES, "User-confirmed aliases")

    source_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in crosswalk:
        key = row_key(row)
        if not all(key) or key in source_by_key:
            raise ValueError(f"Crosswalk has blank or duplicate key: {key}")
        source_by_key[key] = row

    alias_by_pair: dict[tuple[str, str], dict[str, str]] = {}
    for row in aliases:
        if row["name_alias_status"] != "confirmed_by_user" or row["confirmation_basis"] != "user_confirmed_in_chat":
            raise ValueError("Alias register contains a row without explicit user confirmation")
        if row["physical_stop_verification"] != "unverified" or row["coordinate_assignment"] != "not_assigned":
            raise ValueError("Alias register improperly promotes physical verification or coordinate assignment")
        pair = ((row["source_stop_name"] or "").strip(), (row["historical_node_id"] or "").strip())
        if not all(pair) or pair in alias_by_pair:
            raise ValueError(f"Alias register has blank or duplicate pair: {pair}")
        alias_by_pair[pair] = row

    candidate_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in shortlist:
        key = row_key(row)
        if key in candidate_by_key:
            raise ValueError(f"Alias shortlist has duplicate key: {key}")
        candidate_by_key[key] = row

    # Every alias shortlist row must point to a user-confirmed name pair and
    # to the same source stop in the original crosswalk.
    for key, candidate in candidate_by_key.items():
        source = source_by_key.get(key)
        if source is None:
            raise ValueError(f"Shortlist key is absent from source crosswalk: {key}")
        if (source["source_stop_name"] or "").strip() != (candidate["source_stop_name"] or "").strip():
            raise ValueError(f"Shortlist source-name mismatch for {key}")
        pair = ((candidate["source_stop_name"] or "").strip(), (candidate["candidate_node_id"] or "").strip())
        if pair not in alias_by_pair:
            raise ValueError(f"Shortlist candidate is not in user-confirmed alias register: {key} {pair}")
        if (source["coordinate_node_id"] or "").strip():
            raise ValueError(f"Alias would overwrite an existing coordinate candidate: {key}")

    # Build an exact route/name -> alias map. The shortlist supplies sequence
    # identity; the alias register supplies the user's confirmation.
    matches: dict[tuple[str, str], tuple[dict[str, str], dict[str, str]]] = {}
    for key, candidate in candidate_by_key.items():
        pair = ((candidate["source_stop_name"] or "").strip(), (candidate["candidate_node_id"] or "").strip())
        matches[key] = (alias_by_pair[pair], candidate)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "PHASE_5Z_USER_CONFIRMED_ALIAS_RECONCILIATION.csv"
    extra_fields = [
        "name_alias_status", "confirmed_historical_node_id", "alias_confirmation_basis",
        "alias_candidate_source", "physical_stop_verification", "coordinate_assignment",
        "route_approval_status", "next_review_action",
    ]
    fields = crosswalk_fields + [f for f in extra_fields if f not in crosswalk_fields]
    counts = Counter()
    unresolved = Counter()
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for key in sorted(source_by_key, key=lambda k: (k[0], int(k[1]) if k[1].isdigit() else k[1])):
            source = dict(source_by_key[key])
            if key in matches:
                alias, candidate = matches[key]
                source.update({
                    "name_alias_status": "confirmed_by_user",
                    "confirmed_historical_node_id": alias["historical_node_id"],
                    "alias_confirmation_basis": "user_confirmed_in_chat",
                    "alias_candidate_source": "PHASE_5X_shortlist_crosschecked_with_PHASE_5Y",
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_approval_status": "not_approved",
                    "next_review_action": "independently_verify_physical_stop_and_boarding_point_before_coordinate_assignment",
                })
                counts["confirmed_name_alias"] += 1
            else:
                is_unmatched = not (source.get("coordinate_node_id") or "").strip()
                source.update({
                    "name_alias_status": "no_user_confirmed_alias",
                    "confirmed_historical_node_id": "",
                    "alias_confirmation_basis": "",
                    "alias_candidate_source": "",
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_approval_status": "not_approved",
                    "next_review_action": "review_remaining_unmatched_name_candidates_or_obtain_operator_field_evidence" if is_unmatched else "verify_existing_coordinate_candidate_physically",
                })
                counts["no_user_confirmed_alias"] += 1
                if is_unmatched:
                    unresolved[key[0]] += 1
                    counts["remaining_unmatched_without_confirmed_alias"] += 1
            writer.writerow(source)

    report = {
        "status": "phase_5z_name_alias_reconciliation_complete_not_stop_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_crosswalk": {"path": str(crosswalk_path), "sha256": digest(crosswalk_path)},
            "phase_5x_alias_shortlist": {"path": str(shortlist_path), "sha256": digest(shortlist_path)},
            "phase_5y_user_confirmed_aliases": {"path": str(aliases_path), "sha256": digest(aliases_path)},
        },
        "join_policy": "exact route_code + source_stop_sequence; source name and candidate node ID cross-checked",
        "source_crosswalk_rows": len(crosswalk),
        "phase_5x_shortlist_rows": len(shortlist),
        "phase_5y_confirmed_alias_pairs": len(aliases),
        "reconciliation_counts": dict(sorted(counts.items())),
        "remaining_unmatched_by_route": dict(sorted(unresolved.items())),
        "output": {"csv": output_path.name, "sha256": digest(output_path), "rows": len(crosswalk)},
        "safety": [
            "The original Phase 5 crosswalk is not modified.",
            "Confirmed aliases normalize names only; historical node IDs are not copied into coordinate_node_id.",
            "No latitude or longitude is assigned or changed.",
            "All physical_stop_verification values remain unverified.",
            "All route_approval_status values remain not_approved.",
            "No geocoding, snapping, route inference, geometry generation, or production database write is performed.",
        ],
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License 1.0 (ODbL)",
    }
    report_path = output_dir / "PHASE_5Z_USER_CONFIRMED_ALIAS_RECONCILIATION_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", type=Path, default=Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"))
    parser.add_argument("--shortlist", type=Path, default=Path("data/research/PHASE_5X_SPELLING_ALIAS_CANDIDATE_SHORTLIST.csv"))
    parser.add_argument("--aliases", type=Path, default=Path("data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research"))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed; pass --build to create the derived reconciliation register.")
        return 0
    try:
        print(json.dumps(build(args.crosswalk, args.shortlist, args.aliases, args.output_dir), indent=2))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
