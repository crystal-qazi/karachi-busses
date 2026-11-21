import csv
import io
import json
import math
import re
from pathlib import Path

from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for

from app.admin import admin_bp
from app.admin.auth import login_required
from app.admin.errors import db_error_handler
from app.database.helpers import cursor_context
from app.road_network import RoadGraph, route_stops
from app.snapping import RoadSourceError, load_roads_cached, road_snap_candidates
from shapely.geometry import box

CODE_RE = re.compile(r"^[A-Za-z0-9._-]{1,60}$")


def _text(name, max_length, required=False):
    value = request.form.get(name, "").strip()
    if required and not value:
        raise ValueError(f"{name.replace('_', ' ').title()} is required.")
    if len(value) > max_length:
        raise ValueError(f"{name.replace('_', ' ').title()} must be {max_length} characters or fewer.")
    return value or None


def _coordinate(value, label, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a valid number.")
    if not minimum <= number <= maximum:
        raise ValueError(f"{label} is outside its valid range.")
    return number


def _audit(cursor, action, entity_type, entity_id, details=None):
    cursor.execute(
        "INSERT INTO audit_logs (admin_user_id, action, entity_type, entity_id, details) VALUES (%s,%s,%s,%s,%s)",
        (session.get('admin_user_id'), action, entity_type, entity_id, json.dumps(details or {})),
    )


def _mark_route_under_review(cursor, route_id, reason):
    """Withdraw an active route from passenger discovery after structural edits.

    Route managers may edit records, but a previously published route must be
    reviewed and explicitly republished before edited stops or geometry become
    passenger-visible.
    """
    cursor.execute(
        "UPDATE bus_routes SET status='under_review' WHERE id=%s AND status='active'",
        (route_id,),
    )
    if cursor.rowcount:
        _audit(cursor, "unpublish_for_review", "bus_route", route_id, {"reason": reason})


@admin_bp.get("/")
@login_required
@db_error_handler
def dashboard():
    with cursor_context() as (_, cursor):
        counts = {}
        for table, key in (("bus_operators", "operators"), ("bus_routes", "routes"),
                           ("bus_stops", "stops"), ("route_directions", "directions")):
            cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
            counts[key] = cursor.fetchone()["total"]
        cursor.execute("SELECT id, route_code, route_name, status FROM bus_routes ORDER BY updated_at DESC LIMIT 8")
        recent_routes = cursor.fetchall()
    return render_template("admin/dashboard.html", counts=counts, recent_routes=recent_routes)


@admin_bp.route("/operators", methods=["GET", "POST"])
@login_required
@db_error_handler
def operators():
    if request.method == "POST":
        try:
            name = _text("name", 180, True)
            contact = _text("contact", 120)
            website = _text("website", 500)
            with cursor_context(commit=True) as (_, cursor):
                cursor.execute(
                    "INSERT INTO bus_operators (name, contact, website) VALUES (%s,%s,%s)",
                    (name, contact, website),
                )
                _audit(cursor, "create", "bus_operator", cursor.lastrowid, {"name": name})
            flash("Operator added.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        return redirect(url_for("admin.operators"))
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT * FROM bus_operators ORDER BY name")
        rows = cursor.fetchall()
    return render_template("admin/operators.html", operators=rows)


@admin_bp.post("/operators/<int:operator_id>/toggle")
@login_required
@db_error_handler
def toggle_operator(operator_id):
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute("UPDATE bus_operators SET is_active = NOT is_active WHERE id=%s", (operator_id,))
        if cursor.rowcount:
            _audit(cursor, "toggle_active", "bus_operator", operator_id)
    flash("Operator status updated.", "success")
    return redirect(url_for("admin.operators"))


@admin_bp.route("/routes", methods=["GET", "POST"])
@login_required
@db_error_handler
def routes():
    if request.method == "POST":
        try:
            code = _text("route_code", 60, True)
            if not CODE_RE.fullmatch(code):
                raise ValueError("Route code may contain letters, numbers, dot, underscore and hyphen only.")
            name = _text("route_name", 180, True)
            description = _text("description", 5000)
            operator_id = request.form.get("operator_id") or None
            source_id = request.form.get("source_id") or None
            status = request.form.get("status", "draft")
            if status not in {"draft", "inactive", "under_review"}:
                raise ValueError("Routes can only be activated through the verification workflow.")
            if status == "active":
                raise ValueError("Use the Publish after verification action to activate a route.")
            with cursor_context(commit=True) as (_, cursor):
                cursor.execute(
                    "INSERT INTO bus_routes (operator_id, source_id, route_code, route_name, description, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    (operator_id, source_id, code, name, description, status),
                )
                route_id = cursor.lastrowid
                _audit(cursor, "create", "bus_route", route_id, {"route_code": code})
            flash("Route created. Add its directions and stops next.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        return redirect(url_for("admin.routes"))
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT id, name FROM bus_operators WHERE is_active=1 ORDER BY name")
        operators_list = cursor.fetchall()
        cursor.execute("SELECT id, source_name, verification_status FROM data_sources ORDER BY source_name")
        sources_list = cursor.fetchall()
        cursor.execute("""
            SELECT r.*, o.name AS operator_name,
                   (SELECT COUNT(*) FROM route_directions d WHERE d.route_id=r.id) AS direction_count
            FROM bus_routes r LEFT JOIN bus_operators o ON o.id=r.operator_id
            ORDER BY r.updated_at DESC
        """)
        rows = cursor.fetchall()
    return render_template("admin/routes.html", routes=rows, operators=operators_list, sources=sources_list)


@admin_bp.route("/routes/<int:route_id>", methods=["GET", "POST"])
@login_required
@db_error_handler
def route_detail(route_id):
    if request.method == "POST":
        try:
            name = _text("route_name", 180, True)
            description = _text("description", 5000)
            source_id = request.form.get("source_id") or None
            status = request.form.get("status", "draft")
            with cursor_context(commit=True) as (_, cursor):
                cursor.execute("SELECT status FROM bus_routes WHERE id=%s", (route_id,))
                current = cursor.fetchone()
                if not current:
                    raise ValueError("Route not found.")
                allowed = {"draft", "inactive", "under_review"}
                if current["status"] == "active":
                    allowed.add("active")
                if status not in allowed:
                    raise ValueError("Routes can only be activated through the verification workflow.")

                # An active route must always point to a verified source.
                # Changing its source while keeping it active would otherwise
                # bypass the publication verification gate.
                if status == "active":
                    if not source_id:
                        raise ValueError("An active route must have a verified data source.")
                    cursor.execute(
                        "SELECT verification_status FROM data_sources WHERE id=%s",
                        (source_id,),
                    )
                    source = cursor.fetchone()
                    if not source or source["verification_status"] != "verified":
                        raise ValueError("An active route must use a verified data source.")

                cursor.execute(
                    "UPDATE bus_routes SET route_name=%s, description=%s, source_id=%s, status=%s WHERE id=%s",
                    (name, description, source_id, status, route_id),
                )
                if not cursor.rowcount:
                    raise ValueError("Route not found.")
                _audit(cursor, "update", "bus_route", route_id, {"status": status})
            flash("Route updated.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        return redirect(url_for("admin.route_detail", route_id=route_id))

    with cursor_context() as (_, cursor):
        cursor.execute("""SELECT r.*, o.name AS operator_name, ds.source_name,
                          ds.verification_status AS source_verification_status
                          FROM bus_routes r LEFT JOIN bus_operators o ON o.id=r.operator_id
                          LEFT JOIN data_sources ds ON ds.id=r.source_id WHERE r.id=%s""", (route_id,))
        route = cursor.fetchone()
        if not route:
            return "Route not found", 404
        cursor.execute("""
            SELECT d.*, COUNT(rs.id) AS stop_count
            FROM route_directions d LEFT JOIN route_stops rs ON rs.direction_id=d.id
            WHERE d.route_id=%s GROUP BY d.id ORDER BY d.id
        """, (route_id,))
        directions = cursor.fetchall()
        cursor.execute("SELECT id, stop_name, latitude, longitude FROM bus_stops WHERE status='active' ORDER BY stop_name")
        stops = cursor.fetchall()
        cursor.execute("SELECT id, source_name, verification_status FROM data_sources ORDER BY source_name")
        sources = cursor.fetchall()
    return render_template("admin/route_detail.html", route=route, directions=directions, stops=stops, sources=sources)


@admin_bp.post("/routes/<int:route_id>/publish")
@login_required
@db_error_handler
def publish_route(route_id):
    if session.get("admin_role") not in {"super_admin", "data_reviewer"}:
        flash("Only a super administrator or data reviewer can publish routes.", "danger")
        return redirect(url_for("admin.route_detail", route_id=route_id))
    try:
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute("""
                SELECT r.id, r.source_id, ds.verification_status
                FROM bus_routes r LEFT JOIN data_sources ds ON ds.id=r.source_id
                WHERE r.id=%s
            """, (route_id,))
            route = cursor.fetchone()
            if not route:
                raise ValueError("Route not found.")
            if not route["source_id"] or route["verification_status"] != "verified":
                raise ValueError("Attach a verified source before publishing this route.")
            cursor.execute("""
                SELECT d.id, COUNT(rs.id) AS stop_count,
                       SUM(CASE WHEN s.status='active' AND stop_source.verification_status='verified' THEN 1 ELSE 0 END) AS active_stop_count
                FROM route_directions d
                LEFT JOIN route_stops rs ON rs.direction_id=d.id
                LEFT JOIN bus_stops s ON s.id=rs.stop_id
                LEFT JOIN data_sources stop_source ON stop_source.id=s.source_id
                WHERE d.route_id=%s GROUP BY d.id
            """, (route_id,))
            directions = cursor.fetchall()
            if not directions:
                raise ValueError("Add at least one direction before publishing.")
            if any((d["active_stop_count"] or 0) < 2 for d in directions):
                raise ValueError("Every direction must contain at least two active, ordered stops.")
            for direction in directions:
                cursor.execute("SELECT id FROM route_shapes WHERE direction_id=%s", (direction["id"],))
                if not cursor.fetchone():
                    raise ValueError("Every direction must have a saved route shape before publication.")
            cursor.execute("UPDATE bus_routes SET status='active' WHERE id=%s", (route_id,))
            _audit(cursor, "publish", "bus_route", route_id, {"verified_source_id": route["source_id"]})
        flash("Route published. It is now visible in public discovery.", "success")
    except (ValueError, TypeError) as exc:
        flash(f"Route was not published: {exc}", "danger")
    return redirect(url_for("admin.route_detail", route_id=route_id))


@admin_bp.post("/routes/<int:route_id>/directions")
@login_required
@db_error_handler
def create_direction(route_id):
    try:
        name = _text("direction_name", 100, True)
        start = _text("start_label", 180)
        end = _text("end_label", 180)
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute("SELECT id FROM bus_routes WHERE id=%s", (route_id,))
            if not cursor.fetchone():
                raise ValueError("Route not found.")
            cursor.execute(
                "INSERT INTO route_directions (route_id, direction_name, start_label, end_label) VALUES (%s,%s,%s,%s)",
                (route_id, name, start, end),
            )
            _audit(cursor, "create", "route_direction", cursor.lastrowid, {"route_id": route_id})
            _mark_route_under_review(cursor, route_id, "direction_added")
        flash("Direction added.", "success")
    except (ValueError, TypeError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.route_detail", route_id=route_id))


@admin_bp.get("/directions/<int:direction_id>")
@login_required
@db_error_handler
def direction_editor(direction_id):
    with cursor_context() as (_, cursor):
        cursor.execute("""
            SELECT d.*, r.route_code, r.route_name
            FROM route_directions d JOIN bus_routes r ON r.id=d.route_id WHERE d.id=%s
        """, (direction_id,))
        direction = cursor.fetchone()
        if not direction:
            return "Direction not found", 404
        cursor.execute("""
            SELECT rs.stop_sequence, s.id, s.stop_name, s.latitude, s.longitude
            FROM route_stops rs JOIN bus_stops s ON s.id=rs.stop_id
            WHERE rs.direction_id=%s ORDER BY rs.stop_sequence
        """, (direction_id,))
        linked_stops = cursor.fetchall()
        cursor.execute("SELECT id, stop_name, latitude, longitude FROM bus_stops WHERE status='active' ORDER BY stop_name")
        all_stops = cursor.fetchall()
        cursor.execute("SELECT geojson FROM route_shapes WHERE direction_id=%s", (direction_id,))
        shape_row = cursor.fetchone()
    shape = shape_row["geojson"] if shape_row else None
    if isinstance(shape, str):
        shape = json.loads(shape)
    # Defensive: even though save_direction_shape validates the GeoJSON as a
    # LineString, a hand-crafted row could contain anything. Only let a
    # well-formed dict reach the template so the |safe filter in
    # direction_editor.html is applied to validated JSON only.
    if not (shape is None or (isinstance(shape, dict) and shape.get("type") == "LineString" and isinstance(shape.get("coordinates"), list))):
        shape = None
    return render_template("admin/direction_editor.html", direction=direction, linked_stops=linked_stops, all_stops=all_stops, shape_json=json.dumps(shape) if shape else "null")


@admin_bp.post("/directions/<int:direction_id>/stops")
@login_required
@db_error_handler
def add_direction_stop(direction_id):
    try:
        stop_id = int(request.form.get("stop_id", ""))
        sequence = int(request.form.get("stop_sequence", ""))
        if sequence < 1:
            raise ValueError("Stop order must be 1 or greater.")
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute("SELECT route_id FROM route_directions WHERE id=%s", (direction_id,))
            direction = cursor.fetchone()
            if not direction:
                raise ValueError("Direction not found.")
            cursor.execute("INSERT INTO route_stops (direction_id, stop_id, stop_sequence) VALUES (%s,%s,%s)", (direction_id, stop_id, sequence))
            _audit(cursor, "add_stop", "route_direction", direction_id, {"stop_id": stop_id, "sequence": sequence})
            _mark_route_under_review(cursor, direction["route_id"], "direction_stop_added")
        flash("Stop linked to direction.", "success")
    except (ValueError, TypeError) as exc:
        flash(f"Could not add stop: {exc}", "danger")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.post("/directions/<int:direction_id>/stops/<int:stop_id>/remove")
@login_required
@db_error_handler
def remove_direction_stop(direction_id, stop_id):
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute("SELECT route_id FROM route_directions WHERE id=%s", (direction_id,))
        direction = cursor.fetchone()
        if not direction:
            flash("Direction not found.", "danger")
            return redirect(url_for("admin.routes"))
        cursor.execute("DELETE FROM route_stops WHERE direction_id=%s AND stop_id=%s", (direction_id, stop_id))
        if cursor.rowcount:
            _audit(cursor, "remove_stop", "route_direction", direction_id, {"stop_id": stop_id})
            _mark_route_under_review(cursor, direction["route_id"], "direction_stop_removed")
    flash("Stop removed from direction.", "success")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.post("/directions/<int:direction_id>/shape")
@login_required
@db_error_handler
def save_direction_shape(direction_id):
    try:
        raw = request.form.get("geojson", "")
        geometry = json.loads(raw)
        if geometry.get("type") != "LineString":
            raise ValueError("Route geometry must be a GeoJSON LineString.")
        coordinates = geometry.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) < 2 or len(coordinates) > 20000:
            raise ValueError("Draw a line containing between 2 and 20,000 points.")
        for pair in coordinates:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("Every coordinate must contain longitude and latitude.")
            _coordinate(pair[0], "Longitude", -180, 180)
            _coordinate(pair[1], "Latitude", -90, 90)
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute("SELECT route_id FROM route_directions WHERE id=%s", (direction_id,))
            direction = cursor.fetchone()
            if not direction:
                raise ValueError("Direction not found.")
            cursor.execute("""
                INSERT INTO route_shapes (direction_id, geojson) VALUES (%s,%s)
                ON DUPLICATE KEY UPDATE geojson=VALUES(geojson)
            """, (direction_id, json.dumps(geometry)))
            _audit(cursor, "save_shape", "route_direction", direction_id, {"point_count": len(coordinates)})
            _mark_route_under_review(cursor, direction["route_id"], "route_geometry_changed")
        flash("Route shape saved.", "success")
    except (ValueError, TypeError) as exc:
        flash(f"Shape was not saved: {exc}", "danger")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.route("/stops", methods=["GET", "POST"])
@login_required
@db_error_handler
def stops():
    if request.method == "POST":
        try:
            name = _text("stop_name", 180, True)
            lat = _coordinate(request.form.get("latitude"), "Latitude", -90, 90)
            lng = _coordinate(request.form.get("longitude"), "Longitude", -180, 180)
            address = _text("address", 500)
            source_id = request.form.get("source_id") or None
            status = request.form.get("status", "under_review")
            if status not in {"active", "inactive", "under_review"}:
                raise ValueError("Invalid stop status.")
            with cursor_context(commit=True) as (_, cursor):
                if status == "active":
                    cursor.execute("SELECT verification_status FROM data_sources WHERE id=%s", (source_id,))
                    source = cursor.fetchone()
                    if not source or source["verification_status"] != "verified":
                        raise ValueError("An active stop requires a verified data source.")
                cursor.execute(
                    "INSERT INTO bus_stops (stop_name, latitude, longitude, address, source_id, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, lat, lng, address, source_id, status),
                )
                _audit(cursor, "create", "bus_stop", cursor.lastrowid, {"name": name})
            flash("Stop created.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        return redirect(url_for("admin.stops"))
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT * FROM bus_stops ORDER BY stop_name")
        rows = cursor.fetchall()
        cursor.execute("SELECT id, source_name, verification_status FROM data_sources ORDER BY source_name")
        sources = cursor.fetchall()
    return render_template("admin/stops.html", stops=rows, sources=sources)


@admin_bp.post("/stops/<int:stop_id>/update")
@login_required
@db_error_handler
def update_stop(stop_id):
    try:
        name = _text("stop_name", 180, True)
        lat = _coordinate(request.form.get("latitude"), "Latitude", -90, 90)
        lng = _coordinate(request.form.get("longitude"), "Longitude", -180, 180)
        address = _text("address", 500)
        source_id = request.form.get("source_id") or None
        status = request.form.get("status", "under_review")
        if status not in {"active", "inactive", "under_review"}:
            raise ValueError("Invalid stop status.")
        with cursor_context(commit=True) as (_, cursor):
            if status == "active":
                cursor.execute("SELECT verification_status FROM data_sources WHERE id=%s", (source_id,))
                source = cursor.fetchone()
                if not source or source["verification_status"] != "verified":
                    raise ValueError("An active stop requires a verified data source.")
            cursor.execute("""
                SELECT DISTINCT r.id
                FROM bus_routes r
                JOIN route_directions d ON d.route_id=r.id
                JOIN route_stops rs ON rs.direction_id=d.id
                WHERE rs.stop_id=%s AND r.status='active'
            """, (stop_id,))
            affected_route_ids = [row["id"] for row in cursor.fetchall()]
            cursor.execute(
                "UPDATE bus_stops SET stop_name=%s, latitude=%s, longitude=%s, address=%s, source_id=%s, status=%s WHERE id=%s",
                (name, lat, lng, address, source_id, status, stop_id),
            )
            if not cursor.rowcount:
                raise ValueError("Stop not found or unchanged.")
            _audit(cursor, "update", "bus_stop", stop_id)
            for affected_route_id in affected_route_ids:
                _mark_route_under_review(cursor, affected_route_id, "linked_stop_changed")
        flash("Stop updated.", "success")
    except (ValueError, TypeError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.stops"))


@admin_bp.route("/imports/routes", methods=["GET", "POST"])
@login_required
@db_error_handler
def route_imports():
    preview = None
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT id, source_name, verification_status FROM data_sources ORDER BY source_name")
        sources = cursor.fetchall()
    if request.method == "POST":
        upload = request.files.get("file")
        source_id = request.form.get("source_id", "").strip()
        if not upload or not upload.filename.lower().endswith(".csv"):
            flash("Select a UTF-8 route CSV file.", "danger")
            return render_template("admin/route_imports.html", sources=sources, preview=None)
        try:
            if not source_id.isdigit():
                raise ValueError("Select a data source for this route import.")
            stream = io.StringIO(upload.stream.read().decode("utf-8-sig"))
            reader = csv.DictReader(stream)
            required = {
                "route_code", "route_name", "direction_name", "stop_name",
                "latitude", "longitude", "stop_sequence",
            }
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError("Required columns: route_code, route_name, direction_name, stop_name, latitude, longitude, stop_sequence. Optional: operator_name, start_label, end_label, address.")
            grouped = {}
            for line, raw in enumerate(reader, start=2):
                if line > 5001:
                    raise ValueError("A single route import is limited to 5,000 stop rows.")
                code = (raw.get("route_code") or "").strip()
                name = (raw.get("route_name") or "").strip()
                direction_name = (raw.get("direction_name") or "").strip()
                stop_name = (raw.get("stop_name") or "").strip()
                if not CODE_RE.fullmatch(code):
                    raise ValueError(f"Line {line}: invalid route_code.")
                if not name or len(name) > 180 or not direction_name or len(direction_name) > 100:
                    raise ValueError(f"Line {line}: route_name and direction_name are required and must fit the schema.")
                if not stop_name or len(stop_name) > 180:
                    raise ValueError(f"Line {line}: stop_name is required and must be 180 characters or fewer.")
                try:
                    sequence = int(raw.get("stop_sequence", ""))
                except (TypeError, ValueError):
                    raise ValueError(f"Line {line}: stop_sequence must be a positive integer.")
                if sequence < 1:
                    raise ValueError(f"Line {line}: stop_sequence must be a positive integer.")
                row = {
                    "route_code": code, "route_name": name,
                    "operator_name": (raw.get("operator_name") or "").strip()[:180] or None,
                    "direction_name": direction_name,
                    "start_label": (raw.get("start_label") or "").strip()[:180] or None,
                    "end_label": (raw.get("end_label") or "").strip()[:180] or None,
                    "stop_name": stop_name,
                    "latitude": _coordinate(raw.get("latitude"), f"Line {line} latitude", -90, 90),
                    "longitude": _coordinate(raw.get("longitude"), f"Line {line} longitude", -180, 180),
                    "address": (raw.get("address") or "").strip()[:500] or None,
                    "stop_sequence": sequence,
                }
                route = grouped.setdefault(code, {"name": name, "operator_name": row["operator_name"], "directions": {}})
                if route["name"] != name or route["operator_name"] != row["operator_name"]:
                    raise ValueError(f"Line {line}: route name/operator must be consistent for route {code}.")
                direction = route["directions"].setdefault(direction_name, {
                    "start_label": row["start_label"], "end_label": row["end_label"], "stops": []
                })
                if (direction["start_label"], direction["end_label"]) != (row["start_label"], row["end_label"]):
                    raise ValueError(f"Line {line}: direction labels must be consistent for {code}/{direction_name}.")
                direction["stops"].append(row)
            if not grouped:
                raise ValueError("CSV contains no data rows.")
            for code, route in grouped.items():
                for direction_name, direction in route["directions"].items():
                    direction["stops"].sort(key=lambda item: item["stop_sequence"])
                    sequences = [item["stop_sequence"] for item in direction["stops"]]
                    if len(direction["stops"]) < 2:
                        raise ValueError(f"{code}/{direction_name} needs at least two stops.")
                    if len(sequences) != len(set(sequences)):
                        raise ValueError(f"{code}/{direction_name} contains duplicate stop_sequence values.")
                    stop_keys = {
                        (item["stop_name"].casefold(), round(item["latitude"], 6), round(item["longitude"], 6))
                        for item in direction["stops"]
                    }
                    if len(stop_keys) != len(direction["stops"]):
                        raise ValueError(f"{code}/{direction_name} repeats the same stop more than once.")
            if request.form.get("confirm") == "yes":
                with cursor_context(commit=True) as (_, cursor):
                    cursor.execute("SELECT id FROM data_sources WHERE id=%s", (int(source_id),))
                    if not cursor.fetchone():
                        raise ValueError("Selected data source does not exist.")
                    for code, route in grouped.items():
                        cursor.execute("SELECT id FROM bus_routes WHERE route_code=%s", (code,))
                        if cursor.fetchone():
                            raise ValueError(f"Route code {code} already exists. Resolve it before importing.")
                    stop_cache = {}
                    for code, route in grouped.items():
                        operator_id = None
                        if route["operator_name"]:
                            cursor.execute("""
                                INSERT INTO bus_operators (name) VALUES (%s)
                                ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
                            """, (route["operator_name"],))
                            operator_id = cursor.lastrowid
                        cursor.execute("""
                            INSERT INTO bus_routes
                              (operator_id, source_id, route_code, route_name, status)
                            VALUES (%s,%s,%s,%s,'draft')
                        """, (operator_id, int(source_id), code, route["name"]))
                        route_id = cursor.lastrowid
                        for direction_name, direction in route["directions"].items():
                            cursor.execute("""
                                INSERT INTO route_directions
                                  (route_id, direction_name, start_label, end_label)
                                VALUES (%s,%s,%s,%s)
                            """, (route_id, direction_name, direction["start_label"], direction["end_label"]))
                            direction_id = cursor.lastrowid
                            for stop in direction["stops"]:
                                key = (stop["stop_name"].casefold(),
                                       round(stop["latitude"], 6), round(stop["longitude"], 6))
                                stop_id = stop_cache.get(key)
                                if stop_id is None:
                                    cursor.execute("""
                                        SELECT s.id, s.status, ds.verification_status
                                        FROM bus_stops s
                                        LEFT JOIN data_sources ds ON ds.id=s.source_id
                                        WHERE LOWER(s.stop_name)=LOWER(%s)
                                          AND s.latitude BETWEEN %s AND %s
                                          AND s.longitude BETWEEN %s AND %s
                                        LIMIT 1
                                    """, (stop["stop_name"], stop["latitude"] - 0.00025,
                                          stop["latitude"] + 0.00025, stop["longitude"] - 0.00025,
                                          stop["longitude"] + 0.00025))
                                    existing = cursor.fetchone()
                                    if existing:
                                        if existing["status"] != "active" or existing["verification_status"] != "verified":
                                            raise ValueError(
                                                f"Stop {stop['stop_name']} already exists but is not verified/active; resolve it in Bus stops before importing."
                                            )
                                        stop_id = int(existing["id"])
                                    else:
                                        cursor.execute("""
                                            INSERT INTO bus_stops
                                              (stop_name, latitude, longitude, address, source_id, status)
                                            VALUES (%s,%s,%s,%s,%s,'under_review')
                                        """, (stop["stop_name"], stop["latitude"], stop["longitude"],
                                              stop["address"], int(source_id)))
                                        stop_id = cursor.lastrowid
                                    stop_cache[key] = stop_id
                                cursor.execute("""
                                    INSERT INTO route_stops (direction_id, stop_id, stop_sequence)
                                    VALUES (%s,%s,%s)
                                """, (direction_id, stop_id, stop["stop_sequence"]))
                        _audit(cursor, "route_csv_import", "bus_route", route_id,
                               {"route_code": code, "source_id": int(source_id)})
                    _audit(cursor, "route_csv_import_batch", "bus_route", None,
                           {"route_count": len(grouped), "source_id": int(source_id)})
                flash(f"Imported {len(grouped)} routes as drafts. Review stops, draw each direction's map shape, then publish after source verification.", "success")
                return redirect(url_for("admin.routes"))
            preview = {
                "route_count": len(grouped),
                "direction_count": sum(len(route["directions"]) for route in grouped.values()),
                "stop_count": sum(len(direction["stops"]) for route in grouped.values() for direction in route["directions"].values()),
                "routes": list(grouped.keys())[:30],
            }
            flash("CSV validated. Upload the same file again and choose Import to create draft records.", "info")
        except (ValueError, TypeError) as exc:
            flash(f"Route import rejected: {exc}", "danger")
    return render_template("admin/route_imports.html", sources=sources, preview=preview)


@admin_bp.route("/imports", methods=["GET", "POST"])
@login_required
@db_error_handler
def imports():
    preview = None
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT id, source_name, verification_status FROM data_sources ORDER BY source_name")
        sources = cursor.fetchall()
    if request.method == "POST":
        upload = request.files.get("file")
        if not upload or not upload.filename.lower().endswith(".csv"):
            flash("Select a CSV file.", "danger")
        else:
            try:
                stream = io.StringIO(upload.stream.read().decode("utf-8-sig"))
                reader = csv.DictReader(stream)
                required = {"stop_name", "latitude", "longitude"}
                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    raise ValueError("CSV columns required: stop_name, latitude, longitude. Optional: address.")
                source_id = request.form.get("source_id", "").strip()
                if not source_id.isdigit():
                    raise ValueError("Select a data source for this import.")
                with cursor_context() as (_, cursor):
                    cursor.execute("SELECT id FROM data_sources WHERE id=%s", (int(source_id),))
                    if not cursor.fetchone():
                        raise ValueError("Selected data source does not exist.")
                rows = []
                for line_number, row in enumerate(reader, start=2):
                    if len(rows) >= 5000:
                        raise ValueError("A single import is limited to 5,000 stops.")
                    rows.append({
                        "stop_name": (row.get("stop_name") or "").strip()[:180],
                        "latitude": _coordinate(row.get("latitude"), f"Line {line_number} latitude", -90, 90),
                        "longitude": _coordinate(row.get("longitude"), f"Line {line_number} longitude", -180, 180),
                        "address": (row.get("address") or "").strip()[:500] or None,
                        "source_id": int(source_id),
                    })
                    if not rows[-1]["stop_name"]:
                        raise ValueError(f"Line {line_number}: stop_name is required.")
                if not rows:
                    raise ValueError("CSV contains no data rows.")
                # Detect same-name coordinate duplicates in O(n) using neighbouring
                # spatial buckets rather than pairwise comparisons.
                buckets = {}
                for index, row in enumerate(rows):
                    name_key = row["stop_name"].casefold()
                    lat_cell = math.floor(row["latitude"] / 0.00025)
                    lng_cell = math.floor(row["longitude"] / 0.00025)
                    for lat_offset in (-1, 0, 1):
                        for lng_offset in (-1, 0, 1):
                            key = (name_key, lat_cell + lat_offset, lng_cell + lng_offset)
                            if key in buckets:
                                raise ValueError(f"Duplicate stop near line {index + 2}: {row['stop_name']}.")
                    buckets[(name_key, lat_cell, lng_cell)] = index
                if request.form.get("confirm") == "yes":
                    with cursor_context(commit=True) as (_, cursor):
                        for row in rows:
                            cursor.execute("""
                                SELECT id FROM bus_stops
                                WHERE LOWER(stop_name)=LOWER(%s)
                                  AND latitude BETWEEN %s AND %s
                                  AND longitude BETWEEN %s AND %s
                                LIMIT 1
                            """, (row["stop_name"], row["latitude"] - 0.00025,
                                  row["latitude"] + 0.00025, row["longitude"] - 0.00025,
                                  row["longitude"] + 0.00025))
                            if cursor.fetchone():
                                raise ValueError(f"A stop with the same name and nearby coordinates already exists: {row['stop_name']}.")
                            cursor.execute(
                                "INSERT INTO bus_stops (stop_name, latitude, longitude, address, source_id, status) VALUES (%s,%s,%s,%s,%s,'under_review')",
                                (row["stop_name"], row["latitude"], row["longitude"], row["address"], row["source_id"]),
                            )
                        _audit(cursor, "csv_import", "bus_stop", None, {"rows": len(rows)})
                    flash(f"Imported {len(rows)} stops as under review.", "success")
                    return redirect(url_for("admin.stops"))
                preview = rows[:20]
                session_count = len(rows)
                # Do not hold an untrusted large upload in server-side session state.
                flash(f"Validated {session_count} rows. Upload the file again and confirm to import.", "info")
            except (ValueError, TypeError) as exc:
                flash(f"Import rejected: {exc}", "danger")
    return render_template("admin/imports.html", preview=preview, sources=sources)


@admin_bp.get("/historical-network")
@login_required
def historical_network():
    """Read-only QA map for the user-provided, unverified historical network."""
    return render_template("admin/historical_network.html")


@admin_bp.get("/historical-network/data")
@login_required
@db_error_handler
def historical_network_data():
    """Return only records belonging to the historical research source."""
    source_name = "Karachi Bus Network Research Dataset (user-provided cleaned files)"
    with cursor_context() as (_, cursor):
        cursor.execute(
            "SELECT id, source_name, verification_status FROM data_sources WHERE source_name=%s",
            (source_name,),
        )
        source = cursor.fetchone()
        if not source:
            return jsonify(success=False, error="Historical research source not found."), 404

        source_id = int(source["id"])
        cursor.execute(
            """SELECT id, stop_name, latitude, longitude, status
               FROM bus_stops WHERE source_id=%s ORDER BY stop_name, id""",
            (source_id,),
        )
        stops = [
            {"id": int(row["id"]), "name": row["stop_name"],
             "lat": float(row["latitude"]), "lng": float(row["longitude"]),
             "status": row["status"]}
            for row in cursor.fetchall()
        ]

        cursor.execute(
            """SELECT r.id, r.route_code, r.route_name, r.status, d.id AS direction_id,
                      d.direction_name,
                      (SELECT COUNT(*) FROM route_segments sg
                       WHERE sg.direction_id=d.id AND sg.source_id=%s) AS segment_count,
                      (SELECT COUNT(*) FROM route_segments sg
                       WHERE sg.direction_id=d.id AND sg.source_id=%s
                         AND sg.from_stop_id=sg.to_stop_id) AS self_loop_count,
                      (SELECT COUNT(*) FROM route_stops rs WHERE rs.direction_id=d.id) AS ordered_stop_count
               FROM bus_routes r JOIN route_directions d ON d.route_id=r.id
               WHERE r.source_id=%s ORDER BY r.route_code""",
            (source_id, source_id, source_id),
        )
        routes = [
            {"id": int(row["id"]), "code": row["route_code"], "name": row["route_name"],
             "status": row["status"], "direction_id": int(row["direction_id"]),
             "direction": row["direction_name"], "segment_count": int(row["segment_count"]),
             "self_loop_count": int(row["self_loop_count"]),
             "ordered_stop_count": int(row["ordered_stop_count"])}
            for row in cursor.fetchall()
        ]

        cursor.execute(
            """SELECT sg.id, sg.segment_sequence, sg.direction_id, r.route_code,
                      sf.id AS from_id, sf.stop_name AS from_name,
                      sf.latitude AS from_lat, sf.longitude AS from_lng,
                      st.id AS to_id, st.stop_name AS to_name,
                      st.latitude AS to_lat, st.longitude AS to_lng
               FROM route_segments sg
               JOIN route_directions d ON d.id=sg.direction_id
               JOIN bus_routes r ON r.id=d.route_id
               JOIN bus_stops sf ON sf.id=sg.from_stop_id
               JOIN bus_stops st ON st.id=sg.to_stop_id
               WHERE sg.source_id=%s AND r.source_id=%s
               ORDER BY r.route_code, sg.segment_sequence""",
            (source_id, source_id),
        )
        segments = [
            {"id": int(row["id"]), "sequence": int(row["segment_sequence"]),
             "direction_id": int(row["direction_id"]), "route_code": row["route_code"],
             "from": {"id": int(row["from_id"]), "name": row["from_name"],
                      "lat": float(row["from_lat"]), "lng": float(row["from_lng"])},
             "to": {"id": int(row["to_id"]), "name": row["to_name"],
                    "lat": float(row["to_lat"]), "lng": float(row["to_lng"])},
             "self_loop": int(row["from_id"]) == int(row["to_id"])}
            for row in cursor.fetchall()
        ]

    return jsonify(
        success=True,
        source={"id": source_id, "name": source["source_name"],
                "verification_status": source["verification_status"]},
        counts={"stops": len(stops), "routes": len(routes), "segments": len(segments),
                "self_loops": sum(1 for segment in segments if segment["self_loop"])},
        stops=stops, routes=routes, segments=segments,
    )


@admin_bp.get("/historical-network/snap")
@login_required
@db_error_handler
def historical_network_snap():
    """Propose geometric OSM road snap candidates for one historical stop.

    Preview only. The endpoint reads the stop coordinates, runs the pure-geometry
    snapping engine from ``app.snapping`` against the extracted OSM road inventory
    and returns the original coordinate plus a list of nearby road candidates
    ordered by planar distance, each carrying its snapped coordinate, the distance
    in metres, the OSM way id, road name, highway classification, relevant tags and
    the road geometry for map highlighting. It performs **no database writes**:
    route assignments, stop names, statuses and stored coordinates are never
    changed.
    """
    raw = request.args.get("stop_id", "").strip()
    if not raw.isdigit():
        return jsonify(success=False, error={
            "code": "INVALID_STOP_ID", "message": "A numeric stop_id is required."}), 400

    stop_id = int(raw)
    source_name = "Karachi Bus Network Research Dataset (user-provided cleaned files)"
    with cursor_context() as (_, cursor):
        cursor.execute(
            "SELECT id, source_name, verification_status FROM data_sources WHERE source_name=%s",
            (source_name,),
        )
        source = cursor.fetchone()
        if not source:
            return jsonify(success=False, error={
                "code": "NOT_FOUND", "message": "Historical research source not found."}), 404

        cursor.execute(
            """SELECT id, stop_name, latitude, longitude, status
               FROM bus_stops WHERE id=%s AND source_id=%s""",
            (stop_id, int(source["id"])),
        )
        stop = cursor.fetchone()
        if not stop:
            return jsonify(success=False, error={
                "code": "NOT_FOUND", "message": f"Stop {stop_id} was not found in the historical source."}), 404

    try:
        lat = float(stop["latitude"])
        lng = float(stop["longitude"])
    except (TypeError, ValueError):
        lat = lng = None
    if lat is None or lng is None or not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
        return jsonify(success=False, error={
            "code": "INVALID_COORDINATES",
            "message": f"Stop {stop_id} has invalid or out-of-range coordinates."}), 422

    roads_path = Path(current_app.config.get("OSM_ROADS_GEOJSON", ""))
    if not roads_path.is_file():
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "OSM road data is not available. Run scripts/extract_osm_karachi_roads.py first."}), 503

    max_distance_m = float(current_app.config.get("SNAP_MAX_DISTANCE_M", 500))
    max_candidates = int(current_app.config.get("SNAP_MAX_CANDIDATES", 5))
    try:
        # Cached process-wide: the inventory is parsed and indexed once per
        # file version, not once per request or per stop.
        roads = load_roads_cached(roads_path)
    except RoadSourceError:
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "The OSM road inventory exists but could not be read."}), 503
    if roads.is_empty:
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "The OSM road inventory contains no usable road segments."}), 503

    candidates = road_snap_candidates(
        lat, lng, roads,
        max_distance_m=max_distance_m,
        max_candidates=max_candidates,
    )
    original = {"id": stop_id, "name": stop["stop_name"], "status": stop["status"],
                "latitude": lat, "longitude": lng}
    if not candidates:
        return jsonify(
            success=True,
            stop=original,
            snapped=None,
            candidates=[],
            note={"code": "NO_SNAP_WITHIN_RANGE",
                  "message": f"No OSM road segment is within {max_distance_m:g} m of this stop."},
            max_distance_m=max_distance_m,
            max_candidates=max_candidates,
        )

    return jsonify(
        success=True,
        stop=original,
        snapped=candidates[0].as_dict(),
        candidates=[c.as_dict() for c in candidates],
        max_distance_m=max_distance_m,
        max_candidates=max_candidates,
        note={"code": "CANDIDATE_ONLY",
              "message": "A geometrically nearest road is only a candidate, not proof of the bus stop location."},
    )


