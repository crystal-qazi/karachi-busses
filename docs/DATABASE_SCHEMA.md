# Database Schema

Database name: `karachi_buses` (create it before applying migrations).

Initial migration: `migrations/001_initial_schema.sql`.

## Tables
- `data_sources`: provenance and verification status for imported/curated data.
- `bus_operators`: transport operators.
- `route_categories`: route/service categories.
- `bus_routes`: route identity, operator, source and publication status.
- `route_category_map`: many-to-many route categories.
- `route_directions`: independently modelled forward/reverse journeys.
- `bus_stops`: reusable stop records with coordinates.
- `route_stops`: ordered stop membership for a direction.
- `route_shapes`: one GeoJSON geometry per direction.
- `admin_users`: future admin authentication identities.
- `audit_logs`: administrative change history.
- `schema_migrations`: created by the migration runner.

## Geometry conventions
GeoJSON LineString coordinates are `[longitude, latitude]`. Stop coordinates are stored in separate decimal latitude and longitude columns. Validate coordinate ranges in application code as well as database constraints.

## Migration
Run `python scripts/migrate.py`. Applied migration filenames are recorded to avoid reapplication. Back up production data before any future schema changes.
