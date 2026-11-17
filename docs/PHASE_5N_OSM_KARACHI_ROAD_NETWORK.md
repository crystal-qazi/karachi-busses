# Phase 5N — Karachi OSM Road Network Extraction

## Scope and source policy

OpenStreetMap is the primary operational geographic source. This phase builds a candidate-road inventory from the Geofabrik Pakistan regional OSM PBF and clips it to the validated parent administrative relation 6080948 (Karachi Division) only. The seven child subarea identities remain unresolved, so no district-level clipping, labels, aggregation or route claims are introduced.

The extraction does not change bus route records, stop coordinates, application behavior or the production database. It does not claim that an OSM road is bus-accessible merely because it has a road classification.

## Python-only execution

```powershell
python -m pip install -r requirements-gis.txt
python scripts/acquire_osm_road_data.py --download
python scripts/build_osm_boundary.py --build
python scripts/extract_osm_karachi_roads.py --build
```

No standalone Osmium executable, QGIS, GDAL installer, OSGeo utility, Docker or other GIS executable is required.

## Extraction rules

- Include candidate motor-road classes: motorway, trunk, primary, secondary, tertiary and links, unclassified, residential, living_street, service and road.
- Exclude explicitly access=no/private, motor_vehicle=no/private, and vehicle=no/private ways.
- Preserve OSM way ID, version, timestamp and available name, reference, direction, access, vehicle, bus/PSV, surface, speed, lanes, bridge, tunnel, junction, service, lighting, width, layer, destination and turn-lane tags.
- Clip line geometry to the parent relation without scaling, snapping or distorting source coordinates.
- Retain non-empty line segments; record counts and projected lengths by road class.
- Save GeoJSON and gzip-compressed GeoJSON with a source/boundary hash report.

This is a candidate inventory filter, not a complete legal or temporal routing model. Conditional access, bus-specific permissions, vehicle dimensions, turn restrictions and time restrictions still require evaluation before routing.

## Outputs

- data/osm_roads/karachi-osm-bus-roads.geojson
- data/osm_roads/karachi-osm-bus-roads.geojson.gz
- data/osm_roads/road-extraction-report.json

The workflow uploads derived research outputs only; it does not upload the raw Pakistan PBF. Artifacts are retained for 14 days.

## Acceptance and next gate

Accept only after the workflow succeeds, parent-boundary clipping and output integrity are reviewed, and counts/lengths are plausible. This does not validate SMTA routes, EV routes, Green Line or Orange Line station sequences. The next stage is to match independently verified stop coordinates to nearby road segments, report ambiguity and distance, and only then construct road-following candidate directions. Never infer a bus route from proximity alone.

## Attribution and licence

Source data © OpenStreetMap contributors, available under the Open Database License (ODbL). Retain attribution and review ODbL share-alike obligations before redistributing derived databases.
