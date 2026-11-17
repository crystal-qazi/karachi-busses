#!/usr/bin/env python3
"""Create a residual name-only review list after Phase 5Y user-confirmed aliases.

Requires the Phase 5W candidate CSV to have been built first. No coordinates
are read into or emitted by this output. All candidates remain unverified.
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
CROSSWALK = Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv")
CANDIDATES = Path("data/research/PHASE_5W_UNMATCHED_STOP_NAME_CANDIDATES.csv")
SHORTLIST = Path("data/research/PHASE_5X_SPELLING_ALIAS_CANDIDATE_SHORTLIST.csv")
ALIASES = Path("data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv")
OUTPUT = Path("data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES.csv")
REPORT = Path("data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES_REPORT.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path, required: set[str], label: str) -> tuple[list[dict[str, str]], list[str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    missing = required - set(fields)
    if missing:
        raise ValueError(f"{label} missing fields: {sorted(missing)}")
    return rows, fields


def key(row: dict[str, str]) -> tuple[str, str]:
    return tuple((row.get(k) or "").strip() for k in KEYS)


def build(output_path: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    crosswalk, _ = read_rows(CROSSWALK, set(KEYS) | {"source_stop_name", "review_status"}, "Crosswalk")
    candidates, candidate_fields = read_rows(CANDIDATES, set(KEYS) | {"source_stop_name", "review_status"}, "Phase 5W candidates")
    shortlist, _ = read_rows(SHORTLIST, set(KEYS) | {"source_stop_name", "candidate_node_id"}, "Phase 5X shortlist")
    aliases, _ = read_rows(ALIASES, {"source_stop_name", "historical_node_id", "route_codes", "name_alias_status", "confirmation_basis"}, "Phase 5Y aliases")

    alias_pairs = set()
    for row in aliases:
        if row["name_alias_status"] != "confirmed_by_user" or row["confirmation_basis"] != "user_confirmed_in_chat":
            raise ValueError("Phase 5Y includes a non-user-confirmed alias")
        alias_pairs.add(((row["source_stop_name"] or "").strip(), (row["historical_node_id"] or "").strip()))

    source_by_key = {}
    for row in crosswalk:
        k = key(row)
        if not all(k) or k in source_by_key:
            raise ValueError(f"Crosswalk has blank or duplicate key: {k}")
        source_by_key[k] = row
    candidate_by_key = {}
    for row in candidates:
        k = key(row)
        if not all(k) or k in candidate_by_key:
            raise ValueError(f"Phase 5W candidate file has blank or duplicate key: {k}")
        candidate_by_key[k] = row

    unmatched = {key(row): row for row in crosswalk if row.get("review_status") == "unmatched"}
    if set(unmatched) != set(candidate_by_key):
        raise ValueError(
            f"Phase 5W candidate coverage mismatch: unmatched={len(unmatched)}, candidates={len(candidate_by_key)}"
        )

    confirmed_keys = set()
    for row in shortlist:
        k = key(row)
        source = source_by_key.get(k)
        if source is None or source.get("review_status") != "unmatched":
            raise ValueError(f"Phase 5X row is not an unmatched source row: {k}")
        if (source.get("source_stop_name") or "").strip() != (row.get("source_stop_name") or "").strip():
            raise ValueError(f"Phase 5X source name mismatch: {k}")
        pair = ((row.get("source_stop_name") or "").strip(), (row.get("candidate_node_id") or "").strip())
        if pair not in alias_pairs:
            raise ValueError(f"Phase 5X candidate lacks Phase 5Y user confirmation: {k}")
        if k in confirmed_keys:
            raise ValueError(f"Duplicate confirmed alias key: {k}")
        confirmed_keys.add(k)

    if not confirmed_keys.issubset(set(unmatched)):
        raise ValueError("Confirmed aliases include rows absent from unmatched crosswalk set")

    remaining = sorted(set(unmatched) - confirmed_keys, key=lambda k: (k[0], int(k[1]) if k[1].isdigit() else k[1]))
    fields = candidate_fields + [
        "post_alias_review_status",
        "physical_stop_verification",
        "coordinate_assignment",
        "route_approval_status",
        "review_action",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    route_counts = Counter()
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for k in remaining:
            row = dict(candidate_by_key[k])
            row.update({
                "post_alias_review_status": "remaining_unmatched_name_candidate",
                "physical_stop_verification": "unverified",
                "coordinate_assignment": "not_assigned",
                "route_approval_status": "not_approved",
                "review_action": "manual_review_against_operator_or_field_evidence; similarity_score_is_not_confirmation",
            })
            writer.writerow(row)
            route_counts[k[0]] += 1

    report = {
        "status": "phase_5aa_residual_name_review_built_not_stop_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "crosswalk": {"path": str(CROSSWALK), "sha256": sha256(CROSSWALK)},
            "phase_5w_candidates": {"path": str(CANDIDATES), "sha256": sha256(CANDIDATES)},
            "phase_5x_alias_shortlist": {"path": str(SHORTLIST), "sha256": sha256(SHORTLIST)},
            "phase_5y_user_confirmed_aliases": {"path": str(ALIASES), "sha256": sha256(ALIASES)},
        },
        "counts": {
            "source_crosswalk_rows": len(crosswalk),
            "original_unmatched_rows": len(unmatched),
            "confirmed_alias_occurrences_excluded": len(confirmed_keys),
            "remaining_unmatched_rows": len(remaining),
        },
        "remaining_unmatched_by_route": dict(sorted(route_counts.items())),
        "output": {"csv": str(output_path), "sha256": sha256(output_path), "rows": len(remaining)},
        "limitations": [
            "Candidate scores are name-only triage hints and are not confirmation.",
            "No candidate coordinates are emitted or assigned.",
            "No stop, boarding point, road side, bus access, route sequence, or route is approved.",
            "All rows remain physically unverified and not approved.",
            "No geocoding, snapping, route inference, geometry generation, or database write is performed.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("pass --build to write the residual review list")
    try:
        print(json.dumps(build(), indent=2))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
