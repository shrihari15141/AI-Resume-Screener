from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from extensions import db, jwt
from routes.auth import auth_bp
from routes.candidates import candidates_bp
from routes.exports import exports_bp
from routes.jobs import jobs_bp
from routes.reports import reports_bp
from routes.screening import screening_bp


def ensure_sqlite_parent(database_uri: str) -> None:
    sqlite_prefix = "sqlite:///"
    if not database_uri.startswith(sqlite_prefix) or database_uri == "sqlite:///:memory:":
        return
    database_path = database_uri.removeprefix(sqlite_prefix)
    if database_path:
        Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def serve_react_app(app: Flask):
    static_dir = Path(app.config["STATIC_FOLDER"])
    index_file = static_dir / "index.html"
    if not index_file.exists():
        return (
            jsonify(
                {
                    "message": "React production build not found. Run `npm run build` in the frontend directory before deployment."
                }
            ),
            503,
        )
    return send_from_directory(static_dir, "index.html")


def is_safe_static_path(static_dir: Path, requested_path: str) -> bool:
    try:
        (static_dir / requested_path).resolve().relative_to(static_dir.resolve())
    except ValueError:
        return False
    return True


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    ensure_sqlite_parent(app.config["SQLALCHEMY_DATABASE_URI"])

    cors_origins = app.config.get("CORS_ORIGINS") or []
    if cors_origins:
        CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(screening_bp, url_prefix="/api/screening")
    app.register_blueprint(candidates_bp, url_prefix="/api/candidates")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(exports_bp, url_prefix="/api/export")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def frontend_index():
        return serve_react_app(app)

    @app.get("/assets/<path:filename>")
    def frontend_assets(filename: str):
        assets_dir = Path(app.config["STATIC_FOLDER"]) / "assets"
        if not assets_dir.exists():
            return serve_react_app(app)
        return send_from_directory(assets_dir, filename, max_age=31536000)

    @app.get("/<path:path>")
    def frontend_routes(path: str):
        if path.startswith("api/"):
            abort(404)

        static_dir = Path(app.config["STATIC_FOLDER"])
        if is_safe_static_path(static_dir, path) and (static_dir / path).is_file():
            return send_from_directory(static_dir, path)

        return serve_react_app(app)

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"message": "Uploaded file is larger than the configured limit."}), 413

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "Resource not found."}), 404

    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):
            return jsonify({"message": error.description or error.name}), error.code
        if app.debug or app.testing:
            raise error
        app.logger.exception("Unhandled server error")
        return jsonify({"message": "An unexpected server error occurred."}), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
