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

    # Online tile provider used by the interactive Leaflet layers. HTTPS
    # only; must be a provider whose tile policy permits online use.
    MAP_TILE_URL = os.getenv(
        "MAP_TILE_URL",
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    )
    MAP_TILE_MAX_ZOOM = int(os.getenv("MAP_TILE_MAX_ZOOM", "19"))
    MAP_ATTRIBUTION = os.getenv(
        "MAP_ATTRIBUTION",
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    )

    # Offline tile provider (optional). OSM's tile.openstreetmap.org policy
    # does NOT permit offline tile downloads / prefetching / archives, so an
    # offline provider must be a separate, explicitly-licensed source. Leave
    # unset to keep offline tiling disabled.
    OFFLINE_TILE_PROVIDER_URL = os.getenv("OFFLINE_TILE_PROVIDER_URL", "")
    OFFLINE_TILE_MAX_ZOOM = int(os.getenv("OFFLINE_TILE_MAX_ZOOM", "19"))
    OFFLINE_TILE_ATTRIBUTION = os.getenv("OFFLINE_TILE_ATTRIBUTION", "")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    JSON_SORT_KEYS = False

    # OSM candidate-road inventory used by the admin snap preview. Generated
    # by scripts/extract_osm_karachi_roads.py; may be absent until the extract
    # has been run, in which case the snap endpoint reports ROAD_DATA_MISSING.
    OSM_ROADS_GEOJSON = os.getenv(
        "OSM_ROADS_GEOJSON",
        str(Path(__file__).resolve().parent / "data" / "osm_roads" / "karachi-osm-bus-roads.geojson"),
    )
    # Maximum planar distance (metres) a stop may be from a road segment for a
    # snap candidate to be proposed. A geometrically nearest road is only a
    # candidate, never proof of the actual bus stop location.
    SNAP_MAX_DISTANCE_M = float(os.getenv("SNAP_MAX_DISTANCE_M", "500"))
    # Maximum number of alternative road candidates the snap preview proposes,
    # ordered by planar distance. Preview-only; never saved.
    SNAP_MAX_CANDIDATES = int(os.getenv("SNAP_MAX_CANDIDATES", "5"))
