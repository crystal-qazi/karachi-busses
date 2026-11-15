# Development Guide

## Prerequisites
- Python 3.11+
- MySQL 8+
- Git

## Local setup
1. Create the \`karachi_buses\` database with utf8mb4.
2. Create and activate a Python virtual environment.
3. Install dependencies: \`pip install -r requirements.txt\`.
4. Copy \`.env.example\` to \`.env\`; configure a least-privilege MySQL application user.
5. Run migrations: \`python scripts/migrate.py\`.
6. Create an admin: \`python scripts/create_admin.py\`.
7. Start Flask: \`python run.py\`.
8. Run tests: \`pytest\`.

## Delivery phases
- Phase 1: application foundation, schema, map and PWA shell.
- Phase 2: admin route/operator/stop management, geometry and imports.
- Phase 3: GPS nearby discovery, route/stop search and route display.
- Phase 4: direct and one-transfer journey discovery from curated stop names.
- Phase 5: source provenance, reviewer workflow, publication gates and duplicate checks.
- Phase 6: production Docker/Gunicorn configuration, secure settings and release checklist.

## Development conventions
- Keep Flask route handlers thin where possible.
- Use parameterized SQL for every database query.
- Never commit \`.env\`, credentials, personal location data or production dumps.
- Keep migration files ordered and immutable after application; add a new migration for later schema changes.
- Keep route directions and their stop sequences separate.
- Validate GeoJSON type, coordinate order, ranges and geometry size before saving.
- Use HTTPS for deployed GPS functionality.
- Preserve OpenStreetMap attribution and comply with the chosen tile provider's terms.

## Production
See \`docs/PHASE_6.md\` for Docker Compose deployment. Production requires a unique 32+ character SECRET_KEY, DEBUG=false, HTTPS, backups and an approved tile provider.
