"""Direct and single-transfer journey discovery from static route data."""
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


@journey_api_bp.get("/journeys")
def journeys():
    try:
        origin_lat = float(request.args["origin_lat"])
        origin_lng = float(request.args["origin_lng"])
        radius = float(request.args.get("radius", "1500"))
        destination = (request.args.get("destination") or "").strip()
    except (KeyError, TypeError, ValueError):
        return _error("Provide origin_lat, origin_lng and destination.")
    if not all(math.isfinite(v) for v in (origin_lat, origin_lng, radius)):
        return _error("Origin coordinates and radius must be finite numbers.")
    if not -90 <= origin_lat <= 90 or not -180 <= origin_lng <= 180:
        return _error("Origin coordinates are outside valid ranges.")
    if not 100 <= radius <= 10_000:
        return _error("radius must be between 100 and 10,000 metres.")
    if len(destination) < 2 or len(destination) > 100:
        return _error("Destination must contain 2–100 characters.")

    try:
        with cursor_context() as (_, cursor):
            lat_delta = radius / 111_320
            lng_delta = min(radius / (111_320 * max(abs(math.cos(math.radians(origin_lat))), 0.01)), 180)
            term = "%" + destination + "%"
            cursor.execute("""
                SELECT d.id AS direction_id, d.direction_name, d.start_label, d.end_label,
                       r.id AS route_id, r.route_code, r.route_name, o.name AS operator_name,
                       s.id AS stop_id, s.stop_name, s.latitude, s.longitude, s.address,
                       rs.stop_sequence
                FROM route_directions d
                JOIN bus_routes r ON r.id=d.route_id AND r.status='active'
                JOIN data_sources route_source ON route_source.id=r.source_id AND route_source.verification_status='verified'
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                JOIN route_stops rs ON rs.direction_id=d.id
                JOIN bus_stops s ON s.id=rs.stop_id AND s.status='active'
                JOIN data_sources stop_source ON stop_source.id=s.source_id AND stop_source.verification_status='verified'
                WHERE EXISTS (
                    SELECT 1 FROM route_stops origin_rs
                    JOIN bus_stops origin_stop ON origin_stop.id=origin_rs.stop_id
                    JOIN data_sources origin_source ON origin_source.id=origin_stop.source_id
                      AND origin_source.verification_status='verified'
                    WHERE origin_rs.direction_id=d.id AND origin_stop.status='active'
                      AND origin_stop.latitude BETWEEN %s AND %s
                      AND origin_stop.longitude BETWEEN %s AND %s
                ) OR EXISTS (
                    SELECT 1 FROM route_stops destination_rs
                    JOIN bus_stops destination_stop ON destination_stop.id=destination_rs.stop_id
                    JOIN data_sources destination_source ON destination_source.id=destination_stop.source_id
                      AND destination_source.verification_status='verified'
                    WHERE destination_rs.direction_id=d.id AND destination_stop.status='active'
                      AND (destination_stop.stop_name LIKE %s OR destination_stop.address LIKE %s)
                )
                ORDER BY d.id, rs.stop_sequence
            """, (origin_lat-lat_delta, origin_lat+lat_delta,
                  origin_lng-lng_delta, origin_lng+lng_delta, term, term))
            rows = cursor.fetchall()
    except Exception:
        return _error("Journey search is temporarily unavailable.", "DATABASE_UNAVAILABLE", 503)

    directions = {}
    stops = {}
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
            "stops": [],
        })
        direction["stops"].append({**stop, "sequence": int(row["stop_sequence"])})

    destination_lower = destination.casefold()
    destination_stops = [
        stop for stop in stops.values()
        if destination_lower in stop["name"].casefold()
        or destination_lower in (stop["address"] or "").casefold()
    ]
    if not destination_stops:
        return jsonify(success=True, data={
            "destination_query": destination, "destination_matches": [],
            "journeys": [], "message": "No active bus stop matches this destination. Try a nearby stop or area name.",
        })

    origin_stops = [
        stop for stop in stops.values()
        if _distance(origin_lat, origin_lng, stop["lat"], stop["lng"]) <= radius
    ]
    origin_stops.sort(key=lambda stop: _distance(origin_lat, origin_lng, stop["lat"], stop["lng"]))
    if not origin_stops:
        return jsonify(success=True, data={
            "destination_query": destination,
            "destination_matches": destination_stops[:20],
            "journeys": [], "message": "No active route stops were found near your origin.",
        })

    origin_ids = {s["id"] for s in origin_stops}
    destination_ids = {s["id"] for s in destination_stops}
    candidates = []

    # Direct: board at or near origin, then pass a matching destination stop.
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
                        "legs": [{
                            "direction": {k: v for k, v in direction.items() if k != "stops"},
                            "board_stop": board, "alight_stop": alight,
                            "stops": seq[i:j + 1],
                        }],
                        "sort_distance": _distance(origin_lat, origin_lng, board["lat"], board["lng"]),
                    })
                    break

    # One transfer: first direction boards near origin; second direction continues
    # from a shared stop and reaches a matching destination stop.
    for first in directions.values():
        first_stops = first["stops"]
        for i, board in enumerate(first_stops):
            if board["id"] not in origin_ids:
                continue
            for j in range(i + 1, len(first_stops)):
                interchange = first_stops[j]
                for second in directions.values():
                    if second["id"] == first["id"]:
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
                                    {
                                        "direction": {x: y for x, y in first.items() if x != "stops"},
                                        "board_stop": board, "alight_stop": interchange,
                                        "stops": first_stops[i:j + 1],
                                    },
                                    {
                                        "direction": {x: y for x, y in second.items() if x != "stops"},
                                        "board_stop": transfer_board, "alight_stop": alight,
                                        "stops": second_stops[k:m + 1],
                                    },
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

    # Remove duplicate itineraries that differ only by a repeated match in a
    # route's stop list, then prefer fewer transfers and nearer boarding stops.
    unique = {}
    for item in candidates:
        key = (item["type"], tuple(leg["direction"]["id"] for leg in item["legs"]),
               item["origin_stop"]["id"], item["destination_stop"]["id"],
               item.get("transfer_stop", {}).get("id"))
        unique.setdefault(key, item)
    results = sorted(unique.values(), key=lambda item: (
        item["transfer_count"], item["sort_distance"],
        sum(len(leg["stops"]) for leg in item["legs"])
    ))[:20]
    for item in results:
        item.pop("sort_distance", None)
    return jsonify(success=True, data={
        "destination_query": destination,
        "destination_matches": destination_stops[:20],
        "origin_stop_count": len(origin_stops),
        "journeys": results,
        "journey_count": len(results),
        "message": None if results else "No direct or one-transfer journey was found using the currently published routes.",
    })
