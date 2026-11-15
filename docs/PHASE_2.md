# Phase 2 — Route Management

## Delivered in this branch
- Admin login backed by hashed passwords and database admin users.
- Admin dashboard with operator, route, stop and direction counts.
- Operator creation and active/inactive toggle.
- Route creation and editing, route status and operator assignment.
- Independent route directions with start/end labels.
- Stop creation and editing with coordinate range validation.
- Ordered stop linking for each direction.
- Leaflet.Draw route LineString editor with GeoJSON persistence.
- CSV stop import validation/preview and explicit import action (maximum 5,000 rows); imports are set to under review.
- Protected admin map-data API.
- Audit records for administrative writes.
- CSRF protection for admin POST requests.
- Admin creation utility that prompts for a password; no default credentials.

## Setup
1. Install dependencies with `pip install -r requirements.txt`.
2. Apply pending migrations with `python scripts/migrate.py`.
3. Create an administrator: `python scripts/create_admin.py`.
4. Start Flask: `python run.py`.
5. Open `/admin/login`.

## CSV format
Required headers: `stop_name,latitude,longitude`. Optional header: `address`.
Rows are imported with `under_review` status. Review and activate them manually before publishing.

## Important operational notes
- Route code is unique across the database (migration 002).
- Do not activate routes until route shape, stop order and source evidence have been reviewed.
- Only administrators can use the route management pages and map-data API.
- CSRF tokens are injected into admin forms by the shared layout script.
- External Bootstrap, Leaflet and Leaflet.Draw assets currently use public CDNs; plan local/self-hosted assets for strict offline operation.
- This branch is not yet merged into `main`. Run CI and review before merging.
