# Native Android implementation status

Updated: 2026-11-15

## Confirmed architecture decisions
- Native Android client: Kotlin + Jetpack Compose; no WebView wrapper.
- Offline-first transport data stored in Room. Flask/MySQL remains authoritative.
- Map rendering target: MapLibre Native.
- Map strategy: **hybrid**. Bus data and journey planning remain offline-first; map downloads are optional.
- Map coverage: both a Karachi-wide package and independently downloadable neighbourhood/area packages.
- Map packages are versioned and managed separately from the transport dataset. Updating routes does not silently trigger a large map download.
- Online tiles may be used for areas without a local package, subject to the selected provider's online-use terms. Offline downloads require explicit provider permission or self-hosting.
- The public OpenStreetMap tile endpoint is not an offline/bulk-download source.

## Implemented in this branch
- Native Android Gradle application shell using Kotlin and Jetpack Compose.
- Room entities/DAO for published routes, directions, stops, direction-stop ordering, shapes and sync metadata.
- Retrofit snapshot API client and transactional full-snapshot replacement.
- Basic route list/search UI and manual sync action.
- Flask read-only mobile manifest and full snapshot endpoints.
- Content-addressed dataset version/checksum and ETag.
- Android CI workflow and setup instructions.
- Local map-package catalogue entity/DAO and Room 1→2 migration for independently managed city/area packages.
- Official MapLibre Native Android SDK integration, map screen navigation and bounded visible-neighbourhood offline download with progress and Room status persistence.

## Map architecture (approved; implementation pending)
- Separate map-package catalogue from bus-data manifest and synchronization.
- Package types: `karachi_full` and `area`; area packages have stable IDs/slugs and explicit bounds.
- Each package manifest must include package ID, display name, coverage bounds, version, format, byte size, checksum, attribution, provider/source and licence metadata, minimum app/map-style compatibility, and download URI.
- Download flow: inspect package metadata and storage requirement → user confirms Wi-Fi/mobile-data preference → download to a temporary location → verify byte count and SHA-256 → install atomically → retain previous valid package until replacement succeeds.
- A failed, interrupted or corrupt download must never replace the last working package.
- Users can pause/resume, retry, update and remove individual packages; show installed/downloaded size and last-updated time.
- Render local stop and route-shape overlays from Room over whichever basemap is active.
- Online fallback is permitted only where the chosen provider permits it; otherwise show an explicit no-basemap/offline-area state while preserving transport search and journey features.
- No city-wide size estimate or provider is approved yet. Select the provider/self-hosting model only after licensing, coverage, style, storage and operating-cost review.

## Deliberate limitations
- The API currently uses full snapshots. It does not claim incremental synchronization, because existing admin publication changes are not yet recorded in a durable change log with deletion tombstones.
- The native MapLibre renderer and OfflineManager visible-neighbourhood download flow are implemented behind explicit provider configuration and offline-rights flags. A provider/style has not been selected or configured, so the feature is not active in a stock build.
- Full-Karachi package generation, city boundary approval and large-package delivery remain pending.
- Runtime GPS permission/current-location flow, favourites, saved journeys, Urdu/RTL and map overlays remain to implement.
- The current backend dataset is only as complete as the reviewed records entered by operators. No comprehensive Karachi route dataset is bundled.

## Required verification before merge
- Run backend pytest with a MySQL test database or configured integration fixtures.
- Run `gradle assembleDebug testDebugUnitTest` under JDK 17 and Android SDK 35.
- Apply migration 004 in a disposable development database and test both mobile endpoints against published, unverified, inactive and empty records.
- Validate snapshot consistency under concurrent publication changes.
- Select and validate a lawful map source, test package download/recovery and measure Karachi-wide and neighbourhood package sizes on representative devices.
- Replace the release API placeholder before producing a release artifact.
