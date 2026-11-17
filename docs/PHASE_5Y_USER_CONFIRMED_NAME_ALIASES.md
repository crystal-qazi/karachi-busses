# Phase 5Y — User-Confirmed Stop Name Aliases

## Decision

The user explicitly confirmed that the 13 source-name / historical-node-name pairs listed in this register are correct name aliases. This confirmation is recorded as `confirmed_by_user`, with the basis `user_confirmed_in_chat`.

The 13 alias pairs cover 20 route-stop occurrences across R1–R4, R11–R14 and EV-02–EV-05.

## Scope of confirmation

This approval confirms the equivalence of the names as written in the register. It allows the project to use the alias relationship for name normalization and cross-reference purposes.

It does **not** independently establish:
- that the historical node coordinate is the correct physical passenger stop;
- the exact boarding point, road side, direction, or stop platform;
- that a route currently serves the stop;
- road access or bus turning/continuity;
- approval of any route sequence or route geometry.

Accordingly, `physical_stop_verification` remains `unverified` and `coordinate_assignment` remains `not_assigned` for every row. The original Phase 5 stop-node crosswalk is not rewritten by this phase.

## Register

See `data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv`.

## Next safe use

The aliases may be applied in name-only comparisons and candidate grouping. Any coordinate linkage still requires a separate stop-level evidence decision. OSM remains the primary geographic source; road proximity is supporting context, not proof of a passenger stop.
