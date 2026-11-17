# Phase 5H — Independent Boundary Source Cross-Check

**Status:** Source candidate identified; no boundary dataset downloaded or approved. This phase records metadata conflicts and acquisition gates only.

## 1. Candidate: UN OCHA Pakistan Subnational Administrative Boundaries (COD-AB)

Publisher/catalogue record: https://data.humdata.org/dataset/cod-ab-pak

A secondary catalogue identifies a Pakistan COD-AB dataset sourced from World Food Programme SDI and published/quality-assured by OCHA Field Information Services. It lists GeoJSON, Shapefile and file geodatabase resources. The dataset description says it contains:
- Admin 1: provinces/territories
- Admin 2: districts
- Admin 3: tehsils

The same catalogue describes the source dataset version 01 as created 2022-09-02 and valid for humanitarian use from 2022-09-09. A mirrored CKAN catalogue reports the HDX package record last updated 2024-05-07. Another secondary catalogue shows an August 2026 catalogue update, but that must not be confused with the source boundary's effective date.

Sources:
- HDX publisher record: https://data.humdata.org/dataset/cod-ab-pak
- Secondary metadata catalogue: https://findgis.com/datasets/ocha/pakistan-subnational-administrative-boundaries-cod-ab
- Mirrored resource metadata: https://ckan.rimes.int/en_GB/dataset/pakistan-subnational-administrative-boundaries

## 2. Important licence caveat

Available secondary catalogues disagree or are incomplete about licence metadata:
- One catalogue reports "Attribution".
- Another data-source index reports CC BY 3.0 IGO.
- A mirrored CKAN record displays "No License Provided".

The HDX publisher record could not be fetched in this research session (HTTP 403). Therefore **the licence is unverified**. Do not download for redistribution or publish derived polygons until the publisher's current terms, attribution requirements, and redistribution/modification permissions are confirmed directly. Free download does not itself establish a reuse licence.

## 3. Relevance to Karachi

The dataset includes district-level Admin 2 polygons and tehsil-level Admin 3 polygons, so it may provide a useful independent comparison source for Karachi's district structure. However:
- Its source version is from 2022.
- It may predate subsequent administrative changes.
- Its district names, codes (P-codes), boundaries and geometry must be checked against the Commissioner's current seven-district structure.
- The dataset's Admin 2 does not necessarily encode Karachi Division as a polygon; do not assume an aggregate division polygon is included.
- Admin 3 tehsils must not be mistaken for the seven districts.

## 4. Cross-check procedure once authorized

1. Open the HDX publisher record and inspect its current licence and resource metadata.
2. Record exact resource ID, file URL, version, source date, effective date, update date, attribution, licence and SHA-256.
3. If terms permit, acquire the district and tehsil files to a local research-only directory; do not commit raw archives to Git.
4. Inspect attribute schema, district names, P-codes, geometry CRS, validity, multipart structure and topology.
5. Filter Karachi records only by reviewed district identifiers and names; do not filter on name alone.
6. Compare all seven polygons and their union with the Commissioner's published district list/map. Calculate areas using a suitable projected CRS and document the method.
7. Compare the union and individual district areas with the OSM relation candidates. Do not treat agreement between two secondary datasets as legal certification.
8. Have an independent reviewer approve the resulting map and source lineage.

## 5. Decision register

| Source | Current decision | Reason |
|---|---|---|
| Commissioner Karachi pages | Primary administrative reference | Current seven-district listing; no downloadable polygon found in reviewed pages |
| PBS GIS / Census references | Official corroboration | Census vintage and boundary freeze must be respected |
| OCHA COD-AB / WFP SDI | Candidate only | Useful district-level independent comparison; source vintage 2022 and licence needs direct confirmation |
| OSM relation 6080948 | Rejected for clipping pending reconciliation | Secondary area figure conflicts materially with Commissioner's published area |

## 6. Go / no-go

**GO:** continue metadata and attribute-schema research. If the publisher licence is confirmed, acquire a local research copy and inspect it.

**NO-GO:** do not clip road data, generate an authoritative Karachi polygon, publish a boundary, or represent OCHA/OSM as government-certified until source terms, vintage, attributes and independent review are complete.

No boundary files were downloaded, no geometry was modified or created, no roads were extracted, and no application/database data was changed.
