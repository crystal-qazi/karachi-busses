"""Map tile-provider configuration and offline-tile licensing guard.

The interactive map layers are backed by an online tile server. OSM's
tile.openstreetmap.org tile policy does NOT permit offline downloads,
prefetching, or building tile archives of their tiles, so any offline
tile-provider must be a separate, explicitly-licensed source. This module
exposes a single, validated way to read the configured providers so the
templates and any offline tooling cannot silently fall back to the
standard OSM tile server.
"""
import logging

app_logger = logging.getLogger(__name__)

# Hosts that are forbidden for offline tile use. The standard OSM tile
# server (and any of its subdomains, including the {s} subdomain
# placeholder used by Leaflet) is licensed for online tile access only.
_FORBIDDEN_OFFLINE_TILE_HOSTS = {
    "tile.openstreetmap.org",
    "a.tile.openstreetmap.org",
    "b.tile.openstreetmap.org",
    "c.tile.openstreetmap.org",
}
_FORBIDDEN_OFFLINE_TILE_DOMAINS = (
    "openstreetmap.org",
)

_DEFAULT_ONLINE_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
_DEFAULT_ONLINE_MAX_ZOOM = 19
_DEFAULT_ONLINE_ATTRIBUTION = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">'
    "OpenStreetMap contributors</a>"
)


def _is_https(url: str) -> bool:
    return str(url or "").startswith("https://")


def _host_of(url: str) -> str:
    raw = str(url or "")
    rest = raw.split("://", 1)[-1]
    host = rest.split("/", 1)[0]
    host = host.lower().split("@")[-1].split(":", 1)[0]
    # Leaflet's {s} subdomain placeholder expands to a.tile / b.tile /
    # c.tile; strip it so the underlying host is what the guard matches on.
    if host.startswith("{s}."):
        host = host[len("{s}."):]
    return host


def _is_forbidden_offline_host(host: str) -> bool:
    if host in _FORBIDDEN_OFFLINE_TILE_HOSTS:
        return True
    return any(
        host == domain or host.endswith("." + domain)
        for domain in _FORBIDDEN_OFFLINE_TILE_DOMAINS
    )


def online_map_config(config) -> dict:
    """Return a validated, server-driven config for the online map layers.

    The tile URL must be HTTPS. The CSP img-src allow-list only permits
    OSM tile hosts and same-origin images, so a non-OSM online provider
    also requires the CSP to be extended before it can be used.
    """
    url = config.get("MAP_TILE_URL", _DEFAULT_ONLINE_TILE_URL)
    max_zoom = int(config.get("MAP_TILE_MAX_ZOOM", _DEFAULT_ONLINE_MAX_ZOOM))
    attribution = config.get("MAP_ATTRIBUTION", _DEFAULT_ONLINE_ATTRIBUTION)
    if not _is_https(url):
        raise ValueError("MAP_TILE_URL must use HTTPS")
    return {
        "url": url,
        "maxZoom": max_zoom,
        "attribution": attribution,
        "is_osm": _is_forbidden_offline_host(_host_of(url)),
    }


def offline_tile_provider(config):
    """Return the configured offline tile provider, or None.

    Guard: an offline provider must be HTTPS and must not target the
    standard OSM tile server (which does not permit offline tile
    downloads / archives). Returning None means offline tiling is
    simply disabled rather than silently misdirected to OSM.
    """
    url = config.get("OFFLINE_TILE_PROVIDER_URL", "")
    if not url:
        return None
    if not _is_https(url):
        raise ValueError("OFFLINE_TILE_PROVIDER_URL must use HTTPS")
    host = _host_of(url)
    if _is_forbidden_offline_host(host):
        raise ValueError(
            "OFFLINE_TILE_PROVIDER_URL must not target "
            "tile.openstreetmap.org; OSM's tile policy does not permit "
            "offline tile downloads or archives. Use a separate provider "
            "whose terms explicitly allow offline use."
        )
    return {
        "url": url,
        "maxZoom": int(config.get("OFFLINE_TILE_MAX_ZOOM", _DEFAULT_ONLINE_MAX_ZOOM)),
        "attribution": config.get("OFFLINE_TILE_ATTRIBUTION", ""),
        "host": host,
    }


def offline_provider_guard(config):
    """Validate that the configured offline provider is safe to use.

    Raises ValueError if the offline provider targets a forbidden OSM
    host. Safe to call with no offline provider configured (no-op).
    """
    offline_tile_provider(config)
    return True
