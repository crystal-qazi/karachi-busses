# Karachi Buses Android

Native Android client foundation. This app is Kotlin + Jetpack Compose; it is not a WebView wrapper.

## Requirements
- Android Studio with Android SDK 35
- JDK 17
- Gradle wrapper generated/opened by Android Studio

## Open and run (Windows)
1. Open the `android/` directory in Android Studio.
2. Install Android SDK Platform 35 and an Android 26+ emulator/device.
3. Wait for Gradle sync, then run the `app` debug configuration.
4. The debug API URL targets `http://10.0.2.2:5000/api/v1/` for the Android emulator and a Flask server running on the host machine. For a physical device, use your development PC's LAN IP and a network-reachable Flask server.
5. Release API URL is deliberately a placeholder. Configure the real HTTPS production API URL before release.

## Configure a map source

The app uses the official MapLibre Native Android SDK. It does not silently select a public tile server or enable offline downloads without permission.

Add these properties to your user-level Gradle properties file (`%USERPROFILE%\\.gradle\\gradle.properties` on Windows, or `~/.gradle/gradle.properties` on Linux/macOS). This keeps provider configuration out of the repository:
```properties
MAP_STYLE_URL=https://your-approved-provider.example/style.json
MAP_ATTRIBUTION=© OpenStreetMap contributors
MAP_SOURCE_NAME=Your approved tile provider
MAP_LICENSE_NAME=Your provider licence
MAP_LICENSE_URL=https://your-approved-provider.example/terms
MAP_OFFLINE_ALLOWED=true
```
Only set `MAP_OFFLINE_ALLOWED=true` after checking that your provider contract explicitly allows app-level offline downloads. Use a project-controlled/self-hosted style and tile source for a fully open infrastructure path. Do not use the public OSM tile endpoints for bulk/offline downloads.

The map screen can render a configured style and download the currently visible neighbourhood-sized region through MapLibre's OfflineManager. The downloader deliberately rejects large viewports to avoid uncontrolled city-scale tile requests and native memory pressure. Full-Karachi package creation still requires an approved administrative boundary, tile-source licence, zoom policy and size testing.

## Confirmed map behaviour
- MapLibre Native is the selected Android map renderer.
- The app uses a hybrid map strategy: transport data and journey planning are offline-first; map downloads are optional.
- Users will be able to download a Karachi-wide map package or individual neighbourhood/area packages.
- Downloaded packages will work offline. Areas without a package use an approved online tile source when connected.
- Map packages have their own version, size, checksum, attribution and licence metadata. They update separately from bus route/stop data.
- No tile provider or self-hosted package source is approved yet. Do not configure the public OpenStreetMap tile server for offline downloads.

## Current implementation
- Compose application shell and route search screen.
- Room local database for routes, directions, stops, stop order, route shapes and sync state.
- Native MapLibre map screen with configurable style URL.
- Neighbourhood offline map download with confirmation, progress, pause/resume and removal.
- Versioned local map-package catalogue for full-Karachi and area packages, with a database migration; actual tile download/rendering is still pending.
- Read-only full-snapshot fetch and transactional replacement of the local transport dataset.
- Existing locally stored data is retained if the API request or Room transaction fails.

## Known limitations
- This is the initial client foundation, not a store-ready app.
- The backend currently provides content-addressed full snapshots. Incremental sync is not yet enabled.
- The MapLibre renderer and visible-neighbourhood OfflineManager download flow are now wired; provider configuration is required before either can be used. Full-Karachi package preparation/management, runtime GPS discovery, local favourites and saved journeys remain roadmap work.
- Do not use the placeholder release API URL in a release build.
- Android build/device verification must be run in an Android SDK/JDK 17 environment.
