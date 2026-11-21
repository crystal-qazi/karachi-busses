# Karachi Buses — Final Project Handover

**Assessment date:** 2026-11-21  
**Repository:** https://github.com/crystal-qazi/karachi-busses  
**Reviewed ref:** `main`  
**Reviewed commit:** `6023a338211abebe949fa3a6484d4a0f89230b82`

## Executive decision

The application foundation is implemented and the latest main-branch automated Tests workflow passed. The project is **not ready to be described as a complete, verified Karachi-wide passenger transport service**, because the current database export contains mostly unreviewed route and stop records and very little published geometry.

This is a data-readiness limitation, not a reason to discard the software. Keep the application and the evidence-backed dataset; do not invent missing coordinates, sequences, service status, or route shapes to force a green status.

## Read-only database inventory

The source for these figures is `artifacts/full_route_audit_export.json`, generated 2026-11-21 11:57:55 UTC by `scripts/export_full_route_audit.py`. The export is explicitly read-only and preserves stored values.

| Table / status | Count |
|---|---:|
| Data sources | 4 |
| Operators | 1 |
| Route categories | 7 |
| Routes | 98 |
| Routes under review | 95 |
| Inactive routes | 3 |
| Directions | 98 |
| Stops | 572 |
| Active stops | 6 |
| Stops under review | 566 |
| Route-stop associations | 1,281 |
| Historical route segments | 1,415 |
| Saved route shapes | 2 |

The 1,415 historical segments belong to a user-provided research dataset whose original publication metadata and redistribution licence are not independently established. They must not be represented as verified current bus operations.

## Application and release status

| Area | Assessment |
|---|---|
| Flask / MySQL backend | Implemented in repository |
| Bootstrap / Leaflet PWA | Implemented in repository |
| Admin routes, stops, directions and imports | Implemented in repository |
| Nearby discovery and route search | Implemented; result quality depends on approved data |
| Direct / one-transfer journey search | Implemented; data-dependent |
| Data provenance and publication gates | Implemented |
| Docker / Gunicorn deployment scaffold | Implemented; operator configuration still required |
| Native Android foundation | Present; not release-complete |
| Android offline map packages | Provider, lawful tile source, city package generation and operational configuration remain outstanding |
| Complete verified Karachi dataset | Not available in current export |
| Latest main Tests workflow | Passed for reviewed commit |

## Route-data decisions

1. Preserve the supplied 15 KML geometries as immutable source baselines. This is not proof of physical stop locations or complete road-following alignment.
2. Keep all 95 routes under review unless their route identity, source, sequence, geometry and publication requirements are satisfied.
3. Keep the 3 routes already marked inactive inactive; do not reactivate them based on historical lines.
4. Keep the 566 stops under review unless their physical boarding location and source evidence are verified.
5. Treat the 76-route historical network as a separate historical/research layer, not as a current service catalogue.
6. Keep R5/R6/R7/R14 source-coverage questions and R9/R10 sequence gaps explicit. Do not synthesize route geometry or stop order.
7. Do not convert OSM nearest-road proximity into proof of a bus boarding point.
8. Do not change production MySQL data as part of this handover. The reviewed export is read-only.

## What is required for a genuinely complete public launch

These are real-world evidence and operator tasks; code cannot responsibly manufacture them:

- Obtain an authoritative current route and stop catalogue for every service intended for publication.
- Obtain permission/licensing details for route geometry and any third-party map tiles or offline map packages.
- Validate forward and reverse stop sequences and physical boarding-side coordinates, using operator confirmation or field survey where needed.
- Create and review road-following shapes for each published direction.
- Have a data reviewer approve only records meeting the existing publication gate.
- Run the backend test suite against a disposable MySQL test database and run the Android build/unit tests under the documented JDK/SDK toolchain.
- Configure production secrets, HTTPS, backups, monitoring, privacy/support contact and a lawful tile provider before deployment.

## Final handover rule

The software repository is retained as the working product. The current dataset remains a research/staging dataset. The project must not be advertised as providing complete verified Karachi-wide routes until the evidence and publication gates above are satisfied.

**No database rows were modified by this audit.**
