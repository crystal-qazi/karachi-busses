"""Regression tests for the security & reliability improvements.

Covers F2 (login audit + last_login_at), F3 (IP-based rate limiting),
F4 (absolute session lifetime), and F6 (centralized DB error handling).
"""

import json
import os
import tempfile
import time
from contextlib import contextmanager

import mysql.connector
import pytest

from app import create_app
from app.admin import rate_limit
from flask_wtf.csrf import CSRFProtect

# Disable CSRFProtect for the duration of each test in this module so that
# admin POSTs don't fail with a 400 before the authentication logic runs.
# The existing test_admin_routes suite already covers CSRF-on behaviour.
_orig_csrf_init = CSRFProtect.__init__


def _csrf_noop(self, app):
    pass


@pytest.fixture(autouse=True)
def _csrf_off(monkeypatch):
    monkeypatch.setattr(CSRFProtect, "__init__", _csrf_noop)
    yield
    CSRFProtect.__init__ = _orig_csrf_init


@pytest.fixture
def tmp_state_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LOGIN_RATE_LIMIT_STATE_DIR", str(tmp_path))
    yield str(tmp_path)


@pytest.fixture
def db_app():
    """App that uses the real DB with rate limiting on and a tmp state dir."""
    state_dir = tempfile.mkdtemp(prefix="rl_test_")
    os.environ["LOGIN_RATE_LIMIT_STATE_DIR"] = state_dir
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test" * 20,
            "LOGIN_RATE_LIMIT_ENABLED": True,
            "LOGIN_RATE_LIMIT_MAX_ATTEMPTS": 3,
            "LOGIN_RATE_LIMIT_WINDOW_SECONDS": 60,
            "LOGIN_RATE_LIMIT_LOCKOUT_SECONDS": 60,
            "LOGIN_RATE_LIMIT_STATE_DIR": state_dir,
            "SESSION_ABSOLUTE_MAX_AGE": 3600,
            "TRUSTED_PROXY_IPS": ("10.0.0.1", "127.0.0.1"),
        }
    )
    yield app
    # cleanup: remove any state files we may have created
    for p in os.listdir(state_dir):
        try:
            os.unlink(os.path.join(state_dir, p))
        except OSError:
            pass
    os.rmdir(state_dir)
    os.environ.pop("LOGIN_RATE_LIMIT_STATE_DIR", None)


def _seed_admin(app, username, password, active=1, role="super_admin"):
    from werkzeug.security import generate_password_hash
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM admin_users WHERE username=%s", (username,))
    cur.execute(
        "INSERT INTO admin_users (username, password_hash, role, is_active) "
        "VALUES (%s,%s,%s,%s)",
        (username, generate_password_hash(password), role, active),
    )
    conn.commit()
    cur.close()
    conn.close()
    _cleanup_admin = username
    app.extensions.setdefault("_seed_admins", []).append(_cleanup_admin)
    return _cleanup_admin


def _cleanup_seeded(app):
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor()
    for uname in app.extensions.get("_seed_admins", []):
        cur.execute("DELETE FROM admin_users WHERE username=%s", (uname,))
    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture
def seeded_admin(db_app):
    """A real admin account in the DB, removed after the test."""
    _seed_admin(db_app, "regression_admin", "RegressionPW-123")
    yield db_app
    _cleanup_seeded(db_app)


# ---------- F2: login audit + last_login_at ----------


def test_successful_login_sets_last_login_at_and_audit(seeded_admin):
    app = seeded_admin
    tc = app.test_client()
    before = _count_audit_rows(app)
    tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, admin_user_id, action, entity_type, entity_id, details FROM audit_logs "
        "WHERE action=%s AND entity_type=%s ORDER BY id DESC LIMIT 1",
        ("login", "admin_user"),
    )
    row = cur.fetchone()
    cur.execute("SELECT last_login_at FROM admin_users WHERE username=%s", ("regression_admin",))
    last_login = cur.fetchone()["last_login_at"]
    conn.close()
    assert before == 0 or _count_audit_rows(app) >= 1
    assert row is not None, "no login audit row written"
    assert row["action"] == "login"
    assert row["entity_type"] == "admin_user"
    assert row["admin_user_id"] is not None
    details = json.loads(row["details"])
    assert details["success"] is True
    assert details["username"] == "regression_admin"
    assert last_login is not None, "last_login_at was not set on the admin row"


