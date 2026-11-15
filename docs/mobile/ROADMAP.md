# Native Android implementation roadmap

**Status:** Planning baseline. Work should proceed in small reviewable pull requests.

## Phase 0 — Architecture and contract (this change)

- [x] Confirm Android-native Kotlin application, not a WebView wrapper.
- [x] Confirm Room offline-first data storage.
- [x] Confirm MapLibre Native for offline maps.
- [x] Define versioned incremental sync, snapshot fallback and tombstones.
- [x] Define published/verified data visibility.
- [x] Separate transport dataset sync from map package updates.
- [ ] Validate the contract against all current backend migrations and serializers before implementation.

## Phase 1 — Android foundation

- [ ] Create Android Studio/Gradle project under `android/`.
- [ ] Configure Kotlin, Compose, Navigation Compose and centralized dependency versions.
- [ ] Configure development and production API base URLs without embedding secrets.
- [ ] Add Hilt, Retrofit/OkHttp, Room and DataStore.
- [ ] Add a minimal launch screen, theme and navigation.
- [ ] Add Android CI build and unit-test workflow.
- [ ] Document Windows Android Studio/JDK/SDK setup.

**Acceptance:** Debug build compiles in CI, installs and launches on a supported Android device, navigation works, environment URLs are separated and an empty Room database opens.

## Phase 2 — Backend mobile data contract

- [ ] Inspect current MySQL migrations, relationships, serializers and publication checks.
- [ ] Design dataset version and durable change-log/tombstone schema.
- [ ] Implement manifest and consistent full snapshot endpoints.
- [ ] Implement incremental changes endpoint and snapshot fallback.
- [ ] Add checksum, schema version, pagination/compression and ETag support.
- [ ] Add API tests for publish/update/unpublish/delete and version continuity.
- [ ] Verify existing PWA endpoints and admin publication workflow remain unchanged.

**Acceptance:** A test client can bootstrap, apply multiple change batches, detect a version gap and recover through a snapshot; unverified/unpublished data never appears.

## Phase 3 — Room and synchronization

- [ ] Map backend IDs and relationships into Room entities.
- [ ] Add DAOs, indexes, foreign keys and database migrations.
- [ ] Implement snapshot import in a transaction.
- [ ] Implement incremental upserts and tombstones in a transaction.
- [ ] Validate checksums and advance version atomically.
- [ ] Add WorkManager launch/periodic/connectivity-aware sync and backoff.
- [ ] Add manual sync and freshness/error state.
- [ ] Test interrupted downloads, retries, duplicates and rollback.

**Acceptance:** The app retains a usable old dataset through failed updates and reaches the same published version after successful sync.

## Phase 4 — Native passenger features

- [ ] Route and stop search against Room.
- [ ] Nearby stops using device location locally.
- [ ] Manual origin selection.
- [ ] Route detail, direction, ordered stops and geometry.
- [ ] Offline direct and one-transfer journey discovery.
- [ ] Favourites and saved journeys.
- [ ] Compare local journey results with backend rules using shared fixtures.

**Acceptance:** All listed discovery features work with network disabled after initial data sync.

## Phase 5 — Offline maps

- [ ] Integrate MapLibre Native.
- [ ] Choose a tile provider/self-hosted source and verify offline download rights.
- [ ] Define Karachi-wide package bounds, zoom levels, attribution and storage estimate.
- [ ] Implement map package manifest, download, checksum, install and update.
- [ ] Preserve the previous package until replacement succeeds.
- [ ] Overlay locally stored stops and route shapes.
- [ ] Add storage management and Wi-Fi/metered-network preferences.

**Acceptance:** A test device can download the approved Karachi region, restart in airplane mode and render the map and transport overlays. Full coverage is not claimed before a successful size/licensing/device test.

## Phase 6 — Polish, localization and accessibility

- [ ] English and Urdu UI, including RTL layout.
- [ ] Permission rationale and denied-permission fallback.
- [ ] Accessible controls, font scaling and contrast.
- [ ] Share route/stop/journey links or text.
- [ ] Settings, data usage and map storage information.

## Phase 7 — Quality and release

- [ ] Unit, repository, API contract and Room migration tests.
- [ ] Offline/airplane-mode end-to-end tests.
- [ ] Low-memory, low-storage, battery and GPS testing.
- [ ] Test supported Android versions and representative devices.
- [ ] Production HTTPS/API/map hosting, privacy policy and support contact.
- [ ] Signing, release AAB, store listing and staged rollout.

## Scope guardrails

No live tracking, ETAs, fares, timetables, arbitrary geocoding or passenger location history. Do not bundle unverified route data. Do not change existing PWA behaviour to accommodate the Android client.
