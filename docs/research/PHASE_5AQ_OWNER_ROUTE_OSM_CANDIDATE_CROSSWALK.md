# Phase 5AQ — Owner-reviewed route to OSM candidate context crosswalk

**Date:** 19 November 2026  
**Purpose:** Add geographic review context to the existing owner-reviewed route-to-historical-node candidate crosswalk without promoting any stop.

## Inputs

- `data/research/owner_route_node_candidate_crosswalk.csv`: 270 entries across 16 owner-reviewed forward sequences.
- Phase 5AI/5AJ GitHub Actions artifact: `PHASE_5AJ_HISTORICAL_NODE_OSM_STOP_CANDIDATE_AUDIT.csv`, containing the 572-node proximity audit against the Karachi OSM transit-feature inventory.

## Join policy

Only two existing match statuses are joined to the OSM proximity audit:

- `exact_normalized_name`: show the OSM features within 250 metres of the historical candidate coordinate.
- `coordinate_review_required`: show the same proximity context as a diagnostic aid, while preserving the existing coordinate-review warning.

The following statuses are deliberately not joined, even if a node identifier appears in a name-only alias row:

- `user_confirmed_name_alias`: the owner-confirmed alias is name-only and its coordinate assignment remains explicitly unassigned.
- `ambiguous_name_variant`: no candidate is selected.
- `unmatched`: no historical node is selected.

For a joinable row with no OSM feature inside 250 metres, the nearest feature is shown only as `nearest_outside_250m_context_only`. It is not a proximity match. Up to three nearest OSM candidates are emitted per historical node; the full nearby count and truncation flag are preserved.

## Outputs

The workflow publishes the following 14-day GitHub Actions artifact:

- `PHASE_5AQ_OWNER_ROUTE_OSM_CANDIDATE_CROSSWALK.csv`
- `PHASE_5AQ_OWNER_ROUTE_OSM_CANDIDATE_CROSSWALK_REPORT.json`

Workflow: `Phase 5AQ Owner Route OSM Candidate Crosswalk`. It runs after a successful Phase 5AI inventory, on relevant pushes to main, or manually with a retained successful Phase 5AI run ID.

## Interpretation and safeguards

- OSM is the primary geographic reference, but community-mapped bus stops/platforms are not operator-verified boarding points.
- Historical coordinates are secondary research references and may be wrong, stale, offset, or on the wrong side of a road.
- A 250-metre proximity candidate does not prove physical stop identity, route membership, direction, current service, accessibility or boarding side.
- The crosswalk does not infer coordinates for name-only aliases, resolve ambiguous labels, snap to roads, generate route geometry, write to MySQL, change verification states, activate routes or alter public API eligibility.
- All output rows must remain `physical_stop_verification=unverified`, `coordinate_assignment=not_assigned` and `route_assignment=not_assigned`.

This is a review aid only. Field/operator evidence and owner approval remain necessary before any coordinate or route assignment is promoted.
