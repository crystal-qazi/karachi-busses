# Phase 5AM — Think Transportation KML and route register alignment

**Original review date:** 2026-11-18  
**Follow-up decision:** Phase 5AN, 2026-11-18  
**Status:** Think Transportation is accepted by the project owner as an authentic reference for People's Bus Service R-series and EV-series route identity, route descriptions and the supplied KML. This supersedes the earlier wording that treated Think Transportation's website as merely supplementary.

## Accepted Think Transportation material

- Route details: https://thinktransportation.net/red-bus-karachi/ (page updated 3 February 2025).
- KHI-MAP-08 PDF: https://thinktransportation.net/Karachi_transport_map_peoples_bus_service_green_line_orange_line_think_transportation.pdf (dated 1 January 2025).
- Supplied KML: `Think Transportation - Red Bus (Peoples Bus Service) Routes Karachi (1).kml` (description reports 1 February 2025).

Use the Think Transportation route page and KML as authentic project references for R-series and EV-series route identity, published route descriptions and route-line geometry. Retain source dates and attribution. The route page's operational labels are statements published in February 2025, not live dispatch confirmation on the current date.

## Route and geometry handling

1. For routes present in the supplied KML, preserve the original LineString coordinate order, direction and vertices exactly. Do not snap, simplify, reverse, geocode, interpolate or replace the geometry.
2. Use Think Transportation's detailed route page for its published route labels, terminal descriptions and ordered named-entry lists.
3. SMTA route pages and route-map index remain useful government-published comparison evidence. Where they differ from Think Transportation, retain the discrepancy as an alternate source statement; do not silently replace the accepted Think Transportation route reference.
4. User-supplied Google Maps routes and coordinates remain supplementary evidence. Preserve exact user coordinates and waypoint order; do not silently insert waypoints or alter routes.
5. Bus Kahan Hai is live vehicle-position evidence only when its feed supplies usable current observations.
6. TransKarachi is evidence for its BRT corridors and project scope, not a substitute for People's Bus R/EV route detail.
7. OpenStreetMap is supporting geographic and road context only. It is not a replacement for Think Transportation route geometry.

## Supplied KML inventory

- 15 route LineStrings: R1, R2, R3, R4, R8, R9, R10, R11, R12, R13 and EV-01 through EV-05.
- 10,803 coordinate vertices across those lines.
- Approximately 463.52 km combined geodesic line length.
- The KML contains route lines, not separately identified passenger-stop placemarks. Vertices must never be interpreted as bus stops.
- Original KML coordinate order and direction are retained.

### Routes absent from supplied KML

- R5, R6 and R7.
- R14.
- DD01.

Absence from the KML is not evidence of inactivity. R14 and DD01 require separately sourced geometry; do not fabricate replacement lines.

## R-series conflict reconciliation

Phase 5AN records the owner-approved Think Transportation decisions for R1, R2, R3, R4, R8, R11, R12 and R13:

- R1: Think's Khokrapar–Dockyard reference is accepted; retain the KML's "Khokrapar No. 1" label and SMTA spellings without forced equivalence.
- R2: accept Power House–Indus Hospital; retain SMTA's North Karachi–Korangi Crossing description as an alternate statement.
- R3: accept Power House–Nasir Jump; retain the Think page's "Temporary Change" qualifier.
- R4: accept Power House–Keamari; retain Kemari as an alternate spelling, with terminal ordering still to be checked.
- R8: accept Yousuf Goth→Tower as the reference direction; do not infer reverse geometry.
- R11: accept Miran Nakka–Shireen Jinnah Colony; Think lists Ziauddin Hospital as an intermediate entry, while SMTA describes Mera Naka–Ziauddin Hospital.
- R12: accept Naddi Kinara–Lucky Star; retain SMTA's Memon Goth–Sadar Lucky Star statement separately.
- R13: accept the current Think sequence, where Gulbai appears once after Mauripur.

See `docs/research/PHASE_5AN_THINK_TRANSPORTATION_R_SERIES_RECONCILIATION.md` and its CSV companion for route-by-route details.

## Sequence and physical-stop limitations

Think Transportation's ordered named-entry lists are accepted route-description references. They do not provide GPS coordinates for every physical boarding pole or prove the exact boarding side/platform. Keep physical stop identity, coordinate, boarding side and field verification as separate checks. Do not infer a return direction by reversing an outbound sequence or LineString.

## Licensing and attribution

The supplied map/KML carries Think Transportation attribution and a notice restricting use without permission. Retain attribution and confirm applicable permission/terms before public redistribution, publication or production use of the KML or derived geometry. This project phase does not claim that permission has been obtained.

OpenStreetMap-derived supporting context must retain © OpenStreetMap contributors attribution and ODbL 1.0 licensing.

## Explicitly not done

- No MySQL writes, route activation, stop approval or verification-status changes.
- No historical coordinate replacement or stop-to-route assignment.
- No geocoding, snapping, route interpolation or road-following geometry generation.
- No geometry changes to the supplied KML.
- No claim that every named area is a verified physical passenger boarding location.

## Next gate

Apply the accepted Think Transportation reference consistently to EV-01–EV-05, then continue physical stop matching and coordinate/boarding-side verification. Review R14 and DD01 separately because they are absent from the supplied KML. Prepare direction-specific road-following geometry only from reviewed evidence.
