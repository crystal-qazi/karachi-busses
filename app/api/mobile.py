"""Read-only, published transport dataset API for native offline clients.

The first release deliberately uses consistent full snapshots. Incremental
change batches will be enabled only after publication mutations are wired to
a durable change log; a timestamp-only cursor is not safe for deletions.
"""
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, make_response
from app.database.helpers import cursor_context

mobile_api_bp = Blueprint("mobile_api", __name__)


def _json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      default=_json_value).encode("utf-8")


def _published_snapshot():
    """Read a consistent view of all passenger-visible transport records."""
    with cursor_context() as (connection, cursor):
        # A read-only consistent snapshot ensures records are from one DB view.
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        connection.start_transaction(readonly=True, consistent_snapshot=True)
        try:
            cursor.execute("""
                SELECT r.id, r.operator_id, r.route_code, r.route_name, r.description,
                       o.name AS operator_name, r.updated_at
                FROM bus_routes r
                JOIN data_sources ds ON ds.id=r.source_id AND ds.verification_status='verified'
                LEFT JOIN bus_operators o ON o.id=r.operator_id AND o.is_active=1
                WHERE r.status='active'
                ORDER BY r.id
            """)
            routes = [{k: _json_value(v) for k, v in row.items()} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT d.id, d.route_id, d.direction_name, d.start_label, d.end_label
                FROM route_directions d
                JOIN bus_routes r ON r.id=d.route_id AND r.status='active'
                JOIN data_sources ds ON ds.id=r.source_id AND ds.verification_status='verified'
                ORDER BY d.route_id, d.id
            """)
            directions = [{k: _json_value(v) for k, v in row.items()} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT s.id, s.stop_name, s.latitude, s.longitude, s.address, s.updated_at
                FROM bus_stops s
                JOIN data_sources ds ON ds.id=s.source_id AND ds.verification_status='verified'
                WHERE s.status='active'
                ORDER BY s.id
            """)
            stops = [{k: _json_value(v) for k, v in row.items()} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT rs.direction_id, rs.stop_id, rs.stop_sequence
                FROM route_stops rs
                JOIN route_directions d ON d.id=rs.direction_id
                JOIN bus_routes r ON r.id=d.route_id AND r.status='active'
                JOIN data_sources rds ON rds.id=r.source_id AND rds.verification_status='verified'
                JOIN bus_stops s ON s.id=rs.stop_id AND s.status='active'
                JOIN data_sources sds ON sds.id=s.source_id AND sds.verification_status='verified'
                ORDER BY rs.direction_id, rs.stop_sequence
            """)
            direction_stops = [{k: int(v) for k, v in row.items()} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT sh.direction_id, sh.geojson
                FROM route_shapes sh
                JOIN route_directions d ON d.id=sh.direction_id
                JOIN bus_routes r ON r.id=d.route_id AND r.status='active'
                JOIN data_sources ds ON ds.id=r.source_id AND ds.verification_status='verified'
                ORDER BY sh.direction_id
            """)
            shapes = []
            for row in cursor.fetchall():
                geometry = row["geojson"]
                if isinstance(geometry, str):
                    geometry = json.loads(geometry)
                shapes.append({"direction_id": int(row["direction_id"]), "geojson": geometry})
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    return {
        "routes": routes,
        "directions": directions,
        "stops": stops,
        "direction_stops": direction_stops,
        "shapes": shapes,
    }


def _manifest_for(snapshot):
    digest = hashlib.sha256(_canonical_bytes(snapshot)).hexdigest()
    return {
        "dataset_version": digest,
        "schema_version": 1,
        "checksum": "sha256:" + digest,
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "sync_mode": "full_snapshot",
        "incremental_sync_available": False,
    }


@mobile_api_bp.get("/mobile/manifest")
def mobile_manifest():
    try:
        snapshot = _published_snapshot()
        manifest = _manifest_for(snapshot)
        response = make_response(jsonify(success=True, data=manifest))
        response.headers["ETag"] = '"' + manifest["dataset_version"] + '"'
        response.headers["Cache-Control"] = "no-cache"
        return response
    except Exception:
        return jsonify(success=False, error={
            "code": "MOBILE_DATA_UNAVAILABLE",
            "message": "The mobile dataset is temporarily unavailable."
        }), 503


@mobile_api_bp.get("/mobile/snapshot")
def mobile_snapshot():
    try:
        snapshot = _published_snapshot()
        manifest = _manifest_for(snapshot)
        response = make_response(jsonify(success=True, data={
            **manifest,
            "dataset": snapshot,
        }))
        response.headers["ETag"] = '"' + manifest["dataset_version"] + '"'
        response.headers["Cache-Control"] = "no-cache"
        return response
    except Exception:
        return jsonify(success=False, error={
            "code": "MOBILE_DATA_UNAVAILABLE",
            "message": "The mobile dataset is temporarily unavailable."
        }), 503
