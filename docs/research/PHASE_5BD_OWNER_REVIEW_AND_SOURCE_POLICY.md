# Phase 5BD — owner-reviewed route sequences and source-policy reconciliation

**Date:** 18 November 2026  
**Repository:** crystal-qazi/karachi-busses  
**Branch:** research/phase-5bd-owner-review-and-source-policy  
**Scope:** Documentation-only reconciliation. No MySQL or application data changes.

## Decisions recorded

The project owner adopted Think Transportation's published route descriptions as the primary R/EV route identity and displayed forward-sequence reference, and the supplied KML as the primary route-line research reference where present. SMTA route pages remain government-published comparison evidence and conflicts must remain visible.

OSM remains the primary geographic and road-network reference. The Think Transportation KML has a reuse restriction; the permission request is prepared but not yet sent or approved. No KML-derived geometry may be redistributed or published, and route_shapes must remain empty until written permission covers the intended use.

## Owner-review state

See [USER_ROUTE_VERIFICATION_REGISTER.md](USER_ROUTE_VERIFICATION_REGISTER.md) for the full ordered lists and exact corrections.

| Route | Owner review |
|---|---|
| R1 | Confirmed |
| R2 | Confirmed |
| R3 | Confirmed with Shan Chowrangi inserted after Brookes Chowrangi |
| R4 | Confirmed |
| R8 | Confirmed |
| R9 | Confirmed |
| R10 | Confirmed with Do Talwar, Pak Tower and Abdullah Shah Ghazi separated in that order |
| R11 | Confirmed |
| R12 | Confirmed 2026-11-19 |
| R13 | Confirmed 2026-11-19 |

Owner review is not independent physical-stop, operator, dispatch, coordinate, or return-direction verification. No database verification state or publication eligibility changes were made.

## Next actions

1. Prepare the R14 source-comparison and owner-review packet; preserve the fact that the currently adopted Think Transportation route list does not provide an R14 sequence while SMTA publishes a detailed via-description.
2. Continue owner review for EV-01–EV-05 using clearly attributed published sequences and retain source discrepancies.
3. Continue exact-name candidate matching against the 572 historical coordinate nodes; never promote a candidate based only on name similarity or proximity.
4. Keep unverified stops/sources under review and route_shapes empty.
5. Use OSM for geographic/road-network analysis only after candidate boarding points and licence constraints are checked. Do not derive public route geometry from the restricted KML before written permission.

## Validation and safety

- Documentation only.
- No database connection or writes.
- No route/stop coordinate changes, route activation, route-shape creation, source verification, or public API changes.
- No external permission request was sent.
