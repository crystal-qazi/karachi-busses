import csv
import io
import json
import re

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from app.admin import admin_bp
from app.admin.auth import login_required
from app.database.helpers import cursor_context

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


@admin_bp.get("/")
@login_required
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
        except Exception as exc:
            flash(str(exc), "danger")
        return redirect(url_for("admin.operators"))
    with cursor_context() as (_, cursor):
        cursor.execute("SELECT * FROM bus_operators ORDER BY name")
        rows = cursor.fetchall()
    return render_template("admin/operators.html", operators=rows)


@admin_bp.post("/operators/<int:operator_id>/toggle")
@login_required
def toggle_operator(operator_id):
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute("UPDATE bus_operators SET is_active = NOT is_active WHERE id=%s", (operator_id,))
        if cursor.rowcount:
            _audit(cursor, "toggle_active", "bus_operator", operator_id)
    flash("Operator status updated.", "success")
    return redirect(url_for("admin.operators"))


@admin_bp.route("/routes", methods=["GET", "POST"])
@login_required
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
        except Exception as exc:
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
def route_detail(route_id):
    if request.method == "POST":
        try:
            name = _text("route_name", 180, True)
            description = _text("description", 5000)
            status = request.form.get("status", "draft")
            if status not in {"draft", "inactive", "under_review"}:
                raise ValueError("Routes can only be activated through the verification workflow.")
            with cursor_context(commit=True) as (_, cursor):
                cursor.execute(
                    "UPDATE bus_routes SET route_name=%s, description=%s, status=%s WHERE id=%s",
                    (name, description, status, route_id),
                )
                if not cursor.rowcount:
                    raise ValueError("Route not found.")
                _audit(cursor, "update", "bus_route", route_id, {"status": status})
            flash("Route updated.", "success")
        except Exception as exc:
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
    return render_template("admin/route_detail.html", route=route, directions=directions, stops=stops)


@admin_bp.post("/routes/<int:route_id>/publish")
@login_required
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
                       SUM(CASE WHEN s.status='active' THEN 1 ELSE 0 END) AS active_stop_count
                FROM route_directions d
                LEFT JOIN route_stops rs ON rs.direction_id=d.id
                LEFT JOIN bus_stops s ON s.id=rs.stop_id
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
    except Exception as exc:
        flash(f"Route was not published: {exc}", "danger")
    return redirect(url_for("admin.route_detail", route_id=route_id))


@admin_bp.post("/routes/<int:route_id>/directions")
@login_required
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
        flash("Direction added.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.route_detail", route_id=route_id))


@admin_bp.get("/directions/<int:direction_id>")
@login_required
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
    return render_template("admin/direction_editor.html", direction=direction, linked_stops=linked_stops, all_stops=all_stops, shape_json=json.dumps(shape) if shape else "null")


@admin_bp.post("/directions/<int:direction_id>/stops")
@login_required
def add_direction_stop(direction_id):
    try:
        stop_id = int(request.form.get("stop_id", ""))
        sequence = int(request.form.get("stop_sequence", ""))
        if sequence < 1:
            raise ValueError("Stop order must be 1 or greater.")
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute("SELECT id FROM route_directions WHERE id=%s", (direction_id,))
            if not cursor.fetchone():
                raise ValueError("Direction not found.")
            cursor.execute("INSERT INTO route_stops (direction_id, stop_id, stop_sequence) VALUES (%s,%s,%s)", (direction_id, stop_id, sequence))
            _audit(cursor, "add_stop", "route_direction", direction_id, {"stop_id": stop_id, "sequence": sequence})
        flash("Stop linked to direction.", "success")
    except Exception as exc:
        flash(f"Could not add stop: {exc}", "danger")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.post("/directions/<int:direction_id>/stops/<int:stop_id>/remove")
@login_required
def remove_direction_stop(direction_id, stop_id):
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute("DELETE FROM route_stops WHERE direction_id=%s AND stop_id=%s", (direction_id, stop_id))
        _audit(cursor, "remove_stop", "route_direction", direction_id, {"stop_id": stop_id})
    flash("Stop removed from direction.", "success")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.post("/directions/<int:direction_id>/shape")
@login_required
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
            cursor.execute("SELECT id FROM route_directions WHERE id=%s", (direction_id,))
            if not cursor.fetchone():
                raise ValueError("Direction not found.")
            cursor.execute("""
                INSERT INTO route_shapes (direction_id, geojson) VALUES (%s,%s)
                ON DUPLICATE KEY UPDATE geojson=VALUES(geojson)
            """, (direction_id, json.dumps(geometry)))
            _audit(cursor, "save_shape", "route_direction", direction_id, {"point_count": len(coordinates)})
        flash("Route shape saved.", "success")
    except Exception as exc:
        flash(f"Shape was not saved: {exc}", "danger")
    return redirect(url_for("admin.direction_editor", direction_id=direction_id))


@admin_bp.route("/stops", methods=["GET", "POST"])
@login_required
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
        except Exception as exc:
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
            cursor.execute(
                "UPDATE bus_stops SET stop_name=%s, latitude=%s, longitude=%s, address=%s, source_id=%s, status=%s WHERE id=%s",
                (name, lat, lng, address, source_id, status, stop_id),
            )
            if not cursor.rowcount:
                raise ValueError("Stop not found or unchanged.")
            _audit(cursor, "update", "bus_stop", stop_id)
        flash("Stop updated.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.stops"))


@admin_bp.route("/imports", methods=["GET", "POST"])
@login_required
def imports():
    preview = None
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
                rows = []
                for line_number, row in enumerate(reader, start=2):
                    if len(rows) >= 5000:
                        raise ValueError("A single import is limited to 5,000 stops.")
                    rows.append({
                        "stop_name": (row.get("stop_name") or "").strip()[:180],
                        "latitude": _coordinate(row.get("latitude"), f"Line {line_number} latitude", -90, 90),
                        "longitude": _coordinate(row.get("longitude"), f"Line {line_number} longitude", -180, 180),
                        "address": (row.get("address") or "").strip()[:500] or None,
                    })
                    if not rows[-1]["stop_name"]:
                        raise ValueError(f"Line {line_number}: stop_name is required.")
                if not rows:
                    raise ValueError("CSV contains no data rows.")
                if request.form.get("confirm") == "yes":
                    with cursor_context(commit=True) as (_, cursor):
                        for row in rows:
                            cursor.execute(
                                "INSERT INTO bus_stops (stop_name, latitude, longitude, address, status) VALUES (%s,%s,%s,%s,'under_review')",
                                (row["stop_name"], row["latitude"], row["longitude"], row["address"]),
                            )
                        _audit(cursor, "csv_import", "bus_stop", None, {"rows": len(rows)})
                    flash(f"Imported {len(rows)} stops as under review.", "success")
                    return redirect(url_for("admin.stops"))
                preview = rows[:20]
                session_count = len(rows)
                # Do not hold an untrusted large upload in server-side session state.
                flash(f"Validated {session_count} rows. Upload the file again and confirm to import.", "info")
            except Exception as exc:
                flash(f"Import rejected: {exc}", "danger")
    return render_template("admin/imports.html", preview=preview)
