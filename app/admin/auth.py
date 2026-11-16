"""Admin authentication.

``login`` performs the following on every POST:

- Looks up the active admin row with parameterized SQL.
- On a successful credential match, refreshes ``last_login_at``, clears and
  re-issues the session, and records an ``audit_logs`` row.
- On failure, records an ``audit_logs`` row with ``admin_user_id=NULL`` (or
  the matched ``admin_user.id`` when the username exists but the password
  is wrong or the account is inactive) so that failed attempts can be
  audited without exposing the password.

The two DB calls are independent: an audit insert failure must not leak
into the user's session. The success path commits both updates in one
transaction so a session is never established without a durable audit row.
"""

import json
import logging
import time
from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.admin import admin_bp
from app.admin.errors import db_error_handler
from app.admin import rate_limit
from app.database.helpers import cursor_context

logger = logging.getLogger(__name__)


def _absolute_session_exceeded() -> bool:
    """Return True when the admin session has passed its absolute max age.

    The absolute max age is read from ``SESSION_ABSOLUTE_MAX_AGE`` (seconds,
    default 24 h). If the session was issued more than that long ago, the
    next admin request is forced through the login flow again.
    """
    started = session.get("session_started_at")
    if not started:
        return False
    max_age = int(current_app.config.get("SESSION_ABSOLUTE_MAX_AGE", 86400))
    return (time.time() - int(started)) > max_age


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_user_id"):
            return redirect(url_for("admin.login", next=request.path))
        if _absolute_session_exceeded():
            session.clear()
            flash("Your session has expired. Please sign in again.", "warning")
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def _record_login_audit(admin_user_id, username, success, reason):
    """Insert one audit_logs row for a login event.

    ``admin_user_id`` may be ``None`` (failed attempt on an unknown user).
    The call is parameterized and JSON-encoded.
    """
    details = {"username": username, "success": success, "reason": reason}
    with cursor_context(commit=True) as (_, cursor):
        cursor.execute(
            "INSERT INTO audit_logs (admin_user_id, action, entity_type, entity_id, details) "
            "VALUES (%s,%s,%s,%s,%s)",
            (admin_user_id, "login", "admin_user", admin_user_id, json.dumps(details)),
        )


@admin_bp.route("/login", methods=["GET", "POST"])
@db_error_handler
def login():
    if request.method == "POST":
        enabled = bool(current_app.config.get("LOGIN_RATE_LIMIT_ENABLED", True))
        ip = rate_limit.client_ip() if enabled else None
        if enabled and rate_limit.is_locked(ip):
            flash("Too many failed attempts. Please try again in a few minutes.", "danger")
            return render_template("admin/login.html")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        any_user = None
        with cursor_context() as (_, cursor):
            cursor.execute(
                "SELECT id, username, password_hash, role FROM admin_users WHERE username=%s AND is_active=1",
                (username,),
            )
            active_user = cursor.fetchone()
            if not active_user:
                cursor.execute(
                    "SELECT id, is_active FROM admin_users WHERE username=%s",
                    (username,),
                )
                any_user = cursor.fetchone()

        if active_user and check_password_hash(active_user["password_hash"], password):
            with cursor_context(commit=True) as (_, cursor):
                cursor.execute(
                    "UPDATE admin_users SET last_login_at=CURRENT_TIMESTAMP WHERE id=%s",
                    (active_user["id"],),
                )
                cursor.execute(
                    "INSERT INTO audit_logs (admin_user_id, action, entity_type, entity_id, details) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (active_user["id"], "login", "admin_user", active_user["id"],
                     json.dumps({"username": username, "success": True, "reason": None})),
                )
            session.clear()
            session.permanent = True
            session["admin_user_id"] = active_user["id"]
            session["admin_username"] = active_user["username"]
            session["admin_role"] = active_user["role"]
            session["session_started_at"] = int(time.time())
            if enabled:
                rate_limit.record_success(ip)
            target = request.args.get("next", "")
            candidate = urljoin(request.host_url, target)
            parsed = urlparse(candidate)
            if parsed.scheme in {"http", "https"} and parsed.netloc == request.host:
                return redirect(candidate)
            return redirect(url_for("admin.dashboard"))

        # Failure path: audit without leaking the password or the hash.
        if any_user is not None:
            if active_user is None:
                reason = "account_inactive"
            else:
                reason = "bad_password"
            try:
                _record_login_audit(any_user["id"], username, False, reason)
            except Exception:
                logger.exception("Failed to record login-failure audit row")
        else:
            try:
                _record_login_audit(None, username, False, "unknown_user")
            except Exception:
                logger.exception("Failed to record login-failure audit row")

        if enabled:
            rate_limit.record_failure(ip)
        flash("Invalid username or password.", "danger")
    return render_template("admin/login.html")


@admin_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("admin.login"))
