#!/usr/bin/env python3
"""Classify remaining unmatched stop-name candidates for manual evidence review.

Similarity bands are triage only. This script never assigns a node, coordinate,
physical stop, boarding point, road, or route geometry.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

INPUT = Path("data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES.csv")
OUTPUT = Path("data/research/PHASE_5AD_UNMATCHED_STOP_TRIAGE.csv")
REPORT = Path("data/research/PHASE_5AD_UNMATCHED_STOP_TRIAGE_REPORT.json")

def band(score: float) -> str:
    if score >= 0.85:
        return "strong"
    if score >= 0.65:
        return "possible"
    if score >= 0.45:
        return "weak"
    return "low"

def build(input_path: Path = INPUT, output_path: Path = OUTPUT, report_path: Path = REPORT) -> dict:
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        source_fields = list(reader.fieldnames or [])
    required = {
        "route_code", "route_name", "source_stop_sequence", "source_stop_name",
        "candidate_1_node_id", "candidate_1_score", "candidate_2_node_id",
        "candidate_2_score", "candidate_3_node_id", "candidate_3_score",
        "candidate_count_at_or_above_0_45", "physical_stop_verification",
        "coordinate_assignment", "route_approval_status",
    }
    missing = required - set(source_fields)
    if missing:
        raise ValueError(f"Phase 5AA input missing fields: {sorted(missing)}")
    keys = [(r["route_code"], r["source_stop_sequence"]) for r in rows]
    if any(not all(k) for k in keys) or len(keys) != len(set(keys)):
        raise ValueError("Input contains blank or duplicate route/sequence keys")

    fields = source_fields + [
        "top_candidate_band", "top_candidate_gap", "candidate_ambiguity",
        "triage_priority", "triage_reason",
    ]
    top_bands = Counter()
    ambiguities = Counter()
    priorities = Counter()
    routes = defaultdict(Counter)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            scores = []
            for i in range(1, 4):
                raw = (row.get(f"candidate_{i}_score") or "").strip()
                scores.append(float(raw) if raw else 0.0)
            top = scores[0]
            second = scores[1]
            top_band = band(top)
            gap = round(top - second, 4)
            candidate_count = int(row["candidate_count_at_or_above_0_45"] or 0)
            if top < 0.45:
                ambiguity = "no_candidate_at_weak_threshold"
                priority = "low"
                reason = "All listed text candidates are below 0.45; require an external stop source"
            elif candidate_count >= 2 and gap <= 0.05:
                ambiguity = "multiple_close_text_candidates"
                priority = "manual_disambiguation"
                reason = "Two or more node names are plausible by text score; do not select automatically"
            elif top_band in {"strong", "possible"}:
                ambiguity = "leading_text_candidate_only"
                priority = "operator_evidence_first"
                reason = "A leading name candidate exists but requires independent operator/field confirmation"
            else:
                ambiguity = "weak_text_candidate_only"
                priority = "operator_evidence_first"
                reason = "Only weak text similarity; require independent operator/field confirmation"
            if row.get("physical_stop_verification") != "unverified":
                raise ValueError("Phase 5AA row unexpectedly changes physical stop verification")
            if row.get("coordinate_assignment") != "not_assigned":
                raise ValueError("Phase 5AA row unexpectedly contains a coordinate assignment")
            if row.get("route_approval_status") != "not_approved":
                raise ValueError("Phase 5AA row unexpectedly marks a route approved")
            out = dict(row)
            out.update({
                "top_candidate_band": top_band,
                "top_candidate_gap": f"{gap:.4f}",
                "candidate_ambiguity": ambiguity,
                "triage_priority": priority,
                "triage_reason": reason,
            })
            writer.writerow(out)
            top_bands[top_band] += 1
            ambiguities[ambiguity] += 1
            priorities[priority] += 1
            routes[row["route_code"]][priority] += 1
            routes[row["route_code"]]["rows"] += 1

    report = {
        "status": "phase_5ad_triage_complete_not_stop_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path),
        "output": {"csv": str(output_path), "rows": len(rows)},
        "counts": {
            "rows": len(rows),
            "top_candidate_bands": dict(sorted(top_bands.items())),
            "ambiguity": dict(sorted(ambiguities.items())),
            "triage_priority": dict(sorted(priorities.items())),
        },
        "by_route": {route: dict(sorted(c.items())) for route, c in sorted(routes.items())},
        "method": {
            "strong": "top score >= 0.85",
            "possible": "0.65 <= top score < 0.85",
            "weak": "0.45 <= top score < 0.65",
            "low": "top score < 0.45",
            "close_candidate_gap": "top score minus second score <= 0.05, with at least two candidates >= 0.45",
        },
        "limitations": [
            "Similarity scores are linguistic triage hints, not proof of stop identity.",
            "No candidate is assigned to a route stop and no coordinates are copied.",
            "All physical stop verification remains unverified; all coordinate assignments remain not_assigned.",
            "No road snapping, geocoding, route geometry, or production database writes.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("pass --build to write the triage register")
    try:
        print(json.dumps(build(), indent=2))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
