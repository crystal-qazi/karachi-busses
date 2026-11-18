# Phase 5AO — Think Transportation EV-series route reconciliation

**Review date:** 2026-11-18  
**Status:** Think Transportation accepted by the project owner as the authentic route reference for EV-01 through EV-05. Route descriptions below are transcribed from the Think Transportation page updated 3 February 2025 and cross-referenced to the supplied KML route lines. This is not live dispatch confirmation or physical stop verification.

## Accepted source

Think Transportation, [New Red Bus Karachi (Peoples Bus Service) Route Maps](https://thinktransportation.net/red-bus-karachi/), updated 3 February 2025. The same source lists EV-1 to EV-5 in its KHI-MAP-08 map dated 1 January 2025. The supplied KML includes EV-01 through EV-05 LineStrings. Preserve each KML LineString's original vertices, coordinate order and direction exactly.

The source page also carries a disclaimer that Think Transportation does not operate the service and does not warrant the correctness of all supplied information. The project owner has accepted this material as the authentic reference for this project. Its publication date and caveat remain recorded; its operational labels must not be mistaken for real-time dispatch evidence.

## Route-by-route accepted description

| Route | Think Transportation terminals | Published distance | Ordered named entries |
|---|---|---:|---|
| EV-01 | CMH Malir Cantt → Dolmen Mall Clifton | 28 km | CMH Malir Cantt; Tank Chowk; Model Colony Mor; Jinnah Ave; Airport; Colony Gate; Nata Khan Bridge; Drigh Road Station; PAF Base Faisal; Laal Kothi; Karsaz; Nursery; FTC; Korangi Road; DHA Phase 1; Masjid e Ayesha; Clock Tower DHA; Dolmen Mall Clifton |
| EV-02 | Bahria Town → Malir Halt | 30 km | Bahria Town; Dumba Goth; Toll Plaza; Baqai University; Malir Cantt Gate 5; Malir Cantt Gate 6; Tank Chowk; Model Mor; Jinnah Ave; Malir Halt |
| EV-03 | Malir Cantt Check Post 5 → Numaish | 20 km | Malir Cantt Check Post 5; Rim Jhim Tower; Safoora Chowrangi; Mausamiyat Chowrangi; Kamran Chowrangi; Darul Sehat Hospital; Johar Chowrangi; Johar Mor; Millennium Mall; Dalmia Road; Bahria University; National Stadium; Aga Khan Hospital; Liaquat National Hospital; PIB Colony; Jail Chowrangi; Dawood Engineering University; Islamia College; People Secretariat Chowrangi; Numaish |
| EV-04 | Bahria Town → Ayesha Manzil | 34 km | Bahria Town; Dumba Goth; M9 Toll Plaza; Jamali Pull; New Sabzi Mandi; Al Asif; Sohrab Goth; Water Pump; Ayesha Manzil |
| EV-05 | DHA City → Sohrab Goth | 41 km | DHA City; Bahria Town; Dumba Goth; M9 Toll Plaza; Jamali Pull; New Sabzi Mandi; Al Asif; Sohrab Goth |

These are source-listed named entries, not necessarily surveyed passenger boarding poles. Retain source spelling as written; normalize aliases only in a separate crosswalk and never overwrite the source label.

## Reconciliation with earlier SMTA sequence register

The existing Phase 5T / Phase 5AF material records SMTA's own published sequences. Those are now retained as a separate government-published comparison, not as the accepted primary route description for EV routes. Do not delete that evidence or merge its sequence into the Think sequence.

Notable differences include:
- EV-01: Think includes Model Colony Mor, Jinnah Ave, Airport, Drigh Road Station, Laal Kothi, Korangi Road and DHA Phase 1; its ordered list differs materially from SMTA's.
- EV-02: Think includes Dumba Goth, Toll Plaza, Baqai University, Malir Cantt Gate 5 and Gate 6, Model Mor and Jinnah Ave. SMTA's eight-entry sequence is shorter and differs in stop naming/order.
- EV-03: Think's 20-entry list includes Rim Jhim Tower, Darul Sehat Hospital, Dalmia Road, PIB Colony, Jail Chowrangi and Dawood Engineering University. Do not substitute SMTA's 16-entry list.
- EV-04: Think's nine entries include Jamali Pull and New Sabzi Mandi; SMTA's ten-entry sequence differs.
- EV-05: Think identifies DHA City as the origin and includes Bahria Town; the source page's distance is 41 km. Retain SMTA's separate description as a comparison.

## User Google Maps waypoint evidence

- EV-01: the user-supplied Google Maps waypoint order is preserved. The prior KML comparison found all 18 user waypoints within 4.1 m of the KML line, but flagged a possible order inversion between Tank Chowk and Model Colony. Do not reorder either source to force a match.
- EV-02: the user-supplied Google Maps route has seven extracted waypoints, in the supplied order, while Think's published list has ten named entries. The user separately supplied a Karachi Toll Plaza coordinate; do not silently insert it into the Google Maps waypoint list. Preserve the user-supplied Domba Goth and Toll Plaza coordinates as separate coordinate evidence. Prior KML comparison found the supplied waypoints within 105.3 m of the line, but the first user waypoint occurs about 13.44 km along the KML line, so the KML includes a preceding segment.
- No equivalent user waypoint set is recorded here for EV-03, EV-04 or EV-05. Do not fabricate one.

## Geometry and publication gates

1. The supplied KML LineString remains the route geometry reference for EV-01–EV-05. No snapping, simplification, reversal, geocoding, interpolation or replacement.
2. Do not interpret KML vertices as passenger stops.
3. Do not assume every Think named entry is a discrete stop with a known boarding pole, coordinate, side of road or platform.
4. Do not infer a return-direction route by reversing the outbound LineString.
5. Do not modify the MySQL database, activate routes, approve stops or change verification statuses as part of this research.
6. Retain Think Transportation attribution and permission notice. Confirm applicable permission/terms before public redistribution or production use of KML/derived geometry.

## Outputs

- `data/research/PHASE_5AO_THINK_TRANSPORTATION_EV_ROUTE_RECONCILIATION.csv`
- This report.

## Historical 572-node candidate crosswalk

Phase 5AQ compares all 65 Think EV named entries against the existing 572-node historical candidate set using exact normalized node-ID matching only. It found 47 candidate name matches and 18 unmatched names. These are not verified physical stops; all candidate nodes remain under review. See `docs/research/PHASE_5AQ_THINK_EV_TO_572_NODE_CANDIDATE_CROSSWALK.md` and its CSV.

## Next gate

Continue physical stop-name matching and coordinate/boarding-side verification for EV-01–EV-05. Reconcile the EV-01/EV-02 user waypoint evidence without altering the user's order. Then review R14 and DD01 separately because they are absent from the supplied KML.
