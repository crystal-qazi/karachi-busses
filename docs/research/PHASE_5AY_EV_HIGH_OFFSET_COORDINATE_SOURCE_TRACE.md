# Phase 5AY — EV high-offset candidate coordinate source trace

**Review date:** 2026-11-18  
**Status:** Source-row trace complete; coordinate accuracy unresolved. No stop or coordinate is approved.

## Objective

Trace the ten EV candidate coordinates flagged as more than 1 km from their corresponding Think Transportation KML route line back to the original cleaned historical node file. Determine whether the discrepancy was introduced by the audit/crosswalk or is already present in the source data.

## Source files checked

- `data/imports/karachi_bus_network_cleaned_nodes.csv` — original cleaned node coordinate file in the repository.
- `data/research/PHASE_5_NODE_AUDIT.csv` — 572-node review audit.
- `data/research/PHASE_5AS_THINK_EV_CANDIDATE_COORDINATE_TO_KML_AUDIT.csv` — KML proximity results.
- Provenance: Zenodo record [13951512](https://zenodo.org/records/13951512), DOI `10.5281/zenodo.13951512`. The dataset description says stop coordinates were extracted using Google Maps, but the downloadable node file contains no per-stop Google Maps links, capture dates, screenshots, or coordinate-level provenance.

## Result

All ten high-offset candidate coordinate pairs were found verbatim in the original cleaned node CSV and were also carried unchanged into the 572-node audit. The Phase 5AS audit therefore did not introduce these coordinate values.

| Route / Think entry | Historical node ID | Source latitude | Source longitude | KML offset |
|---|---|---:|---:|---:|
| EV-01 PAF Base Faisal | `paf_base_faisal` | 24.96898395 | 67.22331802 | 2,411.4 m |
| EV-01 Nursery | `nursery` | 24.9163873 | 67.1224255 | 3,281.9 m |
| EV-02 Toll Plaza | `toll_plaza` | 24.9793624 | 66.9091871 | 27,471.3 m |
| EV-02 Baqai University | `baqai_university` | 24.9160963 | 67.0308507 | 14,894.4 m |
| EV-02 Malir Cantt Gate 5 | `malir_cantt_gate_5` | 24.9268502 | 67.1615432 | 1,747.4 m |
| EV-02 Malir Cantt Gate 6 | `malir_cantt_gate_6` | 24.91310604 | 67.19857737 | 1,007.4 m |
| EV-03 Safoora Chowrangi | `safoora_chowrangi` | 24.88227667 | 67.14885261 | 3,849.2 m |
| EV-03 Liaquat National Hospital | `liaquat_national_hospital` | 24.9139086 | 67.0308414 | 4,063.5 m |
| EV-04 Water Pump | `water_pump` | 24.874899 | 67.1673 | 11,217.2 m |
| EV-04 Ayesha Manzil | `ayesha_manzil` | 24.85579905 | 67.01541425 | 9,324.9 m |

## Key interpretation

1. The coordinate discrepancy is already present in the historical source file; it is not an accidental change made by the recent crosswalk or proximity audit.
2. The original dataset's general statement that coordinates were extracted using Google Maps is not sufficient to independently validate any one of these ten points.
3. The EV-02 Toll Plaza longitude (`66.9091871`) is preserved exactly as published in the source file. It is a high-priority anomaly, but must not be silently changed based on visual expectation or proximity to the route line.
4. KML distance is a QA signal only. A large offset may reflect a wrong historical coordinate, a changed route, a different stop interpretation, or a mismatch between the historical node and Think's named entry. This trace does not determine which explanation is correct.
5. The source CSV has no row-level coordinate provenance that would allow a more exact trace than the node ID and stored latitude/longitude.

## Decisions and next action

- Preserve every original coordinate exactly in the research register.
- Keep all ten records `under_review`; do not alias, snap, geocode, replace, or activate them.
- Request the original Google Maps pins/screenshots or independently authoritative operator stop coordinates for these ten records, prioritizing EV-02 Toll Plaza and Baqai University, followed by the EV-04 offsets.
- Keep the Think KML route geometry unchanged.
- No MySQL rows, route shapes, API output, or verification statuses were modified.

## Reproducibility

The ten coordinate pairs in the accompanying CSV were matched by exact node ID and exact latitude/longitude string against `data/imports/karachi_bus_network_cleaned_nodes.csv`. The source file contains 572 data rows. The original file and all source values remain unchanged.
