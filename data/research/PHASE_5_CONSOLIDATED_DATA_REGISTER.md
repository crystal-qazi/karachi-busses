# Karachi transport consolidated research register — Phase 5

**Prepared:** 17 November 2026  
**Repository:** `crystal-qazi/karachi-busses`  
**Branch:** `research/karachi-route-register-2026`  
**Status:** Research register / candidate data only. Not approved for database import or public publication.

## Executive findings

> **Source-decision update — 18 November 2026 (Phases 5AN and 5AO):** The project owner has accepted Think Transportation's route page and supplied KML as the authentic reference for People's Bus Service R-series and EV-series route identity, published route descriptions and route geometry where present. This supersedes the earlier hierarchy below wherever it says SMTA individual route pages are the preferred/primary R/EV sequence source or Think Transportation is merely secondary. SMTA's route index and detail pages remain preserved as separate government-published comparison evidence; they do not override the adopted Think Transportation R/EV descriptions. See [Phase 5AN R-series reconciliation](../../docs/research/PHASE_5AN_THINK_TRANSPORTATION_R_SERIES_RECONCILIATION.md), [Phase 5AO EV-series reconciliation](../../docs/research/PHASE_5AO_THINK_TRANSPORTATION_EV_ROUTE_RECONCILIATION.md), and the supplied KML audit. This update does not certify live dispatch, physical boarding locations, stop coordinates or return-direction paths, and it does not change MySQL verification statuses.


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


## Historical dataset provenance update — Phase 5AX (18 November 2026)

The original historical Karachi Bus Network dataset is published as [Zenodo DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512), Version v1, 18 October 2024, by Data Research Lab Pakistan. Creators: Muhammad Qasim Pasta (curator), Moid Raza Khan and Fatima Aslam (collectors), Habib University. The record describes a compilation of 76 public bus routes (BRT and minibuses) from Travel Culture and HamariWeb, with stop coordinates extracted from Google Maps. The published node CSV contains 572 node rows; the route network includes edge records.

This confirms publication, creators, date, publisher and broad coordinate collection method. It does not provide per-stop Google Maps pins, capture dates, operator GPS or current service validation. The dataset remains historical secondary research only. Phase 5AZ resolved the licence evidence: the publisher's companion project page explicitly declares CC BY 4.0, while the Zenodo record's visible Rights section shows no displayed value. Preserve both facts separately; do not claim a populated machine-readable licence field in Zenodo. Preserve the existing source row's identity, add the DOI/source notes through the importer only when the user runs it, and keep its status pending. All imported stops/routes remain under_review.


## DOI and licence reconciliation — Phase 5AZ (18 November 2026)

The canonical historical Karachi Bus Network dataset is [Zenodo DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512), Version v1, a 2024 dataset by Data Research Lab Pakistan with the expected node/edge CSVs, 572 node rows and a description of 76 Karachi public bus routes. The conflicting DOI cited in issue #13, [10.5281/zenodo.13932672](https://zenodo.org/records/13932672), is an unrelated software record named *xIndices*, Version 1.2.1, by Jivesh Dixit. It is not a second version or alternate record for the bus dataset. The [publisher's companion project page](https://darlab-pakistan.github.io/karachi-bus-network/) explicitly declares the Karachi Bus Network dataset as CC BY 4.0. The Zenodo dataset page's visible Rights section currently shows a License heading but no displayed value. Record the publisher declaration and the Zenodo metadata gap separately; do not claim a populated machine-readable license value in the Zenodo record. The dataset remains historical secondary research only; no route/stop verification or database status changes follow from this provenance correction.

## Current BRT status and operator evidence request — Phase 5BA (18 November 2026)

Government of Sindh and PIDCL sources support Green Line operation and completed operationalisation work, but do not supply a current ordered station-ID register. The Provincial Assembly answer of 19-May-2026 reports Orange Line operation from TMA Office Orangi Town to Jinnah University for Women; the 29-Jan-2026 answer gives the same endpoints but a different passenger count. The current SMTA overview labels Orange Line as planned, preserving a website/status inconsistency. Published Orange Line records still differ on four versus five stations and contractual station IDs versus passenger stops. No new BRT stop or route shape is approved. A ready-to-send SMTA evidence request is documented in [Phase 5BA](../../docs/research/PHASE_5BA_CURRENT_BRT_STATUS_AND_OPERATOR_EVIDENCE_REQUEST.md).

