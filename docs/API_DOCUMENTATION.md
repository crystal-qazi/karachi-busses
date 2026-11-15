# API Documentation

Base path: /api/v1. Public discovery endpoints are read-only.

Success envelope: {"success": true, "data": {...}}
Error envelope: {"success": false, "error": {"code": "...", "message": "..."}}

## Health
### GET /health
Checks application and database connectivity. Use check_db=false to skip the database check.

## Nearby discovery
### GET /discover/nearby?lat=24.8607&lng=67.0011&radius=1500&limit=50
Returns active stops served by active routes within a radius of a WGS84 coordinate. Radius is 100–10,000 metres (default 1,500); limit is 1–100 (default 50). Distances are straight-line Haversine estimates.

## Direction detail
### GET /directions/{direction_id}
Returns active direction metadata, ordered active stops and saved GeoJSON LineString. Only routes and stops whose linked data sources are verified are visible.

## Route and stop search
### GET /search?q={text}
Searches active, verified-source route codes, names, descriptions, direction endpoint labels and active, verified-source stop names/addresses. Query length is 2–100 characters.

## Journey discovery
### GET /journeys?origin_lat=24.8607&origin_lng=67.0011&destination=Saddar&radius=1500
Returns direct and one-transfer itineraries from an origin coordinate to a destination stop name/address.
- origin_lat and origin_lng are required WGS84 coordinates.
- destination is 2–100 characters and must match a curated active stop name or address.
- radius is 100–10,000 metres; default 1,500.
- At most 20 results are returned.
- Direct journeys are ranked ahead of one-transfer journeys, then by distance to the boarding stop.
- Transfers require the exact same stop record to be present in both direction sequences.
- No travel time, fare, timetable, walking directions or live vehicle data is inferred.

## Visibility and provenance
Public APIs return only active routes and active stops whose respective data sources have verification_status=verified. Route publication is restricted to super administrators and data reviewers and requires:
- a verified route source;
- at least one direction;
- at least two active, verified-source stops in every direction;
- a saved route GeoJSON shape for every direction.

No browser GPS coordinates are stored. No live vehicle tracking is implemented.
