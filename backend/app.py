from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt
from routes.auth import auth_bp
from routes.candidates import candidates_bp
from routes.exports import exports_bp
from routes.jobs import jobs_bp
from routes.reports import reports_bp
from routes.screening import screening_bp


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
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

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"message": "Uploaded file is larger than the configured limit."}), 413

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "Resource not found."}), 404

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

