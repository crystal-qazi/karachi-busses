# Phase 5AK — SMTA Route to OSM Name Candidate Crosswalk

## Purpose

Compare every operator-published named passenger entry in the Phase 5AF route sequence register with names on the Phase 5AI Karachi OSM bus-stop/platform candidate inventory.

## Matching rules

- Match normalized exact text against OSM `name` and `name:en` fields.
- Apply only Phase 5Y aliases marked `confirmed_by_user`.
- An alias is eligible only on the route codes listed in its alias-register row.
- Preserve every distinct matching OSM object. Multiple matches remain ambiguous candidates.
- Exclude direction descriptors; they are not passenger-stop entries.
- Keep unmatched named entries in the output.

## Output

GitHub Actions artifact: `phase-5ak-smta-route-osm-name-candidate-crosswalk`.

- `PHASE_5AK_SMTA_ROUTE_OSM_NAME_CANDIDATE_CROSSWALK.csv`
- `PHASE_5AK_SMTA_ROUTE_OSM_NAME_CANDIDATE_CROSSWALK_REPORT.json`

The workflow consumes the existing Phase 5AI artifact and does not download or parse the Pakistan PBF again. It runs automatically after a successful Phase 5AI workflow, or can be manually dispatched with a successful Phase 5AI run ID.

## Interpretation limits

Every match is a name-based OSM candidate only. It does not prove a physical passenger stop, current SMTA service, route membership, boarding side, or coordinate correctness. The crosswalk never assigns coordinates or routes, performs no fuzzy/proximity matching, and creates no route geometry. All rows remain `physical_stop_verification=unverified`, `coordinate_assignment=not_assigned`, and `route_assignment=not_assigned`.

## Sources and licensing

The route sequence register cites SMTA route detail pages. The candidate inventory is derived from Geofabrik's Pakistan OSM extract and Karachi Division relation 6080948. Attribution: © OpenStreetMap contributors. License: ODbL 1.0.
