# SMTA Karachi route catalogue import

## What this import does

`data/imports/smta_karachi_route_catalog.json` records 22 Karachi route identities from the SMTA route directory and supporting public-sector alignment sources. `scripts/import_smta_catalog.py` safely inserts missing route metadata, categories, an operator reference, source records and one published-forward direction per route.

The importer is idempotent: existing route codes are preserved and skipped rather than overwritten. It uses a transaction and rolls back on errors. It requires the existing MySQL schema (migrations 001–003).

## What it deliberately does not do

- Does not insert bus-stop coordinates, route-stop links or GeoJSON route shapes.
- Does not activate or publish any route.
- Does not overwrite existing route records.
- Does not claim that the published stop lists have been field-verified.
- Does not create fake coordinates for stops whose coordinates are not yet known.

All routes except those SMTA explicitly lists inactive are seeded as `under_review`. R5, R6 and R7 are seeded as `inactive` according to the SMTA directory. Source records are pending review. Green Line and Orange Line direction endpoints are seeded from supporting references; their complete station sequences are not part of this import.

## Before running

1. Back up the target MySQL database.
2. Confirm `.env` points to the intended development database.
3. Apply migrations if not already applied: `python scripts/migrate.py`.
4. Run a no-write preview: `python scripts/import_smta_catalog.py`.
5. Confirm the printed database name is exactly `karachi_buses`.
6. Apply explicitly: `python scripts/import_smta_catalog.py --apply --confirm-database karachi_buses`.

Do not run this against production without a separately reviewed deployment and backup plan.

## Sources

- SMTA Karachi route directory: https://smta.gos.pk/route-map (accessed 2026-11-16). SMTA states the map is courtesy of Think Transportation and disclaims authentication of third-party service data.
- Provincial Assembly of Sindh, Orange Line service information: https://www.pas.gov.pk/business/questios-details/33/1989 (dated 2026-01-29).
- Shehri BRT TOD Design Booklet, Green Line alignment reference: https://www.shehri.org/BRT%20TOD%20Design%20Booklet.pdf (historical planning reference).

## After import

Use the admin review workflow to check each source. Collect WGS84 coordinates for stops, match stop names carefully (including opposite sides of roads), create forward/reverse direction stop sequences, and draw road-following GeoJSON shapes. Only a data reviewer or super administrator should verify sources and publish routes after all publication gates pass.
