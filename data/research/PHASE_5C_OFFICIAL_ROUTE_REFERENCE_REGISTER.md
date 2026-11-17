# Phase 5C — Published route-source register and stop identity review

**Status:** Source reconciliation only. No stop coordinate is approved by this register. No database or operational route data is changed.

## Source hierarchy and caveat

1. **SMTA current route directory** — https://smta.gos.pk/route-map (accessed 17 Nov 2026). It lists Karachi route codes, termini, active/inactive status and "via" stop descriptions. The page itself says the map data is courtesy of Think Transportation and that SMTA holds no responsibility for authentication of third-party service data.
2. **SMTA-hosted route map PDF KHI-MAP-08, dated 1 Jan 2025** — https://smta.gos.pk/downloads/karachi-bus-route-map.pdf. The PDF repeats the Think Transportation attribution and non-authentication disclaimer. Use as a published route-reference, not proof of current physical stop positions.
3. **Historical crosswalk and 572-node coordinate inventory** — internal research inputs; these are candidate locations, not operator-verified boarding points.
4. **News and other secondary sources** — corroboration only; never override an official/operator source.

The route directory's "via" text is not always a perfectly ordered stop-by-stop itinerary. The source contains repeated place names and conflicts between route index termini and detailed route descriptions. Those conflicts are recorded below rather than silently normalized.

## Current SMTA route descriptions (transcribed, sequence kept as published)

The route lists below preserve the published "via" order. Endpoints are shown separately. A stop named in a published description is **textually corroborated**, not coordinate-verified.

| Code | Published index termini / status | Detailed description endpoints | Source sequence (via) |
|---|---|---|---|
| R1 | Khokhrapar–Dockyard / Pink | Khokharapar 04 → Dockyard | Malir Halt; Kokharpar 04; Suadabad; Model Colony; Malir Halt; Colony Gate; Nata Khan; PAF Base Faisal; Karsaz; Nursery; FTC; Regent Plaza; Metropole Hotel; Press Club; I.I. Chundrigar Road; Tower; ICI Flyover |
| R2 | Powerhouse–Indus Hospital / Pink | North Karachi → Korangi Crossing | Nagan; Shafiq Mor; Sorab Goth; Gulshan; Nipa; Johar; COD; Nata Khan; Colony Gate; Shah Faisal Colony; Singer Chowrangi; Korangi #05; Nasir Jump; Indus Hospital |
| R3 | Powerhouse–Nasir Jump / Pink | North Karachi → Nasir Jump | Nagan; Five Star Chowrangi; Board Office; Nazimabad Petrol Pump; Essa Nagri; National Stadium; Karsaz; Nursery; FTC; Kala Pull; Akhtar Colony; Shan Chowrangi |
| R4 | Powerhouse–Keamari / Red | North Karachi → Kemari | Nagan; Shafiq Mor; Sorab Goth; Ayesha Manzil; Lalukhait; Teen Hatti; Jahangir Road; Guru Mandar; Numaish; Taj Complex; Sindh High Court; Tower; Jackson Market |
| R8 | Tower–Yousuf Goth / Red | Yousuf Goth → Tower | Hub River Road; Yousuf Goth; Saeedabad; Baldia; Ittehad Town; Naval Colony; Moach Goth; Sher Shah; Gulbai; Agra Taj; Dua Restaurant; ICI |
| R11 | Miran Naka–Shireen Jinnah Colony / Red | Mera Naka → Ziauddin Hospital | Maripur Road; Agra Taj Colony; KPT; Bahria Complex; PIDC; Punjabi Chowrangi; Gizri; Khayaban-e-Shamsheer; Abdullah Shah Ghazi Mazar; Bilawal Chowrangi |
| R12 | Naddi Kinara–Lucky Star / Red | Memon Goth → Sadar Lucky Star | Saudabad; Memon Goth; Khokharapar RCD Ground; Kala Board; Malir 15; Qaidabad; Dawood Chowrangi; 89 Chowrangi; Landhi; Korangi; Korangi Crossing; Qayyumabad; Kala Pull; FTC |
| R13 | Hawksbay–Tower / Red | Hawksbay → Tower | Gulbai; Hawksbay; Maripur; Pakistan Marine Academy; Maripur Truck Adda; Gulbai; Agra Taj; Dua Restaurant; ICI |
| R14 | Maymar–Tower / Red | Maymar → Tower | Nawaz Sharif Park; Maymar Ext; Maymar Mor; Ahsanabad; Jamali Pull; Al-Asif; Sorab Goth; Ayesha Manzil; Lalukhait; Teen Hatti; Jahangir Road; Guru Mandar; Numaish; Taj Complex; Sindh High Court |

### EV bus routes

| Code | Published termini | Published via sequence |
|---|---|---|
| EV-01 | CMH Malir Cantt → Dolmen Mall | CMH; Cantt Bazar; Checkpost 02; Tank Chowk; Model Colony; Malir Halt; Colony Gate; Nata Khan; PAF Base Faisal; Karsaz; Nursery; FTC; Kala Pull; Gold Mart; Akhtar Colony; Khayaban-e-Ittehad; Clock Tower |
| EV-02 | Bahria Town → Malir Halt | Usmania; Domba Goth; Karachi Toll Plaza; Checkpost 05; Checkpost 06; Tank Chowk; Model Colony |
| EV-03 | Quaid-e-Azam Square Malir Cantt → Numaish | X-20; Phase 2; Askari 5; Allahwala Chowk; Checkpost 05; Safoora; Mosamiyat; Kamran Chowrangi; Johar; Millennium Mall; Bahria University; Aga Khan Hospital; Liaquat National Hospital; New Town; Islamia College |
| EV-04 | Bahria Town → Ayesha Manzil | M9; Usmania; Domba Goth; Karachi Toll Plaza; Malir Link Road; Old Sabzi Mandi; Maymar Mor; Al-Asif Square; Sorab Goth |
| EV-05 | DHA City → Sorab Goth | M9; Kathore; Usmania; Domba Goth; Karachi Toll Plaza; Malir Link Road; Old Sabzi Mandi; Maymar Mor; Al-Asif Square |

