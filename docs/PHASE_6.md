# Phase 6 — Production Readiness and Release

## Runtime
- Docker image uses Python 3.12 slim and runs Gunicorn as a non-root user.
- Docker Compose runs MySQL 8.4 with a persistent volume and health check.
- Migrations run at web-container startup before Gunicorn.
- Web container binds to localhost; put a TLS-terminating reverse proxy in front of it.
- Production startup rejects a placeholder/short secret and DEBUG=true.
- Session cookies are HttpOnly, SameSite=Lax and Secure in production.
- CSRF protection remains enabled; login sessions are limited to eight hours.

## Deployment
1. Copy .env.production.example to .env and set unique random SECRET_KEY, DB_PASSWORD and MYSQL_ROOT_PASSWORD.
2. Ensure .env is excluded from version control and readable only by the deployment operator.
3. Build and start: docker compose up -d --build.
4. Check: curl http://127.0.0.1:8000/api/v1/health.
5. Create the first admin interactively inside the web container: docker compose exec web python scripts/create_admin.py.
6. Put Nginx/Caddy or a managed ingress in front with HTTPS and proxy headers configured.
7. Confirm GPS works on the HTTPS public domain and test installability on Android Chrome.
8. Back up the MySQL volume/database before each release; test restore procedures.
9. Monitor container logs, disk use, DB availability and GitHub Actions.

## OpenStreetMap
The public OSM standard tile endpoint is subject to a usage policy and is not a free unlimited production tile CDN. Select a suitable tile provider or self-host tiles, preserve attribution and comply with provider terms. Do not bulk-download or prefetch standard OSM tiles.

## Release checklist
- [ ] Unique production SECRET_KEY and DB credentials.
- [ ] DEBUG=false and HTTPS enabled.
- [ ] Database backups and tested restore.
- [ ] Migrations applied and reviewed.
- [ ] Admin account created with a strong password.
- [ ] No default or test credentials in deployment.
- [ ] OSM tile provider approved for expected traffic.
- [ ] GPS permission, manual selection and PWA install tested on real devices.
- [ ] Public route visibility checked against source verification status.
- [ ] Karachi route dataset independently reviewed and coverage gaps published.
- [ ] Privacy notice and contact/support details published.
- [ ] Domain, TLS, monitoring and incident process configured.

## Known release blockers
- No complete verified Karachi route dataset is bundled.
- No arbitrary-address geocoder, fares, timetable, walking directions, ETAs or live vehicle tracking.
- Deployment still needs an operator-owned domain, TLS, backups, tile provider and operational monitoring.
