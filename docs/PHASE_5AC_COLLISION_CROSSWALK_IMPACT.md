# Phase 5AC — Coordinate Collision / SMTA Crosswalk Impact

## Purpose

Determine whether any historical exact-coordinate collision node is actually referenced by the current 191-row SMTA stop crosswalk. Two conservative joins are performed: exact historical node ID and exact coordinate equality (decimal-normalized). No fuzzy or proximity join is used.

## Current source result

The current data returns:

- 10 historical coordinate-collision groups, containing 24 node records.
- 0 crosswalk rows referencing any collision node ID.
- 0 crosswalk rows sharing an exact coordinate with a collision group.
- The crosswalk has 89 rows with a coordinate-node ID overall.

This means the known collisions are not presently used as direct coordinate assignments in the current SMTA stop crosswalk. It does not resolve what the historical nodes represent.

## Outputs

- \`data/research/PHASE_5AC_COLLISION_CROSSWALK_IMPACT.csv\`
- \`data/research/PHASE_5AC_COLLISION_CROSSWALK_IMPACT_REPORT.json\`

## Safety

Only exact joins are performed. The audit does not infer that nearby places are the same stop, transfer historical coordinates, merge nodes, change the crosswalk, verify boarding points, or approve routes. OSM remains the primary geographic source; any future route geometry must wait for verified stops and operator evidence.
