# API Documentation

Base path: /api/v1. All public discovery endpoints are read-only.

Success envelope: {"success": true, "data": {...}}
Error envelope: {"success": false, "error": {"code": "...", "message": "..."}}

## Health
### GET /health
Checks application and database connectivity. Use check_db=false to skip the database check.

## Nearby bus discovery
### GET /discover/nearby?lat=24.8607&lng=67.0011&radius=1500&limit=50
Finds active bus stops served by active routes around a WGS84 coordinate.
- lat and lng are required decimal degrees.
- radius is optional, 100–10,000 metres; default 1,500.
- limit is optional, 1–100; default 50.
- Returns nearby stops, straight-line distance in metres, and active route directions serving each stop.
- The SQL query applies a latitude/longitude bounding box before Haversine distance calculation.
- Coordinates are not stored.

## Route direction detail
### GET /directions/{direction_id}
Returns an active route direction, its ordered active stops, and stored GeoJSON LineString when available. Returns 404 when the direction does not belong to an active route.

## Search
### GET /search?q={text}
Searches active route codes, names and descriptions, direction start/end labels, and active stop names/addresses. Query length must be 2–100 characters.

## Data visibility
Only bus_routes with status active and bus_stops with status active are returned. A direction without a stored shape can still be displayed using its ordered stop markers. No live vehicle positions, arrival predictions or pedestrian directions are returned.
