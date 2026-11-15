# Mobile API contract

**Status:** Proposed contract only. These routes are not implemented or available yet.

Base path remains `/api/v1`. Preserve all existing PWA endpoints and their current success/error envelope:

- Success: `{"success": true, "data": {...}}`
- Error: `{"success": false, "error": {"code": "...", "message": "..."}}`

Existing endpoints remain unchanged: health, nearby discovery, direction detail, search and journey discovery. Mobile endpoints must follow the same envelope and publication visibility rules.

## Proposed endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/mobile/manifest` | Current content-addressed published dataset version and schema metadata (implemented) |
| GET | `/mobile/snapshot` | Complete passenger-visible dataset snapshot (implemented) |
| GET | `/mobile/changes?since={version}` | Ordered changes after a local version |
| GET | `/mobile/routes` | Paginated published routes, if needed for targeted refresh |
| GET | `/mobile/stops` | Paginated published stops, if needed for targeted refresh |
| GET | `/mobile/directions/{id}` | Published direction, ordered stops and shape |
| GET | `/mobile/maps/manifest` | Available offline map packages and versions |
| GET | `/mobile/maps/{package_id}` | Download metadata/authorized package location |

The implemented first iteration uses `/mobile/manifest` and `/mobile/snapshot` with a SHA-256 content-addressed version and ETag. It intentionally downloads a full snapshot when the content changes. Incremental `/mobile/changes` is not implemented until a durable change log and tombstones are atomically integrated with all admin publication mutations. Targeted list/detail endpoints remain future options and should not create a second inconsistent synchronization model.

## Manifest response

```json
{
  "success": true,
  "data": {
    "dataset_version": 104,
    "schema_version": 1,
    "generated_at": "2026-11-15T12:00:00Z",
    "minimum_supported_client": 1,
    "snapshot_checksum": "sha256:...",
    "changes_available_since": 80
  }
}
```

Values above are illustrative, not current repository data.

## Incremental changes response

```json
{
  "success": true,
  "data": {
    "from_version": 100,
    "to_version": 104,
    "schema_version": 1,
    "checksum": "sha256:...",
    "changes": {
      "routes": {"upsert": [], "delete": []},
      "directions": {"upsert": [], "delete": []},
      "stops": {"upsert": [], "delete": []},
      "direction_stops": {"upsert": [], "delete": []},
      "shapes": {"upsert": [], "delete": []}
    }
  }
}
```

A client with local version 100 must receive a complete, gap-free set of changes through version 104 or a response instructing it to fetch a full snapshot. Deletes are tombstones by stable server ID. The backend must include dependent relationship removals.

## Snapshot response

The snapshot must be a consistent view of the passenger-visible dataset at one dataset version. Include dataset version, schema version, generation timestamp, checksum and all required entities/relationships. Paginate or stream large payloads without allowing the client to combine pages from different dataset versions. Prefer compressed responses (gzip or Brotli where supported) and document the canonical checksum input.

## HTTP and error behaviour

- `200`: successful manifest/snapshot/change response.
- `304`: optional conditional response when ETag matches.
- `400`: invalid version/query parameters.
- `409`: client version cannot be incrementally reconciled; fetch snapshot.
- `410`: requested change history has expired; fetch snapshot.
- `429`: rate limited; client backs off and respects `Retry-After`.
- `5xx`: transient server error; retain local data and retry later.

Use ETag/If-None-Match for cache validation where appropriate. All production traffic must use HTTPS. Public endpoints are read-only; do not expose admin mutation APIs to the passenger app.

## Backend implementation requirements

Before coding these endpoints, inspect the real migrations, model/query layer and existing API serializers. Reuse current route/direction/stop relationships rather than creating parallel transport tables. Add a durable published-dataset version and change log with tombstones. Ensure version advancement and change-log writes occur in the same database transaction as publication changes.

The mobile API must:
- include only passenger-visible, active, verified and published records;
- preserve stable IDs and stop sequence ordering;
- include all direction shapes needed for offline map overlays;
- return consistent snapshot/change versions;
- support full snapshot fallback;
- validate query parameters and cap response sizes;
- have tests for publish, edit, unpublish, delete, missing change history, version gaps and checksum mismatch.

## Offline maps

Map package manifests should identify package ID, region/bounds, version, format, byte size, checksum, attribution and provider/license metadata. A route-data version change does not automatically change the map package version. Never promise a downloadable full Karachi map until the tile source, licensing, storage footprint and hosting are verified.
