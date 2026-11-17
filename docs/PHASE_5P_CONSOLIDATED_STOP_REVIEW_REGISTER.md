# Phase 5P — Consolidated Historical Stop Review Register

## Purpose

Create one review-ready row for every route stop in the Phase 5 historical stop-node crosswalk, joining it to the Phase 5O OSM road proximity audit by the exact composite key `route_code + source_stop_sequence`.

## Evidence and interpretation

The register preserves the original route/stop fields and the OSM proximity fields. It adds explicit coordinate, road, stop-verification, route-approval and reviewer fields. It does not upgrade a name match or a nearby road into a verified stop.

Every row starts with `stop_verification_status=unverified` and `route_approval_status=not_approved`. Reviewer decision/evidence/notes are intentionally blank. Unmatched stop records remain in the register and are assigned an evidence-gathering action; no geocoding or coordinate invention is performed.

The builder rejects duplicate keys, missing/extra join rows, and stop-name mismatches. This prevents silent row loss or accidental cross-route joins.

## Run locally (pip-only)

The register builder uses only the Python standard library:

```powershell
python scripts/build_stop_review_register.py
python scripts/build_stop_review_register.py --build
```

The proximity audit CSV must already exist at `data/osm_roads/stop-road-proximity-audit.csv`. No external executable, GIS package, routing service, or production database is required by this register step.

## Outputs

- `data/research/karachi-stop-review-register.csv`
- `data/research/karachi-stop-review-register-report.json`

The report records source hashes, exact join validation, status counts, route counts, distance bands, OSM attribution and ODbL licensing.

## Approval gate

A stop can only move beyond unverified status after suitable operator/field evidence confirms its physical location, boarding side/platform, bus-specific access, route identity and direction. Road proximity alone is not approval. Route geometry remains blocked until stop sequence and access evidence are reviewed.
