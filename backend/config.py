from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")


def _database_url() -> str:
    default = f"sqlite:///{(BASE_DIR / 'instance' / 'database.sqlite').as_posix()}"
    raw = os.getenv("DATABASE_URL") or default
    sqlite_prefix = "sqlite:///"
    if raw.startswith(sqlite_prefix) and not raw.startswith("sqlite:////"):
        db_path = raw.removeprefix(sqlite_prefix)
        if db_path and not Path(db_path).is_absolute() and db_path != ":memory:":
            return f"sqlite:///{(BASE_DIR / db_path).as_posix()}"
    return raw


def _upload_folder() -> str:
    raw = os.getenv("UPLOAD_FOLDER") or "uploads"
    path = Path(raw)
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS")
    flask_env = (os.getenv("FLASK_ENV") or "production").lower()
    if raw is None:
        if flask_env == "development":
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return []

    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if flask_env == "production":
        return [origin for origin in origins if origin != "*"]
    return origins


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-change-me"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "dev-jwt-secret-change-me"
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = _upload_folder()
    STATIC_FOLDER = str(BASE_DIR / "static")
    CORS_ORIGINS = _cors_origins()
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
    MAX_BATCH_UPLOAD_MB = int(os.getenv("MAX_BATCH_UPLOAD_MB", "1024"))
    MAX_CONTENT_LENGTH = MAX_BATCH_UPLOAD_MB * 1024 * 1024
    JSON_SORT_KEYS = False

    LLM_API_KEY = os.getenv("LLM_API_KEY") or ""
    LLM_MODEL = os.getenv("LLM_MODEL") or ""
    LLM_API_URL = os.getenv("LLM_API_URL") or ""
