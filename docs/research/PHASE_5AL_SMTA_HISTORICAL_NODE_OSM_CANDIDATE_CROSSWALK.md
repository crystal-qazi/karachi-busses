# Phase 5AL — SMTA to Historical Node and OSM Candidate Crosswalk

## Purpose

Join the operator-published named entries in Phase 5AF to the 572-record historical coordinate register, then expose the Phase 5AJ OSM transit-feature proximity candidates for each matched historical node.

This is a candidate review register. It does not approve stops or route geometry.

## Matching method

1. Exclude Phase 5AF direction descriptors.
2. Match the official named entry to a historical node ID using normalized exact text.
3. If no exact historical-node name exists, apply only a Phase 5Y alias marked `confirmed_by_user`, and only for the route codes listed in that alias row.
4. Join matched historical node IDs to the Phase 5AJ audit.
5. Preserve each of the three nearest OSM candidates recorded within 250m. Preserve the total nearby count; if more than three candidates exist, flag that the candidate list is truncated.
6. If no OSM candidate exists within 250m, retain the nearest feature only as `nearest_outside_250m_context_only`. It is not treated as a proximity candidate.
7. Keep unmatched official entries in the output.

## Output

GitHub Actions artifact: `phase-5al-smta-historical-node-osm-candidate-crosswalk`.

- `PHASE_5AL_SMTA_HISTORICAL_NODE_OSM_CANDIDATE_CROSSWALK.csv`
- `PHASE_5AL_SMTA_HISTORICAL_NODE_OSM_CANDIDATE_CROSSWALK_REPORT.json`

The workflow consumes the Phase 5AI artifact containing the Phase 5AJ audit. It does not download or parse the Pakistan PBF again.

## Interpretation limits

- Historical coordinates are references from the earlier dataset, not verified passenger boarding points.
- An OSM feature within 250m is a spatial candidate only. Proximity does not prove physical stop identity, route membership, current service, boarding side, or direction.
- Historical route labels are retained as source metadata, not treated as current SMTA route assignments.
- The audit lists up to three nearest candidates per historical node. The total count is preserved and rows are flagged if more than three exist.
- No fuzzy matching, geocoding, snapping, coordinate approval, route assignment, database writes, or route geometry generation is performed.
- Every row remains `physical_stop_verification=unverified`, `coordinate_assignment=not_assigned`, and `route_assignment=not_assigned`.

## Sources and licensing

The official route sequence names are sourced from the SMTA route detail pages recorded in Phase 5AF. Historical coordinate references come from `PHASE_5_NODE_AUDIT.csv`. OSM candidates are from the Phase 5AJ audit derived from the Geofabrik Pakistan OSM extract and Karachi Division relation 6080948. Attribution: © OpenStreetMap contributors. License: ODbL 1.0.
