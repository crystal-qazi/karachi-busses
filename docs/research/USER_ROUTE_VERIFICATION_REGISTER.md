# User route verification register

**Updated:** 2026-11-19  
**Repository:** crystal-qazi/karachi-busses  
**Purpose:** Record route sequence reviews explicitly supplied by the project owner. A user confirmation is recorded as owner-reviewed; it is not represented as independent operator/field verification.

## Think Transportation — source-level verification

- **Source status:** Verified as an identifiable, published reference source for the Karachi Peoples Bus Service route descriptions and the supplied route KML inventory.
- **Verification scope:** Source identity and the presence of published route descriptions / route-line geometry were checked. The source is accepted as the project's primary reference for the R-series and EV-series route identity, published sequence descriptions, and geometry inventory where present.
- **Routes represented in the supplied KML:** R1, R2, R3, R4, R8, R9, R10, R11, R12, R13, EV-01, EV-02, EV-03, EV-04, EV-05.
- **Not covered by this status:** Independent correctness of every stop name/order; physical stop or boarding-pole existence; stop coordinates; current service operation; return-direction details; operator/field confirmation; missing routes not present in the KML.
- **Data distinction:** This source-level status does not automatically change any `bus_stops.verification_status`, `bus_routes`, `route_stops`, `route_shapes`, `data_sources` database status, or public API eligibility. Owner-reviewed route sequences remain separately labelled below.
- **Rights restriction:** The supplied Think Transportation KML includes a restriction against use without permission. Do not publicly redistribute the KML or derived geometry until reuse permission or a suitable licence is established.
- **Primary public reference:** https://thinktransportation.net/red-bus-karachi/

## R1 — Khokrapar to Dockyard

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed stop list and order. This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Khokrapar
2. Saudabad
3. RCD Ground
4. Kalaboard
5. Malir Halt
6. Colony Gate
7. Nata Khan Bridge
8. Drigh Road Station
9. PAF Base Faisal
10. Laal Kothi
11. Karsaz
12. Nursery
13. FTC
14. Regent Plaza
15. Metropole
16. Fawwara Chowk
17. Arts Council
18. Shaheen Complex
19. I.I. Chundrigar
20. Tower
21. Fisheries
22. Dockyard

## R2 — Power House to Indus Hospital

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed stop list and order. This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Power House
2. UP Mor
3. Nagan Chowrangi
4. Shafiq Mor
5. Sohrab Goth
6. Gulshan Chowrangi
7. NIPA
8. Johar Mor
9. COD
10. Drigh Road Station
11. Colony Gate
12. Shah Faisal Colony
13. Singer Chowrangi
14. Khaddi Stop
15. Indus Hospital

## R3 — Power House to Nasir Jump

- **Owner review:** Confirmed with correction
- **Stop order:** Confirmed with the supplied insertion
- **Correction supplied:** Add **Shan Chowrangi** immediately after **Brookes Chowrangi**; all other displayed stops and their order accepted.
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the base sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the published sequence with the explicit addition above. The Think Transportation page labels R3 as a temporary-change route. This owner review does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence (with owner correction)

1. Power House
2. UP More
3. Nagan Chowrangi
4. Sakhi Hasan
5. 5 Star Chowrangi
6. KDA Chowrangi
7. Board Office
8. Nazimabad Eid Gah Ground
9. Liaquatabad 10 Number
10. Essa Nagri
11. Civic Centre
12. National Stadium
13. Karsaz
14. Nursery
15. FTC
16. Korangi Road
17. KPT Interchange
18. Brookes Chowrangi
19. Shan Chowrangi
20. Korangi Crossing
21. Nasir Jump

## R4 — Power House to Keamari

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed stop list and order, including the source's combined final entry "Tower and Keamari". This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Power House
2. UP Mor
3. Nagan Chowrangi
4. Shafiq Mor
5. Sohrab Goth
6. Water Pump
7. Ayesha Manzil
8. Karimabad
9. Liaquatabad 10
10. Laloo Khait
11. Teen Hati
12. Jehangir Road
13. Numaish
14. Mobile Market
15. Urdu Bazar
16. Civil Hospital
17. City Court
18. Light House
19. Bolton Market
20. Tower and Keamari (combined entry in the published source)

## R8 — Yousuf Goth to Tower

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed stop list and order. SMTA publishes a different/more detailed route description; this confirmation applies to the displayed Think Transportation sequence only. It does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Yousuf Goth
2. Naval Colony
3. Baldia
4. Sher Shah
5. Gulbai
6. Agra Taj Colony
7. Daryabad
8. Jinnah Bridge
9. Tower

## R9 — Gulshan-e-Hadeed to Tower

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None; all 35 displayed entries accepted.
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the detailed Think Transportation sequence. This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Gulshan-e-Hadeed
2. Salah Uddin Ayubi Road
3. Allah Wali Chowrangi
4. National Highway 5
5. Steel Mill More
6. Port Bin Qasim More
7. Razzakabad
8. Abdullah Goth
9. Chowkundi More
10. FAST University
11. Bhains Colony More
12. Manzil Pump
13. Quaidabad
14. Murghi Khana
15. Prince Aly Boys School
16. NADRA Center Malir
17. Malir Session Court
18. Malir 15
19. Kalaboard
20. Malir Halt
21. Colony Gate
22. Nata Khan Bridge
23. Drigh Road Station
24. PAF Base Faisal
25. Laal Kothi
26. Karsaz
27. Nursery
28. FTC
29. Regent Plaza
30. Metropole
31. Fawwara Chowk
32. Arts Council
33. Shaheen Complex
34. I.I. Chundrigar Road
35. Tower

