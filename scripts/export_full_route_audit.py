#!/usr/bin/env python3
"""Read-only complete route database export for an independent audit.

Exports every route (all statuses), direction, ordered route-stop
association, stop (including stops not assigned to any route), source,
operator, category mapping, route segment and route shape from the MySQL
database into ``artifacts/full_route_audit_export.json``.

SELECT queries only — the script performs no INSERT/UPDATE/DELETE, no DDL
and no commits. Credentials, admin users and audit logs are excluded.

Usage:
    python scripts/export_full_route_audit.py            # dry run (counts)
    python scripts/export_full_route_audit.py --build    # write JSON export
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.database.helpers import cursor_context  # noqa: E402

OUTPUT_PATH = ROOT / "artifacts" / "full_route_audit_export.json"


def _plain(value):
    """Serialise DB values to JSON-safe equivalents without altering them."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _rows_to_dicts(rows):
    return [{k: _plain(v) for k, v in row.items()} for row in rows]


def export_database() -> dict:
    app = create_app()
    with app.app_context():
        with cursor_context() as (conn, cursor):
            # -- reference tables -------------------------------------------------
            cursor.execute(
                """SELECT id, source_name, source_url, notes, verification_status,
                          verified_at, created_at, updated_at
                   FROM data_sources ORDER BY id""")
            sources = _rows_to_dicts(cursor.fetchall())

            cursor.execute(
                """SELECT id, name, contact, website, is_active, created_at, updated_at
                   FROM bus_operators ORDER BY id""")
            operators = _rows_to_dicts(cursor.fetchall())

            cursor.execute("SELECT id, name, description FROM route_categories ORDER BY id")
            categories = _rows_to_dicts(cursor.fetchall())

            cursor.execute("SELECT route_id, category_id FROM route_category_map")
            category_map = _rows_to_dicts(cursor.fetchall())

            # -- routes, directions, ordered stops --------------------------------
            cursor.execute(
                """SELECT id, operator_id, source_id, route_code, route_name,
                          description, status, created_at, updated_at
                   FROM bus_routes ORDER BY id""")
            routes = _rows_to_dicts(cursor.fetchall())

            cursor.execute(
                """SELECT id, route_id, direction_name, start_label, end_label, created_at
                   FROM route_directions ORDER BY id""")
            directions = _rows_to_dicts(cursor.fetchall())

            # Every route-stop association in its stored sequence order, joined
            # to the stop record and the owning route for audit convenience.
            cursor.execute(
                """SELECT rs.id, rs.direction_id, d.route_id, rs.stop_id,
                          rs.stop_sequence, rs.created_at,
                          s.stop_name, s.latitude, s.longitude, s.status AS stop_status,
                          s.source_id AS stop_source_id
                   FROM route_stops rs
                   JOIN route_directions d ON d.id = rs.direction_id
                   JOIN bus_stops s ON s.id = rs.stop_id
                   ORDER BY d.route_id, rs.direction_id, rs.stop_sequence, rs.id""")
            route_stops = _rows_to_dicts(cursor.fetchall())

            # -- stops (all, including ones not assigned to any route) ------------
            cursor.execute(
                """SELECT id, stop_name, latitude, longitude, address, source_id,
                          status, created_at, updated_at
                   FROM bus_stops ORDER BY id""")
            stops = _rows_to_dicts(cursor.fetchall())

            # -- segments and shapes ----------------------------------------------
            cursor.execute(
                """SELECT id, direction_id, from_stop_id, to_stop_id,
                          segment_sequence, source_id, created_at
                   FROM route_segments ORDER BY direction_id, segment_sequence, id""")
            segments = _rows_to_dicts(cursor.fetchall())

            cursor.execute(
                """SELECT id, direction_id, geojson, created_at, updated_at
                   FROM route_shapes ORDER BY id""")
            raw_shapes = cursor.fetchall()
            shapes = []
            for row in raw_shapes:
                geojson = row["geojson"]
                if isinstance(geojson, str):
                    try:
                        geojson = json.loads(geojson)
                    except json.JSONDecodeError:
                        pass  # keep the raw string exactly as stored
                shapes.append({
                    "id": int(row["id"]),
                    "direction_id": int(row["direction_id"]),
                    "geojson": geojson,
                    "created_at": _plain(row["created_at"]),
                    "updated_at": _plain(row["updated_at"]),
                })

    # ---- derived audit views (no data modification) -------------------------
    route_ids = {r["id"] for r in routes}
    direction_route = {d["id"]: d["route_id"] for d in directions}
    stop_ids = {s["id"] for s in stops}
    assigned_stop_ids = {assoc["stop_id"] for assoc in route_stops}

    routes_export = []
    for route in routes:
        route_directions = [d["id"] for d in directions if d["route_id"] == route["id"]]
        routes_export.append({
            **route,
            "direction_ids": route_directions,
            "category_ids": [
                m["category_id"] for m in category_map
                if m["route_id"] == route["id"]],
        })

    zero_stop_routes = [
        route["id"] for route in routes_export
        if not any(assoc["route_id"] == route["id"] for assoc in route_stops)]

    unassigned_stops = sorted(stop_ids - assigned_stop_ids)

    # Coordinates are NOT NULL in the schema; flag NULLs (should be none) and
    # the 0/0 sentinel in case a source row carried placeholder coordinates.
    def _coord_missing(stop):
        lat, lng = stop.get("latitude"), stop.get("longitude")
        if lat is None or lng is None:
            return True
        return float(lat) == 0.0 and float(lng) == 0.0

    missing_coord_stop_ids = sorted(s["id"] for s in stops if _coord_missing(s))
    routes_with_missing_coords = sorted({
        assoc["route_id"] for assoc in route_stops
        if assoc["stop_id"] in set(missing_coord_stop_ids)})

    shaped_directions = {shape["direction_id"] for shape in shapes}
    routes_with_missing_geometry = sorted({
        route["id"] for route in routes_export
        if not any(d["id"] in shaped_directions for d in directions
                   if d["route_id"] == route["id"])})

    # Orphan checks (referential integrity as observed, read-only).
    orphans = {
        "route_stops_with_unknown_direction": sorted({
            a["id"] for a in route_stops if a["direction_id"] not in direction_route}),
        "route_stops_with_unknown_stop": sorted({
            a["id"] for a in route_stops if a["stop_id"] not in stop_ids}),
        "directions_with_unknown_route": sorted({
            d["id"] for d in directions if d["route_id"] not in route_ids}),
        "category_map_with_unknown_route": sorted([
            m["route_id"] for m in category_map if m["route_id"] not in route_ids]),
        "segments_with_unknown_direction": sorted({
            s["id"] for s in segments if s["direction_id"] not in direction_route}),
        "shapes_with_unknown_direction": sorted({
            s["id"] for s in shapes if s["direction_id"] not in direction_route}),
    }

    routes_by_status = {}
    for route in routes:
        routes_by_status.setdefault(str(route["status"]), 0)
        routes_by_status[str(route["status"])] += 1

    routes_by_family = {}
    category_name = {c["id"]: c["name"] for c in categories}
    mapped_routes = {m["route_id"] for m in category_map}
    for m in category_map:
        name = str(category_name.get(m["category_id"], f"category {m['category_id']}"))
        routes_by_family.setdefault(name, 0)
        routes_by_family[name] += 1
    uncategorised = len([r for r in routes if r["id"] not in mapped_routes])
    if uncategorised:
        routes_by_family["(no category assigned)"] = uncategorised

    export = {
        "export_metadata": {
            "purpose": "complete read-only route database export for independent audit",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "database": app.config["DB_CONFIG"]["database"],
            "read_only": True,
            "excluded_tables": ["admin_users", "audit_logs", "schema_migrations"],
            "excluded_columns": ["data_sources.verified_by (user account reference)"],
            "notes": [
                "Original IDs and stored values are preserved; no normalisation, "
                "correction or modification was applied.",
                "Decimal coordinates are serialised as floats at their stored precision.",
                "route_shapes.geojson values are kept exactly as stored (parsed JSON).",
            ],
        },
        "sources": sources,
        "operators": operators,
        "route_categories": categories,
        "route_category_map": category_map,
        "routes": routes_export,
        "directions": directions,
        "route_stops": route_stops,
        "stops": stops,
        "route_segments": segments,
        "route_shapes": shapes,
        "validation": {
            "counts": {
                "sources": len(sources),
                "operators": len(operators),
                "route_categories": len(categories),
                "route_category_map_rows": len(category_map),
                "routes": len(routes),
                "directions": len(directions),
                "route_stops": len(route_stops),
                "stops": len(stops),
                "route_segments": len(segments),
                "route_shapes": len(shapes),
            },
            "routes_by_status": routes_by_status,
            "routes_by_family": routes_by_family,
            "zero_stop_route_ids": zero_stop_routes,
            "unassigned_stop_ids": unassigned_stops,
            "stops_with_missing_coordinates": {
                "stop_ids": missing_coord_stop_ids,
                "note": "latitude/longitude are NOT NULL in the schema; NULL is "
                        "impossible. Only NULL (defensive) and the 0/0 sentinel "
                        "are flagged.",
            },
            "route_ids_with_missing_coordinate_stops": routes_with_missing_coords,
            "route_ids_with_missing_geometry": routes_with_missing_geometry,
            "routes_with_any_geometry": sorted(
                set(route_ids) - set(routes_with_missing_geometry)),
            "orphan_foreign_keys": orphans,
        },
    }
    return export


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    export = export_database()

    counts = export["validation"]["counts"]
    print("Counts:", json.dumps(counts))
    print("routes_by_status:", json.dumps(export["validation"]["routes_by_status"]))
    print("routes_by_family:", json.dumps(export["validation"]["routes_by_family"]))
    print("zero-stop routes:", len(export["validation"]["zero_stop_route_ids"]))
    print("unassigned stops:", len(export["validation"]["unassigned_stop_ids"]))
    orphans = export["validation"]["orphan_foreign_keys"]
    print("orphans:", {k: len(v) for k, v in orphans.items()})

    if not args.build:
        print("DRY RUN: no files changed; pass --build to write the export.")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    size_kb = round(OUTPUT_PATH.stat().st_size / 1024, 1)
    print(f"Export written to {OUTPUT_PATH} ({size_kb} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
