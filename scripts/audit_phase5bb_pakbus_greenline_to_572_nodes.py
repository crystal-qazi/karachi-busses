#!/usr/bin/env python3
"""Cross-check PakBus Green Line stop candidates against historical Karachi nodes.

This is a proximity QA tool only. It does not create aliases, verify physical stops,
or modify the application database.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "research" / "PHASE_5BB_PAKBUS_GREENLINE_STOP_CANDIDATES.csv"
HISTORICAL = ROOT / "data" / "imports" / "karachi_bus_network_cleaned_nodes.csv"
OUTPUT = ROOT / "data" / "research" / "PHASE_5BB_PAKBUS_GREENLINE_TO_572_NODE_CANDIDATE_CROSSWALK.csv"
EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in metres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def read_historical_nodes(path: Path = HISTORICAL) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        nodes = []
        for row in rows:
            nodes.append(
                {
                    "node": row["node"],
                    "latitude": float(row["latit"]),
                    "longitude": float(row["long"]),
                }
            )
    return nodes


def build_crosswalk(
    source_path: Path = SOURCE, historical_path: Path = HISTORICAL
) -> list[dict[str, object]]:
    nodes = read_historical_nodes(historical_path)
    if len(nodes) != 572:
        raise ValueError(f"Expected 572 historical node rows, found {len(nodes)}")

    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))

    output = []
    for candidate in candidates:
        lat = float(candidate["latitude"])
        lon = float(candidate["longitude"])
        nearest = min(
            nodes,
            key=lambda node: haversine_m(
                lat,
                lon,
                float(node["latitude"]),
                float(node["longitude"]),
            ),
        )
        distance = haversine_m(
            lat,
            lon,
            float(nearest["latitude"]),
            float(nearest["longitude"]),
        )
        output.append(
            {
                "sequence": candidate["sequence"],
                "pakbus_stop_id": candidate["stop_id"],
                "pakbus_stop_name": candidate["stop_name"],
                "pakbus_latitude": candidate["latitude"],
                "pakbus_longitude": candidate["longitude"],
                "nearest_historical_node": nearest["node"],
                "nearest_historical_latitude": nearest["latitude"],
                "nearest_historical_longitude": nearest["longitude"],
                "nearest_distance_m": f"{distance:.1f}",
                "decision": "candidate_only_no_alias_or_coordinate_change",
            }
        )
    return output


def write_crosswalk(rows: list[dict[str, object]], path: Path = OUTPUT) -> None:
    fields = [
        "sequence",
        "pakbus_stop_id",
        "pakbus_stop_name",
        "pakbus_latitude",
        "pakbus_longitude",
        "nearest_historical_node",
        "nearest_historical_latitude",
        "nearest_historical_longitude",
        "nearest_distance_m",
        "decision",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = build_crosswalk()
    write_crosswalk(rows)
    print(f"Wrote {len(rows)} candidate matches to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
