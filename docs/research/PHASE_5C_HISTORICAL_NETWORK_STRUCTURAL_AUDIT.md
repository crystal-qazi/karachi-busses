# Phase 5C — historical network structural audit

**Audit date:** 19 November 2026  
**Inputs:** `data/imports/karachi_bus_network_cleaned_nodes.csv` and `data/imports/karachi_bus_network_cleaned_edges.csv` on `main`.  
**Purpose:** Recheck structural and coordinate integrity of the historical research dataset before any candidate matching. This is not operational route verification or publication approval.

## Source provenance resolution

The canonical source is [Zenodo record 13951512](https://doi.org/10.5281/zenodo.13951512), *Karachi Bus Network*, published 18 October 2024 by Data Research Lab Pakistan. Creators are Muhammad Qasim Pasta, Moid Raza Khan and Fatima Aslam, affiliated with Habib University. The Lab's project page explicitly states CC BY 4.0 and describes the source methodology: route text from Travel Culture and HamariWeb, coordinates extracted using Google Maps.

The former alternate ID `13932672` is not a second version of this dataset; it is an unrelated `xIndices` climate-variability software record. The correct record's Zenodo Rights/License metadata is blank, so the Lab project page is the explicit licence evidence to cite.

The canonical Zenodo downloads contain 572 node rows and 1,490 edge rows. The current project files contain 572 node rows and 1,415 edge rows. The 75-edge delta is unexplained because no complete cleaning/removal log has been located. This audit therefore validates only the current cleaned file's internal structure; it does not certify that the 75-row reduction was correct. Reconcile the raw-to-cleaned edge difference before treating the cleaned network as a complete derivative.

## Input and basic integrity results

| Check | Result |
|---|---:|
| Node records | 572 |
| Directed edge records | 1,415 |
| Distinct route identifiers | 76 |
| Duplicate node identifiers | 0 |
| Missing / non-numeric / invalid WGS84 coordinates | 0 |
| Coordinates outside broad Karachi review bounds (24.6–25.3 N, 66.6–67.6 E) | 0 |
| Dangling edge endpoints (node ID absent from node file) | 0 |
| Duplicate directed edge rows (same from, to and route) | 0 |
| Self-loop edge rows | 1 |
| Exact-coordinate collision groups | 10 |
| Node records participating in exact-coordinate collisions | 24 |

Coordinate envelope in this snapshot:
- Latitude: 24.7734899 to 25.12732678
- Longitude: 66.84802941 to 67.32445453

The broad geographic envelope is only a plausibility screen. It does not establish that a coordinate is the correct passenger boarding point, on the correct side of a road, or even the right landmark.

## Exact-coordinate collision groups

The following distinct source node identifiers share identical coordinates at the source's recorded precision. Keep their identities separate pending source provenance and field/authoritative evidence; do not auto-merge them.

| Shared coordinate (lat, lon) | Source node identifiers |
|---|---|
| 24.8606960, 67.0005244 | `lee_market`, `sabzi_mandi` |
| 24.8344317, 67.0726736 | `korangi_no_5`, `korangi_no_2-1/2`, `korangi_no_6`, `korangi_road` |
| 24.9029771, 67.0386279 | `liaquatabad_no_10`, `liaquatabad` |
| 24.9461056, 67.0128813 | `orangi_no_4`, `orangi_no_10`, `orangi_town` |
| 24.8417060, 67.1339881 | `korangi_industrial_area`, `vita_chowrangi` |
| 24.8570650, 67.0331655 | `lucky_star`, `lucky_star_saddar` |
| 24.9058650, 67.0307183 | `nazimabad`, `nazimabad_no_2`, `nazimabad_no_1` |
| 24.8787907, 67.0475385 | `Karachi_university`, `dawood_engineering_university` |
| 24.9339483, 67.1289529 | `gul_city`, `gulshan_jauhar_goth` |
| 24.8394175, 67.2532666 | `machine_tool_factory`, `bhains_colony` |

These are review flags, not proof that all names are wrong. Some may represent aliasing, coarse source geocoding, or distinct physical places incorrectly assigned one coordinate. The Karachi University / Dawood Engineering University collision and the four-way Korangi collision warrant priority review.

## Directed graph topology

Each route identifier was evaluated independently for weak connectivity, unique start/end, in/out degree and the simple-path condition.

- **69 of 76 route identifiers** form one connected simple directed path in this edge snapshot.
- **7 route identifiers** require topology review; do not flatten them into a single ordered stop list.

| Route identifier | Edges | Unique nodes | Structural issue |
|---|---:|---:|---|
| `17-K` | 26 | 26 | Branch/merge at `jinnah_hospital` |
| `2_-_D` | 16 | 16 | No terminal out-degree-zero node; merge at `noorani_masjid` |
| `6-B` | 30 | 19 | Multiple branches/merges (11 degree-anomaly nodes) |
| `G-27` | 33 | 33 | Branch at `orangi_town` |
| `Sheraz_Coach` | 18 | 18 | Branch at `tower`; merge at `bolton_market` |
| `19-D` | 25 | 25 | Self-loop at `bilawal_chowrangi`; no terminal out-degree-zero node |
| `pink_bus` | 55 | 54 | Multiple starts/ends and four branch/merge nodes; appears to aggregate connected subchains |

The single self-loop is:

```text
bilawal_chowrangi -> bilawal_chowrangi (route 19-D)
```

No exact duplicate directed edge rows were found. That does not remove the need to inspect source route identity, chronology, or route-variant provenance.

## Interpretation and constraints

1. This file pair is a historical/crowd-sourced research network, not a verified operator GTFS or current service catalogue.
2. The original author, canonical publication record, exact source files and redistribution licence still require independent confirmation. Do not redistribute the underlying dataset or derived database/geometry beyond the applicable permission.
3. The 10 coordinate collisions must remain separate node records until resolved. Do not average coordinates, select one label arbitrarily, or merge opposite-side boarding points.
4. A simple directed path in this source is only a graph-shape property. It does not prove that the route is current, correctly named, operated by the claimed provider, or safe to publish.
5. This audit does not match historical nodes to owner-reviewed R/EV sequences, approve any stop coordinate, or infer reverse-direction services.
6. No MySQL rows, verification flags, route-stop links, route shapes, activation, or public API data were changed.

## Next audit steps

- Resolve the canonical Zenodo record and licence/attribution discrepancy before any redistribution.
- Inspect each collision group against OSM features and independent authoritative/field evidence, recording evidence per candidate without merging nodes automatically.
- Reconcile the historical node names against the owner-reviewed sequence register as a separate candidate crosswalk; preserve unmatched and ambiguous cases explicitly.
- Review the seven non-simple route graphs edge-by-edge and retain their original topology.
- Keep OSM as the primary road-network reference for any future, separately authorized geometry work. Do not use restricted Think Transportation KML-derived geometry without written permission.
