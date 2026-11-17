# Phase 5K — Karachi Division Polygon Construction and Validation

**Selected OSM relation:** 6080948 (Karachi Division).
**Status:** reproducible GIS processing tool committed for review; no local PBF or polygon is claimed to have been processed by the remote GitHub session.

## Why Osmium export

Osmium Tool's `export` command assembles OSM multipolygon and boundary relations into multipolygon geometries. Its `--stop-on-error` option prevents silently continuing when an area geometry cannot be assembled. See https://docs.osmcode.org/osmium/latest/osmium-export.html.

## Prerequisites

1. Complete Phase 5J and obtain `data/osm_boundary/osm-relation-6080948-full.osm`.
2. Install Osmium Tool and ensure `osmium` is on PATH.
3. Install optional Python GIS dependencies:

```bash
python -m pip install -r requirements-gis.txt
```

These dependencies are separate from the Flask passenger application requirements.

## Run

Dry run:

```bash
python scripts/build_osm_boundary.py
```

Explicitly build and validate:

```bash
python scripts/build_osm_boundary.py --build
```

The script:
- Exports polygon geometries from the relation extract with OSM relation IDs/version/timestamp.
- Selects exactly one feature with relation ID 6080948.
- Rejects absent or duplicate relation features.
- Uses Shapely to check non-empty Polygon/MultiPolygon topology, ring closure, coordinate ranges and projected geometry validity.
- Uses PyProj to calculate planar area in EPSG:32642 (WGS 84 / UTM zone 42N).
- Writes only the selected boundary to GeoJSON and records SHA-256 provenance.

## Output (local research data; do not commit raw/derived OSM data casually)

- `data/osm_boundary/karachi-division-6080948.geojson`
- `data/osm_boundary/boundary-validation.json`

The GeoJSON uses EPSG:4326 coordinates (RFC 7946). Area is calculated separately in EPSG:32642. The report records the CRS and method.

## Acceptance gates

A successful script run is necessary but not sufficient for approval:
1. Relation identity and source version/timestamp match the extracted relation metadata.
2. Geometry is exactly one Polygon/MultiPolygon feature for relation 6080948.
3. Shapely reports valid topology; every exterior/interior ring is closed.
4. Bounding box is plausible for Karachi Division and not a global or malformed geometry.
5. Computed area is recorded with CRS and compared to the previously reported 3,527 km² Commissioner reference and 7,134.669 km² OSM-derived index. Differences are investigated; no value is forced.
6. Rendered map is visually reviewed, including islands, holes, enclaves and boundary edge.
7. OSM attribution and ODbL obligations are preserved.
8. Independent reviewer signs off before road extraction, clipping, route/stop edits or public app publication.

## Scope and safety

This phase does not discover or certify district polygons, clip the road network, modify bus stops/routes, edit OSM community data, or write to the production DB. The selected boundary is an OSM operational study boundary, not a government legal certification.
