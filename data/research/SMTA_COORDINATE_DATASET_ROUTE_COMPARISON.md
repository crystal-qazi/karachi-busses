# Government Bus Route Comparison — Coordinate Dataset Audit

**Research date:** 16 November 2026  
**Purpose:** Compare SMTA's published Karachi route directory with the uploaded Habib University node/edge dataset.  
**Status:** Research only. No database import or operational verification.

## Sources
- SMTA Karachi route map and route index: https://smta.gos.pk/route-map
- SMTA route pages: https://www.smta.gos.pk/routes/16 (EV-02), https://www.smta.gos.pk/routes/17 (EV-03), https://www.smta.gos.pk/routes/18 (EV-04)
- Mnzil EV-01: https://mnzil.app/vehicles/EV-01
- Mnzil EV-02: https://mnzil.app/vehicles/EV-02
- Mnzil EV-03: https://mnzil.app/vehicles/EV-03
- Mnzil R-03: https://mnzil.app/vehicles/R-03
- Mnzil R-04: https://mnzil.app/vehicles/R-04
- Habib University dataset: https://zenodo.org/records/13951512 (CC BY 4.0; cite original authors when redistributing)

## Uploaded dataset facts
- 572 stop-node records with coordinates.
- 1,490 original directed route-edge records.
- 76 distinct dataset route labels.
- 75 exact duplicate directed edge rows removed in the cleaned research copy, leaving 1,415.
- 10 coordinate-collision groups retained for review.
- One self-loop retained and flagged.
- Dataset route labels are not assumed to equal current SMTA route codes.

## Route-by-route comparison

| SMTA route | Published corridor / distance | Candidate in coordinate dataset | Assessment |
|---|---|---|---|
| R1 Pink | Khokhrapar 04–Dockyard; 31 km | `pink_bus` mixed label | No isolated R1 chain identified |
| R2 Pink | North Karachi–Korangi Crossing; 31 km | `pink_bus` mixed label | No isolated R2 chain identified |
| R3 Pink | North Karachi–Nasir Jump; 32 km | `Route-3` | Mismatch: candidate begins Power House and ends Shan Chowrangi |
| R4 People's Bus | North Karachi/Power House–Kemari; 26 km | `Route-4` | Partial/mismatch: candidate ends Tower, not Kemari |
| R5 People's Bus | Surjani–Masroor; 28 km | None identified | Missing |
| R6 People's Bus | Gulshan-e-Bihar–Singer Chowrangi; 29.6 km | None identified | Missing |
| R7 People's Bus | Mosamiyat–Gulshan-e-Ghazi | None identified | Missing |
| R8 People's Bus | Yousuf Goth–Tower; 17 km | None identified | Missing |
| R9 Pink | Gulshan-e-Hadeed–Tower; 48 km | `Route-9` | Possible corridor overlap; endpoints differ |
| R10 Pink | Numaish–Ibrahim Hyderi; 30 km | `Route-10` | Incomplete: only Numaish–Taj Complex edge |
| R11 People's Bus | Mera Naka–Ziauddin Hospital; 21 km (directory) | `Route-11` | Mismatch: candidate Bilawal Chowrangi–Lyari |
| R12 People's Bus | Memon Goth–Saddar/Lucky Star; 36 km | `Route-12` | Partial: candidate starts Naddi Kinara and ends Lucky Star |
| R13 People's Bus | Hawksbay–Tower; 19 km | None identified | Missing |
| R14 People's Bus | Maymar–Tower; 29 km | None identified | Missing |
| EV-01 | CMH Malir Cantt–Dolmen Mall Clifton; 41 km | `EV-1` | Strong candidate: endpoints/corridor broadly align; stop list differs |
| EV-02 | Bahria Town–Malir Halt; 44 km | `EV-2` | Strong candidate: endpoints align; verify detailed sequence |
| EV-03 | Quaid-e-Azam Square Malir Cantt–Numaish; 23 km | `EV-3` | Strong candidate: endpoints broadly align; sequence differs |
| EV-04 | Bahria Town–Ayesha Manzil; 58 km | None identified | Missing |
| EV-05 | DHA City–Sohrab Goth; 48 km | None identified | Missing |
| Double Decker | Model Colony–Tower; 24 km | None identified | Missing |
| BRT Green | Green Line | `GreenLine_Bus` | Candidate has 22 nodes/21 links; validate official station sequence |
| BRT Orange | Orange Line | `Orange_Line` | Incomplete: only 4 nodes/3 links |

**Important:** SMTA's map index and detailed route directory can differ. For example, the map index describes R11 as Miran Naka–Shireen Jinnah Colony, while the route directory describes Mera Naka–Ziauddin Hospital. Preserve both descriptions as separate source observations until resolved.

## Dataset sequence observations
- `EV-1`: 17 links / 18 nodes, from `cmh_malir_cantt` to `dolmen_mall_clifton`.
- `EV-2`: 9 links / 10 nodes, from `bahria_town` to `malir_halt`.
- `EV-3`: 18 links / 19 nodes, from `malir_cantt_gate_5` to `numaish`.
- `GreenLine_Bus`: 21 links / 22 nodes, from `surjani_town` to `karachi_city_station`.
- `Orange_Line`: 3 links / 4 nodes only.
- `Route-10`: 1 link / 2 nodes only.

## Interpretation and next validation work
1. Do not rename candidate dataset labels to SMTA codes solely because the names look similar.
2. Compare ordered stop sequences, not only route codes or approximate corridors.
3. Check reverse-direction service as a separate direction/sequence.
4. Resolve duplicate-coordinate stop names without automatically merging them.
5. Check every candidate stop against its source map and road network.
6. Obtain or identify missing route chains (R1, R2, R5–R8, R13–R14, EV-04, EV-05 and Double Decker).
7. Obtain complete Orange Line station sequence and validate Green Line stations.
8. After manual review, prepare a proposed mapping table with source attribution and confidence.

## Approval gate
This report and the companion CSV are research artefacts only. Do not import, overwrite, activate, or publish routes in the application database until the user reviews and approves the reconciled records.
