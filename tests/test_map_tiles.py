"""Regression tests for OSM tile access fixes and offline-tile compliance.

Covers the "Fix OpenStreetMap 403 Tile Access" task:
  1. Referrer-Policy is strict-origin-when-cross-origin (so browser tile
     requests to OSM carry a valid Referer).
  2. The other security headers (CSP, X-Content-Type-Options,
     X-Frame-Options) remain intact.
  3. The public map exposes OSM attribution.
  4. The online tile configuration is HTTPS.
  5. Offline tile functionality cannot target the standard OSM tile server
     (tile.openstreetmap.org), which does not permit offline tile use.
"""

import pytest

from app import create_app
from app.maps import (
    online_map_config,
    offline_tile_provider,
    offline_provider_guard,
)

_HTML_EXCLUDED = {"/manifest.json", "/service-worker.js"}


def _html_app(**overrides):
    config = {"TESTING": True, "SECRET_KEY": "test" * 20}
    config.update(overrides)
    return create_app(config)


def _client_get(app, path):
    with app.test_client() as c:
        return c.get(path)


# ---------- 1. Referrer-Policy ----------


def test_referrer_policy_is_strict_origin_when_cross_origin():
    app = _html_app()
    r = _client_get(app, "/")
    assert r.status_code == 200
    assert r.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


# ---------- 2. Other security headers remain intact ----------


def test_csp_still_applied_on_html_and_includes_osm_tile_hosts():
    app = _html_app()
    r = _client_get(app, "/")
    csp = r.headers.get("Content-Security-Policy", "")
    assert "Content-Security-Policy" in r.headers
    assert "upgrade-insecure-requests" in csp
    assert "tile.openstreetmap.org" in csp


def test_no_sniff_and_frame_options_present_on_html():
    app = _html_app()
    r = _client_get(app, "/")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "SAMEORIGIN"


def test_csp_not_applied_to_json_or_service_worker():
    app = _html_app()
    # /service-worker.js is an asset path; CSP must not be applied there.
    r = _client_get(app, "/service-worker.js")
    assert r.status_code == 200
    assert "Content-Security-Policy" not in r.headers


# ---------- 3. Map attribution present ----------


def test_public_map_exposes_osm_attribution():
    app = _html_app()
    body = _client_get(app, "/").get_data(as_text=True)
    assert "OpenStreetMap" in body
    assert "data-tile-attribution" in body
    # The OSM copyright link is surfaced in the attribution markup.
    assert "openstreetmap.org/copyright" in body


def test_public_map_renders_server_driven_tile_url():
    app = _html_app()
    body = _client_get(app, "/").get_data(as_text=True)
    assert 'data-tile-url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"' in body
    assert "data-tile-max-zoom" in body


# ---------- 4. Online configuration is HTTPS ----------


def test_online_tile_config_default_is_https():
    app = _html_app()
    tile = online_map_config(app.config)
    assert tile["url"].startswith("https://")
    assert tile["attribution"]


def test_online_tile_config_rejects_http_url():
    app = _html_app(MAP_TILE_URL="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    with pytest.raises(ValueError):
        online_map_config(app.config)


# ---------- 5. Offline tile functionality cannot target the OSM server ----------


def test_offline_provider_defaults_to_disabled():
    app = _html_app()
    assert offline_tile_provider(app.config) is None


def test_offline_guard_rejects_osm_tile_server():
    app = _html_app(
        OFFLINE_TILE_PROVIDER_URL="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    )
    with pytest.raises(ValueError):
        offline_provider_guard(app.config)


def test_offline_guard_rejects_osm_subdomain():
    app = _html_app(OFFLINE_TILE_PROVIDER_URL="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    with pytest.raises(ValueError):
        offline_provider_guard(app.config)


def test_offline_guard_rejects_http_offline_provider():
    app = _html_app(OFFLINE_TILE_PROVIDER_URL="http://tiles.example.com/{z}/{x}/{y}.png")
    with pytest.raises(ValueError):
        offline_provider_guard(app.config)


def test_offline_guard_accepts_licensed_separate_provider():
    app = _html_app(
        OFFLINE_TILE_PROVIDER_URL="https://tiles.example.com/{z}/{x}/{y}.png",
        OFFLINE_TILE_ATTRIBUTION="Tiles &copy; Example Map",
    )
    assert offline_provider_guard(app.config) is True
    provider = offline_tile_provider(app.config)
    assert provider is not None
    assert provider["url"].startswith("https://")
    assert provider["host"] == "tiles.example.com"


def test_service_worker_never_caches_osm_tiles():
    """The service worker hard-excludes OSM tile hosts from the offline tile
    cache and keeps the offline tile cache disabled by default."""
    with open("static/service-worker.js") as f:
        source = f.read()
    assert "FORBIDDEN_TILE_HOSTS" in source
    for host in ("tile.openstreetmap.org", "a.tile.openstreetmap.org"):
        assert host in source, f"{host} must be in the forbidden tile host list"
    # Offline tile cache is opt-in: disabled unless a provider host is set.
    assert 'const OFFLINE_TILE_PROVIDER_HOST = "";' in source


# ---------- CDN integrity and source-map CSP regressions ----------


def test_leaflet_css_sri_hash_is_current_in_all_templates():
    from pathlib import Path

    expected = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    old = "sha384-EFZ0jt3DbvE1VivitkgNKHKPMhJcP7wjuPgyHHMVLhBd2fvDbmzAzT6Ia2y7qRuu"
    paths = (
        "templates/public/index.html",
        "templates/admin/stops.html",
        "templates/admin/direction_editor.html",
    )
    for path in paths:
        source = Path(path).read_text(encoding="utf-8")
        assert expected in source, f"Official Leaflet CSS SRI hash missing from {path}"
        assert "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" in source, f"Official Leaflet JS SRI hash missing from {path}"
        assert old not in source, f"Stale Leaflet CSS SRI hash remains in {path}"


def test_csp_connect_src_allows_trusted_cdn_source_maps():
    app = _html_app()
    response = _client_get(app, "/")
    csp = response.headers.get("Content-Security-Policy", "")
    connect_src = next((part.strip() for part in csp.split(";") if part.strip().startswith("connect-src ")), "")
    assert "'self'" in connect_src
    assert "https://cdn.jsdelivr.net" in connect_src
    assert "https://unpkg.com" in connect_src


def test_referrer_policy_and_existing_security_headers_remain_intact_after_csp_change():
    app = _html_app()
    response = _client_get(app, "/")
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    csp = response.headers.get("Content-Security-Policy", "")
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'self'" in csp
