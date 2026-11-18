# Karachi transport consolidated research register — Phase 5

**Prepared:** 17 November 2026  
**Repository:** `crystal-qazi/karachi-busses`  
**Branch:** `research/karachi-route-register-2026`  
**Status:** Research register / candidate data only. Not approved for database import or public publication.

## Executive findings

- The SMTA route directory currently publishes individual Karachi route pages for R1–R4, R8, R11–R14 and EV-01–EV-05, with active status and stop/area sequences. These are authoritative **published source statements**, not proof of current bus operation at each stop.
- The Think Transportation KHI-MAP-08 map index (01 Jan 2025) conflicts with several detailed SMTA route pages. SMTA explicitly says its map index is third-party data and disclaims authentication. Prefer the individual SMTA route pages for textual stop sequences, while preserving map-index differences as unresolved source observations.
- R11 remains a major terminal/corridor conflict; R12 remains a terminal/extension conflict. R2–R4 also have map-index vs detail-page start/terminal differences.
- EV-01–EV-05 now have SMTA-published stop/area sequences and distances. The 76-route Habib coordinate dataset only has plausible corridor candidates for EV-01–EV-03; EV-04/05 are absent as distinct labels.
- The Green Line coordinate-dataset chain is not accepted as current station truth. Its 22-node chain terminates at Karachi City Station and includes Aga Khan Hospital/Aurangzeb Market, unlike the commonly published 22-station Surjani–Numaish operational sequence.
- Orange Line official material provides four station names (OL-1–OL-4), but the project page and agreement contain different descriptions of corridor extension/connection. The local coordinate file has only three edges and four nodes; it does not yet establish a complete, verified current route.
- The exact-name crosswalk was generated for 191 source-described bus-route stop rows against 572 coordinate nodes: **89 exact normalized name candidates** and **102 unmatched rows**. Exact matches are only candidate name matches, not verified physical stops. No fuzzy matches were silently accepted. The companion `PHASE_5_NODE_AUDIT.csv` inventories all 572 node IDs, coordinates, historical route-label membership and coordinate-collision flags.
- Road-following GeoJSON was **not fabricated**. The source CSV edges are named-node links, not authoritative road-centreline geometry. Stops need coordinate/boarding-side review before routing/snapping and route-shape production.

## Evidence hierarchy and source register