def test_failed_login_records_audit_without_exposing_password(seeded_admin):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "regression_admin", "password": "WrongPW-123"})
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT admin_user_id, details FROM audit_logs WHERE action=%s ORDER BY id DESC LIMIT 1",
        ("login",),
    )
    row = cur.fetchone()
    conn.close()
    assert row is not None, "no failed-login audit row written"
    details = json.loads(row["details"])
    assert details["success"] is False
    assert details["reason"] in {"bad_password", "account_inactive", "unknown_user"}
    assert "WrongPW-123" not in row["details"], "password must not be stored in audit details"
    assert "WrongPW" not in row["details"]


def test_failed_login_for_unknown_user_records_audit_with_null_admin_id(seeded_admin):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "nobody-here", "password": "x"})
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT admin_user_id, details FROM audit_logs WHERE action=%s AND entity_type=%s ORDER BY id DESC LIMIT 1",
        ("login", "admin_user"),
    )
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row["admin_user_id"] is None
    details = json.loads(row["details"])
    assert details["reason"] == "unknown_user"


# ---------- F3: login rate limiting ----------


def test_lockout_after_max_failed_attempts(seeded_admin, monkeypatch):
    app = seeded_admin
    tc = app.test_client()
    # 3 failures with a bad password
    for _ in range(3):
        tc.post("/admin/login", data={"username": "regression_admin", "password": "bad"})
    # 4th: lockout — even with the correct password
    r = tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    body = r.get_data(as_text=True)
    assert "Too many failed attempts" in body
    with tc.session_transaction() as s:
        assert s.get("admin_user_id") is None, "locked-out login must not set the session"


def test_lockout_expiry_allows_success_after_expiry(seeded_admin, monkeypatch):
    app = seeded_admin
    tc = app.test_client()
    # 3 failures with a bad password
    for _ in range(3):
        tc.post("/admin/login", data={"username": "regression_admin", "password": "bad"})
    # Confirm lockout
    r = tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    assert "Too many failed attempts" in r.get_data(as_text=True)
    # Manually reset the lockout by rewriting the state file with an expired timestamp
    state_dir = app.config["LOGIN_RATE_LIMIT_STATE_DIR"]
    for fname in os.listdir(state_dir):
        p = os.path.join(state_dir, fname)
        raw = json.loads(open(p, "r").read())
        raw["locked_until"] = time.time() - 1  # in the past
        open(p, "w").write(json.dumps(raw))
    # Now the correct password should succeed
    r = tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    with tc.session_transaction() as s:
        assert s.get("admin_user_id") is not None, "after lockout expiry the correct password must succeed"
        assert s.get("admin_username") == "regression_admin"


def test_rate_limit_ignores_untrusted_forwarded_for(seeded_admin):
    """X-Forwarded-For from a trusted proxy is honoured; from an untrusted
    peer it must be ignored (fall back to REMOTE_ADDR). The test client's
    REMOTE_ADDR is 127.0.0.1 which is in TRUSTED_PROXY_IPS, so the XFF
    value is accepted. To prove the untrusted path, monkeypatch the
    config to remove 127.0.0.1 from the trusted list and verify the
    state file is keyed on REMOTE_ADDR instead of XFF.
    """
    app = seeded_admin
    tc = app.test_client()
    app.config["TRUSTED_PROXY_IPS"] = ()  # no trusted proxies in this app
    r = tc.post("/admin/login", data={"username": "regression_admin", "password": "bad"},
                headers={"X-Forwarded-For": "203.0.113.42"})
    assert r.status_code == 200
    # The state file should be keyed on the REMOTE_ADDR (127_0_0_1), not the XFF IP
    state_dir = app.config["LOGIN_RATE_LIMIT_STATE_DIR"]
    files = os.listdir(state_dir)
    assert any("127_0_0_1" in f or "127.0.0.1" in f for f in files), \
        f"expected a state file for REMOTE_ADDR (untrusted proxy), got {files}"
    assert not any("203_0_113_42" in f for f in files), \
        "untrusted X-Forwarded-For must NOT be used as the client IP key"


