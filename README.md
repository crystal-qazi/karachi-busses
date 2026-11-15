# Karachi Buses

A Karachi-wide public transport discovery PWA. Passengers can find nearby verified bus stops, search published routes and plan direct or one-transfer journeys on an OpenStreetMap-based map.

**No live vehicle tracking, ETAs or live bus GPS are included.** Routes and stop sequences are static curated data stored in MySQL.

## Stack
- Python 3.11+
- Flask + MySQL 8
- Bootstrap 5 + vanilla JavaScript
- Leaflet + OpenStreetMap
- Browser Geolocation API
- PWA manifest + service worker
- Gunicorn + Docker Compose for production

## Delivery status
| Phase | Scope | Implementation |
|---|---|---|
| 1 | Flask foundation, schema, migrations, map/PWA shell | Complete |
| 2 | Admin operators/routes/stops/directions, geometry and CSV imports | Complete |
| 3 | GPS/manual nearby discovery, route/stop search and route map | Complete |
| 4 | Direct and one-transfer journey discovery | Implemented; data-dependent |
| 5 | Data provenance, source review, publication gates and duplicate checks | Implemented; Karachi dataset still needs collection |
| 6 | Production Docker/Gunicorn setup, secure settings and release guide | Implemented; deployment still needs operator setup |

## Features
- GPS or manually selected origin.
- Nearby verified stops and routes with configurable search radius.
- Route direction map, stop sequence and saved GeoJSON geometry.
- Search route numbers/names and published stops.
- Direct journey suggestions.
- One-transfer suggestions when two directions share the same stop record.
- Admin data-source register, reviewer verification and route publication gate.
- CSV stop import and multi-route/direction/stop import with source attribution and duplicate checks.
- No storage of passenger GPS coordinates in the application database; hosting logs must be configured to omit them.

## Quick start (Windows / local)
1. Install Python 3.11+ and MySQL 8+.
2. Create the database:
   \`CREATE DATABASE karachi_buses CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\`
3. Create/activate a virtual environment: \`python -m venv .venv\`
4. Install: \`pip install -r requirements.txt\`
5. Copy \`.env.example\` to \`.env\` and configure MySQL.
6. Apply schema: \`python scripts/migrate.py\`
7. Create an admin: \`python scripts/create_admin.py\`
8. Start: \`python run.py\`
9. Open http://127.0.0.1:5000.

Run tests with \`pytest\`. Browser geolocation works on localhost and HTTPS deployments.

## API
- GET /api/v1/health
- GET /api/v1/discover/nearby?lat=24.8607&lng=67.0011&radius=1500
- GET /api/v1/directions/{direction_id}
- GET /api/v1/search?q=Saddar
- GET /api/v1/journeys?origin_lat=24.8607&origin_lng=67.0011&destination=Saddar

See [API documentation](docs/API_DOCUMENTATION.md).

## Data provenance and publication
Public endpoints expose only active routes and stops with verified linked data sources. A route can be published only by a super administrator or data reviewer after it has a verified source, at least one direction, two or more active verified-source stops per direction and a saved shape for every direction.

Admin → Data sources & review records evidence. Imported stops remain under review until checked. See [Phase 5](docs/PHASE_5.md) and [data collection template](docs/PHASE_5_DATA_TEMPLATE.md).

## Production deployment
See [Phase 6 deployment guide](docs/PHASE_6.md). Docker Compose starts MySQL and a Gunicorn web container. Production requires a unique secret, strong DB passwords, HTTPS reverse proxy, backups and an approved tile provider.

## Known limitations / release blockers
- No verified comprehensive Karachi bus-route dataset is bundled. The software is ready to receive reviewed data, but Karachi-wide coverage is not complete until the dataset is collected and validated.
- Destination search matches known stop names/addresses; arbitrary-address geocoding is not included.
- No fares, timetables, travel-time estimates, walking directions, transfer walk links or live vehicle tracking.
- The standard OpenStreetMap tile endpoint is not an unlimited production tile service. Choose a suitable tile provider or self-host tiles, retain attribution and comply with its policy.
- Privacy notice is included; add the responsible operator's support contact and retention details before public launch.

Map data © OpenStreetMap contributors.
