# Phase 5BB — PakBus secondary Karachi route and stop cross-check

**Review date:** 18 November 2026  
**Catalogue snapshot:** 13 November 2026  
**Status:** Secondary route/stop source identified and coverage compared. No database changes and no stop approvals.

## 1. Executive findings

PakBus publishes a Karachi route catalogue and a GTFS download for Karachi Breeze services. Its route catalogue is dated 13 November 2026 and reports 231 routes, 8,684 stops and 46 cities across Pakistan. The Karachi city page reports 20 routes and 319 stops.

This is a useful new **secondary comparison source** because it publishes direction-specific stop order, route pages, coordinates in its JSON catalogue, and timetable information for some Karachi Breeze routes. It is not an operator or government authority. Its About page describes PakBus as an independent service and does not identify the underlying Karachi-specific source records or coordinate-collection method. Do not promote its data to operator-verified status.

The downloadable feed listing explicitly says realtime=false. The PakBus website separately advertises live vehicle locations for Karachi Green and Orange Line; do not infer that live positions are included in the downloadable GTFS feed.

## 2. Publisher, snapshot and use conditions

| Item | Published value |
|---|---|
| Publisher | PakBus |
| Catalogue format | PakBus route catalogue JSON |
| Catalogue as-of date | 2026-11-13 |
| Catalogue counts | 231 routes, 8,684 stops, 461 directions, 46 cities |
| Catalogue SHA-256 | 9114782fe17d1a30ce9c7ac2e1cf500c9c59478926f2b3f62335ccd606263160 |
| GTFS feed version | e3a2619383ec1a2a1d17bd865e46c446ab3be39f3f426641619933c7795d5246 |
| GTFS service dates | 2026-11-13 to 2026-12-13 |
| GTFS feed counts | 231 routes, 8,684 stops, 2,919 trips, 22 scheduled routes, 461 patterns, 68 shapes, 201 routes with fares |
| GTFS feed SHA-256 | 6c15fa89d32fba9ca72abac2af99fcca5a061f9ae462fa56fe213044cc1baaf9 |
| Realtime in downloadable feed | false |
| Data use | Non-commercial use allowed; commercial use requires permission |

PakBus states that route and stop information comes from official public sources, but its About page names PITB for Punjab/Muzaffarabad and CDA for Islamabad. It does not name a Karachi source or explain the Karachi Breeze stop-coordinate provenance. PakBus also states that it is independent and is not run by a government body or bus operator. Therefore the Karachi records remain secondary, even where their names or endpoints agree with SMTA/Think Transportation.

The GTFS ZIP endpoint returned an unsupported content type to the web reader during this review. The feed listing and catalogue JSON were accessible; no claim is made that the ZIP contents were downloaded, fully parsed or validated in this phase.

## 3. Karachi coverage

PakBus reports 20 routes and 319 stops for Karachi:

| PakBus route | Network | Stops reported | Listed endpoints / summary |
|---|---|---:|---|
| 1 Green Line | Karachi Breeze | 22 | Abdullah Chowk – Numaish |
| 2 Orange Line | Karachi Breeze | 5 | TMA Orangi Town – Board Office |
| 3-Exp | Karachi Breeze | 7 | Abdullah Chowk – Numaish |
| 4-PB Pink Bus | Karachi Breeze | 22 | Abdullah Chowk – Numaish |
| EV-03 | People's Bus Service | 27 | Malir Cantt – Numaish |
| Pink-1 | People's Bus Service | 36 | Khokhrapar No 1 – Tower |
| Pink-2 | People's Bus Service | 37 | Power House Chowrangi – Korangi Crossing |
| Pink-3 | People's Bus Service | 42 | Power House Chowrangi – Nasir Jump |
| Pink-9 | People's Bus Service | 53 | Gulshan-e-Hadeed – Tower |
| Pink10 | People's Bus Service | 43 | Quaid e Azam Mazar – Ibrahim Hyderi |
| R1 | People's Bus Service | 40 | Khokhrapar No 1 – Dockyard |
| R10 | People's Bus Service | 43 | Quaid e Azam Mazar – Ibrahim Hyderi |
| R11 | People's Bus Service | 32 | Shireen Jinnah Colony – Miran Naka |
| R12 | People's Bus Service | 47 | Khokhrapar Chaman Colony – Lucky Star |
| R13 | People's Bus Service | 17 | Tower – Hawks Bay |
| R2 | People's Bus Service | 37 | Power House Chowrangi – Korangi Crossing |
| R3 | People's Bus Service | 42 | Power House Chowrangi – Nasir Jump |
| R4 | People's Bus Service | 35 | Power House Chowrangi – Jackson Market |
| R8 | People's Bus Service | 23 | Tower – Yousuf Goth |
| R9 | People's Bus Service | 53 | Gulshan-e-Hadeed – Tower |

The route coverage crosswalk is stored in:
- data/research/PHASE_5BB_PAKBUS_KARACHI_ROUTE_CROSSWALK.csv

