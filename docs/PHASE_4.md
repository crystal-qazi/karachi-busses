# Phase 4 — Journey Discovery

## Delivered
- Public journey endpoint accepts an origin coordinate, search radius and destination stop/area text.
- Direct journey matching checks the ordered stop sequence of each published direction.
- One-transfer matching finds a shared stop between two different published directions.
- Results are ranked with direct journeys first, then by straight-line distance to the boarding stop.
- The PWA journey form uses the user's last GPS or manually selected map origin.
- Each journey leg can be selected to render its complete route geometry and ordered stops.

## API
GET /api/v1/journeys?origin_lat=24.8607&origin_lng=67.0011&destination=Saddar&radius=1500

- Origin is WGS84 latitude/longitude and is not persisted.
- Destination text must match an active, verified bus stop name or address.
- Radius is 100–10,000 metres.
- Maximum 20 itinerary options are returned.
- Supports direct and exactly one transfer.

## Limitations
- No fares, schedules, estimated travel times, service frequency or live vehicle positions.
- No geocoding of arbitrary addresses; destination must match a curated stop or stop address.
- Transfer feasibility is inferred from a shared stop ID; walking distance between different nearby stops is not guessed.
- The algorithm uses currently published directions and stop sequence only.
