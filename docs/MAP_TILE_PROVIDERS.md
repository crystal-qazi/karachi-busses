# Map Tile Providers

This document describes how map tiles are sourced, how the online and
offline providers are kept separate, and the licensing constraints that
govern offline tile use.

## Online map provider

The interactive Leaflet layers on every map page (public discovery map,
admin direction editor, stop picker, historical network QA map) are backed
by a single, **server-driven** online tile provider.

- The provider URL, max zoom, and attribution are read from the Flask
  config in [config.py](../config.py):
  - `MAP_TILE_URL` — default `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
  - `MAP_TILE_MAX_ZOOM` — default `19`
  - `MAP_ATTRIBUTION` — default OSM attribution markup
- [app/maps.py](../app/maps.py) validates the config (`online_map_config`)
  and enforces that the URL is HTTPS. The validated values are exposed to
  templates through a Flask context processor and rendered as `data-*`
  attributes on each map `<div>`, which the Leaflet layer scripts read.
- The CSP `img-src` allow-list only permits the OSM tile hosts and
  same-origin images. If you configure a **non-OSM** online provider, you
  must also extend the CSP `img-src` directive accordingly; otherwise the
  browser will block those tiles.

### Requirements for the online provider

1. Must serve tiles over **HTTPS**.
2. Must permit online, on-demand tile retrieval (interactive use).
3. Attribution must be displayed on the map (the Leaflet `attribution`
   control is always wired to the configured value).
4. Must be an explicit, permitted use of the provider under its terms.

The application's identity is never disguised: tile requests are made as a
normal browser navigation with a valid `Referer` (set by
`Referrer-Policy: strict-origin-when-cross-origin`). The app does not
bypass or evade any provider block.

## Offline map provider

Offline map tiles are a **separate concern** from the online provider and
are disabled by default.

- OSM's `tile.openstreetmap.org` tile policy does **NOT** permit offline
  tile downloads, prefetching, or the construction of tile archives. For
  that reason `tile.openstreetmap.org` (and its `a.`/`b.`/`c.`
  subdomains) is hard-excluded from any offline tile path:
  - [app/maps.py](../app/maps.py) `offline_tile_provider` /
    `offline_provider_guard` raises `ValueError` if an offline provider URL
    targets a forbidden OSM host.
  - [static/service-worker.js](../static/service-worker.js) keeps the OSM
    hosts in a `FORBIDDEN_TILE_HOSTS` set that is always excluded from the
    offline tile cache.
- The service worker's offline tile cache is **opt-in**: it is empty and
  inert until `OFFLINE_TILE_PROVIDER_HOST` is set in the service worker and
  `OFFLINE_TILE_PROVIDER_URL` is set in [config.py](../config.py).

### Enabling offline tiles

Offline tiles may only be enabled when **all** of the following are true:

1. A separate tile provider whose terms explicitly allow offline download,
   caching, and archival of tiles is in place.
2. That provider is not `tile.openstreetmap.org` (or any OSM tile
   subdomain).
3. The provider's terms and required attribution are documented here.
4. `OFFLINE_TILE_PROVIDER_URL` (HTTPS) and, in the service worker,
   `OFFLINE_TILE_PROVIDER_HOST` are both set to that provider.

Do **not** introduce an offline provider until its terms explicitly permit
offline use. Until then, the offline tile cache remains disabled and the PWA
serves the app shell offline only (tiles require a connection).

## Regression coverage

Tests for these constraints live in
[tests/test_map_tiles.py](../tests/test_map_tiles.py) (Referrer-Policy
value, intact security headers, map attribution, HTTPS online config, and
the guard that offline tiling cannot target the standard OSM tile server).
