# Phase 5AM — Think Transportation KML Geometry and SMTA Route Register Alignment

**Review date:** 2026-11-18  
**Status:** Source hierarchy adopted; route inventory and published sequence register updated. No geometry or database records changed.

## Adopted source hierarchy

1. **Think Transportation KML supplied for this project:** primary route-line geometry reference for routes present in the file. Preserve original coordinate order, direction and vertices. Do not snap, simplify, reverse, geocode, interpolate or replace the source line.
2. **Sindh Mass Transit Authority (SMTA):** authority for the route status, route names and numbered stop/area sequences it publishes. Individual route-detail pages are the sequence source; differences with the route-map index remain visible as conflicts.
3. **User-supplied Google Maps routes and coordinates:** supplementary route/waypoint evidence. Preserve exact user coordinates and sequence; do not silently insert waypoints or alter a route.
4. **Think Transportation website and other route directories:** supplementary corroboration only; they do not override SMTA for official status or sequence.
5. **Bus Kahan Hai:** live vehicle-position evidence only when its feed actually provides usable current observations. An empty/stale feed is not proof that a service is inactive.
6. **TransKarachi:** evidence for its BRT corridors and project scope, not a substitute for People's Bus route details.
7. **OpenStreetMap:** supporting geographic and road context only. It is not the primary route geometry source.

## Supplied KML inventory

The supplied file is named `Think Transportation - Red Bus (Peoples Bus Service) Routes Karachi (1).kml`. Its document description reports an update date of 2025-02-01.

- 15 route LineStrings: R1, R2, R3, R4, R8, R9, R10, R11, R12, R13 and EV-01 through EV-05.
- 10,803 coordinate vertices across those lines.
- Approximately 463.52 km combined geodesic line length.
- The KML contains route lines, not separately identified passenger-stop placemarks. Vertices must never be interpreted as bus stops.
- Original KML coordinate order and direction are retained. This audit does not authorize any geometry edit.

### SMTA-listed routes absent from this KML

- R5, R6 and R7 — SMTA currently labels these inactive.
- R14 — SMTA labels this route active.
- DD01 — SMTA labels the Double Decker route active.

Absence from the KML is not evidence of route inactivity. No replacement geometry is inferred for these routes.

## SMTA numbered sequence register

The Phase 5AF register now contains 268 numbered entries from 20 SMTA route-detail pages: R1–R14, EV-01–EV-05 and DD01. The first numbered item on each page is retained as a direction descriptor, not treated as a separately inferred passenger stop. R5–R7 retain their published inactive status.

See:
- `data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv`
- `docs/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.md`

## Known source conflicts retained

- R1: SMTA's Khokharapar 04 / Kokharpar 04 differs from the KML's Khokrapar No. 1 label.
- R2–R4: SMTA individual-page origin descriptions differ from the KML Powerhouse labels.
- R11 and R12: SMTA individual detail-page endpoint descriptions differ from the route-map index labels.
- EV-01: SMTA names CMH Malir Cantt; the KML label is Malir Cantt.
- EV-03: SMTA names Quaid-e-Azam Square Malir Cantt via X-20; KML uses Malir Cantt–Numaish.
- Route lengths published by SMTA are not used to stretch, shorten or otherwise modify KML geometry.

Conflicts are recorded, not silently adjudicated. A route name or sequence does not prove the identity or physical location of a boarding pole.

## Licensing and redistribution

The supplied map/KML carries Think Transportation attribution and a notice restricting use without permission. The source file and derived route geometry are not added to this repository by this phase. Confirm permission or applicable terms before public redistribution, publication, or production use of the KML or derived geometry. Retain attribution and any required notices.

OpenStreetMap-derived supporting context must retain © OpenStreetMap contributors attribution and ODbL 1.0 licensing.

## Explicitly not done

- No MySQL writes, route activation, stop approval or verification-status changes.
- No historical coordinate replacement or stop-to-route assignment.
- No geocoding, snapping, route interpolation or road-following geometry generation.
- No geometry changes to the supplied KML.
- No claim that every SMTA named area is a verified physical passenger boarding location.

## Next gate

Continue route-by-route review against the published SMTA sequence and preserved KML line. Reconcile route identity and direction conflicts; obtain permission for use of the KML; verify physical boarding points independently before assigning coordinates or publishing routes.
