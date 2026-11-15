# Native Android implementation roadmap

**Architecture baseline:** Native Kotlin/Jetpack Compose, Room offline-first transport data, Flask/MySQL source of truth, MapLibre Native map renderer.

## Confirmed map product decision

**Hybrid maps with both Karachi-wide and area-level coverage.**

- Transport data is always stored locally after sync; route search and journey planning do not depend on map tiles.
- Basemap is online by default where an approved provider is configured.
- Users may optionally download one Karachi-wide map package or smaller area/neighbourhood packages, independently.
- A downloaded package works without connectivity; areas without a package use the approved online source when connected.
- Map package versioning, download state, checksums, storage and update lifecycle are independent of the bus dataset version.
- No bulk/prefetch from the public OpenStreetMap tile servers. Offline packages must come from a provider whose terms explicitly permit it or from our own tile infrastructure.

## Phase 0 — Architecture and contract
- [x] Confirm Android-native Kotlin application, not a WebView wrapper.
- [x] Confirm Room offline-first data storage.
- [x] Confirm MapLibre Native as map-rendering target.
- [x] Confirm hybrid online/offline map strategy.
- [x] Confirm both full Karachi and individual area download coverage.
- [x] Separate transport dataset sync from map package updates.
- [x] Define map package metadata, integrity checks and atomic install lifecycle.
- [ ] Select lawful tile provider or self-hosted pipeline after licence, storage, hosting and cost review.
- [ ] Add durable transport change log and atomic publication-event integration before incremental sync.

## Phase 1 — Android foundation
- [x] Create Android Studio/Gradle project under `android/`.
- [x] Configure initial Compose application shell and Room schema.
- [x] Add basic route search and local direct/one-transfer journey planner.
- [x] Add manual full-snapshot sync and periodic WorkManager sync.
- [ ] Configure Kotlin, Compose, Navigation Compose and centralized dependency versions.
- [ ] Configure development and production API base URLs without embedding secrets.
- [ ] Add Hilt, Retrofit/OkHttp, Room and DataStore.
- [ ] Add a minimal launch screen, theme and navigation.
- [ ] Stabilize Android CI unit tests and add Room/map-package tests.
- [ ] Document Windows Android Studio/JDK/SDK setup.

## Phase 2 — Backend mobile data contract
- [ ] Inspect current MySQL migrations, relationships, serializers and publication checks.
- [ ] Design dataset version and durable change-log/tombstone schema.
- [x] Implement content-addressed manifest and consistent full snapshot endpoints.
- [ ] Implement durable incremental change feed, tombstones and publication transaction hooks.
- [ ] Implement incremental changes endpoint and snapshot fallback.
- [ ] Add map package catalogue and read-only map package manifest endpoint.
- [ ] Add package metadata validation and authorized download URL delivery (no arbitrary client-supplied URLs).
- [ ] Add API tests for publish/update/unpublish/delete and map manifest visibility.
- [ ] Verify existing PWA endpoints and admin publication workflow remain unchanged.

## Phase 3 — Room and synchronization
- [x] Map core backend IDs and relationships into initial Room entities.
- [ ] Add migration coverage, favourites and persisted saved journeys.
- [ ] Implement incremental upserts and tombstones in a transaction.
- [ ] Validate checksums and advance transport version atomically.
- [ ] Add WorkManager launch/periodic/connectivity-aware sync and backoff.
- [ ] Add manual sync and freshness/error state.
- [ ] Test interrupted downloads, retries, duplicates and rollback.
- [x] Add local Room map-package registry: package ID, version, bounds, size, checksum, attribution, state and installed path.
- [x] Add Room 1→2 migration and DAO operations for package catalogue state.
- [ ] Keep old installed package active until a verified replacement is committed.
- [ ] Add reliable storage preflight, retry/recovery, metered-network/Wi-Fi-only settings and download scheduling.

## Phase 4 — Native passenger features
- [ ] Route and stop search against Room.
- [ ] Nearby stops using device location locally.
- [ ] Manual origin selection.
- [ ] Route detail, direction, ordered stops and geometry.
- [ ] Offline direct and one-transfer journey discovery.
- [ ] Favourites and saved journeys.
- [ ] Compare local journey results with backend rules using shared fixtures.

## Phase 5 — Hybrid MapLibre maps
- [x] Integrate MapLibre Native Android and configurable style/source.
- [x] Add bounded visible-neighbourhood downloads through MapLibre OfflineManager with progress and local package state.
- [x] Select the project-controlled OpenMapTiles + TileServer GL self-hosting direction; deployment and licence validation remain pending.
- [ ] Define and validate a Karachi-wide administrative boundary and catalogue of neighbourhood/area polygons.
- [x] Document city-wide aggregate-download design using bounded area packages rather than one huge native region.
- [ ] Estimate package size for supported zoom ranges from real generated tiles; do not publish speculative size claims.
- [ ] Implement map catalogue and package manifest API.
- [ ] Complete download lifecycle: robust retry/recovery, storage preflight, package integrity/version validation, update/atomic replacement and backend catalogue integration.
- [x] Implement visible-neighbourhood OfflineManager download with progress, pause/resume and remove controls.
- [ ] Render local stops and route shapes above the basemap.
- [ ] Use approved online tiles for undownloaded areas, with attribution and provider-compliant caching.
- [ ] Show offline map coverage clearly and preserve non-map transport features if basemap unavailable.

**Acceptance:** Test device downloads both a complete Karachi package and a selected area package, restarts in airplane mode, and renders the installed region with transport overlays. An undownloaded region uses online fallback when connected and displays a clear unavailable state offline.

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
