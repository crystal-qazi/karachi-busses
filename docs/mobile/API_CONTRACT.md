# Mobile API contract

Base path remains `/api/v1`. Preserve all existing PWA endpoints and their current success/error envelope:

- Success: `{"success": true, "data": {...}}`
- Error: `{"success": false, "error": {"code": "...", "message": "..."}}`

Existing endpoints remain unchanged: health, nearby discovery, direction detail, search and journey discovery. Mobile endpoints must follow the same envelope and publication visibility rules.

## Transport endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/mobile/manifest` | Current content-addressed published dataset version and schema metadata (implemented) |
| GET | `/mobile/snapshot` | Complete passenger-visible dataset snapshot (implemented) |
| GET | `/mobile/changes?since={version}` | Ordered changes after a local version |
| GET | `/mobile/routes` | Paginated published routes, if needed for targeted refresh |
| GET | `/mobile/stops` | Paginated published stops, if needed for targeted refresh |
| GET | `/mobile/directions/{id}` | Published direction, ordered stops and shape |

The first iteration uses `/mobile/manifest` and `/mobile/snapshot` with a SHA-256 content-addressed version and ETag. It intentionally downloads a full snapshot when content changes. Incremental `/mobile/changes` is not implemented until a durable change log and tombstones are atomically integrated with all admin publication mutations.

## Map package endpoints (approved contract; implementation pending)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/mobile/maps/manifest` | Catalogue of approved Karachi-wide and area-level packages |
| GET | `/mobile/maps/{package_id}` | Metadata for one package and an authorized download location |

The manifest returns package summaries only. Package detail returns:
- `package_id`, `name`, `kind` (`karachi_full` or `area`), stable area slug where applicable;
- geographic bounds (WGS84), display zoom range and map-style compatibility;
- `version`, `format`, `size_bytes`, `checksum_sha256`;
- `attribution`, `source_name`, `licence_name`, `licence_url`, and explicit offline-download permission;
- download URI issued by the backend/provider integration, expiry where signed, and minimum supported app version.

The backend must never accept an arbitrary URL supplied by the Android client. Only packages with verified source/licence metadata and a published status appear. A package is independent of the transport dataset version. The client validates byte count and SHA-256 before installation. A replacement is staged and activated atomically; the previous working package remains active if download or validation fails.

## Illustrative map manifest shape
This is a contract example, not a live response:

```json
{
  "success": true,
  "data": {
    "packages": [
      {
        "package_id": "karachi-full",
        "name": "Karachi",
        "kind": "karachi_full",
        "version": "2026-11-01",
        "bounds": [66.6, 24.7, 67.5, 25.5],
        "format": "provider-defined",
        "size_bytes": 0,
        "checksum_sha256": "hex-digest",
        "attribution": "Map data attribution supplied by provider",
        "source_name": "approved-provider",
        "licence_name": "provider licence",
        "licence_url": "https://provider.example/licence",
        "offline_download_allowed": true
      }
    ]
  }
}
```

Bounds and size above are placeholders for schema illustration only, not approved Karachi package extents or estimates.

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

## Provider, licensing and tile-source rules
- MapLibre is the client renderer; it is not a tile-hosting service or a grant of offline rights.
- Do not bulk download or prefetch from `tile.openstreetmap.org` or the public OSM vector tile service.
- Online fallback and offline package delivery must use a provider whose terms explicitly allow the intended use, or infrastructure operated by the project.
- Preserve required attribution and licence notices in map UI and package metadata.
- Do not select a provider, publish package sizes or promise city-wide zoom coverage until licensing, real tile generation, hosting and device storage tests are complete.

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
