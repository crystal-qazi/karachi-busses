# Phase 5AX — Historical Karachi Bus Network dataset provenance review

**Review date:** 2026-11-18  
**Status:** Canonical dataset DOI and publisher provenance confirmed; publisher companion page declares CC BY 4.0, while the Zenodo Rights field is visibly blank. Individual coordinate accuracy remains unverified.

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

The DOI conflict is resolved in Phase 5AZ: `10.5281/zenodo.13951512` is the Karachi Bus Network dataset. The other DOI previously mentioned in issue #13, `10.5281/zenodo.13932672`, resolves to an unrelated software record named xIndices (Jivesh Dixit, Version 1.2.1), not this dataset. The Data Research Lab Pakistan companion project page explicitly declares the Karachi Bus Network dataset as CC BY 4.0. The Zenodo dataset page's visible Rights section currently shows the License heading without a displayed value. Record the publisher's licence statement and the Zenodo metadata gap separately; do not claim the Zenodo record itself exposes a machine-readable `cc-by-4.0` value.

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
4. Record the publisher companion page's CC BY 4.0 declaration with attribution; note that the Zenodo record's visible Rights field is blank. Keep all imported bus stops and routes under review and the source record pending because it is historical secondary data, not current operator evidence.
5. Do not update MySQL or execute the importer. A future metadata-only source-record correction can set the Zenodo DOI and confirmed provenance while preserving `verification_status='pending'`.
6. Do not state that the Zenodo record displays a machine-readable license value. The publisher's companion project page explicitly declares CC BY 4.0; retain this distinction in attribution and redistribution notes.

## References

- [Zenodo record — Karachi Bus Network](https://zenodo.org/records/13951512)
- [Zenodo node CSV](https://zenodo.org/records/13951512/files/karachi_bus_network_node_data.csv?download=1)
- [Zenodo edge CSV](https://zenodo.org/records/13951512/files/karachi_bus_network_edge_list.csv?download=1)
- [Data Research Lab Pakistan companion project page — declares CC BY 4.0](https://darlab-pakistan.github.io/karachi-bus-network/)
- [Unrelated Zenodo DOI 10.5281/zenodo.13932672 — xIndices software](https://zenodo.org/records/13932672)
- [Phase 5AZ DOI and licence reconciliation](./PHASE_5AZ_ZENODO_DOI_LICENSE_RECONCILIATION.md)
- [Project Phase 5B coordinate review](../../docs/PHASE_5B_COORDINATE_REVIEW.md)
- [Phase 5AS EV coordinate-to-KML audit](./PHASE_5AS_THINK_EV_CANDIDATE_COORDINATE_TO_KML_AUDIT.md)


## Importer metadata behaviour

The importer retains the existing source name `Karachi Bus Network Research Dataset (user-provided cleaned files)` so a future explicit `--apply` run can find and update the existing source row rather than create a duplicate. It writes the Zenodo record URL and the confirmed provenance note, while leaving `verification_status` untouched. The importer remains dry-run by default; no database connection or write was made during this review.


## Optional database metadata correction

A metadata-only SQL script is provided at `sql/updates/phase5ax_historical_dataset_source_provenance.sql`. It selects and updates only the existing historical dataset row by its existing source name, setting the Zenodo record URL and provenance notes. It does not insert or delete records, change `verification_status`, or touch routes, stops, directions, segments or shapes. Review the selected row before committing. The source remains pending because it is historical secondary research and does not establish current service, even though the publisher's companion page declares CC BY 4.0.
