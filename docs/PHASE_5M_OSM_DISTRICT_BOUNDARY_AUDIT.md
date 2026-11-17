# Phase 5M — Karachi OSM District Boundary Audit

## Primary boundary policy

OpenStreetMap (OSM) is the project's primary and operational boundary source. Use OSM relation 6080948 (Karachi Division) and its OSM district subareas as the working geographic reference, subject to internal OSM consistency checks and versioned provenance. Do not reshape, scale, trim, or otherwise alter OSM geometry merely to match a published government area figure.

Government area figures are retained as contextual comparison references. They may reflect older administrative vintages, different definitions, or different extents; disagreement alone does not override OSM. Record the discrepancy and investigate it, but do not treat government figures as acceptance targets.

Audit the seven relation members tagged as `subarea` in OSM relation 6080948. This phase does not authorize road clipping or production use.

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
- District union is compared with the OSM parent polygon; gaps, excess area and overlaps are quantified. This OSM-internal consistency check is the primary geometry acceptance test.
- Both EPSG:32642 projected area and WGS84 geodesic area are reported.

## Reference-area discrepancy

The Commissioner Karachi Area & Maps page states 3,527 km² for Karachi Division:
https://www.commissionerkarachi.gos.pk/area-maps

The Urban Unit's 2024 Karachi City Climate Risk Assessment reports 3,640 km²:
https://urbanunit.gov.pk/Download/Project%20files/8/Deliverable%20D_CCRA_FD_17042024.pdf

A secondary OSM-derived Geoview page reports 7,134.669 km² for relation 6080948:
https://pk.geoview.info/krachy_dwyzhn%2C6080948r

These sources may represent different administrative vintages, definitions or extents. They are contextual references only. OSM remains primary for this project; the discrepancy is documented and investigated but does not cause OSM geometry to be forced to match government figures.

## Acceptance gate

Road extraction may use the OSM parent boundary as the primary project boundary once the OSM parent and district geometries pass validity and internal consistency checks, and district identities are adequately resolved. A mismatch with government-published area figures alone is not a blocker and must not be 'corrected' by distorting OSM geometry. Keep unresolved district identity or topology issues explicit. OSM data attribution and ODbL obligations must be retained.