## Route identity conflicts — must not be auto-resolved

| Code | Conflict | Handling |
|---|---|---|
| R2 | Route index says Powerhouse–Indus Hospital; detailed route says North Karachi–Korangi Crossing, with Indus Hospital as an intermediate point | Keep both variants and request operator clarification |
| R3 | Route index says Powerhouse–Nasir Jump; detailed route says North Karachi–Nasir Jump | Keep both variants |
| R4 | Route index says Powerhouse–Keamari; detailed route says North Karachi–Kemari | Keep both variants |
| R8 | Index direction says Tower–Yousuf Goth; detailed route is written Yousuf Goth–Tower | Treat as reverse presentation of same corridor only if operator confirms |
| R11 | Index says Miran Naka–Shireen Jinnah Colony; detailed route says Mera Naka–Ziauddin Hospital. The 2025 map PDF labels R11 Miran Nakka/Lyari/PIDC and Shireen Jinnah Colony | **Unresolved major route identity conflict**; do not join the detailed stop list to the index route without confirmation |
| R12 | Index says Naddi Kinara–Lucky Star; detailed route says Memon Goth–Sadar Lucky Star | May be an updated/variant route; retain both |
| R13 | Published via text places Gulbai before Hawksbay and repeats Gulbai later | Preserve source text; sequence needs operator/source-map review |
| R1 | Via text repeats Malir Halt and includes Kokharpar 04 after the listed Khokharapar 04 origin | Preserve repeated entries; do not deduplicate without route trace |

The 2025 PDF is a map image/reference and does not resolve every discrepancy in the 2026 route-directory text. It labels R11 as Miran Nakka/Lyari/PIDC and separately names Shireen Jinnah Colony, which supports retaining the conflict.

## Green Line station sequence — provisional secondary-source transcription

The current SMTA-hosted route map identifies the Green Line corridor but its accessible route-directory text does not provide a full station-by-station ordered list. Two current secondary transport guides publish the following 22-stop sequence from Abdullah Chowk (Surjani) to Numaish:

1. Abdullah Chowk
2. KDA Flats
3. Karimi Chowrangi
4. 4K Chowrangi
5. 2 Minute Chowrangi
6. Road 2400 (Aisha Complex)
7. Power House Chowrangi
8. Road 4200 (Saleem Centre)
9. U.P. More
10. Nagan Chowrangi
11. Erum Shopping
12. Jummah Bazar
13. Five Star Chowrangi
14. Hyderi
15. Board Office
16. Annu Bhai Park
17. Enquiry Office
18. Nazimabad No. 1
19. Sanitary Market (Gulbahar)
20. Lasbela Chowk
21. Patel Para (Guru Mandir)
22. Numaish

Sources: https://busupdate.com/pakistan/karachi/bus-routes/route-green-line/ and https://explorepakistan.live/destinations/guides/karachi-green-line-brt. **Status: provisional; secondary sources agree broadly but primary operator station order and current operating status still require confirmation.** The SMTA-hosted Jan 2025 map labels a subset of these stations, including Abdullah Chowk, KDA/Surjani, Karimi, 4K, 2 Mint, Aisha Complex, Power House, Erum Shopping, Sakhi Hassan, Hyderi, KDA Chowrangi/Board Office, Annu Bhai Park, Model Park, Nazimabad No. 1, Lasbela and Guru Mandir.

## Orange Line alignment — official corridor, station sequence not fully evidenced

SMTA's project page describes the Abdul Sattar Edhi Orange Line from TMA Office, Orangi Town to Jinnah University for Women near Matriculation Board Office, with four BRT stations and one depot. The project alignment is approximately 3.88 km. A Sindh government procurement alignment document identifies the corridor via Banaras, KDA Chowrangi and Abdullah College toward Jinnah University/Board Office.

Sources:
- https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line
- https://pprasindh.gov.pk/correction/22701TranspDept100215BD.pdf
- https://pas.gov.pk/business/questios-details/33/1989

**Status:** corridor endpoints and principal alignment landmarks corroborated; exact four station names and stop order are not yet fully verified from an operator station schedule. Do not turn the five named landmarks into a five-station list.

## Phase 5C crosswalk rules

For each of the 102 currently unmatched source-stop rows:

- If the name occurs in the relevant current SMTA route description, record `published_name_confirmed` only. This resolves the route-name evidence gap, **not the coordinate gap**.
- If a spelling or alias differs, record the published spelling and `alias_candidate`; require review before accepting.
- If the source route text itself conflicts, record `route_identity_conflict` and do not infer the route.
- Leave latitude/longitude empty until an authoritative point or field-verified boarding location is available.
- Never copy coordinates from a broad neighbourhood centroid, a different route's similarly named stop, or a collision group merely because the names look similar.

## Acceptance gate before routing

1. Confirm route identity, direction and stop order with operator/current route map.
2. Confirm every physical boarding location, including road side/platform.
3. Obtain a reliable point source or field survey for every stop.
4. Resolve shared-stop reuse and coordinate collisions.
5. Only then perform road-network snapping and route-shape generation.

No database changes, coordinate edits, route activation, geocoding, or routing API calls were made in Phase 5C.
