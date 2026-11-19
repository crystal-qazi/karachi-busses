# Phase 5BJ — Administrative boundary source recheck

**Review date:** 19 November 2026  
**Status:** Research-only source review. No boundary geometry downloaded, clipped, imported, or approved.

## 1. Purpose

Reassess the rejected Karachi Division OSM relation and identify a defensible administrative boundary reference for a future OSM road-network extraction. OSM remains the primary road and map source. Administrative boundary material is used only to establish the study extent, not to replace OSM road data.

## 2. New source findings

### 2.1 Commissioner Karachi — published division extent

The Commissioner Office Karachi's [Area & Maps page](https://www.commissionerkarachi.gos.pk/area-maps) states that Karachi Division covers **3,527 km²**, comprising seven districts and 31 subdivisions. It publishes a district/subdivision area table. The listed district totals are consistent with the 3,527 km² division figure.

Use: authoritative published area benchmark and administrative structure cross-check.

Limit: the page's text does not provide a downloadable GIS boundary or a machine-readable polygon. Its displayed map is not a substitute for source geometry.

### 2.2 Sindh Planning & Development Board — boundary-source disclosure

The P&D Board's [Sindh Development Mapping page](https://pnd.gos.pk/gis-map) states:

> Boundaries: OCHA. Keamari is split from OpenStreetMap.

The same page explicitly warns that the GIS map is under development and contains incomplete data.

Use: direct Government of Sindh evidence that its development map uses OCHA boundary data with an OpenStreetMap-derived Keamari split.

Limit: the page does not identify the exact OCHA release, OSM relation/version, derivation steps, or reuse terms. Because the map is explicitly incomplete, it must not be treated as a finalized production boundary.

### 2.3 WFP ArcGIS district-boundary service

