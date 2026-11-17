# Phase 5J — OSM Karachi Division Relation Acquisition

**Selected object:** OSM relation 6080948 (Karachi Division).
**Acquisition:** Geofabrik Pakistan regional PBF; local parsing with PyOsmium (pip package only).

## Data source and licence
- Geofabrik Pakistan extract: https://download.geofabrik.de/asia/pakistan.html
- OSM relation: https://www.openstreetmap.org/relation/6080948
- PyOsmium: https://osmcode.org/pyosmium/
- OSM data licence: ODbL 1.0; attribution: © OpenStreetMap contributors.

Use a regional PBF rather than repeatedly querying the OSM editing API or scraping standard OSM raster tiles. Preserve the PBF vintage and SHA-256 in the research manifest.

## Python-only setup
Activate the project's existing virtual environment:
```bash
python -m pip install -r requirements-gis.txt
```
No standalone Osmium executable, QGIS, GDAL installer, OSGeo utilities or Docker is required.

## Workflow
Acquire the regional PBF using the project's existing Python acquisition script, then run:
```bash
python scripts/build_osm_boundary.py --build
```
PyOsmium reads the PBF, captures relation 6080948 and assembles its multipolygon through the area handler. The script fails if the relation is missing, has unexpected administrative tags/name, or PyOsmium cannot assemble its area geometry.

## Provenance and review
The local output records input file size/hash, relation tags, version/timestamp/member references, output GeoJSON hash, geometry validation, area CRS, OSM attribution and ODbL licence. Do not commit the raw regional PBF or generated OSM data to Git.

A complete relation area is not legal certification. Validate topology, area, district overlays and visual appearance independently before road extraction or public app use.
