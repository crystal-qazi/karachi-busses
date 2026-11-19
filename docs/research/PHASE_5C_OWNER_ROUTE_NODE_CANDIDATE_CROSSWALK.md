# Phase 5C — owner-reviewed route to historical-node candidate crosswalk

**Audit date:** 19 November 2026  
**Inputs:**
- `docs/research/USER_ROUTE_VERIFICATION_REGISTER.md`
- `data/imports/karachi_bus_network_cleaned_nodes.csv`
- Candidate output: `data/research/owner_route_node_candidate_crosswalk.csv`

## Result

The crosswalk covers 16 owner-reviewed forward sequences (R1–R4, R8–R14 and EV-01–EV-05).

| Measure | Result |
|---|---:|
| Owner-reviewed stop entries | 270 |
| Exact normalized-name matches | 185 |
| Unmatched entries | 80 |
| Distinct unmatched stop labels | 58 |
| Coordinate-collision-flagged exact-name match rows | 4 |
| Ambiguous Ayesha Manzil name-variant rows | 3 |
| Coordinate-review-required Shafiq Mor rows | 2 |

## Matching method

- Lowercase and normalize Unicode, punctuation, spaces and underscores to a common underscore-separated key.
- Match only when the normalized stop label equals exactly one normalized historical node identifier.
- For the explicit annotation `(also named ...)`, use the leading stop label for the exact-name check; preserve the full owner-reviewed label in the output.
- For `(route origin)`, remove the annotation only; do not infer aliases.
- Do not apply fuzzy string matching, geographic proximity, guessed aliases, manual coordinate snapping, or route-shape inference.
- Unmatched rows retain blank candidate node/coordinate fields.

The CSV columns are: route code, sequence, owner-reviewed stop label, match status, candidate source node ID(s), candidate latitude, candidate longitude, coordinate-collision flag, and candidate review note.

## Important interpretation

An exact normalized-name match means only that the label maps to a node identifier under the stated text-normalization rule. It does **not** establish that:
- the historical coordinate is correct or current;
- the node is the physical boarding/alighting pole;
- the coordinate is on the correct side of the road;
- two records sharing a coordinate are the same physical stop;
- the owner-reviewed route is independently operator-confirmed;
- the reverse direction follows the same stop list in reverse.

Four crosswalk rows have exact-name matches to nodes in coordinate-collision groups. They are retained as candidate matches but explicitly flagged in the CSV (three distinct node IDs; Korangi Road appears in both R3 and EV-01):
- Korangi Road → `korangi_road` (shared coordinate with three other Korangi node identifiers)
- Lucky Star Saddar → `lucky_star_saddar` (shared coordinate with `lucky_star`)
- Dawood Engineering University → `dawood_engineering_university` (shared coordinate with `Karachi_university`)

**Ayesha Manzil name-variant conflict:** Three owner-reviewed entries are marked `ambiguous_name_variant`, not assigned a coordinate. The source contains `ayesha_manzil` at 24.85579905,67.01541425, which corresponds to an OSM-backed building in Saddar, and `aisha_manzil` at 24.9265667,67.065173, near the Ayesha Manzil neighbourhood. The labels are close variants, but the coordinates refer to different parts of Karachi. The intended boarding location must be checked; neither candidate is automatically selected. References: https://mapcarta.com/W681000733 and https://mapcarta.com/N2671310324.

**Shafiq Mor coordinate anomaly:** The exact-name node `shafiq_mor` has coordinate 24.85644702,67.0001716, which appears inconsistent with Shafiq Mor in Gulberg/Buffer Zone. Secondary place references return candidate locations around 24.9571–24.9729 N, 67.0643–67.0761 E. Both rows are marked `coordinate_review_required`; do not use its coordinate until checked against OSM and authoritative/field evidence. References: https://www.distancesfrom.com/pk/Shafique-Mor-Bus-Stop-Karachi-latitude-longitude-Shafique-Mor-Bus-Stop-Karachi-latitude-Shafique-Mor/LatLongHistory/9176893.aspx and https://www.distancesfrom.com/pk/Shafiq-Morr-latitude-longitude-Shafiq-Morr-latitude-Shafiq-Morr-longitude/LatLongHistory/1696827.aspx.

The unmatched labels are not automatically errors. Many may require aliases, transliteration, source spelling reconciliation or a separate authoritative place/boarding-point check. Composite labels such as `Tower and Keamari` intentionally remain unmatched.

## Data governance

- This is a research-only candidate crosswalk. It is stored under `data/research/`, not `data/imports/`.
- Historical coordinates originate from the CC BY 4.0 Karachi Bus Network dataset (Zenodo DOI 10.5281/zenodo.13951512); attribution and modification status are documented in `docs/HISTORICAL_NETWORK_IMPORT.md`.
- Do not copy candidate coordinates into MySQL, mark stops verified, activate routes, create passenger-facing geometry, or change public API eligibility based on this crosswalk.
- No database rows, route-stop links, coordinates, route shapes, activation states, or API data were changed.

## Next step

Review the 58 unmatched labels and four collision-flagged matches in a separate evidence-led alias/coordinate register. Resolve each only with source-specific or authoritative evidence. Keep unresolved items blank and retain all original node identifiers.