## PakBus secondary route cross-check — Phase 5BB (18 November 2026)

PakBus catalogue snapshot dated 13-Nov-2026 reports 20 Karachi routes and 319 stops; the wider catalogue reports 231 routes and 8,684 stops across 46 cities. It exposes direction-specific sequences and candidate coordinates, but PakBus is an independent service and its About page does not identify the Karachi-specific source records or coordinate method. The download terms permit non-commercial use only without prior permission; commercial use requires permission. PakBus is therefore secondary evidence only.

The PakBus Green Line page lists 22 stops, matching one secondary passenger-facing list but not the competing CMTA list. Its 22 candidate coordinates were compared to the 572 historical nodes: 2 are under 50 m from a historical node, 3 are under 100 m, 12 are under 250 m, 3 are 250–under 500 m, and 7 are at least 500 m away. Nearest-node proximity is not proof of physical stop identity. The source candidate CSV, generated nearest-node crosswalk and standard-library audit script are stored under Phase 5BB. The Orange Line page says five stops toward Board Office but publishes fifteen entries in the reverse direction, including a loop-like detour; this is unresolved. Endpoint conflicts remain for R2 (Korangi Crossing vs Indus Hospital), R4 (Jackson Market vs Keamari), R10 (Quaid-e-Azam Mazar vs Numaish), R12 (Khokhrapar Chaman Colony vs Naddi Kinara) and EV-03 (Malir Cantt vs Malir Cantt Check Post 5). Direction-only differences for R8, R11 and R13 are retained without changing KML order. See [Phase 5BB](../../docs/research/PHASE_5BB_PAKBUS_SECONDARY_ROUTE_CROSSCHECK.md), [route crosswalk CSV](PHASE_5BB_PAKBUS_KARACHI_ROUTE_CROSSWALK.csv), [Green Line candidate CSV](PHASE_5BB_PAKBUS_GREENLINE_STOP_CANDIDATES.csv) and [Green Line nearest-node crosswalk](PHASE_5BB_PAKBUS_GREENLINE_TO_572_NODE_CANDIDATE_CROSSWALK.csv).

No PakBus stop coordinate was imported or promoted to verified status. All 572 historical stops remain under_review; data sources remain pending; route_shapes remain empty.

## Think Transportation KML permission gate — Phase 5BC (18 November 2026)

The Think Transportation KHI-MAP-08 map/KML is accepted as the primary R/EV route-line reference for research, but its published notice says use without permission is prohibited. SMTA's permission to publish its own route map does not grant this independent application a redistribution licence. Written permission is still required for private storage, public map display, KML-to-GeoJSON conversion, derived geometry, public API/download redistribution, repository hosting, attribution and commercial use. A ready-to-send permission request is documented in [Phase 5BC](../../docs/research/PHASE_5BC_THINK_TRANSPORTATION_KML_PERMISSION_REQUEST.md). The request has not been sent; no permission is implied. Keep route_shapes empty and do not publish Think geometry until the response explicitly permits the intended use.



## Owner sequence review and adopted source policy — Phase 5BD (18 November 2026)

This section supersedes any earlier statement in this register that assigns SMTA individual route pages as the primary R/EV sequence source or treats Think Transportation as merely secondary. The project owner has adopted Think Transportation's published R/EV route descriptions as the primary reference for route identity and displayed forward stop sequence, and the supplied KML as the primary route-line reference for research inventory only. SMTA route pages remain important government-published comparison evidence and must be retained where they conflict; neither source proves physical boarding-pole locations, current dispatch, return-direction order or GPS coordinates.

### Owner-reviewed forward sequences

The owner route review is recorded separately in [USER_ROUTE_VERIFICATION_REGISTER.md](../../docs/research/USER_ROUTE_VERIFICATION_REGISTER.md). As of 18 November 2026:
- R1, R2, R4, R8, R9 and R11: displayed forward sequence and order owner-confirmed.
- R3: owner-confirmed with Shan Chowrangi inserted immediately after Brookes Chowrangi.
- R10: owner-confirmed with the combined source entry split into Do Talwar, Pak Tower and Abdullah Shah Ghazi in that order.
- R12: next route awaiting owner review; do not mark it owner-confirmed.
- These are owner-review decisions, not independent operator or field verification. No MySQL verification status, route activation, route shape, or public API eligibility changes follow from this review.

