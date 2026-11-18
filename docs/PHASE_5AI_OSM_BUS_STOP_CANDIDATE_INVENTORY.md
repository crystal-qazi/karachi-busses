# Phase 5AI — OSM Bus Stop Candidate Inventory

## Purpose

Extract OSM-mapped bus stop/platform features inside Karachi Division relation 6080948, using the same Geofabrik Pakistan PBF and validated OSM boundary process as the road inventory.

## Candidate selection

- `highway=bus_stop`
- `amenity=bus_station`
- `public_transport=platform|stop_position|station` with explicit bus tagging
- `highway=platform` with explicit bus tagging

OSM nodes are emitted as points. OSM ways retain their clipped line/polygon geometry. No centroid, geocoded point, or inferred boarding point is created. Generic rail-only platforms are excluded.

## Historical coordinate comparison (Phase 5AJ)

The same workflow also audits all 572 historical node coordinates against the extracted OSM stop/platform geometries using a 250 m proximity window in EPSG:32642. It reports up to three nearby OSM objects and exact normalized name candidates. This is a review aid only: nearest objects are not assigned, and all historical nodes remain unverified.

## Output

GitHub Actions artifact: `phase-5ai-osm-bus-stop-candidate-inventory`

- `karachi-osm-bus-stop-candidates.geojson`
- `karachi-osm-bus-stop-candidates.geojson.gz`
- `bus-stop-candidate-extraction-report.json`
- `PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT.csv`
- `PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT_REPORT.json`
- OSM boundary and source metadata for reproducibility

The raw regional PBF is not uploaded. Artifact retention is 14 days.

## Interpretation limits

This is a community-mapped OSM feature inventory, not an operator-approved passenger stop list. It does not prove that a bus currently stops there, identify the boarding side, or link an object to any SMTA route. No Phase 5 crosswalk is changed, no historical coordinates are assigned, and no route geometry is created. The Phase 5AJ distance audit does not establish that the nearest OSM feature is the correct stop or boarding location.

The next audit phase may compare candidate names/locations with historical nodes and published route names, but all matches must remain review candidates until independent physical/operator evidence exists.

## Source and licensing

Geofabrik Pakistan regional extract; OpenStreetMap relation 6080948. Attribution: © OpenStreetMap contributors. License: ODbL 1.0. Review ODbL obligations before redistributing derived databases.
