# Phase 5AH — Route Conflict Adjudication Register

## Purpose

Reconcile older Phase 5Q conflict statements against the current individual SMTA route-detail pages transcribed in Phase 5AF and the Phase 5AG name-only comparison.

## Findings

- The individual SMTA detail page is selected as the transcription source for its published named-entry sequence.
- It is **not** treated as proof that the route-map index is obsolete, that the listed route is currently dispatched in the field, or that physical boarding points are verified.
- Some earlier apparent duplicates are explained by the page's first numbered direction descriptor plus a separately named terminal/stop. The descriptor is not a passenger stop.
- R2, R3, R4, R8, R11 and R12 retain important endpoint/direction/identity conflicts requiring operator confirmation.
- R13 and R14 have improved published-sequence clarity, but physical routing and current map/index inconsistencies remain.
- EV-02 to EV-05 via/terminal markers are separated from numbered named entries.
- Green Line station count is 25 based on official procurement evidence, but the 25 identities/order remain unresolved.
- Orange Line's four contract station identities are recorded separately from the wider operating corridor and shared/mixed-traffic segments.

## Register

`data/research/PHASE_5AH_ROUTE_CONFLICT_ADJUDICATION.csv`

Each row records the current published finding, what can be adjudicated from documents, what remains unresolved, the evidence required, and the geometry gate.

## Important limits

This phase does not contact SMTA, TransKarachi, SIDCL or operators. It does not infer live service, approve routes, identify physical stop poles, assign coordinates, or create geometry. No conflict is marked fully resolved without authoritative operator evidence.

Supplied Think Transportation KML is the primary route-line geometry reference for routes present in that file; preserve its original coordinate order and direction without snapping, simplification, or replacement. SMTA is authoritative for published route status, route names and stop sequences. OSM is supporting geographic/road context only. Missing KML routes (including R14 and DD01) remain without adopted geometry until a permitted, source-backed geometry is obtained. Physical boarding-point verification remains a separate gate.
