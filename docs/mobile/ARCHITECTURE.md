# Native Android application architecture

**Status:** Approved architecture; implementation not started.

## Product decisions

- Android only, built as a fully native application. Do not wrap the PWA in a WebView or Capacitor.
- Full offline use for transport data and a downloadable Karachi-wide map.
- Keep the existing Flask + MySQL backend and browser PWA/admin application.
- MySQL remains the authoritative source. Android Room is a local read-optimized replica.
- Only active, verified and published transport data is distributed to passengers.
- No live vehicle tracking, ETAs, fares or timetables are introduced by this work.

## Technology choices

| Concern | Choice |
|---|---|
| Language | Kotlin |
| UI | Jetpack Compose + Navigation Compose |
| Local persistence | Room / SQLite |
| Networking | Retrofit + OkHttp |
| Async work | Coroutines + Flow |
| Background sync | WorkManager |
| Dependency injection | Hilt |
| Preferences | DataStore |
| Native maps | MapLibre Native |
| Location | Android location APIs / fused provider where available |
| Push signal | Firebase Cloud Messaging (optional; never the sole sync mechanism) |

Pin compatible stable dependency versions together when the Android Gradle project is introduced. Keep versions centralized in a Gradle version catalog.

## Repository boundary

The Android client lives in `android/`; mobile/backend contracts live in `docs/mobile/`. Do not move or rewrite the existing Flask/PWA directories as part of Android work.

Suggested Android modules (introduce incrementally, not as empty modules up front):

- `app`: application composition, navigation and app entry point.
- `core:common`: shared result/error types and dispatchers.
- `core:database`: Room database, entities, DAOs and migrations.
- `core:network`: Retrofit service definitions and serialization.
- `core:location`: location permission and location acquisition.
- `core:maps`: MapLibre integration and offline map packages.
- `core:sync`: sync orchestration, version/checksum validation and WorkManager.
- `domain`: domain models, repository contracts and use cases.
- `feature:* `: home, search, routes, stops, journeys, downloads and favourites.

Start with a single Gradle app module if that keeps Phase 1 simpler; split modules when there is real code to isolate.

## Data flow

1. Admin creates or edits transport records in the existing Flask admin.
2. Existing review and publication rules determine whether records are passenger-visible.
3. A publication transaction records a durable dataset change event and advances the mobile dataset version.
4. Android checks the manifest, downloads either a full snapshot or incremental change batch, validates it, and applies it to Room in one transaction.
5. The UI reads from Room. Network availability is not required to browse previously synchronized transport data.
6. FCM may wake/signal the app that a newer version exists. WorkManager and app-launch/manual sync remain the recovery paths.

The backend must never publish draft, unverified, inactive or unpublished data to mobile endpoints.

## Offline product behaviour

- Route and stop search queries Room.
- Nearby-stop search uses the device location and local stop coordinates. The passenger's location is not uploaded for this operation.
- Manual-origin nearby search and journey planning operate on local data.
- Route detail includes ordered stops and downloaded geometry.
- Direct and one-transfer journey discovery runs locally and must match the backend's documented rules.
- Favourites and saved journeys are stored locally.
- Map tiles/regions are managed separately from transport records. A successful route-data sync does not imply the map package is current.
- Show last successful transport sync, local dataset version, map package version and offline/online status.

## Local data model (logical)

Implement Room entities after mapping the actual MySQL schema and current API serializers. Do not assume the following logical names are existing backend table names.

- Route: stable server ID, route code/name/description, publication state and updated version.
- Direction: stable ID, parent route ID, display name and ordering.
- Stop: stable ID, name/address and WGS84 latitude/longitude.
- DirectionStop: direction ID, stop ID and sequence.
- RouteShape: direction ID and GeoJSON LineString (or a documented compact representation).
- Favourite: entity type + server entity ID.
- SavedJourney: origin/destination metadata and a versioned journey representation.
- SyncState: dataset version, schema version, checksum, last successful sync and status.
- MapPackage: region ID, package version, bounds, size and download state.

Use foreign keys, unique constraints and indexes for route codes, stop names where appropriate, coordinates, direction/sequence and all relationship IDs. Preserve server IDs across sync. Avoid storing passenger location history.

## Security, privacy and resilience

- Do not embed backend secrets or privileged admin credentials in the APK.
- Public mobile endpoints are read-only and return published data only.
- Use HTTPS in production. Keep development and production base URLs separate.
- Validate payload schema, dataset version and checksum before applying changes.
- Apply each batch and its version advancement atomically. A failed batch must leave the previous local dataset usable.
- Use tombstones for removals/unpublishing so deleted or hidden records are removed from offline clients.
- Do not rely on client timestamps as the only change-tracking mechanism.
- Do not collect or transmit passenger GPS coordinates for local nearby discovery.
- Add explicit retention, attribution and provider-policy checks for offline map packages.

## Non-goals

No live bus locations, ETA prediction, fare calculation, timetable data, arbitrary-address geocoding, user accounts, passenger tracking or automatic route inference are included in this foundation.
