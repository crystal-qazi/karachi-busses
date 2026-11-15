# Karachi Buses

A Karachi-wide public transport discovery PWA. Users will be able to find nearby bus routes using GPS, search journeys by destination, and view verified route shapes and stops on OpenStreetMap.

**No live vehicle tracking is planned.** Route geometry and stop locations are maintained in the application's database.

## Technology
- Python 3.11+
- Flask
- MySQL 8+
- Bootstrap 5
- Leaflet.js + OpenStreetMap
- Browser Geolocation API
- PWA manifest and service worker

## Current implementation
Phase 1 foundation:
- Flask application factory and configuration
- MySQL connection helper
- Initial MySQL schema migration
- Versioned health API
- Responsive Bootstrap/Leaflet map shell
- PWA manifest and service worker
- Initial automated tests

Route administration, imports, nearby discovery, journey planning and verified Karachi route data are subsequent phases.

## Quick start
1. Install Python 3.11 or newer and MySQL 8.
2. Create the database:
   ```sql
   CREATE DATABASE karachi_buses CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Create and activate a virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update the MySQL credentials.
6. Apply migrations: `python scripts/migrate.py`
7. Start Flask: `python run.py`
8. Open http://127.0.0.1:5000.

The browser map uses OpenStreetMap tiles and requires internet access. GPS access requires HTTPS in production; localhost is generally treated as a secure browser context.

## Configuration
See [.env.example](.env.example). Never commit real credentials. The configured MySQL database must already exist; migrations create application tables, not the database or MySQL user.

## API
- `GET /api/v1/health` — application and database health.
- `GET /api/v1/health?check_db=false` — process health without a database check.

## Database
The initial schema is in `migrations/001_initial_schema.sql`. It includes operators, routes, directions, stops, ordered route stops, GeoJSON route shapes, categories, data sources, admin accounts and audit logs.

The migration runner records applied files in `schema_migrations` and does not reapply them.

## Tests
```bash
pytest
```

## Map attribution and tile usage
The map displays © OpenStreetMap contributors attribution. The public OSM standard tile service has a usage policy and is not an unlimited production tile service. Before public launch, select a tile provider or self-hosted tile infrastructure appropriate for expected traffic and comply with its terms.

## Project principles
- Store verified routes and stops in MySQL; do not infer bus service from road geometry.
- Keep forward and reverse route directions separate.
- Store route geometry as GeoJSON LineString coordinates in [longitude, latitude] order.
- Retain route data provenance and verification status.
- Do not persist a user's GPS location by default.
- Distinguish straight-line proximity from actual pedestrian walking directions.

## License
No license has been selected yet. Add one before accepting external contributions or distributing the project.
