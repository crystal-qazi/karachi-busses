# Phase 5I — Adopt OpenStreetMap Karachi Division Boundary

**Decision:** Use the OpenStreetMap-mapped Karachi Division boundary as the project's operational study-area boundary, as explicitly requested by the project owner.

## Selected OSM object

- Object: relation
- OSM ID: `6080948`
- OSM page: https://www.openstreetmap.org/relation/6080948
- OSM-derived identity: Karachi Division
- OSM-derived administrative tags: `boundary=administrative`, `admin_level=5`
- Independent OSM-derived lookup: https://spatial.demo.geocode.earth/explore/place/osm/relation%3A6080948

The OSM boundary relation model uses relation members with `outer` and optional `inner` roles; complete geometry requires the member ways to form closed polygon rings. Administrative levels are country-specific and should not be interpreted as a universal legal rank. References: https://wiki.openstreetmap.org/wiki/Relations%3Aboundary and https://wiki.openstreetmap.org/wiki/Key:admin_level.

## Scope and interpretation

This relation is adopted as the **OSM operational study boundary** for the Karachi Buses project. It is not represented as a government-certified legal boundary. The previous area discrepancy is retained in the audit trail:

- Commissioner Karachi page: 3,527 km².
- OSM-derived Geoview index: 7,134.669 km².

The difference is a QA item requiring review of the live relation geometry, source history, and measurement method. It is not, by itself, grounds to discard the user's selected OSM source. Do not silently alter the relation or force its area to match a secondary government-page figure.

## Seven-district handling

The seven districts remain separate research entities: Karachi Central, Karachi East, Karachi South, Karachi West, Keamari, Korangi and Malir.

Do not invent district relation IDs. Discover each district relation from a dated OSM extract or OSM API query using exact names, administrative tags and containment within relation 6080948. Record relation ID, version, timestamp, tags, member counts and geometry hash. Confirm that each candidate district geometry is complete and that the union is consistent with the selected division geometry before treating it as a district polygon.

If OSM does not contain a complete or consistent district set, retain the division relation as the outer operational envelope and mark district overlays unavailable; do not fabricate them.

## Required acquisition and geometry QA

1. Acquire a dated OSM PBF or relation geometry through an OSM-supported API/export mechanism, respecting service usage policies.
2. Record OSM timestamp, relation version, source URL, retrieval timestamp, file size and SHA-256.
3. Inspect all relation tags and member ways; verify every outer/inner ring closes.
4. Validate polygon geometry, self-intersections, duplicate rings, gaps, overlaps and unexpected islands.
5. Compute area in a suitable projected CRS (not raw latitude/longitude degrees); document CRS and method.
6. Compare the computed area and outline with the previous OSM-derived area index and the Commissioner reference; report differences without forcing agreement.
7. Produce a review map with OSM attribution: © OpenStreetMap contributors, ODbL 1.0.
8. Obtain project reviewer approval before clipping the road network.

## Road extraction policy

After geometry QA, use the adopted relation as the Karachi study-area envelope. Extract roads with a documented outward buffer so roads crossing the boundary remain connected. Retain operator-confirmed routes outside the boundary if required. Do not clip stops, route directions or operator evidence to the boundary.

This decision authorizes use of OSM relation 6080948 as the project's selected candidate boundary source. It does **not** claim geometry has already been downloaded, validated, or approved for production extraction.

## Safety and licensing

Use OSM data with required attribution and ODbL compliance. Do not scrape standard OSM raster tiles to construct a dataset. Do not edit OSM community data. Do not import candidate geometry into the production passenger application until QA and reviewer sign-off.

## References

- OSM relation: https://www.openstreetmap.org/relation/6080948
- OSM-derived relation identity/tags: https://spatial.demo.geocode.earth/explore/place/osm/relation%3A6080948
- OSM relation boundary model: https://wiki.openstreetmap.org/wiki/Relations:boundary
- OSM administrative levels: https://wiki.openstreetmap.org/wiki/Key:admin_level
- OSM attribution/licence: https://www.openstreetmap.org/copyright
