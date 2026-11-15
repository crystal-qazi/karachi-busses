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
- Read-only full-snapshot fetch and transactional replacement of the local transport dataset.
- Existing locally stored data is retained if the API request or Room transaction fails.

## Known limitations
- This is the initial client foundation, not a store-ready app.
- The backend currently provides content-addressed full snapshots. Incremental sync is not yet enabled.
- MapLibre rendering, tile-provider integration, map package download/management, runtime GPS discovery, local favourites and saved journeys remain roadmap work.
- Do not use the placeholder release API URL in a release build.
- Android build/device verification must be run in an Android SDK/JDK 17 environment.