## 4. Green Line — published 22-stop sequence

PakBus publishes the following direction from Abdullah Chowk toward Numaish:

1. Abdullah Chowk
2. KDA Flats
3. Karimi Chowrangi
4. Surjani (4K) Chowrangi
5. 2 Minute
6. Road 2400 (Aisha Complex)
7. Power House
8. Road 4200 (Saleem Center)
9. Up Mor
10. Nagan Chowrangi
11. Erum Shopping (Shadman No:2)
12. Juma Bazar (Bayani Center)
13. Five Star
14. Hyderi
15. Board Office
16. Annu Bhai Park
17. Enquiry Office
18. Nazimabad No 1
19. Sanitary Market (Gulbahar)
20. Lasbela Chowk
21. Patel Para (Gurumandir)
22. Numaish

The route page presents the opposite direction as a 22-stop sequence. The downloadable catalogue JSON includes stop IDs, latitude, longitude and a locationUsable flag for its stop records.

**Cross-check result:** This sequence agrees with the 22-stop BusUpdate list already reviewed, but differs materially from the other 22-stop CMTA list (which includes names such as Urdu Bazaar, Eid Gah Bagh, North Nazimabad, Orange Line Interchange, Shahrah-e-Humayun and Shahrah-e-Jehangir). Agreement between two non-operator passenger-facing sources does not make the sequence official. The Green Line route remains a secondary candidate sequence only.

## 5. Orange Line — direction asymmetry and count anomaly

PakBus route summary says Orange Line runs TMA Orangi Town to Board Office and serves 5 stops.

**Toward Board Office (5 listed stops):**
1. TMA Orangi Town
2. Punay Paanch Orangi Town
3. Abdullah College
4. Jinnah University
5. Board Office1

**Toward TMA Orangi Town (15 listed stop entries):**
1. Jinnah University
2. Board Office1
3. Hyderi
4. Five Star
5. Juma Bazar (Bayani Center)
6. Erum Shopping (Shadman No:2)
7. Nagan Chowrangi
8. Erum Shopping (Shadman No:2)
9. Juma Bazar (Bayani Center)
10. Five Star
11. Hyderi
12. Board Office1
13. Abdullah College
14. Punay Paanch Orangi Town
15. TMA Orangi Town

This is a material direction asymmetry: the forward direction has five entries, while the reverse direction lists fifteen entries and includes a loop-like detour with repeated stops. The route summary still says five stops. This may be a data-model issue, a route variant, or an actual directional service pattern; the available source does not explain it. Do not silently remove the repeated entries, mirror the forward sequence, or use either sequence as verified.

The PakBus endpoint at Board Office also differs from the 19 May 2026 Provincial Assembly answer's reported endpoint at Jinnah University for Women near Matriculation Board Office. PakBus lists both Jinnah University and Board Office1 in its forward sequence. This is useful evidence for the existing Orange Line endpoint ambiguity, not a resolution of it.

## 6. Cross-source endpoint conflicts for Think Transportation routes

PakBus endpoint comparison against the accepted Think Transportation KML/route reference and the current SMTA directory identifies these specific unresolved items:

| Route | PakBus endpoints | Think / SMTA reference | Decision |
|---|---|---|---|
| R1 | Khokhrapar No 1 – Dockyard | Khokhrapar – Dockyard | Broad endpoint agreement; exact origin stop identity still needs validation |
| R2 | Power House – Korangi Crossing | Power House – Indus Hospital | Material terminal conflict; preserve both claims |
| R3 | Power House – Nasir Jump | Power House – Nasir Jump | Endpoint agreement; does not verify intermediate stops |
| R4 | Power House – Jackson Market | Power House – Keamari | Material terminal conflict; preserve both claims |
| R8 | Tower – Yousuf Goth | Yousuf Goth – Tower | Same broad endpoints, opposite display direction |
| R9 | Gulshan-e-Hadeed – Tower | Gulshan-e-Hadeed – Tower | Broad endpoint agreement |
| R10 | Quaid e Azam Mazar – Ibrahim Hyderi | Numaish Chowrangi – Ibrahim Hyderi | Do not assume the origin labels are equivalent without evidence |
| R11 | Shireen Jinnah Colony – Miran Naka | Miran Naka – Shireen Jinnah Colony | Same broad endpoints, opposite display direction |
| R12 | Khokhrapar Chaman Colony – Lucky Star | Naddi Kinara – Lucky Star | Material origin conflict; preserve both claims |
| R13 | Tower – Hawks Bay | Hawksbay – Tower | Same broad endpoints, opposite display direction |
| EV-03 | Malir Cantt – Numaish | Malir Cantt Check Post 5 – Numaish | PakBus uses a broader start label; exact boarding point unresolved |

PakBus also contains separate Pink service route records whose endpoints overlap with R1/R2/R3/R9/R10. Do not merge the Pink service IDs with the red-bus route IDs merely because their endpoint pairs are similar. PakBus additionally publishes 3-Exp and 4-PB variants not present in the Think KML inventory.

