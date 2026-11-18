# Phase 5AI — OSM Bus Stop Candidate Inventory

## Purpose

Extract OSM-mapped bus stop/platform features inside Karachi Division relation 6080948, using the same Geofabrik Pakistan PBF and validated OSM boundary process as the road inventory.

## Candidate selection

- `highway=bus_stop`
- `amenity=bus_station`
- `public_transport=platform|stop_position|station` with explicit bus tagging
- `highway=platform` with explicit bus tagging

OSM nodes are emitted as points. OSM ways retain their clipped line/polygon geometry. No centroid, geocoded point, or inferred boarding point is created. Generic rail-only platforms are excluded.

## Output

GitHub Actions artifact: `phase-5ai-osm-bus-stop-candidate-inventory`

- `karachi-osm-bus-stop-candidates.geojson`
- `karachi-osm-bus-stop-candidates.geojson.gz`
- `bus-stop-candidate-extraction-report.json`
- OSM boundary and source metadata for reproducibility

The raw regional PBF is not uploaded. Artifact retention is 14 days.

## Interpretation limits

This is a community-mapped OSM feature inventory, not an operator-approved passenger stop list. It does not prove that a bus currently stops there, identify the boarding side, or link an object to any SMTA route. No Phase 5 crosswalk is changed, no historical coordinates are assigned, and no route geometry is created.

The next audit phase may compare candidate names/locations with historical nodes and published route names, but all matches must remain review candidates until independent physical/operator evidence exists.

## Source and licensing

Geofabrik Pakistan regional extract; OpenStreetMap relation 6080948. Attribution: © OpenStreetMap contributors. License: ODbL 1.0. Review ODbL obligations before redistributing derived databases.
