# Phase 5BG — Exact OSM names for unmatched owner-reviewed stops

**Date:** 19 November 2026  
**Purpose:** Identify OSM bus-stop/station objects whose names exactly match owner-reviewed route entries that did not match a historical node name.

## Inputs and method

- `data/research/owner_route_node_candidate_crosswalk.csv`: owner-reviewed route sequence entries and their existing match statuses.
- Phase 5AI artifact `karachi-osm-bus-stop-candidates.geojson`: OSM transit features within Karachi Division relation 6080948.
- Only entries already marked `unmatched` are examined.
- Compare the owner-reviewed label to OSM `name` and `name:en` using Unicode normalization, case folding, punctuation/space normalization and exact equality.
- Preserve every distinct OSM object with an exact normalized-name match. Do not rank fuzzy candidates or infer aliases.

## Initial review result

Using the retained successful Phase 5AI OSM inventory snapshot generated 18 November 2026:

- 77 unmatched route-stop entries across 55 distinct labels were checked.
- 12 route-stop entries across 7 distinct labels have an exact normalized OSM name candidate.
- 65 route-stop entries have no exact OSM name candidate in this snapshot.
- No label in this initial result matched multiple OSM objects, but the workflow preserves multiple objects if later snapshots produce them.

The exact-name candidate labels found were Johar Mor, Brookes Chowrangi, Nasir Jump, Daryabad, Malir 15, Shireen Jinnah Colony and PIB Colony. These names occur on multiple route entries where applicable; the output preserves each route/sequence occurrence.

## Outputs

The workflow publishes a 14-day GitHub Actions artifact:

- `PHASE_5BG_OWNER_UNMATCHED_OSM_NAME_CANDIDATES.csv`
- `PHASE_5BG_OWNER_UNMATCHED_OSM_NAME_CANDIDATES_REPORT.json`

Workflow: `Phase 5BG Owner Unmatched OSM Name Candidates`. It runs after a successful Phase 5AI inventory, on relevant pushes to main, or manually with a retained successful Phase 5AI run ID.

## Interpretation and safeguards

- Exact OSM name equality is a candidate reference only. It does not prove the OSM object is the intended physical boarding stop or that the route serves it.
- The output intentionally omits OSM coordinates and geometry; the OSM object ID and tags are retained for manual inspection.
- No coordinate is copied, no route or stop is assigned, and no status is promoted.
- All output rows remain `physical_stop_verification=unverified`, `coordinate_assignment=not_assigned` and `route_assignment=not_assigned`.
- Composite labels, spelling variants and transliterations remain unmatched unless they have exact normalized equality; no fuzzy matching or alias inference is performed.

This phase reduces the manual research queue only by surfacing exact OSM-name candidates. It does not close any physical-stop verification gate.
