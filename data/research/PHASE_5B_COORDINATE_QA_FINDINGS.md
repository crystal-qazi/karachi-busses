# Phase 5B — Generated coordinate QA findings

**Generated from:** GitHub Actions run 44098557573, commit 9c87283c415750fa07a716ef55ff2437a4c98ccf  
**Artifact:** karachi-phase5b-coordinate-review  
**Status:** Research-only; no stop approvals or database changes.

## Reproducible QA totals

| Check | Result |
|---|---:|
| Historical coordinate nodes | 572 |
| Numerically valid coordinate pairs | 572 |
| Nodes outside coarse Karachi plausibility envelope | 0 |
| Coordinate collision groups | 10 |
| Nodes participating in collisions | 24 |
| SMTA/EV route-stop rows | 191 |
| Exact normalized-name candidates | 89 |
| Unmatched rows | 102 |
| Distinct candidate coordinate nodes | 56 |
| Candidate nodes referenced by multiple source-stop rows | 20 |
| Historical edge rows | 1,415 |
| Historical route labels | 76 |
| Dangling historical edge references | 0 |

The broad coordinate envelope (24.65–25.15 N, 66.65–67.50 E) is only an anomaly screen. It does not prove a point is a bus stop or that it is on the correct side of a road.

## Coordinate collision groups requiring human review

Each group below contains multiple differently named source nodes with exactly the same coordinate. This is a review flag, not proof that the coordinate is wrong: some names may be aliases or nearby areas represented by one coarse landmark point.

| Coordinate (lat, lon) | Node IDs |
|---|---|
| 24.860696, 67.000524 | lee_market; sabzi_mandi |
| 24.834432, 67.072674 | korangi_no_5; korangi_no_2-1/2; korangi_no_6; korangi_road |
| 24.902977, 67.038628 | liaquatabad_no_10; liaquatabad |
| 24.946106, 67.012881 | orangi_no_4; orangi_no_10; orangi_town |
| 24.841706, 67.133988 | korangi_industrial_area; vita_chowrangi |
| 24.857065, 67.033165 | lucky_star; lucky_star_saddar |
| 24.905865, 67.030718 | nazimabad; nazimabad_no_2; nazimabad_no_1 |
| 24.878791, 67.047539 | Karachi_university; dawood_engineering_university |
| 24.933948, 67.128953 | gul_city; gulshan_jauhar_goth |
| 24.839417, 67.253267 | machine_tool_factory; bhains_colony |

**Priority for follow-up:** review the collision groups containing multiple distinct numbered neighbourhoods or distant-sounding landmarks first (Korangi, Orangi, Nazimabad, university pair, and Machine Tool Factory/Bhains Colony). Do not separate points by applying arbitrary coordinate offsets.

## Candidate node reuse across published route-stop rows

Twenty coordinate node IDs are referenced by more than one source route-stop row. This may be a valid shared stop, a route-catalogue alias, or a name collision. It must be confirmed at the physical boarding-point level before route graph construction.

- model_colony — R1 #3; EV-01 #5; EV-02 #8
- malir_halt — R1 #4; EV-01 #6; EV-02 #9
- colony_gate — R1 #5; R2 #10; EV-01 #7
- paf_base_faisal — R1 #7; EV-01 #9
- karsaz — R1 #8; R3 #8; EV-01 #10
- nursery — R1 #9; R3 #9; EV-01 #11
- ftc — R1 #10; R3 #10; R12 #13; EV-01 #12
- tower — R1 #15; R4 #13; R8 #12; R13 #9; R14 #17
- north_karachi — R2 #1; R3 #1; R4 #1
- shafiq_mor — R2 #3; R4 #3
- korangi_crossing — R2 #16; R12 #10
- ayesha_manzil — R4 #5; R14 #9; EV-04 #11
- teen_hatti — R4 #7; R14 #11
- jahangir_road — R4 #8; R14 #12
- numaish — R4 #10; R14 #14; EV-03 #17
- taj_complex — R4 #11; R14 #15
- gulbai — R8 #8; R13 #5
- tank_chowk — EV-01 #4; EV-02 #7
- bahria_town — EV-02 #1; EV-04 #1
- al_asif_square — EV-04 #9; EV-05 #10

## Unmatched rows by route

| Route | Unmatched |
|---|---:|
| R1 | 6 |
| R2 | 8 |
| R3 | 6 |
| R4 | 7 |
| R8 | 4 |
| R11 | 6 |
| R12 | 8 |
| R13 | 6 |
| R14 | 10 |
| EV-01 | 8 |
| EV-02 | 5 |
| EV-03 | 10 |
| EV-04 | 8 |
| EV-05 | 10 |
| **Total** | **102** |

The full unmatched stop names, source sequence numbers and blank reviewer decision fields are in the generated `stop_review_queue.csv` artifact. The full 191-row register is retained; this summary does not alter it.

## Recommended manual-review order

1. Resolve the ten coordinate collision groups, recording whether each is an alias, shared interchange, or wrong/too-coarse coordinate.
2. Review the twenty reused candidate nodes, especially where the same coordinate is assigned to differently described route contexts.
3. Start with unmatched stops that sit between already matched stops in an SMTA sequence; these have the greatest impact on route continuity.
4. Keep route identity conflicts (notably R11/R12) separate from coordinate matching. A coordinate cannot resolve an uncertain route description.
5. Only after stop identity, physical boarding side, direction and sequence are evidenced should road-network snapping and road-following route shapes begin.

## Safety and interpretation

- Exact normalized-name match means candidate match only.
- Historical node membership and edges are not current operator confirmation.
- No geocoding, route snapping, line interpolation, database writes, verification-state changes, or route activation was performed.
- The generated GeoJSON is point-only. The 1,415 historical edges are graph links, not road-centreline geometry.
