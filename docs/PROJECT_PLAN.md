# Karachi Buses — Project Plan

## Product scope
A Karachi-wide, installable public transport discovery PWA. Users can:
- Discover bus routes and stops near their current or manually selected location.
- Search a destination and receive suitable direct journeys, with transfer suggestions in a later iteration.
- Inspect route directions, ordered stops and map geometry.

Out of scope: live vehicle GPS, live bus positions and arrival predictions without verified timetable/live data.

## Technology
Flask, MySQL 8, Bootstrap 5, vanilla JavaScript, Leaflet, OpenStreetMap, GeoJSON and PWA manifest/service worker.

## Delivery phases
1. Foundation: Flask, configuration, MySQL schema/migrations, map shell, PWA shell, tests and documentation.
2. Route management: operators, routes, stops, directions, map editor and CSV/GeoJSON import.
3. Nearby discovery: GPS, radius search, nearest stops, route results and map highlighting.
4. Journey discovery: destination search, direct route matching, then one-transfer suggestions.
5. Data collection: source records, route verification, duplicate checks and Karachi coverage review.
6. Release: security, performance, PWA, hosting and tile-provider readiness.

## Data integrity
- Every public route must be reviewed and verified.
- Forward and reverse directions have independent stop sequences and shapes.
- GeoJSON coordinates use longitude then latitude.
- Stops may be shared across routes.
- Preserve source/provenance and audit administrative changes.
- Do not persist user GPS coordinates by default.

## Initial acceptance criteria
See the Phase 1 backlog and tests in the repository. Route discovery is not considered complete until real, verified route and stop data is loaded and tested.
