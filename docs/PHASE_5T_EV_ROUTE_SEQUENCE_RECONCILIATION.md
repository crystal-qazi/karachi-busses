# Phase 5T — EV-01 to EV-05 published stop-sequence reconciliation

**Status:** Historical SMTA sequence comparison retained for traceability. Phase 5AO (2026-11-18) supersedes this document as the accepted primary EV-01–EV-05 route-description reference: Think Transportation route page and supplied KML. This file remains a record of what SMTA separately publishes, not the adopted primary EV sequence.

## Source and method

Accessed 18 November 2026. Individual SMTA route-detail pages identify all five EV routes as **Active**, give bus type and route distance, and publish numbered "Stops and areas covered" lists:

- EV-01: [SMTA route 15](https://smta.gos.pk/routes/15)
- EV-02: [SMTA route 16](https://smta.gos.pk/routes/16)
- EV-03: [SMTA route 17](https://smta.gos.pk/routes/17)
- EV-04: [SMTA route 18](https://smta.gos.pk/routes/18)
- EV-05: [SMTA route 19](https://smta.gos.pk/routes/19)

The SMTA route-map directory credits its map data to Think Transportation and disclaims authentication of third-party service data. The SMTA "Active" labels and numbered lists below are retained as separate SMTA-published statements only. They do not override the Think Transportation EV route descriptions accepted by the project owner in Phase 5AO, and they are not live dispatch confirmation.

## Reconciliation rule

The existing historical crosswalk contains 66 EV route rows. Four labels—EV-02 "Usmania", EV-03 "X-20", EV-04 "M9", and EV-05 "M9"—are mentioned as route-via corridor markers, not numbered passenger stops on their individual route pages. They are therefore classified as `via_corridor_marker_not_passenger_stop`, not deleted. This produces 62 numbered passenger-stop entries across the five pages. EV-01's route description says "via CMH" within the first terminal item; CMH remains part of that terminal label and is not added as a separate stop.

The CSV retains every original crosswalk row and its candidate node/coordinates, while adding the individual page's numbered passenger-stop sequence, route-page ID, published status, distance, bus type, classification, source date and review note. Unmatched coordinate candidates remain unmatched. No fuzzy matching, geocoding, snapping or coordinate edits are performed.

## Route summary

| Route | Published passenger stops | Via-only markers removed from passenger sequence | Published distance | Bus |
|---|---:|---:|---:|---|
| EV-01 | 18 | 0 | 41 km | 12 m |
| EV-02 | 8 | 1 | 44 km | 12 m |
| EV-03 | 16 | 1 | 23 km | 9 m |
| EV-04 | 10 | 1 | 58 km | 12 m |
| EV-05 | 10 | 1 | 48 km | 12 m |
| **Total** | **62** | **4** | — | — |

## Geometry gate

All 62 passenger-stop rows remain coordinate-unverified. A historical name match does not confirm the physical boarding point, platform side, direction, or current operator use. The five SMTA route sequences remain available for comparison only. For the adopted EV route descriptions, use Phase 5AO and its CSV. Road-following geometry remains blocked pending physical boarding-point verification and direction-specific road-path review.

Think Transportation route page is the accepted EV route-description reference and its supplied KML is the primary route-line geometry reference where a route is present; preserve original coordinates, order and direction. SMTA remains an independent government-published comparison source for its own status and sequence statements. OSM and the Phase 5N road network are supporting geographic/road context only; they do not replace KML geometry or establish that a bus is permitted to use a road. OSM one-way, access, bus/PSV and conditional restrictions require separate review.

## Safety / scope

No route activation, production database writes, route inference, auto-snapping, invented coordinates, or external executable installation. Only pip-based Python tooling is used elsewhere in the project.

## Output

`data/research/PHASE_5T_EV_ROUTE_SEQUENCE_RECONCILIATION.csv` — all 66 original EV crosswalk rows, with via-only corridor markers explicitly classified and 62 numbered passenger-stop positions mapped to the source page sequences.
