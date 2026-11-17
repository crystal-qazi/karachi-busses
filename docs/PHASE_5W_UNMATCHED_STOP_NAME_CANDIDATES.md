# Phase 5W — Unmatched Stop Name Candidate Review

## Purpose

Create a reproducible, conservative name-similarity triage register for unmatched rows in the historical Phase 5 stop-node crosswalk. It proposes up to three historical node-name candidates per unmatched stop; it does not match stops to coordinates.

## Method

- Reads `PHASE_5_STOP_NODE_CROSSWALK.csv` and `PHASE_5_NODE_AUDIT.csv`.
- Uses Python standard-library text normalization, a small explicit spelling-alias table, SequenceMatcher, and token Dice overlap.
- Ranks at most three node IDs per unmatched stop and labels similarity bands.
- Emits no latitude/longitude, road geometry, route assignment, or boarding-side data.
- Preserves every unmatched stop as `unverified_name_candidates_only`; all route approvals remain blocked.

## Interpretation safeguards

A high text score is not proof that two names identify the same place. Short names, common words, historical labels, spelling differences, and repeated place names can mislead. Reviewers must check independent operator or field evidence and physical boarding location before changing the source crosswalk. Do not copy coordinates or accept route order from this register.

## Run (pip-only)

```powershell
python scripts/build_unmatched_stop_name_candidates.py --build
python -m unittest discover -s tests -p 'test_unmatched_stop_name_candidates.py' -v
```

Outputs:

- `data/research/PHASE_5W_UNMATCHED_STOP_NAME_CANDIDATES.csv`
- `data/research/PHASE_5W_UNMATCHED_STOP_NAME_CANDIDATES_REPORT.json`

No external executable, extra GIS package, web geocoder, routing engine, or production database is required.
