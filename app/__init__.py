from flask import Flask, jsonify, render_template, send_from_directory

from config import Config


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    from app.api.health import health_bp
    app.register_blueprint(health_bp, url_prefix="/api/v1")

    @app.get("/")
    def index():
        return render_template(
            "public/index.html",
            map_lat=app.config["MAP_DEFAULT_LAT"],
            map_lng=app.config["MAP_DEFAULT_LNG"],
            map_zoom=app.config["MAP_DEFAULT_ZOOM"],
        )

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
        if app.request_class and _is_api_request():
            return jsonify(success=False, error={"code": "NOT_FOUND", "message": "Resource not found"}), 404
        return render_template("public/error.html", status_code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify(success=False, error={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}), 500

    return app


def _is_api_request() -> bool:
    from flask import request
    return request.path.startswith("/api/")
