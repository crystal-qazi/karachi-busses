# Karachi Bus Network — coordinate dataset intake

**Source:** Pasta, Muhammad Qasim; Khan, Moid Raza; Aslam, Fatima. *Karachi Bus Network*, Data Research Lab Pakistan / Habib University, version 1, published 2024-10-18.
**DOI:** https://doi.org/10.5281/zenodo.13951512
**Landing page:** https://zenodo.org/records/13951512
**Project documentation:** https://darlab-pakistan.github.io/karachi-bus-network/
**License:** CC BY 4.0 (retain attribution and license metadata).
**Our status:** Candidate coordinate source; not imported, not verified for current operation, and not published in the passenger app.

## Dataset contents reported by publisher

| File | Described content |
|---|---|
| `karachi_bus_network_node_data.csv` | Stop/node ID, stop name, longitude, latitude |
| `karachi_bus_network_edge_list.csv` | Source node, target node, route ID, route name |
| `karachi_bus_network.graphml` | Graph representation with node and edge attributes |
| `generate_bus_network.R` | Script used to generate GraphML from edge list |

The authors report 76 public bus services (BRT and minibuses) and 572 stop nodes. The landing page describes 1,490 edges in its dataset summary but reports 1,139 edges in the network-metrics table. This discrepancy must be resolved by counting rows in the downloaded files and checking directed/undirected and duplicate-edge handling.

## Research quality and limitations

- Authors say route information was collected from Travel & Culture and HamariWeb, with stop coordinates extracted using Google Maps.
- Their documentation warns that some minibuses may no longer operate and that some stop coordinates may be inaccurate.
- Coordinates are candidate point locations only. They are not proof that a bus currently boards at that exact location.
- An edge indicates a network connection in the research graph; it is not a road-following polyline and should not be rendered as a road route without map matching.
- The dataset is a secondary research compilation, not a government operational feed.
- The route count is not directly comparable to SMTA route codes until service variants, directions, and route naming are normalized.

## Intake and validation procedure

1. Download the two CSV files and GraphML from the Zenodo record. Preserve original bytes and record file hashes.
2. Inspect actual headers, row counts, nulls, duplicate IDs, duplicate edges, coordinate ranges, and geometry plausibility.
3. Check all coordinates fall within a Karachi/Pakistan plausibility envelope; flag rather than silently delete outliers.
4. Resolve each edge's endpoint IDs to the node table; reject or quarantine dangling references.
5. Group edges by route ID/name and reconstruct ordered sequences only after determining whether the edge list encodes direction and ordering. Do not infer a sequence from an undirected graph.
6. Compare stop names and route claims against our independent source registers: SMTA, Mnzil, URC 2010, and Travel & Culture.
7. Store the dataset's route/stop identity separately from our internal route/stop IDs; retain source IDs and attribution.
8. Assign each coordinate a provenance record: source dataset, source node ID, original coordinates, import timestamp, review status, and reviewer.
9. Use map preview for human validation. Only approved coordinates may enter the production seed/import.
10. Generate road-following geometry separately using a permitted road-network source/service; label generated geometry as derived and validate alignment visually.

## Coordinate confidence policy

- `source_unreviewed`: copied from this 2024 research dataset; not independently checked.
- `cross_source_match`: stop identity corroborated by another route source, but point still needs location review.
- `map_reviewed`: point visually checked against a reliable map reference.
- `field_verified`: location confirmed by a rider/operator/field survey.
- `rejected`: incorrect or ambiguous point.

Do not represent `source_unreviewed` as verified GPS.

## Download references

The Zenodo record lists:
- `karachi_bus_network_node_data.csv` (21.8 kB)
- `karachi_bus_network_edge_list.csv` (52.0 kB)
- `karachi_bus_network.graphml` (179.1 kB)
- `generate_bus_network.R` (994 bytes)

The raw file links are available from the Zenodo record's Files section. If Zenodo rate-limits automated retrieval, download manually from the record page and add the original files to the research intake area without editing them.

## Current execution status

- [x] Identify dataset and confirm published license/attribution.
- [x] Record documented schema and reported dataset counts.
- [x] Define QA, provenance, and verification requirements.
- [ ] Retrieve original files and calculate hashes.
- [ ] Parse actual CSV rows and reconcile 1,490 vs 1,139 edge counts.
- [ ] Produce route-by-route and stop-coordinate QA reports.
- [ ] Generate an interactive coordinate review map.
- [ ] Obtain user approval before any database import.

**No production database changes have been made.**
