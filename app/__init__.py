from flask import Flask, jsonify, render_template, send_from_directory

from config import Config


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
    from app.api.mobile import mobile_api_bp
    from app.admin import admin_bp
    from app.admin import auth, routes, sources  # noqa: F401
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_api_bp, url_prefix="/api/v1")
    app.register_blueprint(public_api_bp, url_prefix="/api/v1")
    app.register_blueprint(journey_api_bp, url_prefix="/api/v1")
    app.register_blueprint(mobile_api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp)

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
    def internal_error(_error):
        return jsonify(success=False, error={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}), 500

    return app


def _is_api_request() -> bool:
    from flask import request
    return request.path.startswith("/api/")
