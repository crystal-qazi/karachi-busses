"""Public read-only APIs for static Karachi bus route discovery."""
import json
import math
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Blueprint, jsonify, request
from app.database.helpers import cursor_context

public_api_bp = Blueprint("public_api", __name__)
EARTH_RADIUS_METRES = 6_371_000

DEFAULT_RADIUS_METRES = 1_500
_LOCATION_CACHE = {}
_LAST_GEOCODE_REQUEST = 0.0


@public_api_bp.get("/locations/search")
def search_locations():
    """Geocode a user-entered map place within the Karachi region using OSM Nominatim."""
    global _LAST_GEOCODE_REQUEST
    query = (request.args.get("q") or "").strip()
    if len(query) < 2 or len(query) > 100:
        return _error("Location search must contain 2–100 characters.")
    cache_key = query.casefold()
    if cache_key in _LOCATION_CACHE:
        return jsonify(success=True, data={"query": query, "locations": _LOCATION_CACHE[cache_key]})

    # Nominatim's public service policy limits usage to one request per second.
    import threading
    lock = getattr(search_locations, "_lock", None)
    if lock is None:
        lock = threading.Lock()
        search_locations._lock = lock
    try:
        with lock:
            wait = 1.05 - (time.monotonic() - _LAST_GEOCODE_REQUEST)
            if wait > 0:
                time.sleep(wait)
            params = urlencode({
                "q": query, "format": "jsonv2", "limit": 8,
                "countrycodes": "pk", "bounded": 1,
                "viewbox": "66.5,25.1,67.6,24.5",
            })
            req = Request(
                "https://nominatim.openstreetmap.org/search?" + params,
                headers={"User-Agent": "KarachiBuses/1.0 (public route finder)", "Accept": "application/json"},
            )
            with urlopen(req, timeout=7) as response:
                payload = json.loads(response.read().decode("utf-8"))
            _LAST_GEOCODE_REQUEST = time.monotonic()
        locations = [{
            "name": item.get("name") or item.get("display_name", query).split(",")[0],
            "label": item.get("display_name", query),
            "lat": float(item["lat"]), "lng": float(item["lon"]),
            "type": item.get("type"),
        } for item in payload if item.get("lat") and item.get("lon")]
        _LOCATION_CACHE[cache_key] = locations
        if len(_LOCATION_CACHE) > 256:
            _LOCATION_CACHE.pop(next(iter(_LOCATION_CACHE)))
    except Exception:
        return _error("Map location search is temporarily unavailable. You can also tap the map to choose a point.",
                      "GEOCODING_UNAVAILABLE", 503)
    return jsonify(success=True, data={"query": query, "locations": locations})


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



@public_api_bp.get("/routes/map")
def map_routes():
    """Return published route directions that have saved road geometry for the default map."""
    try:
        with cursor_context() as (_, cursor):
            cursor.execute("""
                SELECT d.id AS direction_id, d.direction_name,
                       r.id AS route_id, r.route_code, r.route_name,
                       rs.geojson
                FROM route_directions d
                JOIN bus_routes r ON r.id=d.route_id
                JOIN data_sources route_source ON route_source.id=r.source_id
                    AND route_source.verification_status='verified'
                JOIN route_shapes rs ON rs.direction_id=d.id
                WHERE r.status='active'
                ORDER BY r.route_code, d.direction_name
            """)
            rows = cursor.fetchall()
    except Exception:
        return _error("Published map routes are temporarily unavailable.",
                      "DATABASE_UNAVAILABLE", 503)

    directions = []
    for row in rows:
        shape = _shape_value(row.get("geojson"))
        if not isinstance(shape, dict) or shape.get("type") != "LineString":
            continue
        coordinates = shape.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) < 2:
            continue
        directions.append({
            "id": int(row["direction_id"]),
            "name": row["direction_name"],
            "route": {
                "id": int(row["route_id"]),
                "code": row["route_code"],
                "name": row["route_name"],
            },
            "shape": shape,
        })
    return jsonify(success=True, data={
        "direction_count": len(directions),
        "directions": directions,
    })


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
        JOIN data_sources route_source ON route_source.id=r.source_id AND route_source.verification_status='verified'
        JOIN data_sources stop_source ON stop_source.id=s.source_id AND stop_source.verification_status='verified'
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
                JOIN data_sources route_source ON route_source.id=r.source_id AND route_source.verification_status='verified'
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                WHERE d.id=%s AND r.status='active'
            """, (direction_id,))
            direction = cursor.fetchone()
            if not direction:
                return _error("Active route direction not found.", "NOT_FOUND", 404)
            cursor.execute("""
                SELECT s.id, s.stop_name, s.latitude, s.longitude, s.address, rs.stop_sequence
                FROM route_stops rs JOIN bus_stops s ON s.id=rs.stop_id
                JOIN data_sources stop_source ON stop_source.id=s.source_id AND stop_source.verification_status='verified'
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
                JOIN data_sources route_source ON route_source.id=r.source_id AND route_source.verification_status='verified'
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
                JOIN data_sources stop_source ON stop_source.id=s.source_id AND stop_source.verification_status='verified'
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
