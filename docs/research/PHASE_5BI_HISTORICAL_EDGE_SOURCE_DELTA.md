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


## Verified result — Phase 5BI run 1 (19 November 2026)

The first workflow run successfully downloaded the canonical source CSV on attempt 1 and compared all rows.

| Metric | Verified result |
|---|---:|
| Zenodo source rows | 1,490 |
| Distinct source edge tuples | 1,415 |
| Exact duplicate occurrences in source | 75 |
| Project cleaned rows | 1,415 |
| Distinct project edge tuples | 1,415 |
| Matched source edge occurrences | 1,415 |
| Source distinct tuples missing from project | 0 |
| Extra project tuples | 0 |

Duplicate occurrences by route identifier:

| Route | Duplicate occurrences |
|---|---:|
| D-10 | 32 |
| 17-I | 26 |
| 45-A | 16 |
| Sheraz_Coach | 1 |
| **Total** | **75** |

**Conclusion:** The project cleaned edge file is exactly the distinct-edge set of the canonical Zenodo CSV. All 75 excess source rows are exact duplicate occurrences; no unique edge was removed or altered. This closes the 1,490-versus-1,415 row-count discrepancy.

Source CSV SHA-256: `a9c6c79f78de6df4df80edc365a193fc72770f359adca04060beaf42d9a73892`.  
Project cleaned CSV SHA-256: `19e269a3b6b88458295417d1b749368e9128d7ae7b074a51122b00620d98f96f`.

The GitHub Actions artifact `phase-5bi-historical-edge-source-delta` contains the row-level 75-occurrence delta CSV and JSON report (14-day retention). The original Zenodo CSV is not committed or re-uploaded.
