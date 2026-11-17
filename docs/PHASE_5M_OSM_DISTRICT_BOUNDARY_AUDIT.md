# Phase 5M — Karachi OSM District Boundary Audit

## Purpose

Audit the seven relation members tagged as `subarea` in OSM relation 6080948 (Karachi Division). This phase does not authorize road clipping or production use.

## Run (Python packages only)

```powershell
python -m pip install -r requirements-gis.txt
python scripts/acquire_osm_road_data.py --download
python scripts/build_osm_boundary.py --build
python scripts/audit_osm_district_boundaries.py --build
```

No standalone Osmium executable, QGIS, GDAL installer, OSGeo utility, Docker or other GIS executable is required.

## Outputs

- `data/osm_boundary/karachi-districts-osm-subareas.geojson`
- `data/osm_boundary/district-boundary-audit.json`
- `data/osm_boundary/karachi-boundary-preview.html`

The HTML preview uses Leaflet and OpenStreetMap tiles; an internet connection is required to load the basemap. The GeoJSON itself is self-contained.

## Checks

- Parent relation has exactly seven relation members with role `subarea`.
- Each child relation is an administrative boundary at admin_level=6.
- Each district geometry is assembled from the regional PBF and validated.
- English names are matched conservatively to the seven official district names; unmatched labels are reported, not guessed.
- District union is compared with the parent polygon; gaps, excess area and overlaps are quantified.
- Both EPSG:32642 projected area and WGS84 geodesic area are reported.

## Reference-area discrepancy

The Commissioner Karachi Area & Maps page states 3,527 km² for Karachi Division:
https://www.commissionerkarachi.gos.pk/area-maps

The Urban Unit's 2024 Karachi City Climate Risk Assessment reports 3,640 km²:
https://urbanunit.gov.pk/Download/Project%20files/8/Deliverable%20D_CCRA_FD_17042024.pdf

A secondary OSM-derived Geoview page reports 7,134.669 km² for relation 6080948:
https://pk.geoview.info/krachy_dwyzhn%2C6080948r

These sources may represent different administrative vintages or extents. This phase records the discrepancy; it does not force OSM geometry to match any reference.

## Acceptance gate

Do not extract/clip roads until the seven district identities, district union, boundary gaps/overlaps, and the area discrepancy have been reviewed. OSM data attribution and ODbL obligations must be retained.
