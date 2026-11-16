"""Idempotently seed SMTA route catalogue metadata (not stop coordinates or geometry).

Dry-run by default. Apply only with:
  python scripts/import_smta_catalog.py --apply --confirm-database karachi_buses

This script never creates fake coordinates, route_stops or route_shapes. All imported
routes remain under_review except SMTA-listed inactive routes (inactive).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
from config import Config  # noqa: E402

CATALOG = ROOT / "data" / "imports" / "smta_karachi_route_catalog.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write records; otherwise perform a dry run")
    parser.add_argument("--confirm-database", help="must exactly match the connected database name")
    args = parser.parse_args()
    data = json.loads(CATALOG.read_text(encoding="utf-8"))

    connection = None
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE() AS db_name, VERSION() AS server_version")
        identity = cursor.fetchone()
        db_name = identity["db_name"]
        print(f"Connected database: {db_name}; MySQL: {identity['server_version']}")
        if not db_name:
            raise RuntimeError("No default database selected.")
        if args.apply and args.confirm_database != db_name:
            raise RuntimeError("Refusing write: --confirm-database must exactly match SELECT DATABASE().")
        required = {"data_sources", "bus_operators", "route_categories", "bus_routes",
                    "route_category_map", "route_directions"}
        cursor.execute("SHOW TABLES")
        tables = {next(iter(row.values())) for row in cursor.fetchall()}
        missing = required - tables
        if missing:
            raise RuntimeError("Required schema tables missing: " + ", ".join(sorted(missing)))

        print(f"Catalog contains {len(data['routes'])} route identities.")
        if not args.apply:
            print("DRY RUN ONLY. No records written. Review the catalogue, then rerun with --apply --confirm-database <exact database name>.")
            return 0

        connection.start_transaction()
        source_ids = {}
        for source in data["sources"]:
            cursor.execute("SELECT id FROM data_sources WHERE source_name=%s ORDER BY id LIMIT 1", (source["name"],))
            row = cursor.fetchone()
            if row:
                source_ids[source["key"]] = row["id"]
            else:
                cursor.execute(
                    "INSERT INTO data_sources (source_name, source_url, notes, verification_status) VALUES (%s,%s,%s,'pending')",
                    (source["name"], source["url"], source["notes"]),
                )
                source_ids[source["key"]] = cursor.lastrowid

        operator_id = None
        op = data["operator"]
        cursor.execute("SELECT id FROM bus_operators WHERE name=%s", (op["name"],))
        row = cursor.fetchone()
        if row:
            operator_id = row["id"]
        else:
            cursor.execute("INSERT INTO bus_operators (name, website) VALUES (%s,%s)", (op["name"], op["website"]))
            operator_id = cursor.lastrowid

        inserted = skipped = directions_added = 0
        for route in data["routes"]:
            source_id = source_ids[route["source"]]
            cursor.execute("SELECT id FROM bus_routes WHERE route_code=%s", (route["code"],))
            existing = cursor.fetchone()
            if existing:
                route_id = existing["id"]
                skipped += 1
            else:
                assigned_operator = operator_id if route["category"] in {"Pink Bus", "Red Bus", "EV Bus", "Double Decker"} else None
                description = json.dumps({
                    "published_via_stops": route["stops"],
                    "published_distance_km": route.get("distance_km"),
                    "catalog_retrieved_on": data["retrieved_on"],
                    "catalog_policy": data["import_policy"],
                }, ensure_ascii=False)
                cursor.execute(
                    "INSERT INTO bus_routes (operator_id, source_id, route_code, route_name, description, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    (assigned_operator, source_id, route["code"], route["name"], description, route["status"]),
                )
                route_id = cursor.lastrowid
                inserted += 1

            direction_name = "Published forward alignment"
            cursor.execute(
                "SELECT id FROM route_directions WHERE route_id=%s AND direction_name=%s",
                (route_id, direction_name),
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO route_directions (route_id, direction_name, start_label, end_label) VALUES (%s,%s,%s,%s)",
                    (route_id, direction_name, route["start"], route["end"]),
                )
                directions_added += 1

            cursor.execute("SELECT id FROM route_categories WHERE name=%s", (route["category"],))
            category = cursor.fetchone()
            if category:
                category_id = category["id"]
            else:
                cursor.execute("INSERT INTO route_categories (name, description) VALUES (%s,%s)",
                               (route["category"], "Service type from SMTA Karachi route catalogue."))
                category_id = cursor.lastrowid
            cursor.execute(
                "INSERT IGNORE INTO route_category_map (route_id, category_id) VALUES (%s,%s)",
                (route_id, category_id),
            )

        connection.commit()
        print(f"Import committed. New routes: {inserted}; existing routes preserved: {skipped}; directions added: {directions_added}.")
        print("No bus_stops, route_stops, or route_shapes were created. No route was activated.")
        return 0
    except Exception as exc:
        if connection is not None and connection.is_connected():
            connection.rollback()
        print(f"Import not committed: {exc}", file=sys.stderr)
        return 1
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
