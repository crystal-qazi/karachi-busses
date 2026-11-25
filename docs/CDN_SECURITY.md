# CDN Security (SRI + CSP)

External resources are loaded from:

| Resource | Host | SRI |
|---|---|---|
| Bootstrap 5.3.3 CSS/JS | https://cdn.jsdelivr.net | Yes |
| Leaflet 1.9.4 CSS/JS | https://unpkg.com | Yes |
| Leaflet.markercluster 1.5.3 | https://unpkg.com | Yes |
| Leaflet.draw 1.0.4 | https://cdnjs.cloudflare.com | Yes |
| OSM tiles | https://{s}.tile.openstreetmap.org | No (raster, dynamic) |

Every `<script>` and `<link rel="stylesheet">` that pulls a version-pinned
asset from a CDN carries a `integrity="sha384-…"` attribute and a
`crossorigin="anonymous"` attribute so the browser will verify the content
before executing or rendering it.

## Content-Security-Policy

`app/__init__.py` sets the following CSP on all HTML responses (manifest
and service worker are exempt because they need their own MIME types and
service-worker scope handling):

```
default-src 'self';
script-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com;
img-src 'self' data: https://cdnjs.cloudflare.com https://tile.openstreetmap.org https://*.tile.openstreetmap.org;
connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com;
frame-ancestors 'self';
base-uri 'self';
form-action 'self' https://www.openstreetmap.org;
object-src 'none';
upgrade-insecure-requests
```

`style-src` permits `'unsafe-inline'` because the stop-picker template contains an inline `<style>` block. This is acceptable while that style is static, server-rendered HTML.

Additional headers on all HTML responses:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: SAMEORIGIN` (PWA service worker stays functional)

## Resources that cannot use SRI

- **OpenStreetMap raster tiles** (`https://{s}.tile.openstreetmap.org/…`):
  these are binary PNG images served on demand with no stable integrity
  hash and no SRI support in `img-src`. They are limited to the OSM tile
  domain by `img-src`.
- **Inline `<style>` blocks in the stop-picker admin template**: no SRI for inline content; the style rule is pinned to `'unsafe-inline'`. If this block is extracted into an external file,
  the CSP should be tightened to remove `'unsafe-inline'` and add the new
  CSS files to `style-src` with SRI.

## Update procedure

To bump any version-pinned CDN resource:

1. Download the new file and recompute the SHA-384 SRI hash
   (`openssl dgst -sha384 -binary new-file.js | openssl base64 -A`).
2. Replace the integrity hash in every template that loads the resource.
3. Re-run the test suite (`pytest`) and the Docker build.
4. Update this table.
