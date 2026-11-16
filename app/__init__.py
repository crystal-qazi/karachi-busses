import logging

from flask import Flask, jsonify, render_template, request, send_from_directory

from config import Config

app_logger = logging.getLogger(__name__)


# Content-Security-Policy that is compatible with the application's CDN usage
# (Bootstrap 5.3.3, Leaflet 1.9.4 + markercluster 1.5.3 + leaflet.draw 1.0.4)
# and the OSM tile endpoint. SRI hashes are the primary control; host
# allow-lists are included so that the browser can fall back to host matching
# when the SHA-384 integrity attribute is not enforced.
CSP_DEFAULT = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com; "
    "img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org; "
    "connect-src 'self'; "
    "frame-ancestors 'self'; "
    "base-uri 'self'; "
    "form-action 'self' https://www.openstreetmap.org; "
    "object-src 'none'; "
    "upgrade-insecure-requests"
)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static", instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    if app.config.get("APP_ENV") == "production":
        secret = app.config.get("SECRET_KEY", "")
        if not secret or secret == "development-only-change-me" or len(secret) < 32:
            raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters.")
        if app.config.get("DEBUG"):
            raise RuntimeError("DEBUG must be disabled in production.")

    from flask_wtf.csrf import CSRFProtect
    CSRFProtect(app)

    from app.api.health import health_bp
    from app.api.public import public_api_bp
    from app.api.journeys import journey_api_bp
    from app.api.admin import admin_api_bp
    from app.admin import admin_bp
    from app.admin import auth, routes, sources  # noqa: F401
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_api_bp, url_prefix="/api/v1")
    app.register_blueprint(public_api_bp, url_prefix="/api/v1")
    app.register_blueprint(journey_api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp)

    csp_policy = app.config.get("CSP_POLICY") or CSP_DEFAULT

    @app.after_request
    def apply_security_headers(response):
        # Send CSP only on HTML responses. JSON/asset responses should not
        # be constrained here (they are not subject to script-src etc.).
        content_type = response.headers.get("Content-Type", "")
        path = request.path
        if "text/html" in content_type and path not in {"/manifest.json", "/service-worker.js"}:
            response.headers.setdefault("Content-Security-Policy", csp_policy)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        # SAMEORIGIN lets the PWA's service worker and manifest (same origin)
        # keep working while blocking clickjacking from cross-origin frames.
        if path not in {"/manifest.json", "/service-worker.js"}:
            response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response

    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return {"csrf_token": generate_csrf}

    @app.get("/")
    def index():
        return render_template(
            "public/index.html",
            map_lat=app.config["MAP_DEFAULT_LAT"],
            map_lng=app.config["MAP_DEFAULT_LNG"],
            map_zoom=app.config["MAP_DEFAULT_ZOOM"],
        )

    @app.get("/privacy")
    def privacy():
        return render_template("public/privacy.html")

    @app.get("/offline")
    def offline():
        return render_template("public/offline.html")

    @app.get("/manifest.json")
    def manifest():
        return app.send_static_file("manifest.json")

    @app.get("/service-worker.js")
    def service_worker():
        response = send_from_directory(app.static_folder, "service-worker.js")
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        if _is_api_request():
            return jsonify(success=False, error={"code": "NOT_FOUND", "message": "Resource not found"}), 404
        return render_template("public/error.html", status_code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app_logger.exception("Unhandled 500 on %s", getattr(error, "description", "unknown endpoint"))
        if _is_api_request():
            return jsonify(success=False, error={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}), 500
        return render_template("public/error.html", status_code=500, message="An unexpected error occurred. Please try again."), 500

    return app


def _is_api_request() -> bool:
    from flask import request
    return request.path.startswith("/api/")
