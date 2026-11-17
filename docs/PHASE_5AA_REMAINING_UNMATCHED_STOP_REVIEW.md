# Phase 5AA — Remaining Unmatched Stop Name Review

## Purpose

Create a smaller, conservative name-review queue after removing only the exact 20 route-stop occurrences backed by the user's 13 Phase 5Y confirmed name aliases.

## Method

1. Rebuild the Phase 5W name-only candidate file from the original 191-row route-stop crosswalk and the historical 572-node name inventory.
2. Join Phase 5X shortlist entries to Phase 5Y user-confirmed aliases.
3. Exclude only those exact confirmed route/sequence occurrences from the unmatched queue.
4. Preserve the remaining Phase 5W top-three name candidates and similarity scores as triage hints.

No candidate coordinates are copied. Similarity scores are not treated as proof.

## Expected counts from current source data

- Original unmatched route-stop rows: 102
- User-confirmed alias occurrences excluded: 20
- Remaining unmatched name-review rows: 82

The workflow recomputes and reports these counts from the current source files rather than hard-coding them.

## Outputs

- \`data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES.csv\`
- \`data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES_REPORT.json\`

The GitHub Actions workflow publishes both in a review-only artifact.

## Safety

Every remaining row is explicitly marked:

- \`physical_stop_verification = unverified\`
- \`coordinate_assignment = not_assigned\`
- \`route_approval_status = not_approved\`

This phase does not alter the original crosswalk, assign coordinates, geocode, snap, infer route geometry, or write to the production database. OSM remains the primary geographic reference; road proximity does not verify a passenger stop.