# ---------- F4: absolute session lifetime ----------


def test_expired_session_is_forced_back_to_login(seeded_admin):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    # Simulate an expired session
    with tc.session_transaction() as s:
        s["session_started_at"] = int(time.time()) - 100000  # way past SESSION_ABSOLUTE_MAX_AGE
    r = tc.get("/admin/")
    assert r.status_code == 302
    assert "/admin/login" in r.headers["Location"]
    with tc.session_transaction() as s:
        assert s.get("admin_user_id") is None, "expired session must be cleared"


def test_active_session_within_max_age_is_accepted(seeded_admin):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    r = tc.get("/admin/")
    assert r.status_code == 200, "active session within max-age must not be logged out"


# ---------- F6: DB error handling ----------


class _RaisingCursor:
    def __init__(self, *args, **kwargs):
        raise mysql.connector.Error("Simulated database failure")


def test_db_error_in_admin_route_returns_flash_and_redirect(seeded_admin, monkeypatch):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    import app.database.helpers as helpers_module

    @contextmanager
    def _boom(**kwargs):
        raise mysql.connector.Error("Simulated database failure")

    # Patch where cursor_context is actually imported (in routes / sources / auth)
    # rather than the original module, so the patch reaches the call sites.
    import app.admin.routes as routes_module
    import app.admin.sources as sources_module
    import app.admin.auth as auth_module
    monkeypatch.setattr(routes_module, "cursor_context", _boom)
    monkeypatch.setattr(sources_module, "cursor_context", _boom)
    monkeypatch.setattr(auth_module, "cursor_context", _boom)
    r = tc.get("/admin/operators")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/admin/operators")
    with tc.session_transaction() as s:
        assert s.get("admin_user_id") is not None, "session must survive a transient DB failure"
    # The flash message is on the first redirect response (Flask test client
    # renders it when the next GET follows the redirect in a real browser).
    # We patch the cursor back so that the follow-through succeeds.
    import app.admin.routes as routes_module2
    import app.database.helpers as helpers_module
    monkeypatch.undo()
    r2 = tc.get("/admin/operators", follow_redirects=True)
    assert "Database temporarily unavailable" in r2.get_data(as_text=True)


def test_db_error_in_json_endpoint_returns_503(seeded_admin, monkeypatch):
    app = seeded_admin
    tc = app.test_client()
    tc.post("/admin/login", data={"username": "regression_admin", "password": "RegressionPW-123"})
    import app.admin.routes as routes_module

    @contextmanager
    def _boom(**kwargs):
        raise mysql.connector.Error("Simulated database failure")

    monkeypatch.setattr(routes_module, "cursor_context", _boom)
    r = tc.get("/admin/historical-network/data")
    assert r.status_code == 503
    payload = r.get_json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DATABASE_UNAVAILABLE"
    # No SQL text or credentials should leak
    text = json.dumps(payload).lower()
    for needle in ("select", "insert", "update", "root", "password"):
        assert needle not in text, f"leak: {needle!r} in JSON error payload"


# ---------- helper ----------


def _count_audit_rows(app):
    conn = mysql.connector.connect(**app.config["DB_CONFIG"])
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM audit_logs")
    n = cur.fetchone()["n"]
    conn.close()
    return n



# ---------- Admin route integrity regressions ----------


def test_admin_form_handlers_do_not_swallow_database_exceptions():
    from pathlib import Path

    source = Path("app/admin/routes.py").read_text(encoding="utf-8")
    assert "except Exception as exc:" not in source
    assert "except (ValueError, TypeError) as exc:" in source


def test_active_route_edits_require_a_verified_data_source():
    from pathlib import Path

    source = Path("app/admin/routes.py").read_text(encoding="utf-8")
    route_detail = source.split("def route_detail", 1)[1].split(
        "@admin_bp.post(\"/routes/<int:route_id>/publish\")", 1
    )[0]
    assert 'if status == "active":' in route_detail
    assert 'SELECT verification_status FROM data_sources WHERE id=%s' in route_detail
    assert 'source["verification_status"] != "verified"' in route_detail
