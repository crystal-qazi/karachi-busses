# Phase 5S — All 572 historical coordinate nodes against OSM roads

**Status:** Reproducible research register tooling. The output is proximity evidence only; no node becomes an approved stop.

## Purpose

Extend the earlier 191-row stop-to-road proximity audit to the complete 572-node historical coordinate inventory. This phase reuses the already-built Phase 5N OSM road artifact and does not download or extract the Pakistan PBF again.

## Inputs

- `data/research/PHASE_5_NODE_AUDIT.csv`: 572 source nodes, historical route-label membership, coordinate-collision groups.
- `data/research/PHASE_5_STOP_NODE_CROSSWALK.csv`: exact-name candidate links to SMTA-published route-stop text. Blank mappings remain blank.
- Phase 5N OSM road GeoJSON and validated Karachi Division relation 6080948 boundary, retrieved from the original successful workflow artifact.
- Distances use EPSG:32642; input/output point coordinates remain WGS84 longitude/latitude.

## Output

- `karachi-572-node-osm-road-review.csv`: exactly one row per source node, including source labels, candidate SMTA stop references, collision group, nearest OSM way, distance band, and up to five distinct nearby OSM way candidates.
- `karachi-572-node-osm-road-review-report.json`: source hashes, OSM/boundary hashes, counts, limitations, and ODbL attribution.

The workflow is manually dispatched and downloads the existing Phase 5N artifact by run ID (default `44156081494`). It installs only Python packages from `requirements-gis.txt`; it does not install GIS executables or other local software.

## Interpretation rules

- A nearby road is not proof that a bus route serves it.
- A nearest road does not identify the correct carriageway, boarding side, platform, direction, or access permission.
- Historical route labels are preserved as dataset metadata, not current service memberships.
- Coordinate collisions remain visible; no points are moved or split automatically.
- Nodes outside OSM relation 6080948 are retained and flagged, not clipped or silently discarded.
- No snapping, geocoding, route geometry, direction inference, application/API exposure, or database writes occur.

## Provenance and licensing

The historical coordinate dataset is attributed to Pasta, Muhammad Qasim; Khan, Moid Raza; Aslam, Fatima, *Karachi Bus Network*, Data Research Lab Pakistan / Habib University (2024), DOI [10.5281/zenodo.13951512](https://doi.org/10.5281/zenodo.13951512), CC BY 4.0.

OSM road data is © OpenStreetMap contributors, ODbL 1.0. Preserve attribution and applicable ODbL obligations for derived road data.
