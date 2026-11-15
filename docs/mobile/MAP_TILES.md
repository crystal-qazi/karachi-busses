# Karachi Buses map tile infrastructure decision

Updated: 2026-11-15

## Decision

Use **MapLibre Native Android** as the client renderer and prefer a **project-controlled OpenMapTiles/TileServer GL stack** for production tile hosting and offline rights. This is a technical direction, not a deployed provider: the tile server, style, tile archives and domain must be provisioned and validated before enabling the Android flags.

Why this direction:
- MapLibre Native is an open-source renderer with an Android OfflineManager that downloads a style's resources for a geographic region and reports resource progress.
- OpenMapTiles provides an open vector-tile schema and a self-hosting generation pipeline. The generated map remains subject to OpenStreetMap ODbL attribution and OpenMapTiles attribution requirements.
- TileServer GL can serve generated MBTiles over HTTP to MapLibre clients.
- A self-hosted source gives the project control over online fallback, offline downloads, caching, package versions and service continuity without depending on public OSM tile servers.

## Licensing and attribution

For OSM-derived tiles, retain the required attribution in the map UI:
`© OpenMapTiles © OpenStreetMap contributors`

OpenMapTiles schema code is BSD-licensed and cartographic design/schema components are CC-BY; OSM-derived data remains subject to ODbL. Review the current upstream licences and all included fonts, sprites, icons and other assets before deployment. This document is not a substitute for a licence review.

Do not use `tile.openstreetmap.org` or the public OSM vector tile service for offline/bulk downloads. A project-operated TileServer GL instance is a separate source with its own capacity, security, caching and uptime responsibilities.

## Hosting and generation pipeline

1. Obtain a Karachi/Pakistan OSM PBF extract from a suitable OSM data extract provider.
2. Generate vector tiles using the OpenMapTiles pipeline; start with conservative zoom ranges and increase only after resource and output-size measurements.
3. Generate and host a compatible style JSON, sprites and glyph/font resources. Every URL referenced by the style must be reachable by Android and permitted for offline retrieval.
4. Serve MBTiles through TileServer GL behind HTTPS, with access controls/rate limits and monitoring.
5. Add a project-controlled map package catalogue that publishes style version, source version, geographic bounds, zoom range, byte estimate (measured from actual generated data), attribution and licence metadata.
6. Test MapLibre online fallback and OfflineManager downloads against this source before enabling `MAP_OFFLINE_ALLOWED=true`.

OpenMapTiles upstream recommends Linux/Docker and notes its generation process has material disk/RAM requirements; actual Karachi extract requirements must be measured rather than extrapolated from the sample quickstart.

## Full Karachi versus neighbourhood downloads

- Neighbourhood downloads use bounded MapLibre OfflineManager regions. The Android implementation currently limits a visible-area download to a small viewport and zoom range 10–15 to avoid accidental city-scale downloads.
- A full-Karachi one-tap download must not be implemented as one unbounded OfflineManager region. Large bounding-box downloads have known native memory-pressure/OOM risks.
- Build a validated Karachi administrative boundary and divide it into bounded neighbourhood/area packages. The city-wide choice should orchestrate the complete set of area packages with aggregate progress, storage preflight, pause/resume, retries and cancellation.
- The app must not label a rectangle as the official Karachi boundary. Boundary geometry and the neighbourhood catalogue must be sourced and reviewed before the city-wide download is released.
- The Room package catalogue stores individual package/region state; a later group record will represent the aggregate `karachi_full` download and its member area packages.

## Current implementation status

- Android dependency: MapLibre Native Android SDK 13.6.1.
- Style URL and attribution/licence fields are supplied through local Gradle properties; the repository contains no provider key.
- Offline downloads are disabled by default. The UI requires explicit `MAP_OFFLINE_ALLOWED=true` and non-empty attribution/source/licence values.
- The Android map screen renders a configured style and supports downloading the visible neighbourhood-sized viewport with progress, pause/resume and remove controls.
- No provider has been configured, no tile package has been generated, and no package sizes are claimed.
- Full-Karachi package catalogue/API and area boundary dataset remain pending.

## Local Android configuration

Add these local (uncommitted) values to `android/gradle.properties` only after a provider/source is configured:

```properties
MAP_STYLE_URL=https://maps.example.invalid/styles/karachi/style.json
MAP_ATTRIBUTION=© OpenMapTiles © OpenStreetMap contributors
MAP_SOURCE_NAME=Karachi self-hosted OpenMapTiles
MAP_LICENSE_NAME=OpenStreetMap ODbL and OpenMapTiles BSD/CC-BY components
MAP_LICENSE_URL=https://www.openstreetmap.org/copyright
MAP_OFFLINE_ALLOWED=true
```

The example hostname is deliberately nonfunctional. Do not copy it as a production endpoint.
