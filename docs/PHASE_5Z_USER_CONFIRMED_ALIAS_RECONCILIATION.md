# Phase 5Z — User-Confirmed Alias Reconciliation

## Purpose

Apply the 13 name equivalences explicitly confirmed by the user in Phase 5Y to the historical route-stop crosswalk as a **derived name-review register**. This makes the name-only matches visible without modifying the source crosswalk or assigning coordinates.

## Exact matching and inputs

The builder reads:

- \`data/research/PHASE_5_STOP_NODE_CROSSWALK.csv\`
- \`data/research/PHASE_5X_SPELLING_ALIAS_CANDIDATE_SHORTLIST.csv\`
- \`data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv\`

It joins shortlist rows to the source crosswalk by the exact pair \`route_code + source_stop_sequence\`, checks the original stop name, and checks that the candidate node ID is one of the explicitly user-confirmed Phase 5Y name pairs.

## Output

- \`PHASE_5Z_USER_CONFIRMED_ALIAS_RECONCILIATION.csv\`
- \`PHASE_5Z_USER_CONFIRMED_ALIAS_RECONCILIATION_REPORT.json\`

The workflow publishes both as a downloadable GitHub Actions artifact. The output preserves every source crosswalk row and all original coordinate fields.

## Interpretation

A row marked \`confirmed_by_user\` means only that the user confirmed the two names refer to the same named place for normalization/cross-reference purposes. The historical node ID is recorded in a separate candidate field; it is **not** copied into \`coordinate_node_id\`.

For every row:

- \`physical_stop_verification = unverified\`
- \`coordinate_assignment = not_assigned\`
- \`route_approval_status = not_approved\`

Rows without a confirmed alias remain in the register. They are not discarded and are not automatically matched to Phase 5W fuzzy candidates.

## Safety boundaries

This phase does not:

- change the Phase 5 source crosswalk;
- copy candidate coordinates or change latitude/longitude;
- confirm a physical passenger stop, platform, road side, boarding point, or route use;
- geocode, snap, infer a route, or build geometry;
- write to the production database.

OSM remains the primary geographic source. OSM road proximity is supporting context only and is not proof of a passenger stop.

## Rebuild

\`\`\`bash
python scripts/reconcile_user_confirmed_stop_aliases.py --build
python -m unittest tests.test_phase5z_alias_reconciliation -v
\`\`\`

The script uses only the Python standard library. No local executable or GIS installation is required.
