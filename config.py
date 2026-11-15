import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    DEBUG = _as_bool(os.getenv("DEBUG"), False)
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME", "karachi_buses"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "connection_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        "charset": "utf8mb4",
        "use_unicode": True,
    }
    MAP_DEFAULT_LAT = float(os.getenv("MAP_DEFAULT_LAT", "24.8607"))
    MAP_DEFAULT_LNG = float(os.getenv("MAP_DEFAULT_LNG", "67.0011"))
    MAP_DEFAULT_ZOOM = int(os.getenv("MAP_DEFAULT_ZOOM", "11"))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    JSON_SORT_KEYS = False
