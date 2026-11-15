"""Public read-only APIs for static Karachi bus route discovery."""
import json
import math
from flask import Blueprint, jsonify, request
from app.database.helpers import cursor_context

public_api_bp = Blueprint("public_api", __name__)
EARTH_RADIUS_METRES = 6_371_000
DEFAULT_RADIUS_METRES = 1_500


def _error(message, code="INVALID_PARAMETER", status=400):
    return jsonify(success=False, error={"code": code, "message": message}), status


def _shape_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return None
    return value


@public_api_bp.get("/discover/nearby")
def nearby():
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
        radius = float(request.args.get("radius", DEFAULT_RADIUS_METRES))
        limit = int(request.args.get("limit", "50"))
    except (KeyError, TypeError, ValueError):
        return _error("Provide valid lat, lng, radius and limit parameters.")
    if not all(math.isfinite(v) for v in (lat, lng, radius)):
        return _error("Coordinates and radius must be finite numbers.")
    if not -90 <= lat <= 90:
        return _error("lat must be between -90 and 90.")
    if not -180 <= lng <= 180:
        return _error("lng must be between -180 and 180.")
    if not 100 <= radius <= 10_000:
        return _error("radius must be between 100 and 10,000 metres.")
    if not 1 <= limit <= 100:
        return _error("limit must be between 1 and 100.")

    lat_delta = radius / 111_320
    cos_lat = max(abs(math.cos(math.radians(lat))), 0.01)
    lng_delta = min(radius / (111_320 * cos_lat), 180)
    distance_sql = """(2 * %s * ASIN(SQRT(
        POWER(SIN(RADIANS(s.latitude - %s) / 2), 2) +
        COS(RADIANS(%s)) * COS(RADIANS(s.latitude)) *
        POWER(SIN(RADIANS(s.longitude - %s) / 2), 2)
    )))"""
    sql = f"""
        SELECT s.id AS stop_id, s.stop_name, s.latitude, s.longitude, s.address,
               d.id AS direction_id, d.direction_name, d.start_label, d.end_label,
               r.id AS route_id, r.route_code, r.route_name, o.name AS operator_name,
               {distance_sql} AS distance_metres
        FROM bus_stops s
        JOIN route_stops rs ON rs.stop_id=s.id
        JOIN route_directions d ON d.id=rs.direction_id
        JOIN bus_routes r ON r.id=d.route_id
        LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
        WHERE s.status='active' AND r.status='active'
          AND s.latitude BETWEEN %s AND %s
          AND s.longitude BETWEEN %s AND %s
          AND {distance_sql} <= %s
        ORDER BY distance_metres ASC, r.route_code ASC, d.direction_name ASC
        LIMIT %s
    """
    params = (
        EARTH_RADIUS_METRES, lat, lat, lng,
        lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta,
        EARTH_RADIUS_METRES, lat, lat, lng, radius, limit,
    )
    try:
        with cursor_context() as (_, cursor):
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    except Exception:
        return _error("Nearby route search is temporarily unavailable.", "DATABASE_UNAVAILABLE", 503)

    stops = {}
    for row in rows:
        stop_id = int(row["stop_id"])
        stop = stops.setdefault(stop_id, {
            "id": stop_id, "name": row["stop_name"],
            "lat": float(row["latitude"]), "lng": float(row["longitude"]),
            "address": row.get("address"),
            "distance_metres": round(float(row["distance_metres"]), 1),
            "directions": [],
        })
        direction_id = int(row["direction_id"])
        if not any(item["id"] == direction_id for item in stop["directions"]):
            stop["directions"].append({
                "id": direction_id, "name": row["direction_name"],
                "start": row.get("start_label"), "end": row.get("end_label"),
                "route": {
                    "id": int(row["route_id"]), "code": row["route_code"],
                    "name": row["route_name"], "operator": row.get("operator_name"),
                },
            })
    result = sorted(stops.values(), key=lambda item: item["distance_metres"])
    return jsonify(success=True, data={
        "origin": {"lat": lat, "lng": lng}, "radius_metres": radius,
        "stop_count": len(result), "stops": result,
    })


