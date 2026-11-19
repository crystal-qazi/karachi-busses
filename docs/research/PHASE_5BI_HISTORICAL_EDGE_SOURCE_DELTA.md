# Phase 5BI — Historical edge source row-level reconciliation

**Date:** 19 November 2026  
**Canonical source:** Zenodo DOI 10.5281/zenodo.13951512, *Karachi Bus Network*, Data Research Lab Pakistan.  
**Purpose:** Compare the published edge CSV directly with the repository's cleaned edge CSV using duplicate-aware row counts.

## Method

The workflow downloads the public source file from the canonical Zenodo record to a temporary GitHub Actions runner directory. It compares tuples of `stop1`, `stop2` and `bus_name` using multiset counts:

- Surrounding whitespace is stripped.
- Case, punctuation, node spelling, edge direction and route code are preserved exactly.
- Duplicate row multiplicity is preserved.
- Missing source rows and extra project rows are written to a delta CSV.
- SHA-256 hashes and per-route missing/extra counts are recorded.

The original Zenodo CSV is not committed to the repository or uploaded as an artifact. Only the small row-level delta CSV and JSON report are retained for 14 days.

## Outputs

- `PHASE_5BI_HISTORICAL_EDGE_SOURCE_DELTA.csv`
- `PHASE_5BI_HISTORICAL_EDGE_SOURCE_DELTA_REPORT.json`

Workflow: `Phase 5BI Historical Edge Source Delta Audit`. It runs on relevant pushes to main and can be run manually.

## Interpretation

The comparison can establish exactly which edge rows differ and whether duplicate multiplicities account for any part of the difference. It cannot explain *why* an edge was removed or changed. Every difference must be reviewed against the source methodology and project cleaning history before modifying the project CSV.

The workflow is read-only with respect to the source and project CSVs. It does not update MySQL, route-stop links, verification states, route shapes, activation or public API data.
