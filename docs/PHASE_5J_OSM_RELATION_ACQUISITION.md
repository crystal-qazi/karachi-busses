# Phase 5J — OSM Karachi Division Relation Acquisition

**Selected object:** OpenStreetMap relation 6080948 (Karachi Division).
**Status:** acquisition tooling added; actual XML and geometry remain unacquired until the explicit local download is run.

## Source and endpoint

- Relation page: https://www.openstreetmap.org/relation/6080948
- Full relation endpoint: https://api.openstreetmap.org/api/0.6/relation/6080948/full
- The `/full` response contains the relation and its member ways/nodes needed for subsequent local geometry assembly.
- Licence: ODbL 1.0; attribution: © OpenStreetMap contributors.

This workflow uses the OSM API for one selected relation. It does not call Overpass, scrape raster tiles, edit OSM, or query private services.

## Run locally

From the repository root:

```bash
python scripts/acquire_osm_boundary.py
```

Dry run only: no network request or file write.

After reviewing OSM's current API policies and ensuring network access:

```bash
python scripts/acquire_osm_boundary.py --download
```

Output:
- `data/osm_boundary/osm-relation-6080948-full.osm`
- `data/osm_boundary/relation-metadata.json`

Do not commit the raw XML to Git. Keep it locally or in an appropriately licensed, access-controlled research data store. Record the metadata manifest and SHA-256 in the project evidence register.

## What the script validates

- HTTPS host restricted to `api.openstreetmap.org`, including redirects.
- Exact relation endpoint and ID 6080948.
- Relation exists and carries `boundary=administrative`.
- Relation name is Karachi Division or Karachi.
- OSM relation version, timestamp, changeset, tags and member roles/counts.
- Raw XML file size and SHA-256.

The script intentionally does **not** claim the relation is a valid polygon. Member ways may form rings from multiple fragments; relation geometry needs proper stitching, inner/outer ring assembly, topology validation and independent map review.

## Next local GIS processing

After acquisition succeeds:
1. Use a maintained OSM geometry library (e.g. PyOsmium/osmium) to assemble the multipolygon from relation members.
2. Confirm every outer and inner ring is closed and valid; inspect gaps, overlaps, self-intersections, duplicate rings and islands.
3. Export a research GeoJSON in EPSG:4326 and calculate area using a suitable projected CRS; record both methods.
4. Render a boundary preview with visible OSM attribution.
5. Discover district relations separately; never infer or invent their IDs from names alone.
6. Compare district polygons and their union against the selected division relation.
7. Require independent review before using the polygon to clip the Pakistan road extract.

## Known discrepancy

A previous OSM-derived index reported 7,134.669 km² for relation 6080948, while the Commissioner Karachi page reported 3,527 km². This difference remains an explicit QA issue. The newly acquired relation's geometry must be measured independently; do not force it to match either figure or silently edit the OSM relation.

## Safety and publication

No production database changes. No bus stop/route coordinates are altered. No unverified geometry is imported into the public application. OSM attribution and ODbL obligations must be assessed before redistributing any derived database.
