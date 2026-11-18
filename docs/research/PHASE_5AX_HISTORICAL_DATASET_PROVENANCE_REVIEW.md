# Phase 5AX — Historical Karachi Bus Network dataset provenance review

**Review date:** 2026-11-18  
**Status:** Publisher and source-method metadata confirmed; individual coordinate accuracy and reuse licence remain subject to record-level verification.

## Primary record

The original dataset is published on Zenodo as [Karachi Bus Network, DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512), Version v1, published 18 October 2024 by Data Research Lab Pakistan.

Creators:
- Muhammad Qasim Pasta — Data curator
- Moid Raza Khan — Data collector
- Fatima Aslam — Data collector
- Affiliation: Habib University

The record includes:
- `karachi_bus_network_node_data.csv` — 572 node rows, with `node`, `latit`, and `long` fields
- `karachi_bus_network_edge_list.csv` — route edge records
- `karachi_bus_network.graphml`
- `generate_bus_network.R`

## Authors' stated source method

The Zenodo description says route data for 76 public buses (BRT and minibuses) was sourced from Travel Culture and HamariWeb. Stop longitude/latitude values were extracted using Google Maps. The authors then cleaned and standardized node and edge attributes and used the resulting data to construct a graph of stops and route edges.

This confirms the research dataset's publication provenance and the broad coordinate collection method. It does **not** provide per-stop Google Maps URLs, capture dates, screenshots, operator GPS records, field survey evidence, or a current operating timetable. The original route information is a secondary compilation, not a current operator feed.

## Relationship to this repository's data

The repository's historical node inventory contains 572 nodes and 1,415 directed edges across 76 route labels. These correspond to the published dataset's node/edge network model. The source attribution already present in `docs/PHASE_5B_COORDINATE_REVIEW.md` is therefore supported by the Zenodo record.

The importer `scripts/import_historical_network.py` currently says the original publication, author, date and redistribution licence have not been independently confirmed. The first three items are now confirmed by the Zenodo record. The licence needs careful treatment: the current Zenodo page extraction exposes a Rights/License section but did not expose a readable licence value in the reviewed page text, while the repository's Phase 5B documentation records CC BY 4.0. Do not silently change the database's rights note until the machine-readable record rights value or an explicit source licence statement is checked.

## Coordinate-quality implications

The authors describe coordinates as Google Maps extractions, but no per-row source link or coordinate capture timestamp is included in the dataset description or node CSV. Therefore:
- The dataset establishes where the submitted historical node coordinate values came from at a broad method level, not the exact pin/source used for each node.
- A mismatch between a candidate node and Think Transportation KML cannot be corrected by assuming the KML is wrong or that the historical point is wrong.
- The Phase 5AS high-offset candidates must remain unchanged until a specific source pin, route-specific stop identity, operator evidence or field survey resolves them.
- The original dataset's broad historical route graph must not be used as proof that a bus currently serves a named place.

## High-priority coordinate records requiring original-source evidence

The Phase 5AS audit identified ten candidate coordinates more than 1 km from their corresponding Think EV KML line. Highest offsets include:
- EV-02 `toll_plaza`: approximately 27.47 km
- EV-02 `baqai_university`: approximately 14.89 km
- EV-04 `water_pump`: approximately 11.22 km
- EV-04 `ayesha_manzil`: approximately 9.32 km
- EV-03 `liaquat_national_hospital`: approximately 4.06 km
- EV-03 `safoora_chowrangi`: approximately 3.85 km
- EV-01 `nursery`: approximately 3.28 km
- EV-01 `paf_base_faisal`: approximately 2.41 km
- EV-02 `malir_cantt_gate_5`: approximately 1.75 km
- EV-02 `malir_cantt_gate_6`: approximately 1.01 km

These are source-coordinate QA flags only. They do not authorize coordinate correction, node deletion, alias assignment, or route sequence changes.

## Decisions

1. Replace the stale statement that publication, creators and publication date are unknown with the confirmed Zenodo citation in research documentation.
2. Keep the historical network classified as a 2024 secondary research dataset, not current operator evidence.
3. Keep the 572 node coordinates, 1,415 directed edges and all derived route records unchanged.
4. Keep all imported bus stops and routes under review; keep the source record pending until its exact rights value and scope are confirmed.
5. Do not update MySQL or execute the importer. A future metadata-only source-record correction can set the Zenodo DOI and confirmed provenance while preserving `verification_status='pending'`.
6. Do not claim the licence is confirmed until the Zenodo machine-readable Rights metadata or a clear licence statement is inspected.

## References

- [Zenodo record — Karachi Bus Network](https://zenodo.org/records/13951512)
- [Zenodo node CSV](https://zenodo.org/records/13951512/files/karachi_bus_network_node_data.csv?download=1)
- [Zenodo edge CSV](https://zenodo.org/records/13951512/files/karachi_bus_network_edge_list.csv?download=1)
- [Project Phase 5B coordinate review](../../docs/PHASE_5B_COORDINATE_REVIEW.md)
- [Phase 5AS EV coordinate-to-KML audit](./PHASE_5AS_THINK_EV_CANDIDATE_COORDINATE_TO_KML_AUDIT.md)


## Importer metadata behaviour

The importer retains the existing source name `Karachi Bus Network Research Dataset (user-provided cleaned files)` so a future explicit `--apply` run can find and update the existing source row rather than create a duplicate. It writes the Zenodo record URL and the confirmed provenance note, while leaving `verification_status` untouched. The importer remains dry-run by default; no database connection or write was made during this review.
