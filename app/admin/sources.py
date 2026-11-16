"""Admin data-source provenance and verification workflow."""
import json
from flask import flash, redirect, render_template, request, session, url_for
from app.admin import admin_bp
from app.admin.auth import login_required
from app.admin.errors import db_error_handler
from app.database.helpers import cursor_context


@admin_bp.route("/data-sources", methods=["GET", "POST"])
@login_required
@db_error_handler
def data_sources():
    if request.method == "POST":
        name = request.form.get("source_name", "").strip()
        url = request.form.get("source_url", "").strip() or None
        notes = request.form.get("notes", "").strip() or None
        if not name or len(name) > 180 or (url and len(url) > 1000):
            flash("Provide a source name (maximum 180 characters) and a valid-length URL.", "danger")
            return redirect(url_for("admin.data_sources"))
        with cursor_context(commit=True) as (_, cursor):
            cursor.execute(
                "INSERT INTO data_sources (source_name, source_url, notes, verification_status) VALUES (%s,%s,%s,'pending')",
                (name, url, notes),
            )
            source_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO audit_logs (admin_user_id, action, entity_type, entity_id, details) VALUES (%s,%s,%s,%s,%s)",
                (session.get("admin_user_id"), "create", "data_source", source_id,
                 json.dumps({"source_name": name})),
            )
        flash("Source recorded as pending verification.", "success")
        return redirect(url_for("admin.data_sources"))
    with cursor_context() as (_, cursor):
        cursor.execute("""
            SELECT ds.*,
              (SELECT COUNT(*) FROM bus_routes r WHERE r.source_id=ds.id) AS route_count
            FROM data_sources ds ORDER BY ds.created_at DESC
        """)
        rows = cursor.fetchall()
    return render_template("admin/data_sources.html", sources=rows)


@admin_bp.post("/data-sources/<int:source_id>/verification")
@login_required
@db_error_handler
def update_source_verification(source_id):
    status = request.form.get("verification_status", "")
    if status not in {"pending", "verified", "rejected", "unverified"}:
        flash("Invalid source verification status.", "danger")
        return redirect(url_for("admin.data_sources"))
    if status == "verified" and session.get("admin_role") not in {"super_admin", "data_reviewer"}:
        flash("Only a super administrator or data reviewer can verify a source.", "danger")
        return redirect(url_for("admin.data_sources"))
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute("""UPDATE data_sources
                           SET verification_status=%s,
                               verified_by=CASE WHEN %s='verified' THEN %s ELSE NULL END,
                               verified_at=CASE WHEN %s='verified' THEN CURRENT_TIMESTAMP ELSE NULL END
                           WHERE id=%s""",
                           (status, status, session.get("admin_user_id"), status, source_id))
        if cursor.rowcount:
            cursor.execute(
                "INSERT INTO audit_logs (admin_user_id, action, entity_type, entity_id, details) VALUES (%s,%s,%s,%s,%s)",
                (session.get("admin_user_id"), "verify_source", "data_source", source_id,
                 json.dumps({"verification_status": status})),
            )
        else:
            flash("Source not found.", "danger")
            return redirect(url_for("admin.data_sources"))
    flash("Source verification status updated.", "success")
    return redirect(url_for("admin.data_sources"))