@public_api_bp.get("/directions/<int:direction_id>")
def public_direction(direction_id):
    try:
        with cursor_context() as (_, cursor):
            cursor.execute("""
                SELECT d.id, d.direction_name, d.start_label, d.end_label,
                       r.id AS route_id, r.route_code, r.route_name, o.name AS operator_name
                FROM route_directions d
                JOIN bus_routes r ON r.id=d.route_id
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                WHERE d.id=%s AND r.status='active'
            """, (direction_id,))
            direction = cursor.fetchone()
            if not direction:
                return _error("Active route direction not found.", "NOT_FOUND", 404)
            cursor.execute("""
                SELECT s.id, s.stop_name, s.latitude, s.longitude, s.address, rs.stop_sequence
                FROM route_stops rs JOIN bus_stops s ON s.id=rs.stop_id
                WHERE rs.direction_id=%s AND s.status='active'
                ORDER BY rs.stop_sequence
            """, (direction_id,))
            stop_rows = cursor.fetchall()
            cursor.execute("SELECT geojson FROM route_shapes WHERE direction_id=%s", (direction_id,))
            shape_row = cursor.fetchone()
    except Exception:
        return _error("Route details are temporarily unavailable.", "DATABASE_UNAVAILABLE", 503)

    shape = _shape_value(shape_row["geojson"]) if shape_row else None
    return jsonify(success=True, data={
        "direction": {
            "id": int(direction["id"]), "name": direction["direction_name"],
            "start": direction.get("start_label"), "end": direction.get("end_label"),
            "route": {
                "id": int(direction["route_id"]), "code": direction["route_code"],
                "name": direction["route_name"], "operator": direction.get("operator_name"),
            },
        },
        "stops": [{
            "id": int(row["id"]), "name": row["stop_name"],
            "lat": float(row["latitude"]), "lng": float(row["longitude"]),
            "address": row.get("address"), "sequence": int(row["stop_sequence"]),
        } for row in stop_rows],
        "shape": shape,
    })


@public_api_bp.get("/search")
def search():
    query = (request.args.get("q") or "").strip()
    if len(query) < 2:
        return _error("Search text must contain at least 2 characters.")
    if len(query) > 100:
        return _error("Search text must be 100 characters or fewer.")
    term = "%" + query + "%"
    try:
        with cursor_context() as (_, cursor):
            cursor.execute("""
                SELECT r.id, r.route_code, r.route_name, o.name AS operator_name,
                       d.id AS direction_id, d.direction_name, d.start_label, d.end_label
                FROM bus_routes r
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                LEFT JOIN route_directions d ON d.route_id=r.id
                WHERE r.status='active'
                  AND (r.route_code LIKE %s OR r.route_name LIKE %s OR r.description LIKE %s
                       OR d.start_label LIKE %s OR d.end_label LIKE %s)
                ORDER BY r.route_code, d.id LIMIT 100
            """, (term, term, term, term, term))
            route_rows = cursor.fetchall()
            cursor.execute("""
                SELECT s.id, s.stop_name, s.latitude, s.longitude, s.address
                FROM bus_stops s
                WHERE s.status='active' AND (s.stop_name LIKE %s OR s.address LIKE %s)
                ORDER BY s.stop_name LIMIT 50
            """, (term, term))
            stop_rows = cursor.fetchall()
    except Exception:
        return _error("Search is temporarily unavailable.", "DATABASE_UNAVAILABLE", 503)

    routes = {}
    for row in route_rows:
        route_id = int(row["id"])
        route = routes.setdefault(route_id, {
            "id": route_id, "code": row["route_code"], "name": row["route_name"],
            "operator": row.get("operator_name"), "directions": [],
        })
        if row.get("direction_id") is not None:
            route["directions"].append({
                "id": int(row["direction_id"]), "name": row["direction_name"],
                "start": row.get("start_label"), "end": row.get("end_label"),
            })
    stops = [{
        "id": int(row["id"]), "name": row["stop_name"],
        "lat": float(row["latitude"]), "lng": float(row["longitude"]),
        "address": row.get("address"),
    } for row in stop_rows]
    return jsonify(success=True, data={
        "query": query, "routes": list(routes.values()), "stops": stops,
        "route_count": len(routes), "stop_count": len(stops),
    })
