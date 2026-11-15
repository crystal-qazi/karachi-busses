# Karachi Buses — Project Plan

## Product scope
A Karachi-wide installable public transport discovery PWA. Passengers can discover nearby bus stops, search published routes and plan direct or one-transfer journeys from their current or manually selected location.

No live vehicle GPS, vehicle tracking or arrival predictions.

## Technology
Flask, MySQL 8, Bootstrap 5, vanilla JavaScript, Leaflet, OpenStreetMap, GeoJSON and PWA manifest/service worker. Production uses Gunicorn and Docker Compose.

## Delivery phases
1. Foundation — Flask application, configuration, schema/migrations, map shell, PWA shell, tests and documentation.
2. Route management — operators, routes, stops, directions, geometry editor and CSV imports.
3. Nearby discovery — GPS, manual origin, nearby stop/radius search, route display and search.
4. Journey discovery — direct route matching and one-transfer suggestions based on shared stop IDs.
5. Data collection — source provenance, review workflow, publication gates, duplicate checks and Karachi coverage review.
6. Release — secure settings, production container, database readiness, PWA and tile-provider readiness.

## Data integrity
- Every public route and stop must have verified source provenance.
- Forward and reverse directions have independent ordered stops and shapes.
- Stops can be shared across routes only when they represent the same physical boarding point.
- GeoJSON coordinates use longitude then latitude.
- Preserve provenance and audit administrative changes.
- Do not persist passenger GPS coordinates by default.
- Never fabricate route records or mark uncertain data verified.

## Journey matching
Direct journeys use one direction with an origin-near boarding stop followed by a destination-matching stop. One-transfer journeys use two different directions with a shared stop record as the interchange. Arbitrary-address geocoding, fares, timetables, walking links and ETAs are out of scope.

## Completion criteria
The application features and release configuration can be considered implemented when automated tests pass and a production deployment is configured. Complete Karachi route coverage remains a separate data acquisition and field-verification effort; the repository does not claim the dataset is comprehensive.
