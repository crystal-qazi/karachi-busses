# Phase 5G — Karachi Administrative Boundary Review

**Status:** Administrative scope recommended; GIS boundary not yet approved. No polygon has been fabricated, downloaded, or used to clip road data.

## 1. Decision: define the extraction scope

For a Karachi-wide public-transport application, use **Karachi Division's seven-district administrative extent as the initial road-network study envelope**, not a hand-drawn "city" polygon and not any single district.

The seven districts listed by the Commissioner Office Karachi are:
1. Karachi Central
2. Karachi East
3. Karachi South
4. Karachi West
5. Keamari
6. Korangi
7. Malir

The Commissioner Office describes Karachi Division as seven districts and 31 subdivisions. Its Area & Maps page publishes district/subdivision descriptions and a division map.

This is a recommended study scope, not proof that every bus route is confined to the division. Route corridors that cross the division boundary must be retained where an operator-confirmed route requires them. Use an additional, documented corridor buffer for network continuity; do not clip a route at an administrative border.

## 2. Why boundary levels must not be mixed

Pakistan Bureau of Statistics (PBS) describes the administrative hierarchy as province → division → district → sub-division, and notes that administrative boundaries can change between censuses. Its Census 2023 mapping material is an important reference, but the FOP describes boundaries frozen on 1 April 2022 for that census operation. It is not automatically a current 2026 legal boundary dataset.

The Commissioner Office's current administrative pages are the best public reference found for the present seven-district structure. They do not, in the material reviewed, provide a downloadable authoritative GIS polygon.

An OSM `boundary=administrative` relation is an openly mapped representation, not a government-certified legal boundary. It may be used as a candidate only after relation tags, completeness, geometry, and district membership are reviewed against government sources.

## 3. Boundary source register

| Source | What it establishes | What it does not establish | Use |
|---|---|---|---|
| Commissioner Karachi — Area & Maps | Seven-district structure, 31 subdivisions, division overview map | Downloadable GIS boundary polygon or legal survey coordinates | Primary administrative reference |
| Commissioner Karachi — Administration Structure | Names of seven districts and administrative roles | Boundary geometry | Cross-check district list |
| PBS GIS Section | Administrative hierarchy, GIS/census mapping process, boundary-change caveat | A directly downloadable Karachi GIS polygon on the reviewed page | Official GIS data custodian to approach |
| PBS Census 2023 FOP | Census administrative framework; boundaries frozen 2022-04-01 for census operation | Current 2026 legal boundary | Historical/census corroboration |
| OpenStreetMap administrative relations | Community-maintained candidate boundary geometry | Government certification | Candidate geometry only |

## 4. Required boundary approval process

1. Request current Karachi Division and seven district GIS boundary files from the relevant Government of Sindh/Commissioner/PBS GIS custodian, including datum/CRS, effective date, feature IDs and usage terms.
2. If official GIS data is unavailable, inspect OSM administrative relations for Karachi Division and each district. Record exact relation IDs, tags, member completeness, geometry validity, timestamp and source extract hash.
3. Compare OSM candidate boundaries with the Commissioner district map and official administrative list. Do not claim a visual map comparison establishes survey-level accuracy.
4. Produce a map showing the division outline and seven district polygons, with source and date labels.
5. Record discrepancies, gaps, overlaps, multipolygons and disputed areas. Do not silently repair or simplify a boundary.
6. Obtain a second reviewer approval before using any polygon for clipping.
7. Keep an outward route-corridor buffer and retain operator-confirmed route segments crossing the study envelope.

## 5. Proposed extraction geometry policy

- Study envelope: Karachi Division, seven districts.
- Districts: separate polygons retained for audit and map display.
- Network extraction: clip/crop road data only after the approved boundary is available; include a documented buffer sufficient to preserve roads crossing the boundary and network connectivity.
- Route corridors: may extend beyond the division when supported by current operator evidence.
- No stop coordinates, route sequences, or bus-access permissions are inferred from administrative boundaries.
- Never substitute a rectangular bounding box for the administrative polygon in final data.

## 6. Go / no-go

**GO:** use the seven-district list as the scope for sourcing and boundary research.

**NO-GO:** do not run Osmium extraction, create Karachi road graph, or generate route geometry until an actual polygon is acquired, provenance recorded, geometry validated, and second-review approval recorded.

## 7. References

- Commissioner Karachi — Area & Maps: https://www.commissionerkarachi.gos.pk/area-maps
- Commissioner Karachi — Administration Structure: https://www.commissionerkarachi.gos.pk/administration-structure
- PBS GIS Section: https://www.pbs.gov.pk/gis/
- PBS Census 2023 Field Operation Plan: https://www.pbs.gov.pk/sites/default/files/population/2023/reports/Field%20Operation%20Plan%20%28FOP%29.pdf
- Geofabrik Pakistan extract: https://download.geofabrik.de/asia/pakistan.html
- OpenStreetMap copyright/licence: https://www.openstreetmap.org/copyright

This is an engineering research decision, not a legal boundary determination or legal advice.