@admin_bp.get("/historical-network/route-geometry")
@login_required
@db_error_handler
def historical_network_route_geometry():
    """Propose connected OSM road geometry for a historical route's ordered stops.

    Preview only. For every direction of the route, the ordered stop sequence
    is routed leg-by-leg through the connected road graph built from the
    extracted OSM inventory (``app.road_network``): one-way restrictions are
    respected, paths stay on connected roads and legs that cannot be routed
    are flagged instead of being bridged by a fabricated line. Routed legs are
    connected-road **candidates**, not proof of the historical bus alignment.
    No database writes: stop coordinates, statuses, route assignments and
    stored shapes are never changed.
    """
    raw = request.args.get("route_id", "").strip()
    if not raw.isdigit():
        return jsonify(success=False, error={
            "code": "INVALID_ROUTE_ID", "message": "A numeric route_id is required."}), 400
    route_id = int(raw)

    source_name = "Karachi Bus Network Research Dataset (user-provided cleaned files)"
    with cursor_context() as (_, cursor):
        cursor.execute(
            """SELECT r.id, r.route_code, r.route_name, r.status
               FROM bus_routes r
               JOIN data_sources s ON s.id=r.source_id
               WHERE r.id=%s AND s.source_name=%s""",
            (route_id, source_name),
        )
        route = cursor.fetchone()
        if not route:
            return jsonify(success=False, error={
                "code": "NOT_FOUND",
                "message": f"Route {route_id} was not found in the historical source."}), 404

        cursor.execute(
            """SELECT id, direction_name, start_label, end_label
               FROM route_directions WHERE route_id=%s ORDER BY id""",
            (route_id,),
        )
        directions = cursor.fetchall()
        directions_payload = []
        for direction in directions:
            cursor.execute(
                """SELECT s.id, s.stop_name, s.latitude, s.longitude, s.status,
                          rs.stop_sequence
                   FROM route_stops rs
                   JOIN bus_stops s ON s.id=rs.stop_id
                   WHERE rs.direction_id=%s
                   ORDER BY rs.stop_sequence, s.id""",
                (int(direction["id"]),),
            )
            stops = [
                {"id": int(row["id"]), "name": row["stop_name"],
                 "sequence": int(row["stop_sequence"]), "status": row["status"],
                 "lat": row["latitude"], "lng": row["longitude"]}
                for row in cursor.fetchall()
            ]
            directions_payload.append({
                "direction_id": int(direction["id"]),
                "direction_name": direction["direction_name"],
                "start_label": direction["start_label"],
                "end_label": direction["end_label"],
                "stops": stops,
            })

    if not directions_payload:
        return jsonify(success=False, error={
            "code": "NO_DIRECTIONS",
            "message": f"Route {route_id} has no directions."}), 404

    roads_path = Path(current_app.config.get("OSM_ROADS_GEOJSON", ""))
    if not roads_path.is_file():
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "OSM road data is not available. Run scripts/extract_osm_karachi_roads.py first."}), 503
    try:
        roads = load_roads_cached(roads_path)
    except RoadSourceError:
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "The OSM road inventory exists but could not be read."}), 503
    if roads.is_empty:
        return jsonify(success=False, error={
            "code": "ROAD_DATA_MISSING",
            "message": "The OSM road inventory contains no usable road segments."}), 503

    max_snap_distance_m = float(current_app.config.get("ROUTE_SNAP_MAX_DISTANCE_M", 150))
    bbox_pad_m = float(current_app.config.get("ROUTE_BBOX_PAD_M", 1500))
    cost_budget_factor = float(current_app.config.get("ROUTE_COST_BUDGET_FACTOR", 3.0))
    cost_budget_extra_m = float(current_app.config.get("ROUTE_COST_BUDGET_EXTRA_M", 2500))

    routed_directions = []
    for direction in directions_payload:
        stops = direction["stops"]
        if not stops:
            routed_directions.append({
                "direction_id": direction["direction_id"],
                "direction_name": direction["direction_name"],
                "stops": [], "stops_without_coordinates": [],
                "summary": {"status": "no_stops", "leg_count": 0,
                            "routed_legs": 0, "problem_legs": 0},
                "legs": [], "geometry": [],
            })
            continue

        # Boundary check: route_stops needs numeric coordinates; stops without
        # valid coordinates are reported instead of silently skipped.
        invalid_stops = []
        routable = []
        for stop in stops:
            try:
                lat = float(stop["lat"])
                lng = float(stop["lng"])
            except (TypeError, ValueError):
                invalid_stops.append({"id": stop["id"], "name": stop["name"],
                                      "sequence": stop["sequence"]})
                continue
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
                invalid_stops.append({"id": stop["id"], "name": stop["name"],
                                      "sequence": stop["sequence"]})
                continue
            stop["lat"] = lat
            stop["lng"] = lng
            routable.append(stop)

        direction_payload = {
            "direction_id": direction["direction_id"],
            "direction_name": direction["direction_name"],
            "stops": [
                {"id": s["id"], "name": s["name"], "sequence": s["sequence"],
                 "lat": s["lat"], "lng": s["lng"], "status": s["status"]}
                for s in routable
            ],
            "stops_without_coordinates": invalid_stops,
        }
        if not routable:
            direction_payload["summary"] = {
                "status": "no_stops", "leg_count": 0,
                "routed_legs": 0, "problem_legs": 0}
            direction_payload["legs"] = []
            direction_payload["geometry"] = []
            routed_directions.append(direction_payload)
            continue
        if invalid_stops:
            direction_payload["summary"] = {
                "status": "missing_coordinates", "leg_count": 0,
                "routed_legs": 0, "problem_legs": 0}
            direction_payload["legs"] = []
            direction_payload["geometry"] = []
            routed_directions.append(direction_payload)
            continue

        pad_deg = bbox_pad_m / 111_000.0
        area = box(
            min(s["lng"] for s in routable) - pad_deg,
            min(s["lat"] for s in routable) - pad_deg,
            max(s["lng"] for s in routable) + pad_deg,
            max(s["lat"] for s in routable) + pad_deg,
        )
        graph = RoadGraph.from_parts(roads.parts_intersecting(area))
        result = route_stops(
            graph, roads, routable,
            max_snap_distance_m=max_snap_distance_m,
            cost_budget_factor=cost_budget_factor,
            cost_budget_extra_m=cost_budget_extra_m,
        )
        direction_payload["summary"] = result["summary"]
        direction_payload["legs"] = result["legs"]
        direction_payload["geometry"] = result["geometry"]
        routed_directions.append(direction_payload)

    return jsonify(
        success=True,
        route={"id": int(route["id"]), "code": route["route_code"],
               "name": route["route_name"], "status": route["status"]},
        directions=routed_directions,
        config={"max_snap_distance_m": max_snap_distance_m,
                "bbox_pad_m": bbox_pad_m,
                "cost_budget_factor": cost_budget_factor,
                "cost_budget_extra_m": cost_budget_extra_m},
        note={"code": "CANDIDATE_ONLY",
              "message": "Routed legs are connected-road candidates from current OSM data, "
                         "not proof of the historical bus alignment. Problem legs are "
                         "flagged, never bridged by a fabricated path. Nothing is saved."},
    )
