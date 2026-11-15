# Native Android implementation status

Updated: 2026-11-15

## Implemented in this branch
- Native Android Gradle application shell using Kotlin and Jetpack Compose.
- Room entities/DAO for published routes, directions, stops, direction-stop ordering, shapes and sync metadata.
- Retrofit snapshot API client and transactional full-snapshot replacement.
- Basic route list/search UI and manual sync action.
- Flask read-only mobile manifest and full snapshot endpoints.
- Content-addressed dataset version/checksum and ETag.
- Android CI workflow and setup instructions.
- Migration placeholder for mobile dataset schema metadata.

## Deliberate limitations
- The API currently uses full snapshots. It does not claim incremental synchronization, because existing admin publication changes are not yet recorded in a durable change log with deletion tombstones.
- WorkManager background scheduling is not wired yet.
- The map SDK and offline tile packages are not integrated. A lawful tile provider, Karachi package sizing and device testing must be selected first.
- Local nearby search, local direct/one-transfer journey planning, favourites, saved journeys, Urdu/RTL and map overlays remain to implement.
- The current backend dataset is only as complete as the reviewed records entered by operators. No comprehensive Karachi route dataset is bundled.

## Required verification before merge
- Run backend pytest with a MySQL test database or configured integration fixtures.
- Run `gradle assembleDebug testDebugUnitTest` under JDK 17 and Android SDK 35.
- Apply migration 004 in a disposable development database and test both mobile endpoints against published, unverified, inactive and empty records.
- Validate snapshot consistency under concurrent publication changes.
- Replace the release API placeholder before producing a release artifact.
