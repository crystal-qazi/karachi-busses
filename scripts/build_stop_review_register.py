#!/usr/bin/env python3
"""Build a conservative, evidence-preserving review register for historical route stops.

This joins the Phase 5 crosswalk with the Phase 5O OSM proximity audit. It never
approves stops, changes coordinates, snaps points, infers routes, or writes to a DB.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

KEYS = ("route_code", "source_stop_sequence")
REQUIRED_AUDIT_FIELDS = set(KEYS) | {"source_stop_name", "audit_status", "nearest_osm_way_id", "nearest_distance_m", "proximity_band"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_unique_csv(path: Path, label: str) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if not fields:
        raise ValueError(f"{label} CSV has no header: {path}")
    missing = set(KEYS) - set(fields)
    if missing:
        raise ValueError(f"{label} CSV missing key fields: {sorted(missing)}")
    seen = set()
    for row in rows:
        key = tuple((row.get(k) or "").strip() for k in KEYS)
        if not all(key):
            raise ValueError(f"{label} CSV contains a blank join key: {key}")
        if key in seen:
            raise ValueError(f"{label} CSV contains duplicate join key: {key}")
        seen.add(key)
    return rows, fields


def build_register(crosswalk_path: Path, audit_path: Path, output_dir: Path) -> dict:
    crosswalk_rows, crosswalk_fields = read_unique_csv(crosswalk_path, "Crosswalk")
    audit_rows, audit_fields = read_unique_csv(audit_path, "Proximity audit")
    missing_audit = REQUIRED_AUDIT_FIELDS - set(audit_fields)
    if missing_audit:
        raise ValueError(f"Proximity audit missing required fields: {sorted(missing_audit)}")

    crosswalk_by_key = {tuple(row[k].strip() for k in KEYS): row for row in crosswalk_rows}
    audit_by_key = {tuple(row[k].strip() for k in KEYS): row for row in audit_rows}
    missing = sorted(set(crosswalk_by_key) - set(audit_by_key))
    extra = sorted(set(audit_by_key) - set(crosswalk_by_key))
    if missing or extra:
        raise ValueError(f"Crosswalk/audit keys do not match exactly: missing={len(missing)}, extra={len(extra)}")

    fields = list(dict.fromkeys(crosswalk_fields + [f for f in audit_fields if f not in crosswalk_fields]))
    fields += [
        "coordinate_review_status",
        "road_review_status",
        "stop_verification_status",
        "route_approval_status",
        "review_action",
        "reviewer_decision",
        "reviewer_evidence",
        "reviewer_notes",
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "karachi-stop-review-register.csv"
    audit_counts = Counter()
    route_counts: dict[str, Counter] = defaultdict(Counter)
    band_counts = Counter()

    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for key in sorted(crosswalk_by_key, key=lambda k: (k[0], int(k[1]) if k[1].isdigit() else k[1])):
            source = crosswalk_by_key[key]
            audit = audit_by_key[key]
            if (source.get("source_stop_name") or "").strip() != (audit.get("source_stop_name") or "").strip():
                raise ValueError(f"Stop-name mismatch for {key}")
            status = (audit.get("audit_status") or "").strip()
            if status == "proximity_only_unverified":
                coordinate_status = "historical_coordinate_candidate_unverified"
                road_status = "nearby_osm_road_candidate_unverified"
                action = "confirm_physical_stop_boarding_side_bus_access_and_route_use"
            elif status == "no_coordinate_candidate":
                coordinate_status = "no_coordinate_candidate"
                road_status = "not_assessed_no_coordinate"
                action = "obtain_operator_or_field_coordinate_evidence"
            elif status == "candidate_outside_parent_boundary":
                coordinate_status = "candidate_outside_osm_parent_boundary"
                road_status = "not_assessed_outside_boundary"
                action = "review_source_coordinate_and_karachi_boundary_membership"
            elif status in {"nearest_road_over_250m", "invalid_candidate_coordinate"}:
                coordinate_status = "historical_coordinate_candidate_requires_review"
                road_status = status
                action = "review_coordinate_and_nearby_road_context"
            else:
                raise ValueError(f"Unexpected audit_status {status!r} for {key}")
            row = {**source, **audit}
            row.update({
                "coordinate_review_status": coordinate_status,
                "road_review_status": road_status,
                "stop_verification_status": "unverified",
                "route_approval_status": "not_approved",
                "review_action": action,
                "reviewer_decision": "",
                "reviewer_evidence": "",
                "reviewer_notes": "",
            })
            writer.writerow(row)
            audit_counts[status] += 1
            route_counts[key[0]][status] += 1
            if audit.get("proximity_band"):
                band_counts[audit["proximity_band"]] += 1

    report = {
        "status": "review_register_built_not_stop_or_route_approval",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "crosswalk_source": str(crosswalk_path),
        "crosswalk_sha256": sha256_file(crosswalk_path),
        "proximity_audit_source": str(audit_path),
        "proximity_audit_sha256": sha256_file(audit_path),
        "rows": len(crosswalk_rows),
        "join_key": list(KEYS),
        "join_validation": "exact_one_to_one",
        "audit_status_counts": dict(sorted(audit_counts.items())),
        "distance_band_counts": dict(sorted(band_counts.items())),
        "route_status_counts": {route: dict(sorted(counts.items())) for route, counts in sorted(route_counts.items())},
        "outputs": {"csv": csv_path.name, "csv_sha256": sha256_file(csv_path)},
        "review_policy": [
            "No stop is approved by this register.",
            "Historical coordinates and nearest OSM roads are candidates only.",
            "Unmatched records remain present; no geocoding or coordinate invention is performed.",
            "Operator or field evidence is required before stop verification and route approval.",
            "No snapping, route inference, production database write, or geometry generation is performed.",
        ],
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License 1.0 (ODbL)",
    }
    report_path = output_dir / "karachi-stop-review-register-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", type=Path, default=Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"))
    parser.add_argument("--audit", type=Path, default=Path("data/osm_roads/stop-road-proximity-audit.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research"))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed; pass --build to create the review register.")
        return 0
    try:
        print(json.dumps(build_register(args.crosswalk, args.audit, args.output_dir), indent=2))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
