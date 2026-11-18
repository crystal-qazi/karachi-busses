# Phase 5AS — Think EV candidate coordinate-to-KML proximity audit

**Review date:** 2026-11-18  
**Status:** Candidate-coordinate QA only. No stop is verified and no coordinate or route geometry is changed.

## Method

- Used the supplied Think Transportation route GeoJSON audit extraction, parsed from the original KML without changing coordinate order.
- Compared each of the 47 existing exact-normalized-name candidate coordinates against its corresponding EV LineString.
- Reprojected WGS84 coordinates to UTM zone 42N (EPSG:32642) and measured nearest point-to-line distance.
- Recorded nearest KML chainage for QA only. Chainage is not a stop sequence, and nearest-line distance is not proof of a physical boarding point.
- Kept the 18 entries without exact-name coordinate candidates blank. No alias matching, geocoding, snapping, interpolation, or coordinate correction was performed.
- Original candidate latitude/longitude strings are preserved in the CSV.

## Results

| Route | Candidate coordinates | Within 250 m | 250 m–1 km | Over 1 km | No coordinate candidate |
|---|---:|---:|---:|---:|---:|
| EV-01 | 15 | 11 | 2 | 2 | 3 |
| EV-02 | 9 | 5 | 0 | 4 | 1 |
| EV-03 | 15 | 10 | 3 | 2 | 5 |
| EV-04 | 5 | 3 | 0 | 2 | 4 |
| EV-05 | 3 | 3 | 0 | 0 | 5 |
| **Total** | **47** | **32** | **5** | **10** | **18** |

## High-priority coordinate QA flags

These are large offsets from the corresponding KML route line, not a decision that either source is wrong:

- EV-02 Toll Plaza candidate: approximately **27.47 km** from the EV-02 line.
- EV-02 Baqai University candidate: approximately **14.89 km**.
- EV-04 Water Pump candidate: approximately **11.22 km**.
- EV-04 Ayesha Manzil candidate: approximately **9.32 km**.
- EV-03 Liaquat National Hospital candidate: approximately **4.06 km**.
- EV-03 Safoora Chowrangi candidate: approximately **3.85 km**.
- EV-01 Nursery candidate: approximately **3.28 km**.
- EV-01 PAF Base Faisal candidate: approximately **2.41 km**.
- EV-02 Malir Cantt Gate 5 candidate: approximately **1.75 km**.
- EV-02 Malir Cantt Gate 6 candidate: approximately **1.01 km**.

The EV-02 Toll Plaza longitude in the existing candidate row is retained exactly as stored; it has not been silently corrected. These records should be checked against their original source or a confirmed stop identifier.

## Sequence / chainage observations

The nearest-line chainage values show non-monotonic candidate projections in several routes (notably EV-01, EV-03 and EV-04). Some points are also far enough from the route line that their projected chainage clamps to a line endpoint. Therefore, chainage is only a diagnostic attribute and cannot be used to reorder the Think stop list or validate the historical candidate sequence.

## Decisions

1. Keep all 47 coordinate candidates and 18 unmatched entries in the research register.
2. Keep every existing candidate status as `under_review_not_verified`.
3. Prioritize the ten over-1-km records for source-coordinate review.
4. Do not change KML geometry, route sequence, stop coordinates, MySQL records, or public API publication state.
5. Next safe task: trace the high-offset candidate coordinates to their original source records, then separately resolve the 18 no-exact-name-match entries using evidence-backed aliases or new authoritative coordinates.