# Karachi Buses

A Karachi-wide public transport discovery PWA. Users can find nearby bus routes using GPS, search routes and stops, and view verified route shapes and stops on OpenStreetMap.

**No live vehicle tracking is implemented or planned.** Route geometry and stop locations are maintained in MySQL.

## Technology
- Python 3.11+
- Flask
- MySQL 8+
- Bootstrap 5
- Leaflet.js + OpenStreetMap
- Browser Geolocation API
- PWA manifest and service worker

## Current implementation
### Phase 1 — Foundation
- Flask application factory and configuration
- MySQL connection helper and schema migrations
- Versioned health API
- Responsive Bootstrap/Leaflet map shell
- PWA manifest and service worker

### Phase 2 — Route management
- Protected admin authentication and dashboard
- Operator, route, direction and stop management
- Ordered route stops and Leaflet route geometry editor
- GeoJSON route import and CSV stop import
- Administrative audit log and CSRF protection

### Phase 3 — Nearby discovery
- GPS-based nearby stop search with configurable radius
- Manual map selection fallback
- Nearby stop cards with serving routes and directions
- Route geometry and ordered stop display
- Search for active route codes/names and active stop names
- Public read-only discovery APIs
- No GPS history or live vehicle tracking

## Quick start
1. Install Python 3.11+ and MySQL 8+.
2. Create the database:
   \`CREATE DATABASE karachi_buses CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\`
3. Create and activate a virtual environment:
   \`python -m venv .venv\`
   Windows PowerShell: \`.venv\\Scripts\\Activate.ps1\`
4. Install dependencies: \`pip install -r requirements.txt\`
5. Copy \`.env.example\` to \`.env\` and configure MySQL credentials.
6. Apply migrations: \`python scripts/migrate.py\`
7. Create an admin: \`python scripts/create_admin.py\`
8. Start Flask: \`python run.py\`
9. Open http://127.0.0.1:5000. Admin login is at /admin/login.

The configured MySQL database must already exist. Never commit real credentials. Browser geolocation requires HTTPS in production; localhost is normally treated as secure.

## API
- GET /api/v1/health
- GET /api/v1/discover/nearby?lat=24.8607&lng=67.0011&radius=1500
- GET /api/v1/directions/{direction_id}
- GET /api/v1/search?q={text}

See docs/API_DOCUMENTATION.md and docs/PHASE_3.md.

## Data quality
No sample or invented Karachi route data is published. Only active routes and active stops entered and verified by administrators are discoverable. Nearby distance is straight-line distance, not walking distance. Journey planning, transfers, ETAs and live vehicle tracking are not provided.

## Map attribution and tile usage
Map data © OpenStreetMap contributors. The standard OpenStreetMap tile service is not an unlimited production tile service. Before public launch, choose an appropriate tile provider or self-hosted tile infrastructure and comply with its terms.

## License
No license has been selected yet. Add one before accepting external contributions or distributing the project.
