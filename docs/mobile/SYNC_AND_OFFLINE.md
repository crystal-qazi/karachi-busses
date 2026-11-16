# Mobile synchronization and offline strategy

**Status:** Design contract. Endpoints and sync worker are not implemented yet.

## Source of truth

MySQL remains authoritative. The Android Room database is a local replica of the passenger-visible dataset. Admin edits are not mobile-visible until the existing verification and publication workflow approves them.

## Version model

Maintain a monotonically increasing integer `dataset_version` for the published passenger dataset. Advance it only when a passenger-visible change is committed. Draft edits that do not alter published data must not advance this version.

A published change batch must represent a complete, ordered range:

- `from_version`: exclusive starting version.
- `to_version`: inclusive ending version.
- `changes`: upserts and tombstones for routes, directions, stops, direction-stop relationships and shapes.
- `checksum`: checksum of the canonical batch or snapshot bytes.
- `schema_version`: payload contract version.

Use durable change-log records or immutable versioned batches. Do not derive correctness solely from `updated_at` timestamps. Keep tombstones long enough for supported clients to consume them; if a client is too far behind the retained history, require a full snapshot.

## Sync sequence

1. Read local dataset version and schema version from Room.
2. Fetch the mobile manifest.
3. If the local schema is incompatible, the version is unsupported, or the requested change range has expired, download a full snapshot.
4. Otherwise fetch changes since the local version.
5. Validate response shape, version continuity, supported schema and checksum.
6. In one Room transaction, apply all upserts and tombstones and update the local dataset version/checksum.
7. Commit only after every record is applied. On failure, roll back and retain the old version/data.
8. Record last successful sync and expose status to the UI.

A repeated request must be safe. Applying a batch twice must not create duplicate records; stable server IDs and upsert semantics provide idempotency.

## Triggers and retry

- First app launch / onboarding.
- App foreground/resume when a refresh is due.
- User taps **Sync now**.
- WorkManager periodic work under Android's scheduling constraints.
- WorkManager one-time work when network connectivity returns.
- Optional FCM data message indicating that a newer dataset version is available.

FCM is only a hint to check the API; it must not carry the authoritative dataset and must not be required for correctness. Notifications may be delayed, disabled or dropped. WorkManager periodic sync and app-launch checks remain mandatory.

Use exponential backoff for transient failures. Do not spin in a tight retry loop. Respect metered networks and user data-saver settings for large full snapshots and map packages.

## Publication and removal semantics

Only active, verified-source and published data is included. Changes that unpublish, deactivate or delete an entity must generate tombstones for the affected entity and dependent relationships. A route removal must not leave orphaned directions, stop associations or shapes in Room.

The backend should validate publication invariants before adding records to the passenger dataset. A single admin action that changes several related records should produce a coherent batch.

## Transport data vs map data

Transport records and offline map packages have independent manifests and versions.

- Transport sync updates route/stop metadata, sequences and route geometry.
- Map package sync updates vector/raster tiles and style resources for geographic regions.
- A map download must be resumable where the provider/format supports it, integrity-checked, and installed atomically.
- Keep the previously installed map usable until the replacement package is complete and validated.
- Display map package version and storage usage separately from transport dataset freshness.

Use an approved tile source or self-hosted tile service. Do not treat the public OpenStreetMap standard tile endpoint as an unlimited offline bulk-download source. Include required OpenStreetMap attribution and comply with the selected provider's terms.

## Room transaction pseudocode

```kotlin
database.withTransaction {
    changeSet.upserts.forEach(repository::upsert)
    changeSet.tombstones.forEach(repository::deleteAndCascade)
    syncStateDao.updateVersion(
        version = changeSet.toVersion,
        checksum = changeSet.checksum
    )
}
```

The version update must be in the same transaction as the record changes. Do not advance the version before applying the batch.

## User-visible status

Expose:
- Online / offline state.
- Last successful transport sync time.
- Current local dataset version.
- Whether an update is available or sync is in progress.
- A useful error and retry action when sync fails.
- Offline map region, package version and download progress.

When offline, continue showing the last successfully synchronized dataset and clearly label its freshness. Never blank the local database just because a refresh failed.
