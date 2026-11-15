# Development Guide

## Prerequisites
- Python 3.11+
- MySQL 8+
- Git

## Local setup
1. Create the `karachi_buses` database with utf8mb4.
2. Create a Python virtual environment.
3. Install `requirements.txt`.
4. Copy `.env.example` to `.env`; configure a least-privilege MySQL application user.
5. Run `python scripts/migrate.py`.
6. Run `python run.py`.
7. Run tests with `pytest`.

## Development conventions
- Keep Flask route handlers thin; put business logic in service modules.
- Use parameterized SQL for every database query.
- Never commit `.env`, credentials, personal location data or production dumps.
- Keep migration files ordered and immutable after application; create a new migration for later schema changes.
- Keep route directions and their stop sequences separate.
- Validate GeoJSON type, coordinate order, ranges and geometry size before saving.
- Use HTTPS for deployed GPS functionality.
- Preserve OpenStreetMap attribution and comply with the chosen tile provider's terms.

## Current limitations
The map shell and location marker are implemented. Route data ingestion, route editor, nearby search, journey search and admin authentication are not implemented in Phase 1.
