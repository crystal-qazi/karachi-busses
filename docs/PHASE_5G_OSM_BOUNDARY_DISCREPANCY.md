# Phase 5G — OSM Karachi Division candidate discrepancy

**Finding:** OSM relation 6080948 is discoverable as "Karachi Division" in secondary OSM-derived indexes, but its reported area is not consistent with the Commissioner Karachi area figure. It is therefore rejected for extraction pending reconciliation.

## Evidence

- Commissioner Karachi Area & Maps page reports Karachi Division area as **3,527 km²** and describes seven districts and 31 subdivisions: https://www.commissionerkarachi.gos.pk/area-maps
- An OSM-derived Geoview page identifies relation **6080948**, `admin_level=5`, timestamp **2025-01-14 11:35 UTC**, and reports area **7,134.669 km²**: https://pk.geoview.info/krachy_dwyzhn%2C6080948r
- Direct OSM relation: https://www.openstreetmap.org/relation/6080948

The reported OSM-derived area is approximately 2.02 times the Commissioner's published area. These figures may use different boundary vintages, measurement methods, or extents. The discrepancy does not prove which polygon is legally correct; it proves this relation is not safe to use without further investigation.

## Required investigation

1. Obtain the exact relation geometry from a dated, permitted OSM extract and compute its area in a suitable projected CRS.
2. Inspect relation tags, member ways, multipolygon validity, subarea relations, and administrative level.
3. Compare the relation against the Commissioner's official division map and current district records.
4. Seek an authoritative GIS polygon or written confirmation from the responsible government GIS custodian.
5. Record the reason for any correction or replacement. Never modify the OSM relation or imply authority over community mapping.
6. Keep the candidate rejected for clipping until independent review is complete.

## Decision

- Relation 6080948: **not approved** for Karachi road extraction.
- No alternative relation ID is asserted in this audit.
- No boundary polygon was downloaded, changed, or generated.
- No roads were clipped and no application/database data was modified.

This is a research QA flag, not a legal boundary determination.