| Source | Use | Limit |
|---|---|---|
| [SMTA Karachi route map and route directory](https://smta.gos.pk/route-map) | Primary published route index and detailed directory | SMTA says the map index is courtesy of Think Transportation and is not authenticated by SMTA |
| Individual SMTA route pages linked below | Published route identity, status, distance and ordered via list | No GPS stop coordinates, service timetable, reverse direction, or road geometry |
| [Think Transportation KHI-MAP-08, 01 Jan 2025](https://thinktransportation.net/Karachi_transport_map_peoples_bus_service_green_line_orange_line_think_transportation.pdf) | Secondary map-index endpoint cross-check | Its own disclaimer says it does not authenticate services/data |
| [Habib University Karachi Bus Network dataset, DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512) | Historical/coordinate candidate network | Not equivalent to current SMTA service; retain CC BY 4.0 attribution |
| [JICA Karachi Transportation Improvement Project, 2012](https://openjicareport.jica.go.jp/pdf/12086393_01.pdf) | Historic Green Line station planning and corridor context | Proposed design from 2012, not a current as-built station register |
| [SMTA Orange Line project page](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line) | Orange Line project scope and operational commencement claims | Project page refers to TMA–Jinnah University/KDA Roundabout corridor; verify current operational stopping pattern |
| [Orange Line Facility Management Agreement, Exhibit 1](https://pidcl.com.pk/wp-content/uploads/2021/02/Orange-Line-Project-Facility-Management-Agreement_compressed.pdf) | Official contract exhibit listing OL-1 to OL-4 | Contract alignment evidence, not proof of every current service stop |

## Route-by-route register

### R1 — Khokharapar 04 to Dockyard (31 km)

**SMTA detailed page:** [Route 01](https://smta.gos.pk/routes/1) — Pink Bus, Active.  
**Published sequence:** Khokharapar 04 → Suadabad → Model Colony → Malir Halt → Colony Gate → Nata Khan → PAF Base Faisal → Karsaz → Nursery → FTC → Regent Plaza → Metropole Hotel → Press Club → I.I. Chundrigar Road → Tower → ICI Flyover → Dockyard.

**Conflict resolution:** Map index says Khokhrapar–Dockyard; detailed page says Khokharapar 04–Dockyard. This is likely a spelling/terminal-label variation, not evidence of a different corridor. Retain the official detail-page spelling; field-confirm the precise terminal boarding point. The coordinate dataset's `pink_bus` label is a mixed multi-corridor graph and must not be treated as R1.

### R2 — North Karachi to Korangi Crossing (31 km)

**SMTA detailed page:** [Route 02](https://smta.gos.pk/routes/2) — Pink Bus, Active.  
**Published sequence:** North Karachi → Nagan → Shafiq Mor → Sorab Goth → Gulshan → Nipa → Johar → COD → Nata Khan → Colony Gate → Shah Faisal Colony → Singer Chowrangi → Korangi #05 → Nasir Jump → Indus Hospital → Korangi Crossing.

**Conflict resolution:** Map index says Powerhouse–Indus Hospital. Detailed route page says North Karachi–Korangi Crossing and lists Indus Hospital as an intermediate stop. Use the detailed page as the working published sequence; do not silently erase the map-index statement. Confirm whether the index is stale or represents a truncated map label.

### R3 — North Karachi to Nasir Jump (32 km)

**SMTA detailed page:** [Route 03](https://smta.gos.pk/routes/3) — Pink Bus, Active.  
**Published sequence:** North Karachi → Nagan → Five Star Chowrangi → Board Office → Nazimabad Petrol Pump → Essa Nagri → National Stadium → Karsaz → Nursery → FTC → Kala Pull → Akhtar Colony → Shan Chowrangi → Nasir Jump.

**Conflict resolution:** Map index says Powerhouse–Nasir Jump; detailed page says North Karachi–Nasir Jump. The coordinate dataset's `Route-3` begins Power House and ends Shan Chowrangi; it is a non-equivalent historical/candidate chain, not a match to this published R3 sequence.

### R4 — North Karachi to Kemari (26 km)

**SMTA detailed page:** [Route 04](https://smta.gos.pk/routes/4) — People's Bus Service, Active.  
**Published sequence:** North Karachi → Nagan → Shafiq Mor → Sorab Goth → Ayesha Manzil → Lalukhait → Teen Hatti → Jahangir Road → Guru Mandar → Numaish → Taj Complex → Sindh High Court → Tower → Jackson Market → Kemari.

**Conflict resolution:** Map index says Powerhouse–Keamari; detailed page says North Karachi–Kemari. Prefer the detailed route page as the working source statement. Coordinate dataset `Route-4` starts Power House and terminates Tower, so it is incomplete/mismatched for current R4.

### R8 — Yousuf Goth to Tower (17 km)

**SMTA detailed page:** [Route 08](https://smta.gos.pk/routes/8) — People's Bus Service, Active.  
**Published sequence:** Yousuf Goth → Saeedabad → Baldia → Ittehad Town → Naval Colony → Moach Goth → Sher Shah → Gulbai → Agra Taj → Dua Restaurant → ICI → Tower.

**Conflict resolution:** Map index presents Tower–Yousuf Goth; detailed page presents Yousuf Goth–Tower. Treat this as reversed display orientation of the same corridor. The return-direction ordered stop list still needs operator confirmation; do not assume every segment is traversed in exact reverse order.

### R11 — Mera Naka to Ziauddin Hospital (21 km)

**SMTA detailed page:** [Route 11](https://smta.gos.pk/routes/11) — People's Bus Service, Active.  
**Published sequence:** Mera Naka → Agra Taj Colony → KPT → Bahria Complex → PIDC → Punjabi Chowrangi → Gizri → Khayaban-e-Shamsheer → Abdullah Shah Ghazi Mazar → Bilawal Chowrangi → Ziauddin Hospital.

**Unresolved major conflict:** Think Transportation map index says Miran Naka–Shireen Jinnah Colony. These are materially different endpoints/corridors. Use the SMTA detailed page only as the current published textual candidate; request operator confirmation before matching coordinates or publishing. Coordinate dataset `Route-11` runs Bilawal Chowrangi–Lyari and does not match either published description.

### R12 — Memon Goth to Sadar Lucky Star (36 km)

**SMTA detailed page:** [Route 12](https://smta.gos.pk/routes/12) — People's Bus Service, Active.  
**Published sequence:** Memon Goth → Khokharapar RCD Ground → Kala Board → Malir 15 → Qaidabad → Dawood Chowrangi → 89 Chowrangi → Landhi → Korangi → Korangi Crossing → Qayyumabad → Kala Pull → FTC → Sadar Lucky Star.

**Unresolved terminal/extension conflict:** Map index says Naddi Kinara–Lucky Star. Detail page says Memon Goth–Sadar Lucky Star. Coordinate dataset `Route-12` begins Naddi Kinara and ends Lucky Star Saddar, with 24 links. It may represent an alternate/extended/historical alignment, but the sequence is not interchangeable with the SMTA detail-page sequence. Keep both source statements and request operator confirmation of origin/branch.

### R13 — Hawksbay to Tower (19 km)

**SMTA detailed page:** [Route 13](https://smta.gos.pk/routes/13) — People's Bus Service, Active.  
**Numbered published sequence:** Hawksbay → Maripur → Pakistan Marine Academy → Maripur Truck Adda → Gulbai → Agra Taj → Dua Restaurant → ICI → Tower.

**Sequence note:** The prose says “via Gulbai” before naming Hawksbay, then the numbered stops place Gulbai after Maripur Truck Adda. Treat the numbered list as the working forward order, but confirm whether the prose's first Gulbai is a loop/approach or editorial ordering error.

### R14 — Maymar to Tower (29 km)

**SMTA detailed page:** [Route 14](https://smta.gos.pk/routes/14) — People's Bus Service, Active.  
**Published sequence:** Maymar → Nawaz Sharif Park → Maymar Ext → Maymar Mor → Ahsanabad → Jamali Pull → Al-Asif → Sorab Goth → Ayesha Manzil → Lalukhait → Teen Hatti → Jahangir Road → Guru Mandar → Numaish → Taj Complex → Sindh High Court → Tower.

**Directory note:** Route 14 is included in SMTA's detailed Karachi directory (20 Karachi entries) but absent from the Think Transportation map index route list. Keep as an SMTA-published route; map coverage gap does not invalidate the directory record.

### EV-01 — CMH Malir Cantt to Dolmen Mall (41 km)

**SMTA page:** [EV-01](https://smta.gos.pk/routes/15), Active.  
**Published sequence:** CMH Malir Cantt → Cantt Bazar → Checkpost 02 → Tank Chowk → Model Colony → Malir Halt → Colony Gate → Nata Khan → PAF Base Faisal → Karsaz → Nursery → FTC → Kala Pull → Gold Mart → Akhtar Colony → Khayaban-e-Ittehad → Clock Tower → Dolmen Mall.

**Dataset comparison:** `EV-1` has 17 links and the same broad endpoints, but uses alternate waypoints such as Jinnah Avenue, Airport, Drigh Road, Korangi Road, DHA Phase 1 and Masjid-e-Ayesha. Candidate corridor only; do not overwrite SMTA stop names with dataset nodes.

### EV-02 — Bahria Town to Malir Halt (44 km)

**SMTA page:** [EV-02](https://smta.gos.pk/routes/16), Active.  
**Published sequence:** Bahria Town → Usmania → Domba Goth → Karachi Toll Plaza → Checkpost 05 → Checkpost 06 → Tank Chowk → Model Colony → Malir Halt.

**Dataset comparison:** `EV-2` has 9 links and same broad endpoints, but includes Baqai University and Malir Cantt gates, and omits some SMTA-listed areas. Candidate only.

### EV-03 — Quaid-e-Azam Square Malir Cantt to Numaish (23 km)

**SMTA page:** [EV-03](https://smta.gos.pk/routes/17), Active.  
**Published sequence:** Quaid-e-Azam Square Malir Cantt → X-20 → Phase 2 → Askari 5 → Allahwala Chowk → Checkpost 05 → Safoora → Mosamiyat → Kamran Chowrangi → Johar → Millennium Mall → Bahria University → Aga Khan Hospital → Liaquat National Hospital → New Town → Islamia College → Numaish.

**Dataset comparison:** `EV-3` has 18 links and same broad corridor/terminal, but differs in several intermediate stops (Malir Cantt Gate 5, Rim Jhim Tower, Safoora Chowrangi, Jauhar Chowrangi, Dalmia Road, National Stadium, PIB Colony). Candidate only.

### EV-04 — Bahria Town to Ayesha Manzil (58 km)

**SMTA page:** [EV-04](https://smta.gos.pk/routes/18), Active.  
**Published sequence:** Bahria Town → M9 → Usmania → Domba Goth → Karachi Toll Plaza → Malir Link Road → Old Sabzi Mandi → Maymar Mor → Al-Asif Square → Sorab Goth → Ayesha Manzil.

**Dataset comparison:** No dedicated EV-04 route label was found in the 76 route labels. Some individual place nodes exist, but no route chain is proven.

### EV-05 — DHA City to Sorab Goth (48 km)

**SMTA page:** [EV-05](https://smta.gos.pk/routes/19), Active.  
**Published sequence:** DHA City → M9 → Kathore → Usmania → Domba Goth → Karachi Toll Plaza → Malir Link Road → Old Sabzi Mandi → Maymar Mor → Al-Asif Square → Sorab Goth.

**Dataset comparison:** No dedicated EV-05 route label was found. A few shared area nodes are present; no chain is proven.

## BRT station sequence register

### Green Line — provisional operational sequence (22 stations)

The commonly published current passenger-facing list runs Surjani/Abdullah Chowk to Numaish. The list below is a **secondary-source corroborated candidate**, not yet confirmed against a current operator station dataset or as-built station GIS. The 2012 JICA design register contains a different 23-station proposal, including KESC Power House, KDA Chowrangi Surjani, Road 2400/Road 4200 and Municipal Park. Do not merge the historic design and current passenger-facing list.

1. Abdullah Chowk (Surjani Town terminal)
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

**Direction:** Reverse the passenger-facing sequence only as a provisional display order. Confirm actual station platforms, branch/extension status, and official stop IDs with SIDCL/TransKarachi before publication.

**Dataset comparison:** `GreenLine_Bus` has 21 edges / 22 named nodes, but its chain is Surjani Town → 4-K Chowrangi → North Karachi → UP Mor → Nagan → Sakhi Hasan → Shahrah-e-Jehangir → Hyderi → Shahrah-e-Humayun → Orange Line → North Nazimabad → Eid Gah Bagh → Urdu Bazaar → Gul Bahar → Lasbela → Gurumandir → Numaish → Aga Khan Hospital → Aurangzeb Market → Merewether Tower → Karachi City Station. This is not the same sequence as the current 22-station candidate and includes a southern extension/extra corridor not substantiated by the current station list. Keep it separate as historical/unverified candidate geometry.

### Orange Line — official contract station names (4 stations)

The SMTA project page identifies the line as Abdul Sattar Edhi BRT, from TMA Orangi toward Jinnah University/KDA Roundabout and states four BRT stations. The 2021 Facility Management Agreement Exhibit 1 names:

1. OL-1 — 5 No. Chowrangi
2. OL-2 — Orangi Town Police Station
3. OL-3 — Abdullah College
4. OL-4 — Dilpasand Sweets

The agreement describes a TMA Orangi–Board Office operating service with Orange Line buses continuing in mixed traffic between Board Office and Hydri before joining the Green Line busway and turning at Nagan. The SMTA project page also describes the project extension toward Jinnah University/KDA Roundabout. This is an important scope/operation distinction: the four named stations are contract-exhibit station identities, not a complete list of every mixed-traffic connection or every point shown on the map.

**Dataset comparison:** `Orange_Line` contains only three links/four nodes: Town Municipal Administration Office → Pone Panch Chowrangi → Abdullah Chowrangi → Jinnah University. These node names do not match the OL-1–OL-4 contract station names. Do not label this chain as the final Orange Line station sequence.

## 572-node coordinate crosswalk

The generated companion CSV `PHASE_5_STOP_NODE_CROSSWALK.csv` has one row per SMTA-published stop/area for R1–R4, R8, R11–R14 and EV-01–EV-05. The companion `PHASE_5_NODE_AUDIT.csv` has all 572 source nodes with coordinates, historical route-label membership and collision flags.

Matching policy:
- Only exact normalized name equality was used (case and punctuation normalization only).
- An exact match is labelled `candidate_name_match`, not verified.
- Unmatched source names remain blank; no guessed geocoding or fuzzy alias assignment.
- A name match does not prove that the point is the correct stop, route direction, platform, road side, or current boarding location.
- A single source stop may have several physical candidate locations; a node can be reused across routes only after a shared boarding point is confirmed.

The existing cleaned coordinate files contain 572 nodes and 1,415 directed edges across 76 historical route labels. Earlier read-only QA found 10 coordinate-collision groups (24 named nodes), one self-loop, and 7 route graphs that are not simple directed paths. These topology/collision flags remain open and must be resolved before producing routable route shapes.

## Directions and road-following GeoJSON

No reverse direction or road-following LineString has been fabricated in this register.

Required next steps for each route:
1. Obtain operator-approved forward and reverse ordered stop IDs.
2. Verify each physical boarding point, including side of road/platform and coordinate precision.
3. Match source stop IDs to reviewed coordinate records; split same-name opposite-side stops.
4. Obtain an authoritative road-centreline or routing network with an acceptable licence.
5. Snap ordered stops to the correct carriageway/road path, inspect one-way streets, U-turns, flyovers, access restrictions and route variants.
6. Produce one GeoJSON LineString/MultiLineString per direction with coordinates in **[longitude, latitude]** order.
7. Compare calculated road length to SMTA published distance; explain deviations rather than forcing a match.
8. Keep every shape in draft/review status until operator or field validation.

The 1,415 edge CSV is a historical graph of links between named places. A straight line between node coordinates is not a bus-road route shape and must not be exposed as one.

## Consolidated verification decision

| Group | Source evidence | Candidate dataset match | Decision |
|---|---|---|---|
| R1 | SMTA detail page | Mixed `pink_bus` graph | Published sequence recorded; coordinate match unresolved |
| R2 | SMTA detail page conflicts with map index | No exact chain | Use detail-page text provisionally; endpoint conflict retained |
| R3 | SMTA detail page conflicts with map index | `Route-3` mismatch | Do not match/publish from historical chain |
| R4 | SMTA detail page conflicts with map index | `Route-4` mismatch | Do not match/publish from historical chain |
| R8 | SMTA detail page + reversed map index | No exact route label | Direction display conflict resolved; return path still unverified |
| R11 | SMTA detail page vs map index major conflict | `Route-11` mismatch | Unresolved; operator confirmation required |
| R12 | SMTA detail page vs map index + candidate Route-12 | Partial/variant candidate | Unresolved origin/extension |
| R13 | SMTA page internal sequence wording issue | No exact chain | Numbered sequence recorded; confirm Gulbai ordering |
| R14 | SMTA detail page; absent from map index | No dedicated route label | Source-described route recorded; coordinate match unresolved |
| EV-01 | SMTA detail page | `EV-1` broad corridor only | Candidate only |
| EV-02 | SMTA detail page | `EV-2` broad corridor only | Candidate only |
| EV-03 | SMTA detail page | `EV-3` broad corridor only | Candidate only |
| EV-04 | SMTA detail page | No dedicated chain | Missing route geometry |
| EV-05 | SMTA detail page | No dedicated chain | Missing route geometry |
| Green Line | Secondary 22-stop passenger list + old JICA design | Existing 22-node chain differs | Provisional station sequence; operator confirmation needed |
| Orange Line | SMTA project page + 2021 agreement | Existing 4-node chain differs | Four contract station names recorded; operational stop order needs operator confirmation |

## Publication gate

**Nothing in this research register is approved for public API exposure.** SMTA source status is recorded as active on its pages, but the local project's own provenance rules require route source verification, at least two active verified-source stops per direction, and a saved road-following route shape for every direction. All source records and candidate stops must remain under review until the project reviewer completes those checks.

## Source URLs

- [SMTA route map / directory](https://smta.gos.pk/route-map)
- [R1](https://smta.gos.pk/routes/1) · [R2](https://smta.gos.pk/routes/2) · [R3](https://smta.gos.pk/routes/3) · [R4](https://smta.gos.pk/routes/4)
- [R8](https://smta.gos.pk/routes/8) · [R11](https://smta.gos.pk/routes/11) · [R12](https://smta.gos.pk/routes/12) · [R13](https://smta.gos.pk/routes/13) · [R14](https://smta.gos.pk/routes/14)
- [EV-01](https://smta.gos.pk/routes/15) · [EV-02](https://smta.gos.pk/routes/16) · [EV-03](https://smta.gos.pk/routes/17) · [EV-04](https://smta.gos.pk/routes/18) · [EV-05](https://smta.gos.pk/routes/19)
- [SMTA Orange Line project](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line)
- [Orange Line Facility Management Agreement](https://pidcl.com.pk/wp-content/uploads/2021/02/Orange-Line-Project-Facility-Management-Agreement_compressed.pdf)
- [JICA Karachi Transportation Improvement Project, 2012](https://openjicareport.jica.go.jp/pdf/12086393_01.pdf)
- [Passenger-facing Green Line station list (secondary)](https://busupdate.com/pakistan/karachi/bus-routes/route-green-line/)
- [Habib University coordinate dataset](https://zenodo.org/records/13951512)


## BRT source reconciliation update — Phase 5AV / 5AW (18 November 2026)

### Green Line
- Government/PIDCL project evidence: 25 stations reported; 2016 presentation names 29 corridor points. The 2021 employer response confirms the count but not the station IDs.
- Two passenger-facing 2026 lists claim 22 stations but differ materially. Neither is an operator-issued station register; do not merge or adopt either as verified.
- Think Transportation KHI-MAP-08 (01-Jan-2025), hosted on the SMTA route-map page, visually depicts the Green Line corridor and labels multiple locations. Treat these as schematic map annotations, not verified current passenger platforms, station IDs, stop coordinates or road-following geometry.
- Municipal Park remains an extension endpoint reported for FY 2026–27, not a verified current operating passenger stop.

### Orange Line
- Provincial Assembly answer (19-May-2026) reports the 4 km service operating from TMA Office Orangi Town to Jinnah University for Women near Matriculation Board Office.
- Sindh Transport Department project page reports 3.88 km and five bus stations; SMTA project page reports four BRT stations plus one depot; 2021 Facility Management Agreement lists four contract station IDs (OL-1 to OL-4). These are different published scope claims and are not reconciled by assumption.
- KHI-MAP-08 provides a dated schematic depiction but no current operator station-ID register or unambiguous physical platform sequence.
- Retain OL-1 to OL-4 as contractual identities only. Do not invent a fifth station or infer which station is missing from the contract list.

### Publication gate
No Green or Orange BRT station coordinate, passenger stop status, route shape, or database record is approved by these phases. The project still requires a current SIDCL/SMTA operator station register or official operational drawing before BRT stop publication.

Sources: [Provincial Assembly answer](https://pas.gov.pk/business/questios-details/33/2019); [Sindh Transport Department Orange Line](https://transport.sindh.gov.pk/orange-line); [SMTA Orange Line](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line); [Think Transportation KHI-MAP-08](https://smta.gos.pk/downloads/karachi-bus-route-map.pdf); [PIDCL Green Line 2016 presentation](https://pidcl.com.pk/wp-content/uploads/2016/08/Updated-Progress-Presentation-Green-Line-16-8-16.pdf); [SIDCL/PIDCL 2021 response](https://pidcl.com.pk/wp-content/uploads/2021/03/2021-03-19-Response-Document-Final-Version-.pdf).
