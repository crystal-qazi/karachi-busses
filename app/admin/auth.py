from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.admin import admin_bp
from app.database.helpers import cursor_context


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_user_id"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with cursor_context() as (_, cursor):
            cursor.execute(
                "SELECT id, username, password_hash, role FROM admin_users WHERE username=%s AND is_active=1",
                (username,),
            )
            user = cursor.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["admin_user_id"] = user["id"]
            session["admin_username"] = user["username"]
            session["admin_role"] = user["role"]
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("admin/login.html")


@admin_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("admin.login"))
