# Phase 5AB — Exact Coordinate Collision Review

## Purpose

Create a review queue for historical node records that share exactly the same latitude/longitude. The audit is diagnostic: identical coordinates can be duplicate data, generalized area points, or distinct named places represented by one historical coordinate. The data alone cannot decide which.

## Current source result

The current 572-node audit contains:

- 572 node records
- 10 exact duplicate-coordinate clusters
- 24 node records within those clusters
- 548 node records outside duplicate clusters

The workflow recomputes these values from \`PHASE_5_NODE_AUDIT.csv\`.

## Output

- \`data/research/PHASE_5AB_COORDINATE_COLLISION_REVIEW.csv\`
- \`data/research/PHASE_5AB_COORDINATE_COLLISION_REVIEW_REPORT.json\`

Each collision row preserves the source node name, coordinate, and historical route labels. It also reports route labels shared by every node in a cluster and the union of labels across the cluster.

## Safety

- No node is automatically merged, renamed, preferred, or moved.
- Shared route labels do not prove a common physical stop.
- Coordinates are not assigned to SMTA stops.
- No physical stop is verified and no route is approved.
- No geocoding, snapping, route inference, geometry generation, or database write is performed.

This phase uses only Python's standard library and requires no local executable installation.
