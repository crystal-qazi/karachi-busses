# Phase 5AN — Think Transportation R-series route reconciliation

**Review date:** 2026-11-18  
**Status:** Think Transportation accepted by the project owner as an authentic reference for People's Bus Service R-series and EV-series route identity, published route descriptions and the supplied route KML. This phase records the R-series decisions below. It does not certify live dispatch, physical boarding poles, coordinates or reverse-direction paths.

## Accepted reference

- Think Transportation, **New Red Bus Karachi (Peoples Bus Service) Route Maps**, updated 3 February 2025: https://thinktransportation.net/red-bus-karachi/
- Think Transportation KHI-MAP-08, dated 1 January 2025: https://thinktransportation.net/Karachi_transport_map_peoples_bus_service_green_line_orange_line_think_transportation.pdf
- Project-supplied KML: `Think Transportation - Red Bus (Peoples Bus Service) Routes Karachi (1).kml`, whose description reports an update date of 1 February 2025.

The route webpage provides route tables, terminal descriptions and ordered named-entry lists. The supplied KML provides route LineStrings for R1, R2, R3, R4, R8, R9, R10, R11, R12, R13 and EV-01 through EV-05. Keep the KML coordinate sequence, direction and vertices unchanged.

The webpage's operational labels and route details are source statements from its February 2025 publication, not proof of live service on the review date. Preserve publication date and source attribution.

## R-series reconciliation decisions

| Route | Accepted Think Transportation reference | Reconciliation decision | Remaining limitation |
|---|---|---|---|
| R1 | Khokrapar–Dockyard; detailed list begins Khokrapar, Saudabad, RCD Ground, Kalaboard and continues via Malir Halt to Dockyard | Accept Think's Khokrapar spelling and corridor. KML label "Khokrapar No. 1" is retained verbatim as its geometry label; do not force it to SMTA's "Khokharapar 04 / Kokharpar 04". | Exact terminal/boarding-point identity and the difference between "Khokrapar" and "Khokrapar No. 1" remain physical/name-level checks. Think's detailed list names Malir Halt once. |
| R2 | Power House–Indus Hospital; 15 listed entries, ending Indus Hospital | Accept Power House–Indus Hospital and Think's listed order as the working R2 reference. Preserve SMTA's North Karachi–Korangi Crossing variant as a conflicting published statement, not as the adopted R2 identity. | Physical stop positions and whether the SMTA page reflects another revision/variant remain unverified. |
| R3 | Power House–Nasir Jump; page labels Route 3 "Temporary Change" and lists 20 entries ending Nasir Jump | Accept Power House–Nasir Jump and Think's temporary-change list as the working reference. Do not substitute SMTA's North Karachi origin. | The temporary-change label is retained; effective date/current continuation and physical stops are not independently established. |
| R4 | Power House–Keamari; listed path passes Tower and ends with the combined wording "Tower and Keamari" | Accept Power House–Keamari as the route identity. Preserve "Keamari" as Think's spelling; record "Kemari" as an alternate spelling only. | The source combines Tower and Keamari in its final entry; exact terminal sequence and boarding location need separate checking. |
| R8 | Yousuf Goth–Tower; detailed list runs through Naval Colony, Baldia, Sher Shah, Gulbai, Agra Taj Colony, Daryabad and Jinnah Bridge | Accept Yousuf Goth→Tower as the reference direction. Treat the SMTA index's Tower–Yousuf Goth wording as the opposite corridor presentation, not a different route. | Do not generate a reverse direction by simply reversing the stop list or KML vertices; a return path needs its own evidence/geometry. |
| R11 | Miran Nakka–Shireen Jinnah Colony; detailed list includes Miran Nakka, Gulistan Colony, Bihar Colony, Agra Taj, Daryabad, Jinnah Bridge, Bahria Complex, M.T. Khan Road, PICD, Submarine Chowk, Bahria Complex 3, Khadda Market, Abdullah Shah Ghazi, Bilawal Chowrangi, Ziauddin Hospital and Shireen Jinnah Colony | Accept Think's Miran Nakka–Shireen Jinnah Colony corridor and detailed list as the R11 reference. Ziauddin Hospital is an intermediate listed entry, not the endpoint. Preserve SMTA's Mera Naka–Ziauddin Hospital description as an alternate conflicting source statement. | Physical identity of Miran Nakka/Miran Naka and stop locations remain unverified. |
| R12 | Naddi Kinara–Lucky Star; detailed list begins Naddi Kinara, Khokhrapar, Saudabad Chowrangi, RCD Ground and continues through Korangi/Qayyumabad to Lucky Star Saddar | Accept Think's Naddi Kinara–Lucky Star corridor and listed order. Preserve SMTA's Memon Goth–Sadar Lucky Star as a conflicting published description, not an adopted replacement. | Whether SMTA reflects a later revision or separate variant is not established. Do not merge the two sequences. |
| R13 | Hawksbay–Tower; detailed list is Hawksbay, Mauripur, Gulbai, Agra Taj, Daryabad, Jinnah Bridge, Tower | Accept Think's Hawksbay–Tower sequence. The current detailed list has Gulbai once, after Mauripur; the older anomaly is not used to reorder this sequence. | Physical stop identities and road-side boarding points remain unverified. |

## Geometry and sequence handling

1. The KML LineString is the route geometry reference for each R route present in the supplied file.
2. Preserve original coordinate order, direction, vertices and source labels. No snapping, simplification, reversal, geocoding, interpolation or road replacement is authorized by this reconciliation.
3. The website's ordered named-entry list is a route-description reference. It does not itself provide GPS coordinates or prove that each named area is a discrete passenger boarding pole.
4. Do not infer return-direction geometry by reversing the outbound LineString.
5. Keep SMTA's conflicting descriptions in the source-conflict register for traceability. They no longer block selection of Think Transportation as the project's accepted R-series reference, but they remain recorded as source differences.
6. No route, stop, source or geometry verification status in MySQL is changed by this research phase.

## Licensing and attribution

Retain Think Transportation attribution and the source notice. The KHI-MAP-08 PDF states that use without permission is prohibited. Confirm applicable permission/terms before public redistribution or production publication of the supplied KML or derived geometry. This phase does not claim that permission has been obtained.

## Next work

- Apply the same accepted Think Transportation reference treatment to EV-01–EV-05, preserving their existing route/waypoint reconciliation evidence.
- Continue physical stop matching and coordinate/boarding-side verification separately.
- Review R14 and DD01, which are not present in the supplied KML, without fabricating replacement geometry.
- Prepare direction-specific road-following geometry only from reviewed evidence.
