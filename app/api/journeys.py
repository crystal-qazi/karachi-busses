"""Direct and single-transfer journey discovery between two map locations."""
import json
import math

from flask import Blueprint, jsonify, request

from app.database.helpers import cursor_context

journey_api_bp = Blueprint("journey_api", __name__)
EARTH_RADIUS_METRES = 6_371_000


def _error(message, code="INVALID_PARAMETER", status=400):
    return jsonify(success=False, error={"code": code, "message": message}), status


def _distance(a_lat, a_lng, b_lat, b_lng):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp = p2 - p1
    dl = math.radians(b_lng - a_lng)
    value = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_METRES * math.asin(min(1, math.sqrt(value)))


def _shape_value(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None
    return value


def _segment_shape(shape, start, end):
    """Return only the saved LineString section between the selected stops."""
    if not shape:
        return None
    if shape.get("type") == "Feature":
        shape = shape.get("geometry") or {}
    if shape.get("type") != "LineString":
        return None
    coordinates = shape.get("coordinates") or []
    if len(coordinates) < 2:
        return None

    def nearest_index(stop):
        return min(
            range(len(coordinates)),
            key=lambda i: (coordinates[i][0] - stop["lng"]) ** 2
            + (coordinates[i][1] - stop["lat"]) ** 2,
        )

    first, last = nearest_index(start), nearest_index(end)
    if first == last:
        return None
    if last > first:
        segment = coordinates[first:last + 1]
    else:
        segment = list(reversed(coordinates[last:first + 1]))
    if len(segment) < 2:
        return None
    return {"type": "LineString", "coordinates": segment}


def _make_leg(direction, board, alight, stops):
    return {
        "direction": {
            key: value for key, value in direction.items()
            if key not in {"stops", "shape"}
        },
        "board_stop": board,
        "alight_stop": alight,
        "stops": stops,
        "shape": _segment_shape(direction.get("shape"), board, alight),
    }


@journey_api_bp.get("/journeys")
def journeys():
    try:
        origin_lat = float(request.args["origin_lat"])
        origin_lng = float(request.args["origin_lng"])
        destination_lat = float(request.args["destination_lat"])
        destination_lng = float(request.args["destination_lng"])
        radius = float(request.args.get("radius", "1500"))
    except (KeyError, TypeError, ValueError):
        return _error("Provide valid From and To coordinates.")
    values = (origin_lat, origin_lng, destination_lat, destination_lng, radius)
    if not all(math.isfinite(value) for value in values):
        return _error("Coordinates and radius must be finite numbers.")
    if not -90 <= origin_lat <= 90 or not -90 <= destination_lat <= 90:
        return _error("Latitude values must be between -90 and 90.")
    if not -180 <= origin_lng <= 180 or not -180 <= destination_lng <= 180:
        return _error("Longitude values must be between -180 and 180.")
    if not 100 <= radius <= 10_000:
        return _error("radius must be between 100 and 10,000 metres.")

    try:
        with cursor_context() as (_, cursor):
            cursor.execute("""
                SELECT d.id AS direction_id, d.direction_name, d.start_label, d.end_label,
                       r.id AS route_id, r.route_code, r.route_name, o.name AS operator_name,
                       s.id AS stop_id, s.stop_name, s.latitude, s.longitude, s.address,
                       rs.stop_sequence, sh.geojson AS shape_geojson
                FROM route_directions d
                JOIN bus_routes r ON r.id=d.route_id AND r.status='active'
                JOIN data_sources route_source ON route_source.id=r.source_id
                  AND route_source.verification_status='verified'
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                JOIN route_stops rs ON rs.direction_id=d.id
                JOIN bus_stops s ON s.id=rs.stop_id AND s.status='active'
                JOIN data_sources stop_source ON stop_source.id=s.source_id
                  AND stop_source.verification_status='verified'
                LEFT JOIN route_shapes sh ON sh.direction_id=d.id
                ORDER BY d.id, rs.stop_sequence
            """)
            rows = cursor.fetchall()
    except Exception:
        return _error("Journey search is temporarily unavailable.", "DATABASE_UNAVAILABLE", 503)

    directions, stops = {}, {}
    for row in rows:
        stop_id = int(row["stop_id"])
        stop = stops.setdefault(stop_id, {
            "id": stop_id, "name": row["stop_name"],
            "lat": float(row["latitude"]), "lng": float(row["longitude"]),
            "address": row.get("address"),
        })
        direction_id = int(row["direction_id"])
        direction = directions.setdefault(direction_id, {
            "id": direction_id, "name": row["direction_name"],
            "start": row.get("start_label"), "end": row.get("end_label"),
            "route": {
                "id": int(row["route_id"]), "code": row["route_code"],
                "name": row["route_name"], "operator": row.get("operator_name"),
            },
            "shape": _shape_value(row.get("shape_geojson")),
            "stops": [],
        })
        direction["stops"].append({**stop, "sequence": int(row["stop_sequence"])})

    origin_stops = [
        stop for stop in stops.values()
        if _distance(origin_lat, origin_lng, stop["lat"], stop["lng"]) <= radius
    ]
    destination_stops = [
        stop for stop in stops.values()
        if _distance(destination_lat, destination_lng, stop["lat"], stop["lng"]) <= radius
    ]
    origin_stops.sort(key=lambda stop: _distance(origin_lat, origin_lng, stop["lat"], stop["lng"]))
    destination_stops.sort(key=lambda stop: _distance(destination_lat, destination_lng, stop["lat"], stop["lng"]))

    if not origin_stops or not destination_stops:
        message = (
            "No active published bus stops were found near your starting location."
            if not origin_stops else
            "No active published bus stops were found near your destination."
        )
        return jsonify(success=True, data={
            "origin_stop_count": len(origin_stops),
            "destination_stop_count": len(destination_stops),
            "journeys": [], "journey_count": 0, "message": message,
        })

    origin_ids = {stop["id"] for stop in origin_stops}
    destination_ids = {stop["id"] for stop in destination_stops}
    candidates = []

    # A direct journey is valid only when the same direction serves From then To.
    for direction in directions.values():
        seq = direction["stops"]
        for i, board in enumerate(seq):
            if board["id"] not in origin_ids:
                continue
            for j in range(i + 1, len(seq)):
                alight = seq[j]
                if alight["id"] in destination_ids:
                    candidates.append({
                        "type": "direct", "transfer_count": 0,
                        "origin_stop": board, "destination_stop": alight,
                        "legs": [_make_leg(direction, board, alight, seq[i:j + 1])],
                        "sort_distance": _distance(origin_lat, origin_lng, board["lat"], board["lng"]),
                    })
                    break

    # One-transfer journeys must share a real published interchange stop.
    for first in directions.values():
        first_stops = first["stops"]
        for i, board in enumerate(first_stops):
            if board["id"] not in origin_ids:
                continue
            for j in range(i + 1, len(first_stops)):
                interchange = first_stops[j]
                for second in directions.values():
                    if second["route"]["id"] == first["route"]["id"]:
                        continue
                    second_stops = second["stops"]
                    for k, transfer_board in enumerate(second_stops):
                        if transfer_board["id"] != interchange["id"]:
                            continue
                        for m in range(k + 1, len(second_stops)):
                            alight = second_stops[m]
                            if alight["id"] not in destination_ids:
                                continue
                            candidates.append({
                                "type": "one_transfer", "transfer_count": 1,
                                "origin_stop": board, "transfer_stop": interchange,
                                "destination_stop": alight,
                                "legs": [
                                    _make_leg(first, board, interchange, first_stops[i:j + 1]),
                                    _make_leg(second, transfer_board, alight, second_stops[k:m + 1]),
                                ],
                                "sort_distance": _distance(origin_lat, origin_lng, board["lat"], board["lng"]),
                            })
                            break
                        else:
                            continue
                        break
                    else:
                        continue
                    break

    unique = {}
    for item in candidates:
        key = (item["type"], tuple(leg["direction"]["id"] for leg in item["legs"]),
               item["origin_stop"]["id"], item["destination_stop"]["id"],
               item.get("transfer_stop", {}).get("id"))
        unique.setdefault(key, item)
    results = sorted(unique.values(), key=lambda item: (
        item["transfer_count"], item["sort_distance"],
        sum(len(leg["stops"]) for leg in item["legs"])
    ))[:30]
    for item in results:
        item.pop("sort_distance", None)
    return jsonify(success=True, data={
        "origin_stop_count": len(origin_stops),
        "destination_stop_count": len(destination_stops),
        "journeys": results,
        "journey_count": len(results),
        "message": None if results else
            "No direct or one-transfer journey was found using the currently published routes.",
    })
