# Phase 5AU — SMTA current route-directory cross-check against Think Transportation

**Review date:** 2026-11-18  
**Source:** [Sindh Mass Transit Authority — Karachi Bus Route Map and Full Provincial Route Directory](https://smta.gos.pk/route-map)  
**Evidence class:** Current government-published route directory; separate from Think Transportation's route map and KML.

## Source statement and attribution

The SMTA page identifies the route-map data as courtesy of Think Transportation, published with permission, reference KHI-MAP-08. The same page separately presents a route index and a full provincial route directory. SMTA also states it does not authenticate the third-party service data shown on the map. The permission statement for SMTA's publication must not be treated as a general redistribution licence for the original Think KML.

## R-series and Double Decker

The current SMTA directory lists:
- **R5 — Surjani to Masroor: Inactive**
- **R6 — Gulshan-e-Bihar Orangi Town to Singer Chowrangi: Inactive**
- **R7 — Mosamiyat to Gulshan-e-Ghazi: Inactive**
- **R14 — Maymar to Tower: Active**, 29 km, with a published via list including Jamali Pull, Al-Asif, Sohrab Goth, Ayesha Manzil, Numaish and Tower.
- **DD01 / Double Decker — Model Colony to Tower: Active**, 24 km.

This resolves the prior R14 evidence gap at the government-directory level: R14 is listed as active by SMTA, although it remains absent from the reviewed Think route table/KML. R14's SMTA sequence is preserved as a separate government-published variant; no geometry is inferred. DD01 is also present in SMTA's current directory but absent from Think KML. Its published via list repeats Malir Halt; retain that duplication as source text pending clarification.

The route index and directory are not fully identical: the index presents R5–R7 without status, while the detailed directory explicitly marks them inactive. Use the detailed route records for the directory's status claim, and retain the index as a separate page section.

## EV-series comparison

SMTA's directory labels all five EV routes Active and reports distances of 41, 44, 23, 58 and 48 km for EV-01 through EV-05. Think Transportation's published descriptions report 28, 30, 20, 34 and 41 km respectively. The SMTA via lists also differ from Think's named-entry sequences, including additional or differently named entries such as Cantt Bazar, Checkpost 02/05/06, Karachi Toll Plaza, Malir Link Road, Old Sabzi Mandi and Maymar Mor.

These differences are preserved as two source versions. The user-selected Think Transportation reference remains the primary source for R/EV route identity, published descriptions and supplied KML geometry. The SMTA directory is retained as current government-published status and comparison evidence, not used to overwrite Think's route descriptions or geometry.

## Data and publication decisions

1. Treat SMTA's R14 and DD01 records as government-published route candidates; R14 is explicitly listed Active.
2. Treat R5–R7 as Inactive according to the detailed SMTA route directory; do not activate them.
3. Keep all five SMTA EV route descriptions and distances as separate variants; do not merge their via lists into Think's sequences.
4. Do not create R14 or DD01 route geometry from stop names or road descriptions.
5. No stop coordinate, route geometry, MySQL record, verification status, or API publication state was changed.
6. Preserve source attribution. The SMTA statement that its map was published with permission does not establish the user's independent right to redistribute the original KML.
