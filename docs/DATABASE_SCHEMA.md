# Database Schema

Database name: \`karachi_buses\` (create it before applying migrations).

Apply migrations in order with \`python scripts/migrate.py\`.

## Tables
- \`data_sources\`: source name, URL, notes, verification status, reviewer and verification timestamp.
- \`bus_operators\`: transport operators.
- \`route_categories\`: route/service categories.
- \`bus_routes\`: route identity, operator, source and publication status.
- \`route_category_map\`: many-to-many route categories.
- \`route_directions\`: independent forward/reverse directions.
- \`bus_stops\`: reusable stop records, coordinates and source provenance.
- \`route_stops\`: ordered stop membership for a direction.
- \`route_shapes\`: one GeoJSON geometry per direction.
- \`admin_users\`: admin identities and roles.
- \`audit_logs\`: administrative change history.
- \`schema_migrations\`: migration runner history.

## Migrations
1. \`001_initial_schema.sql\` — base entities and route relationships.
2. \`002_unique_route_code.sql\` — globally unique route code.
3. \`003_data_provenance.sql\` — stop source link and source verification reviewer/timestamp.

## Geometry conventions
GeoJSON LineString coordinates are \`[longitude, latitude]\`. Stop coordinates are decimal latitude/longitude. Validate coordinate ranges in application code and database constraints.

## Publication integrity
Public endpoints require active routes/stops and verified linked data sources. A route can be published only by a super administrator or data reviewer, after it has a verified source, at least one direction, two or more active verified-source stops in every direction, and a saved shape for each direction.

## Backups
Back up the production database before applying schema migrations. Migrations are recorded and are not re-applied once recorded.
