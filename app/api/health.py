from flask import Blueprint, current_app, jsonify, request

from app.database.connection import get_db_connection

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    check_db = request.args.get("check_db", "true").strip().lower() not in {"false", "0", "no"}
    payload = {"success": True, "data": {"application": "healthy"}}

    if not check_db:
        payload["data"]["database"] = "not_checked"
        return jsonify(payload), 200

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        payload["data"]["database"] = "healthy"
        return jsonify(payload), 200
    except Exception:
        current_app.logger.exception("Database health check failed")
        return jsonify({
            "success": False,
            "data": {"application": "healthy", "database": "unavailable"},
            "error": {"code": "DATABASE_UNAVAILABLE", "message": "Database health check failed"},
        }), 503
    finally:
        if connection is not None:
            connection.close()
