# Karachi Buses self-hosted map tiles

This folder is the deployment scaffold for the project-controlled MapLibre tile source. It does not include generated map data or a production style yet.

## Why self-host

The Android client uses MapLibre Native. Production online fallback and offline downloads should use a source that Karachi Buses controls and is explicitly allowed to serve for offline use. This scaffold uses TileServer GL to serve project-generated OpenMapTiles MBTiles and styles.

## Prepare map data

1. Use a current Karachi/Pakistan OSM PBF extract from an appropriate OSM data extract provider.
2. Generate a vector tileset with the OpenMapTiles pipeline. Start with a low maximum zoom and a limited extract; measure build memory, CPU, disk and output size before increasing zoom.
3. Copy the generated MBTiles file into `data/` and provide the matching style, sprites and glyphs under the configured data paths.
4. Confirm that the style's source, sprite and glyph URLs resolve through this TileServer GL instance. Do not leave remote font/sprite dependencies pointing at an unapproved third-party service.
5. Start the development server:

```powershell
docker compose up -d
docker compose logs -f tileserver
```

The local development port is `http://127.0.0.1:8080`. Check the TileServer GL landing page and style JSON before using its style URL in Android.

## Android configuration

Set local, uncommitted properties in `android/gradle.properties`:

```properties
MAP_STYLE_URL=https://maps.your-domain.example/styles/karachi/style.json
MAP_ATTRIBUTION=© OpenMapTiles © OpenStreetMap contributors
MAP_SOURCE_NAME=Karachi Buses self-hosted OpenMapTiles
MAP_LICENSE_NAME=OpenStreetMap ODbL; OpenMapTiles BSD/CC-BY components
MAP_LICENSE_URL=https://www.openstreetmap.org/copyright
MAP_OFFLINE_ALLOWED=true
```

Do not enable offline downloads until the generated style and all dependent resources are served by this project-controlled host and the included data/assets have been licence-reviewed.

## Production hardening

The compose port binds to loopback for local development. For production:
- terminate TLS at a reverse proxy;
- restrict allowed hosts and origins as appropriate;
- add rate limiting, request logging, health monitoring, backups and capacity alerts;
- protect administrative endpoints and do not expose the TileServer GL GUI unnecessarily;
- publish immutable style/tile versions and retain the prior version during rollout;
- monitor disk usage and concurrent offline download traffic.

## Karachi-wide versus area packages

Do not create one huge city-wide OfflineManager region. The Android SDK downloads resources per region and large bounds at high zoom can put significant memory pressure on devices. Validate the city boundary and area polygons, then expose a catalogue of bounded neighbourhood packages. A city-wide user action should orchestrate those packages with aggregate progress, storage preflight, retries and pause/resume.

## Attribution and licensing

Display `© OpenMapTiles © OpenStreetMap contributors` in the map UI, and retain the current OSM/ODbL and OpenMapTiles BSD/CC-BY notices. Review all style, font, sprite, icon and data-source licences before release. The OpenMapTiles schema does not remove OSM data attribution requirements.