### Geometry, geography and rights

- OSM remains the primary geographic and road-network reference for the application.
- Think Transportation KML remains the primary R/EV route-line research reference where a route is present, but its use restriction remains a hard publication gate. The permission request documented in Phase 5BC has not been sent/approved; do not redistribute the KML, convert it to public GeoJSON, host it for public download, or populate publishable route_shapes from it until written permission covers the exact intended uses.
- SMTA's publication of its map does not grant this application rights to redistribute Think Transportation's independently supplied KML.
- Historical 572-node coordinates, PakBus candidates and SMTA textual stop lists remain evidence/candidates only. Do not infer a physical stop from name similarity, proximity, or a straight-line graph edge.
- Keep route_shapes empty and all candidate stops/sources under review until the project's existing verification and rights gates are satisfied.

### Next work

1. Obtain current operator evidence for unresolved R-series identity/terminal variants and both Green/Orange BRT station sequences. Owner review of a published list does not close operator or physical-stop verification.
2. Reconcile the 75-edge difference between the canonical 1,490-edge Zenodo file and the project's 1,415-edge cleaned file before treating the cleaned graph as complete.
3. Continue the exact-name candidate crosswalk review. Keep the 55 unmatched labels, three Ayesha Manzil name-variant rows, two Shafiq Mor coordinate-review rows and four collision-flagged exact-name rows unresolved until evidence supports a decision. Three additional user-confirmed name aliases are recorded separately with coordinates deliberately unassigned.
4. Obtain written permission for the supplied Think Transportation KML before any redistribution, conversion to public GeoJSON or use in publishable `route_shapes`.
5. Use OSM as the primary road-network reference only after physical boarding points and their coordinates are reviewed. Do not derive public route geometry from unverified stop candidates.
6. Present the refreshed consolidated register and unresolved items for explicit owner approval before database writes, activation or public publication.

## Current consolidated status — 19 November 2026

### Owner-reviewed published stop sequences

The project owner has now confirmed the displayed forward stop names/order for:

- **Think Transportation R-series:** R1, R2, R3 (including the owner-supplied Shan Chowrangi insertion), R4, R8, R9, R10 (including the owner-supplied Do Talwar / Pak Tower / Abdullah Shah Ghazi split), R11, R12 and R13.
- **SMTA R-series:** R14 (the owner confirmation applies to the SMTA-published 17-entry sequence because R14 is absent from the adopted Think Transportation KML inventory).
- **Think Transportation EV-series:** EV-01, EV-02 (including the Gate 5/Checkpost 05 and Gate 6/Checkpost 06 aliases), EV-03, EV-04 and EV-05.

Detailed decisions and complete ordered lists are in [the owner route verification register](../../docs/research/USER_ROUTE_VERIFICATION_REGISTER.md), with individual packets for EV-03, EV-04 and EV-05. Owner review confirms the displayed list only; it does not independently verify current dispatch, physical boarding platforms, coordinates, reverse-direction service, or geometry rights. The separate SMTA via-descriptions remain comparison evidence and have not been merged into the adopted Think sequences.

### BRT station evidence remains provisional

- **Green Line:** government project evidence records 25 stations; a historical planning presentation lists 29 corridor points; two 2026 passenger-facing secondary lists each claim 22 stops and materially disagree. No current operator-issued ordered station-ID register has been received.
- **Orange Line:** the 2021 contract lists OL-1 to OL-4 (5 No. Chowrangi, Orangi Town Police Station, Abdullah College, Dilpasand Sweets). A 19 May 2026 Assembly answer confirms the operating corridor endpoints TMA Office Orangi Town to Jinnah University for Women near Matriculation Board Office. Official sources still differ on four versus five passenger stations.
- Reconciled source evidence and required operator clarifications are recorded in [the Phase 5C BRT station evidence review](../../docs/research/PHASE_5C_BRT_STATION_EVIDENCE_REVIEW.md), alongside the prior Phase 5AR/5BA/5AV evidence. No complete current BRT station sequence is approved.

