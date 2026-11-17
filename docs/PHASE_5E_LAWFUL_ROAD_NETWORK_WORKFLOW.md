# Phase 5E — Lawful Road-Network and Geometry Workflow

**Status:** Design and compliance controls only. No road data has been downloaded, no tile archive created, and no route geometry has been generated or published.

## 1. Purpose

Prepare a reproducible, source-attributed process for converting verified transport stop sequences into road-following route geometry. This phase must not turn historical graph edges or approximate stop coordinates into passenger directions.

## 2. Approved source strategy

### OpenStreetMap road data

Use an openly downloadable regional OSM data extract (for example, Geofabrik Pakistan extract) for offline analysis and routing-engine input. Record:
- Provider and exact download URL
- Download timestamp (UTC)
- Source file name, file size and SHA-256
- OSM data timestamp/replication sequence where supplied
- Licence: Open Database License 1.0 (ODbL)
- Attribution: © OpenStreetMap contributors
- Processing software and version
- Derived output file hashes and lineage

Geofabrik states that its OSM-derived downloads are under ODbL 1.0 and require acknowledgement. OSM-derived databases must retain the applicable share-alike obligations. Review the licence and the database/produced-work distinction before distributing any derived dataset.

### Map tiles are a separate service

Do not bulk-download tiles from `tile.openstreetmap.org`, create MBTiles from that tile service, automate map panning, or offer offline downloads backed by those standard tiles. The standard OSM raster tile service is for normal interactive viewing, requires visible attribution, correct identification and caching, and explicitly prohibits bulk/offline tile fetching.

For offline map packages, choose a provider whose written terms explicitly permit offline downloads, or operate a self-hosted renderer using appropriately licensed source data. Keep the tile provider separate from the OSM road-data extract used for routing.

## 3. Geometry pipeline (not yet executed)

1. Freeze a source snapshot and hash it.
2. Ingest only road-network data from a permitted extract; retain source attribution and licence metadata.
3. Validate candidate stop coordinates and physical boarding side independently. Exclude unresolved stop points from production routing.
4. Resolve route identity and both directional stop sequences from operator evidence.
5. Snap verified stop points to plausible routable road edges using a documented distance threshold and road-access rules. Flag ambiguous snaps for review; never silently move stops.
6. Generate each direction independently using a routing engine configured for bus-appropriate roads and access restrictions. Do not assume pedestrian/car routing equals bus routing.
7. Compare generated geometry against the ordered stops, route evidence, one-way restrictions, access tags, bridges/tunnels and known terminal access.
8. Produce a QA report with off-network stops, excessive detours, U-turns, discontinuities, forbidden-road use and sequence mismatches.
9. Require human review of map previews and evidence before approving a shape.
10. Store provenance, source hash, routing-engine version/configuration, reviewer and approval date with each shape.

## 4. Publication gates

A route direction is not publishable unless all are true:
- Current route identity and service status are supported by acceptable evidence.
- Ordered stop sequence and direction are supported by an operator source or documented field survey.
- Every passenger-facing stop has a verified physical boarding coordinate and side/platform.
- Road geometry follows a valid bus-accessible network and passes QA.
- The geometry's source and licence are recorded.
- Required ODbL attribution/share-alike obligations are met for distributed OSM-derived data.
- Independent reviewer approval is recorded.

## 5. Data model and provenance fields

For every road-network source:
`source_id, provider, source_url, retrieved_at_utc, source_timestamp, sha256, licence, attribution, processing_tool, tool_version, processing_config, output_sha256`.

For every generated direction shape:
`route_id, direction_id, stop_sequence_revision, road_source_id, road_source_sha256, router_name, router_version, router_profile, generated_at_utc, geometry_sha256, qa_status, reviewer, reviewed_at_utc, evidence_refs`.

Do not put credentials, personal contact details, or private operator correspondence in public repository files. Keep confidential correspondence in an appropriately access-controlled location and publish only permitted metadata.

## 6. Current work blockers

- Operator confirmation is still needed for the route identity/direction conflicts tracked in Issue #20.
- The 191-row Phase 5D queue contains 89 historical coordinate candidates and 102 unmatched names; none is a physically verified boarding point.
- Green Line and Orange Line current station registers need authoritative confirmation.
- No approved road extract has yet been acquired and hashed for this project.

## 7. Legal and operational references

- OpenStreetMap copyright/licence: https://www.openstreetmap.org/copyright
- OSM Foundation attribution guidance: https://osmfoundation.org/wiki/Attribution_Guidelines
- Standard raster tile usage policy: https://operations.osmfoundation.org/policies/tiles/
- Vector tile usage policy: https://operations.osmfoundation.org/policies/vector/
- Geofabrik downloads and licence: https://www.geofabrik.de/data/download.html

This document is project guidance, not legal advice. Check the current terms and obtain appropriate advice for the intended distribution model before release.
