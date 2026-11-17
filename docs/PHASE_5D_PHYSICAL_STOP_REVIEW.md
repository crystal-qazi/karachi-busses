# Phase 5D — Physical Stop Identity and Boarding-Point Review

**Status:** Research worksheet only. No stop is physically verified by this document.

## Purpose

Convert the Phase 5C text crosswalk into a defensible stop register without treating a name match as proof of a physical boarding point. The 572 historical coordinate nodes remain candidate locations until the identity, road side/platform, and source are checked.

## Review sequence

1. Resolve route identity and direction first. If the route variant is unresolved, set `route_identity_status=unresolved` and do not approve its stop sequence.
2. Compare the published stop label with local aliases and nearby landmarks. Record aliases; never silently overwrite the original source label.
3. Identify the actual boarding point, not the neighbourhood centroid or the opposite carriageway.
4. Record WGS84 coordinates in decimal degrees and the coordinate capture method.
5. Record the road name, travel direction, road side, platform/bay, and accessibility notes where known.
6. Attach evidence: current operator route sheet/timetable, dated official map, operator written confirmation, or dated field survey. A generic web map or historical node is corroboration only.
7. Have a second reviewer check the evidence and coordinate placement before changing status.

## Status vocabulary

- `unreviewed`: not yet examined.
- `candidate_name_match`: text/alias match only; not a physical-stop approval.
- `needs_operator_confirmation`: route, direction, service, or boarding point is ambiguous.
- `needs_field_survey`: source describes the stop but no reliable physical boarding coordinate exists.
- `reviewed_candidate`: evidence and coordinates have been inspected, but publication gates are not all met.
- `verified`: operator or field evidence establishes route, direction, stop identity, boarding side/platform, and coordinate; second review completed.
- `rejected_match`: candidate node is not the same physical stop.

## Evidence grades

- `A_operator_current`: current operator-issued route sheet, stop register, timetable/map, or written confirmation.
- `B_official_project`: official government/project document, but not necessarily current operational stop-level evidence.
- `C_field_survey`: dated on-site observation with GPS/photo/observer and boarding-side details.
- `D_secondary`: secondary publication or general mapping; candidate corroboration only.
- `E_historical_dataset`: legacy coordinate dataset; historical candidate only.

A stop may be marked `verified` only with Grade A or Grade C evidence, or a documented combination explicitly accepted by the data reviewer. Grade B/D/E alone cannot verify current boarding location.

## Publication gate

Do not import, activate, or publish a stop or route from this worksheet. Route publication still requires verified route identity, both directions, ordered stops, verified source, verified stop coordinates/boarding sides, and road-following geometry for each direction, as defined in `docs/PHASE_5.md`.

## Current blockers

Issue #20 tracks operator confirmation for R2/R3/R4/R8/R11/R12, R1/R13 sequence anomalies, and Green/Orange Line station order. These blockers must remain visible in the review register; a missing response is not evidence of correctness.
