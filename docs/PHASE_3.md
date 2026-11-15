# Phase 3 — Nearby Bus Discovery

## Delivered
- GPS-based nearby stop discovery with a configurable straight-line radius.
- Manual map-point selection when location permission is denied or unavailable.
- Nearby stop results include active routes and directions serving each stop.
- Read-only route-direction detail API returns ordered active stops and saved GeoJSON.
- Search across active route codes/names/descriptions, direction endpoint labels, and active stop names/addresses.
- Route highlighting, stop sequence markers and route selection on the Leaflet map.
- PWA shell cache version bumped; API responses are not cached so users do not see stale discovery results.
- No GPS location is stored server-side.
- No vehicle positions, live tracking, arrival predictions or pedestrian routing.

## API
- GET /api/v1/discover/nearby?lat=24.8607&lng=67.0011&radius=1500&limit=50
  - lat/lng required; WGS84 decimal degrees.
  - radius optional, 100–10,000 metres (default 1,500).
  - limit optional, 1–100 (default 50).
  - Returns nearby active stops, distance in metres and active directions/routes serving each stop.
  - Distance is Haversine straight-line distance, not walking distance.
- GET /api/v1/directions/{direction_id}
  - Returns active route/direction metadata, ordered active stops and saved GeoJSON LineString if available.
- GET /api/v1/search?q={text}
  - Searches active route codes, names, descriptions, direction endpoint labels and active stop names/addresses.
  - Requires 2–100 characters.

## Performance and privacy
- Nearby SQL first applies a latitude/longitude bounding box, then Haversine distance and a result limit.
- Existing indexes on stop coordinates, route status and route-stop stop ID support the lookup.
- Browser coordinates are sent only when a user explicitly uses GPS or selects a map point.
- No location history is recorded.
- Only active routes and active stops appear in public discovery.
- OpenStreetMap tiles and browser geolocation need an internet connection; geolocation requires HTTPS in production.
- Service worker does not cache API responses.

## Data quality and limitations
- No fabricated Karachi bus services are seeded.
- Only routes and stops entered and activated by administrators appear publicly.
- Routes without a saved shape can still show ordered stop markers.
- Nearby distance is straight-line proximity, not a confirmed walkable path.
- Search is route/stop lookup; turn-by-turn journey planning and transfer recommendations are a later phase.
