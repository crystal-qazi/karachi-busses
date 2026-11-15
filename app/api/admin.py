from flask import Blueprint, jsonify

from app.admin.auth import login_required
from app.database.helpers import cursor_context

admin_api_bp = Blueprint("admin_api", __name__)


@admin_api_bp.get("/admin/routes/<int:route_id>/directions/<int:direction_id>/map-data")
@login_required
def direction_map_data(route_id, direction_id):
    with cursor_context() as (_, cursor):
        cursor.execute("""
            SELECT d.id, d.direction_name, r.route_code, r.route_name, rs.stop_sequence,
                   s.id AS stop_id, s.stop_name, s.latitude, s.longitude
            FROM route_directions d
            JOIN bus_routes r ON r.id=d.route_id
            LEFT JOIN route_stops rs ON rs.direction_id=d.id
            LEFT JOIN bus_stops s ON s.id=rs.stop_id
            WHERE r.id=%s AND d.id=%s
            ORDER BY rs.stop_sequence
        """, (route_id, direction_id))
        rows = cursor.fetchall()
        if not rows:
            return jsonify(success=False, error={"code":"NOT_FOUND","message":"Direction not found"}), 404
        cursor.execute("SELECT geojson FROM route_shapes WHERE direction_id=%s", (direction_id,))
        shape = cursor.fetchone()
    return jsonify(success=True, data={
        "direction": {"id": direction_id, "name": rows[0]["direction_name"], "route_code": rows[0]["route_code"], "route_name": rows[0]["route_name"]},
        "stops": [{"id": r["stop_id"], "name": r["stop_name"], "lat": float(r["latitude"]), "lng": float(r["longitude"]), "sequence": r["stop_sequence"]} for r in rows if r["stop_id"] is not None],
        "shape": shape["geojson"] if shape else None,
    })
