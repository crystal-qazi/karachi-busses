# Phase 5K — Karachi Division Boundary (pip-only)

Selected OSM relation: 6080948 (Karachi Division).

## Install
Activate the existing project virtual environment:
```bash
python -m pip install -r requirements-gis.txt
```
Only Python packages are installed: PyOsmium, Shapely and PyProj. No separate Osmium executable, QGIS, GDAL installer, OSGeo utility or Docker is required.

## Run
```bash
python scripts/build_osm_boundary.py
python scripts/build_osm_boundary.py --build
```
The script reads the regional PBF directly with PyOsmium's relation and area handlers, obtains the assembled multipolygon, validates topology/ring closure with Shapely and calculates area in EPSG:32642 with PyProj.

Default input: data/osm_source/pakistan-latest.osm.pbf.

## Outputs
- data/osm_boundary/karachi-division-6080948.geojson
- data/osm_boundary/boundary-validation.json

The manifest records PBF SHA-256, relation version/timestamp/tags/member references, GeoJSON SHA-256, validation results, area CRS, OSM attribution and ODbL licence.

## Acceptance gates
1. Correct administrative relation identity and name.
2. PyOsmium assembles its relation area; failure is a hard stop.
3. Shapely validates topology and closed rings.
4. Plausible Karachi Division bounds.
5. Area compared with the previously cited 3,527 km² and 7,134.669 km² references; discrepancies investigated, never forced.
6. Visual inspection of islands, holes and boundary edges.
7. Preserve OSM attribution and ODbL obligations.
8. Independent review before road extraction or production use.

This OSM boundary is a research reference, not legal certification. No district overlay, road clipping, route/stop edit or production DB write occurs in this phase.
