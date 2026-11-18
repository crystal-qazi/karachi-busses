# Phase 5AT — Think EV unmatched-name candidate triage

**Review date:** 2026-11-18  
**Status:** Alias candidates only; no name or coordinate mapping is approved.

## Scope and method

Reviewed the 18 Think EV named entries that did not have an exact normalized-name match in the 572-node historical audit. Checked the existing node IDs for plausible name variants and measured only the shortlisted candidate node's distance to the corresponding supplied Think KML LineString. This is a research triage, not geocoding or physical stop verification.

## Findings

- **Possible alias candidates requiring independent confirmation:** Model Colony Mor → `model_colony`; Drigh Road Station → `drigh_road`; Al Asif → `al_asif_square`.
- **Do not alias without stronger evidence:** Clock Tower DHA → `seaview_clock_tower` (different explicit place identity); Malir Cantt Check Post 5 → `malir_cantt_gate_5` (Gate 5 is not proven equivalent to Check Post 5 and is 1.44 km from EV-03); M9 Toll Plaza → `toll_plaza` (existing candidate is 16.69 km from EV-04 and 18.16 km from EV-05 KML lines).
- **No defensible candidate found in the historical node audit:** Dumba Goth, Darul Sehat Hospital, Johar Chowrangi, Johar Mor, Millennium Mall, Jamali Pull and DHA City.

## Route-level counts

| Route | Think entries without exact match | Possible aliases needing confirmation | Explicit do-not-alias flags | No candidate found |
|---|---:|---:|---:|---:|
| EV-01 | 3 | 2 | 1 | 0 |
| EV-02 | 1 | 0 | 0 | 1 |
| EV-03 | 5 | 0 | 1 | 4 |
| EV-04 | 4 | 1 | 1 | 2 |
| EV-05 | 5 | 1 | 1 | 3 |
| **Total** | **18** | **4 route-entry candidates** | **4** | **10** |

The 4 possible-alias route entries represent 3 unique candidate node IDs (Model Colony, Drigh Road, Al Asif Square). They remain unresolved. The 10 no-candidate rows include repeated names across routes.

## Decisions

1. Do not modify the Phase 5AQ exact-name crosswalk.
2. Do not assign any candidate alias to a Think stop until an independent source confirms the same physical stop/boarding point.
3. Preserve the unusual existing Toll Plaza coordinate unchanged and investigate its original source.
4. Keep all 572 historical nodes under review; no DB writes, approvals, coordinate changes, route activation, or geometry edits.
5. The next evidence task is to trace the original source for the three plausible alias candidates and the anomalous Toll Plaza coordinate, then seek operator/field evidence for names with no candidate.