## 7. Routes absent from this PakBus Karachi catalogue

The PakBus Karachi city page does not list these project routes:
- EV-01, EV-02, EV-04 and EV-05
- R5, R6 and R7
- R14
- DD01

Absence from PakBus is not proof that a service is discontinued. Use the SMTA status directory and other source-specific evidence for service status. The PakBus page's 20-route count includes route variants and Pink services that do not map one-to-one to SMTA route codes.

## 8. Coordinate and route-geometry handling

- PakBus catalogue JSON exposes stop IDs, names, latitude, longitude and a locationUsable flag. These are secondary candidate coordinates; the reviewed About page does not identify the coordinate capture method for Karachi.
- Do not copy PakBus coordinates into the production database as verified stop coordinates.
- Do not use the downloadable feed's 68 shapes as a replacement for Think Transportation's primary R/EV geometry without checking which routes those shapes cover, their provenance, licence, and alignment against the accepted KML.
- The downloadable feed declares realtime=false. The live map advertised on the PakBus website is a separate website capability.
- The non-commercial data-use permission is not a blanket commercial redistribution licence. Obtain written permission if the application is commercial or revenue-generating.
- OSM/MapLibre/Geoapify base map attribution requirements remain separate from PakBus data permission.

## 9. PakBus Green Line coordinates versus the 572 historical nodes

The 22 PakBus Green Line stop records in the 13-Nov-2026 catalogue expose latitude/longitude and locationUsable=true. These coordinates were screened against the 572 rows in data/imports/karachi_bus_network_cleaned_nodes.csv using great-circle Haversine distance to each historical node. The nearest-node result is only a proximity comparison; it does not establish that the two records refer to the same physical boarding point.

| Nearest historical-node distance | Candidate count |
|---|---:|
| Under 50 m | 2 |
| 50–under 100 m | 1 |
| 100–under 250 m | 9 |
| 250–under 500 m | 3 |
| 500 m or more | 7 |
| **Total** | **22** |

The two candidates under 50 m are Enquiry Office (29.9 m from historical node nazimabad) and Numaish (32.1 m from historical node numaish). Up Mor is 61.2 m from the historical up_mor node. Several other names have their nearest historical point hundreds of metres away; for example, Abdullah Chowk is 542.5 m from kda_stop, Karimi Chowrangi is 880.6 m from kda_stop, and Board Office is 674.5 m from kda_chowrangi. These offsets are not proof of incorrectness or correctness; the historical node file is not a verified stop register.

Reproducible artifacts:
- Source candidate coordinates: data/research/PHASE_5BB_PAKBUS_GREENLINE_STOP_CANDIDATES.csv
- Nearest-node crosswalk: data/research/PHASE_5BB_PAKBUS_GREENLINE_TO_572_NODE_CANDIDATE_CROSSWALK.csv
- Standard-library audit script: scripts/audit_phase5bb_pakbus_greenline_to_572_nodes.py
- Tests: tests/test_phase5bb_pakbus_greenline_crosswalk.py

The script requires the repository's existing 572-row historical node CSV and does not access the network. It writes only the crosswalk CSV. It does not create aliases, edit source coordinates, update MySQL or change verification status.

## 10. Project decisions

1. Add PakBus as a named secondary research source, not an authoritative operator source.
2. Use its Green Line sequence and coordinates only as candidates for comparison against SIDCL/SMTA drawings and the existing 572-stop historical dataset.
3. Keep the Orange Line five-versus-fifteen directional sequence anomaly unresolved.
4. Preserve R2, R4, R10 and R12 endpoint conflicts in the reconciliation register.
5. Preserve direction-only differences for R8, R11 and R13 without altering the Think KML coordinate order.
6. Keep all 572 historical stops under_review, all data sources pending, and route_shapes empty.
7. No MySQL import, route activation, stop approval, coordinate change or public API update was performed.

## 11. Sources

- PakBus Karachi city route inventory: https://pakbus.app/cities/karachi
- PakBus Green Line route and ordered stops: https://pakbus.app/routes/karachi-green-line
- PakBus Orange Line route and ordered stops: https://pakbus.app/routes/karachi-orange-line
- PakBus Karachi station catalogue: https://pakbus.app/cities/karachi/stations
- PakBus downloadable data and use terms: https://pakbus.app/data
- PakBus feed listing: https://pakbus.app/gtfs/feeds.json
- PakBus route catalogue JSON: https://pakbus.app/gtfs/catalogue.json
- PakBus About / data provenance: https://pakbus.app/about
- SMTA current route map and directory: https://smta.gos.pk/route-map
- Think Transportation KML/route source: https://thinktransportation.net/red-bus-karachi/
- Provincial Assembly Orange Line answer, 19 May 2026: https://www.pas.gov.pk/business/questios-details/33/2019