The [WFP ArcGIS FeatureServer](https://atlas.geospatial.wfp.org/server/rest/services/Hosted/pak_bnd_adm3district_aha_usda/FeatureServer) exposes layer 0 as a WGS84 polygon feature layer. Its published attributes include province, district name, district code/label/number and OCHA district code, plus creation/edit timestamps.

The service description records:
- Base data acquired from Al-Hassan Associates in 2012 and last updated in 2016.
- Keamari district creation from West Karachi on 16 June 2025.
- Karachi district boundary adjustments during January–March 2026 following formation of new tehsils.

The [ArcGIS item metadata](https://atlas.geospatial.wfp.org/server/rest/services/Hosted/pak_bnd_adm3district_aha_usda/FeatureServer/info/iteminfo) credits Al-Hassan Associates and World Food Programme and says the dataset can be shared outside WFP.

Use: a potentially current district-level feature service with a documented update history and useful administrative identifiers.

Limit: “can be shared outside WFP” is not an explicit open licence or permission for unrestricted derivative redistribution. The service metadata does not, by itself, establish a validated Karachi Division union polygon or prove that the geometry matches the Commissioner's published district areas. No feature query or geometry was downloaded in this review.

### 2.4 Rejected OSM division relation

The previously investigated [OSM relation 6080948](https://www.openstreetmap.org/relation/6080948) is still not approved for clipping. The OSM-derived GeoView record reports an area of **7,134.669 km²**, materially different from the Commissioner's **3,527 km²** figure.

This discrepancy remains unexplained. The new P&D Board disclosure suggests an OCHA-plus-OSM-Keamari approach may be relevant, but it does not prove that relation 6080948 is the relation used by the Government map or that it is geometrically correct.

## 3. Evidence decision

| Candidate | What is established | Decision |
|---|---|---|
| Commissioner Karachi area page | Seven districts; 31 subdivisions; 3,527 km² published division area | Accept as an area/administrative benchmark, not as polygon geometry |
| P&D Board GIS map | Government disclosure of OCHA boundaries plus OSM Keamari split | Record as a useful methodology lead; not production-ready because the map is incomplete |
| WFP ArcGIS district layer | WGS84 district polygon service with Karachi updates through Jan–Mar 2026 | Candidate for read-only district-feature inspection; licence and geometry validation remain open |
| OSM relation 6080948 | OSM-derived area reported as 7,134.669 km² | Keep rejected for clipping pending geometry and area reconciliation |

## 4. Next validation steps

1. Make a read-only query of the WFP layer for the seven Karachi district records. Capture attributes, feature IDs, edit timestamps and geometry without editing the service.
2. Calculate each returned district polygon area using a suitable equal-area/geodesic method and compare it with the Commissioner's district-area table. Record method and tolerance; do not expect rounded published areas to match exactly.
3. Check district coverage, gaps, overlaps, topology and the seven-district union extent. Determine whether the service includes the current Keamari boundary and the January–March 2026 adjustments.
4. Compare the WFP district geometries with the P&D Board's disclosed OCHA base plus OSM Keamari method, if the P&D source data or a reproducible OSM relation/version can be obtained.
5. Revisit OSM relation 6080948 only after inspecting its current member lineage and geometry. Do not clip roads to it merely because its name and administrative tags look correct.
6. Confirm reuse terms for the WFP/OCHA geometry and any OSM-derived Keamari split before committing or redistributing boundary files.

## 5. Safety and data impact

- No database changes.
- No stop coordinates or route shapes changed.
- No public map or API publication settings changed.
- No boundary polygon or road extraction generated.
- OSM remains the primary map/road-network reference.
- All candidate boundary sources remain research-only until geometry, area, topology and reuse checks pass.

## 6. Source register

- Commissioner Office Karachi, [Area & Maps](https://www.commissionerkarachi.gos.pk/area-maps), accessed 19 November 2026.
- Sindh Planning & Development Board, [Sindh Development Mapping](https://pnd.gos.pk/gis-map), accessed 19 November 2026.
- World Food Programme, [Pakistan district boundary FeatureServer](https://atlas.geospatial.wfp.org/server/rest/services/Hosted/pak_bnd_adm3district_aha_usda/FeatureServer), accessed 19 November 2026.
- World Food Programme, [FeatureServer item metadata](https://atlas.geospatial.wfp.org/server/rest/services/Hosted/pak_bnd_adm3district_aha_usda/FeatureServer/info/iteminfo), accessed 19 November 2026.
- OpenStreetMap, [Karachi Division relation 6080948](https://www.openstreetmap.org/relation/6080948), candidate rejected for clipping pending reconciliation.
- OSM-derived GeoView record, [Karachi Division relation area summary](https://pk.geoview.info/krachy_dwyzhn%2C6080948r), reports 7,134.669 km²; secondary diagnostic only.


## 7. Independent district-area benchmark conflict

A second source comparison shows that published district areas are not consistent across administrative vintages and source methodologies:

- The current Commissioner Office Karachi page reports a division total of **3,527 km²** and district areas: Central 69, East 139, South 122, West 370, Keamari 559, Korangi 108 and Malir 2,160 km².
- A July 2026 Karachi Mobility Project / World Bank YBRT package repeats the same five values for Central (69), East (139), Korangi (108), South (122) and Keamari (559) km². It is a corridor document, however, and does not provide a complete seven-district division total.
- An Urban Unit city profile dated 2024 reports a materially different set: Central 64, East 159, South 81, West 88, Keamari 761, Korangi 95 and Malir 2,487 km², with a stated division area of 3,640 km².

The largest differences concern West, Keamari and Malir. They may reflect different administrative vintages, boundary definitions or source geometries. The available documents do not explain the differences sufficiently to reconcile them.

**Decision:** use the Commissioner page as the current published administrative benchmark, while recording source date and vintage for every comparison. Do not use a simple area match as sole proof that WFP polygons or an OSM relation are correct. Geometry coverage, topology, overlaps/gaps and administrative lineage must be inspected independently.

Additional source:
- Karachi Mobility Project, [Final Approved CLRP – YBRT Package 3](https://kmp.gos.pk/wp-content/uploads/2026/07/Final-Approved-CLRP-YLBRT-Package-3-Approved-by-WB-on-17-July-2026.pdf), July 2026.
- Urban Unit, [City Profile / Deliverable D](https://urbanunit.gov.pk/Download/Project%20files/8/Deliverable%20D_CCRA_FD_17042024.pdf), 2024.

No new boundary geometry was downloaded or accepted as part of this comparison.

## 8. Independent ArcGIS Online Karachi district layer — candidate only

A separate ArcGIS Online service was discovered during the follow-up source search:

- Service: [Karachi_Map_WFL1 FeatureServer](https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Karachi_Map_WFL1/FeatureServer)
- Layer 2: [Karachi_districts](https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Karachi_Map_WFL1/FeatureServer/2)
- Geometry type: polygon; layer spatial reference EPSG:3857 (Web Mercator).
- District labels exposed in the layer renderer/templates: Central, East, **Kaemari**, Korangi, Malir, South and West.
- Attributes: `FID`, `id`, `District`, `Town`, `Shape__Area`, `Shape__Length`.
- Layer metadata reports last data edit, schema edit and layer edit as 2 May 2025.
- The REST layer metadata has blank Description and Copyright Text fields. The service description and copyright text are also blank.

### Temporal and provenance warning

The layer already contains a `Kaemari` district label, while the WFP service change log records Keamari's creation from West Karachi on **16 June 2025**. The ArcGIS layer's reported last data edit is **2 May 2025**, earlier than that recorded creation date. This chronology needs explanation from the item owner; it must not be assumed to be an authoritative post-creation boundary. The spelling `Kaemari` is retained exactly as a source attribute and is not an approved alias correction.

### Retrieval and decision

The ArcGIS REST query operation is exposed, but the feature query response could not be retrieved through the available research interface. Consequently, no feature IDs, district attribute records, numeric areas, geometries, topology, gaps/overlaps or union extent have been inspected. The `Shape__Area` field must not be treated as square kilometres without verifying its calculation method and units; EPSG:3857 planar areas also require care because of projection distortion.

**Decision:** record this as a potentially useful independent comparison layer, but keep it **unverified and not approved for clipping/import**. Obtain the item owner and source lineage, a clear reuse licence, the exact data vintage, and a read-only export/query of all seven features before any geometric comparison. Do not use this service's household layers; this review concerns only the district polygon layer.

Additional source:
- ArcGIS Online, [Karachi_Map_WFL1 service and layer directory](https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Karachi_Map_WFL1/FeatureServer/layers), accessed 19 November 2026.
- ArcGIS Online, [Karachi_districts layer 2](https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Karachi_Map_WFL1/FeatureServer/2), accessed 19 November 2026.

No geometry was downloaded, no boundary was imported, and no database, route, stop-coordinate, public-map or API setting changed.
