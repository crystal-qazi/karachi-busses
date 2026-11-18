"""Import the published 2024 historical Karachi network dataset without asserting current service.

Required files:
  data/imports/karachi_bus_network_cleaned_nodes.csv
  data/imports/karachi_bus_network_cleaned_edges.csv

Dataset provenance: Zenodo DOI 10.5281/zenodo.13951512 (Data Research Lab Pakistan,
published 2024-10-18). The authors describe route compilation from Travel Culture and
HamariWeb and coordinate extraction from Google Maps. No per-stop source pins or
current operator validation are supplied. The publisher companion project page declares CC BY 4.0;
the Zenodo page's visible Rights field shows no value, so record this distinction accurately.
The importer records the source as pending because it is not current operator evidence.

Dry-run by default. Apply only after backup:
  python scripts/import_historical_network.py --apply --confirm-database karachi_buses

All created stops/routes remain under_review; the source remains pending. No route is activated.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
from config import Config  # noqa: E402

NODES_FILE = ROOT / "data" / "imports" / "karachi_bus_network_cleaned_nodes.csv"
EDGES_FILE = ROOT / "data" / "imports" / "karachi_bus_network_cleaned_edges.csv"
SOURCE_NAME = "Karachi Bus Network Research Dataset (user-provided cleaned files)"
SOURCE_URL = "https://zenodo.org/records/13951512"
SOURCE_NOTES = (
    "Historical 2024 research dataset, Version v1, published 2024-10-18 by Data Research Lab Pakistan; "
    "creators: Muhammad Qasim Pasta (curator), Moid Raza Khan and Fatima Aslam (collectors), Habib University. "
    "The Zenodo description says 76 Karachi public bus routes (BRT and minibuses) were compiled from "
    "Travel Culture and HamariWeb, with stop coordinates extracted using Google Maps. "
    "The node/edge files are historical secondary research, not current operator GPS or proof of current service. "
    "No per-stop source pins or capture dates are supplied. The publisher companion project page declares CC BY 4.0; "
    "the Zenodo page's visible Rights field shows no value, so preserve this metadata distinction. "
    "Keep verification_status pending and imported stops/routes under_review because this is historical data."
)
CATEGORY_NAME = "Historical / Unverified Network"
DIRECTION_NAME = "Source-listed network (unverified)"


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required input file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def display_stop_name(key: str) -> str:
    words = key.replace("-", " ").replace("_", " ").split()
    rendered = []
    for word in words:
        if word.isdigit():
            rendered.append(word)
        elif word.lower() in {"m.a", "nipa", "kda", "kpt", "ftc", "f.b"}:
            rendered.append(word.upper())
        else:
            rendered.append(word[:1].upper() + word[1:])
    return " ".join(rendered)[:180]


def validate_dataset(nodes: list[dict[str, str]], edges: list[dict[str, str]]) -> dict:
    node_coords: dict[str, tuple[float, float]] = {}
    for row in nodes:
        key = row["node"].strip()
        if not key or key in node_coords:
            raise ValueError(f"Blank or duplicate node key: {key!r}")
        lat, lon = float(row["latit"]), float(row["long"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinates for {key}: {lat}, {lon}")
        node_coords[key] = (lat, lon)

    route_edges: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in edges:
        route = row["bus_name"].strip()
        start, end = row["stop1"].strip(), row["stop2"].strip()
        if not route or not start or not end:
            raise ValueError("Blank route code or edge endpoint found.")
        if start not in node_coords or end not in node_coords:
            raise ValueError(f"Edge references unknown node: {route}: {start} -> {end}")
        route_edges[route].append((start, end))

    if not route_edges:
        raise ValueError("No route edges found.")
    return {"node_coords": node_coords, "route_edges": route_edges}


def linear_order(edges: list[tuple[str, str]]) -> list[str] | None:
    """Return a stop sequence only when the directed graph is exactly one simple path."""
    outgoing = Counter(a for a, _ in edges)
    incoming = Counter(b for _, b in edges)
    nodes = set(outgoing) | set(incoming)
    if any(outgoing[n] > 1 or incoming[n] > 1 for n in nodes):
        return None
    starts = [n for n in nodes if incoming[n] == 0 and outgoing[n] == 1]
    ends = [n for n in nodes if outgoing[n] == 0 and incoming[n] == 1]
    if len(starts) != 1 or len(ends) != 1 or len(edges) != len(nodes) - 1:
        return None
    next_stop = {a: b for a, b in edges}
    sequence = [starts[0]]
    while sequence[-1] in next_stop:
        sequence.append(next_stop[sequence[-1]])
        if len(sequence) > len(nodes):
            return None
    return sequence if len(sequence) == len(nodes) and sequence[-1] == ends[0] else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write data; default is dry-run")
    parser.add_argument("--confirm-database", help="must exactly match SELECT DATABASE()")
    args = parser.parse_args()

    nodes = read_csv(NODES_FILE, {"node", "latit", "long"})
    edges = read_csv(EDGES_FILE, {"stop1", "stop2", "bus_name"})
    dataset = validate_dataset(nodes, edges)
    node_coords = dataset["node_coords"]
    route_edges = dataset["route_edges"]
    linear_routes = {route: linear_order(items) for route, items in route_edges.items()}
    simple_count = sum(sequence is not None for sequence in linear_routes.values())

    print(f"Node rows: {len(nodes)}")
    print(f"Directed edge rows: {len(edges)}")
    print(f"Distinct route identifiers: {len(route_edges)}")
    print(f"Routes representable as one simple stop sequence: {simple_count}")
    print(f"Branching/cyclic/non-linear routes retained as segments only: {len(route_edges) - simple_count}")
    print("All source records will remain unverified; no routes will be activated.")

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

        required_tables = {"data_sources", "bus_routes", "route_directions", "bus_stops", "route_stops", "route_segments"}
        cursor.execute("SHOW TABLES")
        tables = {next(iter(row.values())) for row in cursor.fetchall()}
        missing = required_tables - tables
        if missing:
            raise RuntimeError("Required tables missing; apply migrations first: " + ", ".join(sorted(missing)))

        if not args.apply:
            print("DRY RUN ONLY. No records written.")
            return 0

        # End the implicit read transaction opened by the preflight SELECTs.
        connection.commit()
        connection.start_transaction()

        cursor.execute("SELECT id FROM data_sources WHERE source_name=%s ORDER BY id LIMIT 1", (SOURCE_NAME,))
        source_row = cursor.fetchone()
        if source_row:
            source_id = source_row["id"]
        else:
            cursor.execute(
                "INSERT INTO data_sources (source_name, source_url, notes, verification_status) "
                "VALUES (%s,%s,%s,'pending')",
                (SOURCE_NAME, SOURCE_URL, SOURCE_NOTES),
            )
            source_id = cursor.lastrowid

        # Refresh provenance metadata for an existing matching source row without
        # changing its verification_status. This runs only with --apply.
        cursor.execute(
            "UPDATE data_sources SET source_url=%s, notes=%s WHERE id=%s",
            (SOURCE_URL, SOURCE_NOTES, source_id),
        )

        stop_ids: dict[str, int] = {}
        new_stops = 0
        for key, (lat, lon) in node_coords.items():
            name = display_stop_name(key)
            cursor.execute(
                "SELECT id FROM bus_stops WHERE source_id=%s AND stop_name=%s "
                "AND latitude=%s AND longitude=%s ORDER BY id LIMIT 1",
                (source_id, name, lat, lon),
            )
            found = cursor.fetchone()
            if found:
                stop_ids[key] = found["id"]
            else:
                cursor.execute(
                    "INSERT INTO bus_stops (stop_name, latitude, longitude, address, source_id, status) "
                    "VALUES (%s,%s,%s,%s,%s,'under_review')",
                    (name, lat, lon, f"Source node key: {key}", source_id),
                )
                stop_ids[key] = cursor.lastrowid
                new_stops += 1

        new_routes = 0
        existing_routes = 0
        new_directions = 0
        new_segments = 0
        new_route_stops = 0
        non_linear_routes = 0

        cursor.execute(
            "SELECT id FROM route_categories WHERE name=%s",
            (CATEGORY_NAME,),
        )
        category_row = cursor.fetchone()
        if category_row:
            category_id = category_row["id"]
        else:
            cursor.execute(
                "INSERT INTO route_categories (name, description) VALUES (%s,%s)",
                (CATEGORY_NAME, "Unverified historical/source-listed network data; not a current-service claim."),
            )
            category_id = cursor.lastrowid

        for route_code, route_edge_list in route_edges.items():
            cursor.execute("SELECT id, source_id FROM bus_routes WHERE route_code=%s", (route_code,))
            route_row = cursor.fetchone()
            if route_row:
                if route_row["source_id"] != source_id:
                    existing_routes += 1
                    continue
                route_id = route_row["id"]
                existing_routes += 1
            else:
                description = json.dumps({
                    "dataset_classification": "historical_or_unverified",
                    "source_edge_count": len(route_edge_list),
                    "sequence_policy": "Only simple directed paths are mapped to route_stops; all edges are retained in route_segments.",
                    "operating_status": "unknown",
                })
                cursor.execute(
                    "INSERT INTO bus_routes (operator_id, source_id, route_code, route_name, description, status) "
                    "VALUES (NULL,%s,%s,%s,%s,'under_review')",
                    (source_id, route_code, route_code, description),
                )
                route_id = cursor.lastrowid
                new_routes += 1

            cursor.execute(
                "SELECT id FROM route_directions WHERE route_id=%s AND direction_name=%s",
                (route_id, DIRECTION_NAME),
            )
            direction_row = cursor.fetchone()
            if direction_row:
                direction_id = direction_row["id"]
            else:
                sequence = linear_routes[route_code]
                start_label = display_stop_name(sequence[0]) if sequence else None
                end_label = display_stop_name(sequence[-1]) if sequence else None
                cursor.execute(
                    "INSERT INTO route_directions (route_id, direction_name, start_label, end_label) "
                    "VALUES (%s,%s,%s,%s)",
                    (route_id, DIRECTION_NAME, start_label, end_label),
                )
                direction_id = cursor.lastrowid
                new_directions += 1

            cursor.execute(
                "INSERT IGNORE INTO route_category_map (route_id, category_id) VALUES (%s,%s)",
                (route_id, category_id),
            )

            cursor.execute("SELECT COUNT(*) AS total FROM route_segments WHERE direction_id=%s", (direction_id,))
            if cursor.fetchone()["total"] == 0:
                for seq, (start, end) in enumerate(route_edge_list, start=1):
                    cursor.execute(
                        "INSERT INTO route_segments "
                        "(direction_id, from_stop_id, to_stop_id, segment_sequence, source_id) "
                        "VALUES (%s,%s,%s,%s,%s)",
                        (direction_id, stop_ids[start], stop_ids[end], seq, source_id),
                    )
                    new_segments += 1

            stop_sequence = linear_routes[route_code]
            if stop_sequence:
                cursor.execute("SELECT COUNT(*) AS total FROM route_stops WHERE direction_id=%s", (direction_id,))
                if cursor.fetchone()["total"] == 0:
                    for seq, key in enumerate(stop_sequence, start=1):
                        cursor.execute(
                            "INSERT INTO route_stops (direction_id, stop_id, stop_sequence) VALUES (%s,%s,%s)",
                            (direction_id, stop_ids[key], seq),
                        )
                        new_route_stops += 1
            else:
                non_linear_routes += 1

        connection.commit()
        print(
            "Import committed. "
            f"New stops: {new_stops}; new routes: {new_routes}; existing routes preserved: {existing_routes}; "
            f"directions added: {new_directions}; segments added: {new_segments}; "
            f"ordered route-stop rows added: {new_route_stops}; non-linear routes: {non_linear_routes}."
        )
        print("All imported stops/routes remain under_review. No route_shapes were generated and no route was activated.")
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