## R10 — Numaish Chowrangi to Ibrahim Hyderi

- **Owner review:** Confirmed with correction
- **Stop order:** Confirmed with the supplied correction
- **Correction supplied:** Split the source's combined "Do Talwar / Abdullah Shah Ghazi" entry into three stops in this exact order: **Do Talwar**, **Pak Tower**, **Abdullah Shah Ghazi**.
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the base sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed Think Transportation sequence with the explicit split/insertion above. This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence (with owner correction)

1. Numaish Chowrangi
2. Mobile Market
3. Metropole
4. Frere Hall
5. Teen Talwar
6. Do Talwar
7. Pak Tower
8. Abdullah Shah Ghazi
9. Dolmen Mall
10. Clock Tower DHA
11. 26 Street
12. Masjid-e-Ayesha
13. Rahat Park
14. KPT Interchange
15. Korangi Crossing
16. CBM University
17. Parco
18. Ibrahim Hyderi

## R11 — Miran Nakka to Shireen Jinnah Colony

- **Owner review:** Confirmed
- **Stop order:** Confirmed
- **Corrections supplied:** None; all 16 displayed entries accepted.
- **Reviewed by:** Project owner
- **Review date:** 2026-11-18
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page (published route description; accessed 2026-11-18): https://thinktransportation.net/red-bus-karachi/
- **Important distinction:** The owner confirmed the displayed Think Transportation sequence. This does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Miran Nakka
2. Gulistan Colony
3. Bihar Colony
4. Agra Taj
5. Daryabad
6. Jinnah Bridge
7. Bahria Complex
8. M.T. Khan Road
9. PICD
10. Submarine Chowk
11. Bahria Complex 3
12. Khadda Market
13. Abdullah Shah Ghazi
14. Bilawal Chowrangi
15. Ziauddin Hospital
16. Shireen Jinnah Colony

## R12 — Naddi Kinara to Lucky Star Saddar

- **Owner review:** Confirmed
- **Stop order:** Confirmed exactly as displayed below
- **Corrections supplied:** None; all 25 displayed entries accepted in the published order.
- **Reviewed by:** Project owner
- **Review date:** 2026-11-19
- **Reference used for the displayed sequence:** Think Transportation, New Red Bus Karachi route page, updated 3 February 2025: https://thinktransportation.net/red-bus-karachi/
- **Published source terminal label:** Naddi Kinara to Lucky Star.
- **Important source conflict:** SMTA's detailed route page describes Memon Goth to Sadar Lucky Star. The historical coordinate dataset's Route-12 chain begins at Naddi Kinara and ends at Lucky Star Saddar. The owner confirmation applies to the displayed Think Transportation sequence; it does not resolve the separate SMTA origin conflict.
- **Important distinction:** Owner confirmation does not independently verify physical boarding poles, GPS coordinates, current dispatch, return-direction sequence, or permission to redistribute Think Transportation's KML geometry.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Owner-confirmed forward stop sequence

1. Naddi Kinara
2. Khokhrapar
3. Saudabad Chowrangi
4. RCD Ground
5. Kalaboard
6. Malir 15
7. Malir Mandir
8. Malir Session Court
9. Murghi Khana
10. Quaidabad
11. Dawood Chowrangi
12. Babar Market
13. Landhi Road
14. Nasir Jump
15. Indus Hospital
16. Korangi Crossing
17. Qayyumabad
18. Defence Mor
19. National Medical Center
20. Gora Qabristan
21. FTC
22. Jutt Land
23. Lines Area
24. Army Public School
25. Lucky Star Saddar
- **Reference used for the review draft:** Think Transportation, New Red Bus Karachi route page, updated 3 February 2025: https://thinktransportation.net/red-bus-karachi/
- **Published source terminal label:** Naddi Kinara to Lucky Star.
- **Important source conflict:** SMTA's detailed route page describes Memon Goth to Sadar Lucky Star. The historical coordinate dataset's Route-12 chain begins at Naddi Kinara and ends at Lucky Star Saddar. These are distinct source statements; this review draft does not resolve the origin conflict.
- **Review request:** Confirm whether the following displayed Think Transportation names and their exact order are correct. If a name or order is wrong, provide the correction and its position.
- **Database impact:** None. No MySQL rows, route/stop verification statuses, route shapes, or public API publication state were changed.

### Published Think Transportation forward sequence — awaiting owner confirmation

1. Naddi Kinara
2. Khokhrapar
3. Saudabad Chowrangi
4. RCD Ground
5. Kalaboard
6. Malir 15
7. Malir Mandir
8. Malir Session Court
9. Murghi Khana
10. Quaidabad
11. Dawood Chowrangi
12. Babar Market
13. Landhi Road
14. Nasir Jump
15. Indus Hospital
16. Korangi Crossing
17. Qayyumabad
18. Defence Mor
19. National Medical Center
20. Gora Qabristan
21. FTC
22. Jutt Land
23. Lines Area
24. Army Public School
25. Lucky Star Saddar

