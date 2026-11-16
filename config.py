import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_csv(value: str | None, default: tuple = ()) -> tuple:
    raw = (value or "").strip()
    if not raw:
        return default
    return tuple(part.strip() for part in raw.split(",") if part.strip())


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
    DEBUG = _as_bool(os.getenv("DEBUG"), False)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = APP_ENV == "production"
    SESSION_COOKIE_SAMESITE = "Lax"
    # Sliding: after each request, the session cookie is extended by this
    # many seconds. Used to keep active admins signed in.
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", "28800"))
    # Absolute: a session that is older than this many seconds is force-logged
    # out regardless of activity. Independent of the sliding lifetime.
    SESSION_ABSOLUTE_MAX_AGE = int(os.getenv("SESSION_ABSOLUTE_MAX_AGE", "86400"))
    WTF_CSRF_TIME_LIMIT = 3600

    # Login rate limiting (IP-based, file-backed, no Redis dependency).
    LOGIN_RATE_LIMIT_ENABLED = _as_bool(os.getenv("LOGIN_RATE_LIMIT_ENABLED"), True)
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("LOGIN_RATE_LIMIT_MAX_ATTEMPTS", "5"))
    LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", "300"))
    LOGIN_RATE_LIMIT_LOCKOUT_SECONDS = int(os.getenv("LOGIN_RATE_LIMIT_LOCKOUT_SECONDS", "300"))
    LOGIN_RATE_LIMIT_STATE_DIR = os.getenv(
        "LOGIN_RATE_LIMIT_STATE_DIR",
        str(Path(__file__).resolve().parent / "data" / "rate_limits"),
    )

    # Trusted reverse-proxy IPs. When set, the rightmost non-trusted hop in
    # X-Forwarded-For is used as the client IP; otherwise REMOTE_ADDR is used.
    TRUSTED_PROXY_IPS = _as_csv(os.getenv("TRUSTED_PROXY_IPS"))

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
