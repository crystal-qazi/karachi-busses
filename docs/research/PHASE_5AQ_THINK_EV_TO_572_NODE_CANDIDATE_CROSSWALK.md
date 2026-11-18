# Phase 5AQ — Think Transportation EV stop-name crosswalk against the 572-node candidate set

**Review date:** 2026-11-18  
**Input:** Think Transportation EV-01–EV-05 ordered entries from Phase 5AO; `data/research/PHASE_5_NODE_AUDIT.csv` (572 historical coordinate candidates).

## Method

Each Think Transportation named entry was compared only against the normalized existing node ID (case/punctuation/spacing normalization). No fuzzy matching, alias inference, geocoding, coordinate calculation, route projection or nearest-node matching was performed. A match is a **candidate name match only**. Every candidate coordinate retains its existing `under_review` status and is not a verified physical boarding location.

## Results

| Route | Think entries | Exact normalized candidate matches | No exact name match |
|---|---:|---:|---:|
| EV-01 | 18 | 15 | 3 |
| EV-02 | 10 | 9 | 1 |
| EV-03 | 20 | 15 | 5 |
| EV-04 | 9 | 5 | 4 |
| EV-05 | 8 | 3 | 5 |
| **Total** | **65** | **47** | **18** |

## Interpretation

- An exact normalized match means only that a historical node ID has the same normalized label as a Think entry. It does not establish that the coordinate is the correct physical stop, side of road, platform, or current boarding point.
- Unmatched names remain unmatched. No coordinates are invented.
- Do not change source spelling or overwrite the Think sequence.
- EV-01 and EV-02 user Google Maps waypoints remain separate evidence. Their order and coordinates are not modified or merged into this name crosswalk.
- This crosswalk does not update MySQL or change any stop's verification status.

## Output

`data/research/PHASE_5AQ_THINK_EV_TO_572_NODE_CANDIDATE_CROSSWALK.csv`
