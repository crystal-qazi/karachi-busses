"""Centralized handlers for MySQL errors in the admin blueprints.

- ``db_error_handler`` wraps a view that performs one or more DB operations.
  On a MySQL exception it logs the traceback server-side and returns either a
  JSON ``503`` payload (for API-style endpoints) or a redirect back to the
  same path with a user-safe flash message (for HTML views).
- ``DatabaseErrorRedirect`` is raised by the wrapper so that HTML endpoints
  can be returned as a redirect without leaking technical details to the UI.
"""

import functools
import json
import logging

import mysql.connector
from flask import current_app, flash, jsonify, redirect, request, url_for

logger = logging.getLogger(__name__)


class DatabaseErrorRedirect(Exception):
    """Raised by the decorator to signal a redirect back to the view with a flash."""

    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"database unavailable: {message}")


def _is_api_request() -> bool:
    """Mirror app._is_api_request plus the admin JSON endpoint.

    - ``/api/...``: any API blueprint request.
    - ``Accept: application/json``: a browser or fetch call expecting JSON.
    - ``/admin/.../map-data``: the admin direction map-data API endpoint.
    """
    path = request.path
    if path.startswith("/api/"):
        return True
    if request.headers.get("Accept", "").startswith("application/json"):
        return True
    if path.endswith("/data") or path.endswith("/map-data"):
        return True
    return False


def db_error_handler(view):
    """Wrap an admin view with safe, server-side-logged DB error handling.

    - HTML endpoints: flash a safe message and redirect to the same path
      (no loop: redirects do not re-run the handler).
    - JSON endpoints (``/api/v1/...`` or ``Accept: application/json``):
      return a structured ``503`` response.

    Technical details (SQL text, credentials, stack) go to the server log
    only; user-facing output is a fixed, safe string.
    """

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except DatabaseErrorRedirect as exc:
            flash(exc.message, "danger")
            return redirect(exc.path)
        except mysql.connector.Error as exc:
            logger.exception(
                "MySQL error in %s %s (endpoint=%s)",
                request.method,
                request.path,
                request.endpoint,
            )
            if _is_api_request():
                return (
                    jsonify(
                        success=False,
                        error={
                            "code": "DATABASE_UNAVAILABLE",
                            "message": "Database health check failed",
                        },
                    ),
                    503,
                )
            flash("Database temporarily unavailable. Try again in a moment.", "danger")
            return redirect(request.path)
        except Exception:
            logger.exception("Unexpected error in %s %s", request.method, request.path)
            raise

    return wrapped