### Historical coordinate dataset and candidate crosswalk

- Canonical source: [Zenodo DOI 10.5281/zenodo.13951512](https://doi.org/10.5281/zenodo.13951512), Data Research Lab Pakistan / Habib University, published 18 October 2024. The publisher project page states CC BY 4.0; the Zenodo Rights/License field is blank. DOI 13932672 is unrelated `xIndices` software.
- Current cleaned files: 572 nodes, 1,415 directed edges and 76 route identifiers. The canonical published edge file has 1,490 rows; the 75-row raw-to-cleaned delta remains unexplained.
- Structural QA: no duplicate node IDs, invalid WGS84 coordinates, dangling edge endpoints or duplicate directed edge rows; 10 exact-coordinate collision groups involve 24 nodes; one self-loop remains; seven route identifiers require topology review.
- The new all-route owner-sequence crosswalk covers 270 stop entries across 16 owner-reviewed forward sequences: 185 exact normalized-name matches, three user-confirmed name aliases with no coordinate assignment, 77 unmatched entries (55 distinct labels), three Ayesha Manzil name-variant rows withheld as ambiguous, two Shafiq Mor rows marked for coordinate review, and four exact-name match rows flagged for coordinate collisions. See [candidate crosswalk CSV](../../data/research/owner_route_node_candidate_crosswalk.csv), [method/review notes](../../docs/research/PHASE_5C_OWNER_ROUTE_NODE_CANDIDATE_CROSSWALK.md), and the source [user-confirmed alias register](PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv).
- All candidate coordinates remain research-only. No fuzzy matches, automatic alias merges, coordinate averaging or database promotion were performed.

### Database and map publication state

The owner-supplied 16 November 2026 database snapshot contains 572 historical research stops, all `under_review`, with the historical source `pending`; `route_shapes` has zero rows. Public discovery intentionally returns only active stops on published/verified routes, so this snapshot provides no public stop markers. The admin-only `/admin/historical-network` QA map is the correct layer for inspecting the unverified candidate markers. PR #94 adds a fallback to individual Leaflet markers if the optional MarkerCluster asset is unavailable and clarifies the public empty state. If the admin QA map still shows no markers, inspect its authenticated `/admin/historical-network/data` response and browser console; live visual behavior has not been independently verified.

### Rights, safety and publication gates

- The supplied Think Transportation KML still has a restrictive permission notice. The permission request documented in Phase 5BC has **not** been sent or approved. Do not redistribute the KML, convert it to public GeoJSON, host it for public download, or populate publishable `route_shapes` until written permission covers the exact intended uses.
- No database records, verification states, route-stop links, coordinates, route shapes, activation, or public API data were changed by the owner sequence reviews or research updates.
- **CI verification:** GitHub Actions `Tests` completed successfully on the PR head commits for PRs #87–#96. The `Phase 5AD Unmatched Stop Triage` and `Phase 5AG Official Sequence Name Reconciliation` workflows also completed successfully on those PR heads. The GitHub connector returned no combined status entries for the squash merge commits, but the PR-triggered Actions runs are successful. This verifies the automated tests/workflows, not live-browser visual rendering of the admin map.


## OSM candidate coverage and unmatched-stop triage — Phase 5AP (19 November 2026)

This update records the completed Phase 5AI/5AJ OSM inventory, Phase 5AL SMTA-to-historical/OSM crosswalk artifact, and latest Phase 5AD unmatched-stop triage artifact. These are research coverage results only; they do not verify physical boarding locations or authorize coordinate assignments.

### Karachi OSM transit-feature inventory and historical-node proximity

The Phase 5AI workflow extracted **1,133 OSM transit features** from the Geofabrik Pakistan regional extract, clipped/reviewed against OpenStreetMap Karachi Division relation 6080948. The inventory contains 1,018 `highway=bus_stop` features, 113 bus stations and 2 bus platforms. OSM nodes remain points and mapped ways retain their geometry; no centroid or inferred boarding point was created.

The Phase 5AJ read-only proximity audit compared all 572 historical node coordinates with that inventory using a 250-metre search radius in EPSG:32642:

| Historical-node review result | Count |
|---|---:|
| Exact normalized name and OSM candidate within 250 m | 21 |
| Proximity candidates only (no exact-name candidate) | 196 |
| No OSM candidate within 250 m | 355 |
| **Total historical nodes** | **572** |
| Historical nodes with multiple nearby candidates | 72 |

The 21 exact-name-and-proximity results are candidates for manual inspection, not verified stops. A nearby OSM feature may be a different stop, the opposite side of a road, an obsolete feature, or a general station/platform object. The 355 no-candidate result does not prove that a physical stop is absent; it means no qualifying mapped feature was found within the chosen radius in this OSM snapshot. The source artifact was generated 18 November 2026; OSM coverage is community-maintained and can change.

### SMTA published-entry to historical/OSM crosswalk — Phase 5AL

The Phase 5AL artifact contains 281 rows representing 248 official named entries after excluding 20 direction descriptors and preserving multiple OSM candidates as separate rows. Its report records:

- 121 exact historical-node name matches, 18 route-scoped user-approved aliases, and 109 official entries without a historical-node name match.
- 60 unique official entries have at least one OSM candidate within 250 m.
- 79 unique official entries have only a nearest OSM feature outside 250 m.
- 109 unique official entries have no historical-node name match.
- 24 unique official entries have multiple within-250-metre OSM candidates.

The Phase 5AL crosswalk is based on SMTA's published named entries and is kept separate from the adopted Think Transportation owner-reviewed R/EV sequence register. Its historical coordinates and OSM features remain unverified; no OSM object or coordinate is assigned to an official route stop.

### Residual unmatched owner-sequence names — Phase 5AD

The latest successful Phase 5AD workflow (run 115, 19 November 2026) generated a fresh 82-row triage artifact from the current Phase 5AA residual queue. The triage distribution is:

| Triage category | Rows |
|---|---:|
| Possible text candidate (0.65–under 0.85) | 30 |
| Weak text candidate (0.45–under 0.65) | 29 |
| Low text candidate (under 0.45) | 23 |
| **Total** | **82** |

The 82 rows comprise 28 leading-text-candidate-only cases, 19 multiple-close-candidate cases, 23 cases with no candidate at or above 0.45, and 12 weak-text-only cases. Priority grouping is 40 operator-evidence-first, 19 manual-disambiguation and 23 low-priority. Similarity scores are linguistic triage hints only. No candidate node or coordinate is selected, and the physical-stop, coordinate-assignment and route-approval fields remain unverified/not-assigned/not-approved.

### Files, artifacts and next actions

- Phase 5AI/5AJ: GitHub Actions artifact `phase-5ai-osm-bus-stop-candidate-inventory`; reproducibility and limitations are documented in [Phase 5AI](../../docs/PHASE_5AI_OSM_BUS_STOP_CANDIDATE_INVENTORY.md).
- Phase 5AL: GitHub Actions artifact `phase-5al-smta-historical-node-osm-candidate-crosswalk`; method and safeguards are documented in [Phase 5AL](../../docs/research/PHASE_5AL_SMTA_HISTORICAL_NODE_OSM_CANDIDATE_CROSSWALK.md).
- Phase 5AD: GitHub Actions artifact `phase-5ad-unmatched-stop-triage`; method and safeguards are documented in [Phase 5AD](../../docs/PHASE_5AD_UNMATCHED_STOP_TRIAGE.md).

The next useful research step is a human-readable review of the 21 exact-name/proximity candidates and the 72 multi-candidate historical nodes, prioritizing coordinate collisions and known anomalies. Do not promote them automatically. The 82 unmatched owner-sequence entries still need route-specific operator/field evidence; OSM name similarity alone cannot close them. The 75-edge raw-to-cleaned discrepancy, current operator station registers, KML written permission, and live admin-map rendering remain separate open blockers.

No database records, verification states, route-stop links, coordinates, route shapes, activation, or public API data were changed by these audits.


**Artifact freshness note:** Phase 5AI run 11 is the latest successful OSM inventory artifact available for this review (generated 18 November 2026). The subsequent run 12 failed at the Geofabrik download step with a runner-side `Network is unreachable` error; its focused tests passed, but it produced no refreshed OSM inventory. The Phase 5AI/5AJ figures above therefore describe the successful 18-November snapshot, not a newly refreshed 19-November extract.
