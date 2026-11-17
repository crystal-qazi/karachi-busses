# Phase 5J — OSM Karachi Division Boundary Extraction

**Selected object:** OpenStreetMap relation 6080948 (Karachi Division).
**Status:** local extraction tooling added; actual PBF and relation geometry are not yet acquired in this environment.

## Why use a regional extract

The OSM Foundation's API usage policy says the main API is for editing, not read-only project data extraction, and recommends regional extracts or other providers for larger/repeated data use. This workflow therefore uses the existing Geofabrik Pakistan PBF acquisition process and extracts the selected relation locally.

## Source and licence

- Geofabrik Pakistan extract: https://download.geofabrik.de/asia/pakistan.html
- Selected OSM relation: https://www.openstreetmap.org/relation/6080948
- Osmium Tool manual: https://osmcode.org/osmium-tool/manual/
- OSM data licence: ODbL 1.0; attribution: © OpenStreetMap contributors.

OSM data must be attributed and ODbL obligations respected. Do not scrape standard OSM raster tiles or edit community data.

## Run locally

First acquire the Pakistan regional PBF only after checking disk space and reviewing the source:

```bash
python scripts/acquire_osm_road_data.py --download
```

Install Osmium Tool and ensure `osmium` is on PATH. Then perform a dry run:

```bash
python scripts/acquire_osm_boundary.py
```

Explicitly extract the selected relation and all recursively referenced objects:

```bash
python scripts/acquire_osm_boundary.py --extract
```

Equivalent Osmium operation:

```bash
osmium getid -r -f osm -o data/osm_boundary/osm-relation-6080948-full.osm data/osm_source/pakistan-latest.osm.pbf r6080948
```

The `-r/--add-referenced` option recursively includes relation members, member ways and referenced nodes. The script checks the relation identity, administrative tag, name, direct member presence and node references for included ways. It records input PBF and extracted XML SHA-256 values, sizes, OSM version/timestamp and member counts.

## Output

- `data/osm_boundary/osm-relation-6080948-full.osm`
- `data/osm_boundary/relation-metadata.json`

Do not commit the raw OSM XML/PBF to Git. Retain it in a local research data directory and record the manifest in the project evidence register.

## Geometry is a separate validation stage

A complete referenced-object extract is **not yet a valid polygon**. Next:
1. Assemble outer and inner rings with a maintained OSM geometry library.
2. Validate multipolygon topology, ring closure, gaps, overlaps, self-intersections, duplicate rings and islands.
3. Export research GeoJSON in EPSG:4326.
4. Calculate area in an appropriate projected CRS and document method.
5. Discover the seven district relations separately from the same dated PBF; do not guess relation IDs.
6. Compare district polygons and their union against relation 6080948.
7. Render a preview with OSM attribution and obtain independent review before road clipping.

## Known discrepancy

A previous OSM-derived index reported 7,134.669 km² for relation 6080948, while the Commissioner Karachi page reported 3,527 km². Preserve this discrepancy as a QA item; do not force the geometry to match either figure or edit OSM.

## Safety

No live OSM editing, no OSM editing API requests, no tile scraping, no production database writes and no unverified route/stop changes. No road extraction or passenger-app publication until the boundary is validated and independently reviewed.
