const CACHE_NAME = "karachi-buses-shell-v4";
const APP_SHELL = [
  "/", "/offline", "/privacy", "/manifest.json", "/static/css/app.css",
  "/static/js/app.js", "/static/images/bus.svg"
];

// Offline map tiles are intentionally NOT cached by default. The standard
// OSM tile server (tile.openstreetmap.org) does not permit offline tile
// downloads / prefetching / archives, so it must never be a target of any
// offline tile cache. A separate offline tile provider may only be enabled
// when its terms explicitly allow offline use AND it is configured here.
// Leave OFFLINE_TILE_PROVIDER_HOST empty to keep offline tiling disabled.
const OFFLINE_TILE_PROVIDER_HOST = "";
const TILE_CACHE_NAME = "karachi-buses-offline-tiles-v1";
// OSM subdomains used by the standard tile URL — always excluded from any
// offline tile cache regardless of configuration.
const FORBIDDEN_TILE_HOSTS = new Set([
  "tile.openstreetmap.org",
  "a.tile.openstreetmap.org",
  "b.tile.openstreetmap.org",
  "c.tile.openstreetmap.org"
]);

function isOfflineTile(url) {
  if (!OFFLINE_TILE_PROVIDER_HOST) return false;
  if (FORBIDDEN_TILE_HOSTS.has(url.host)) return false;
  return url.host === OFFLINE_TILE_PROVIDER_HOST;
}

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key.startsWith("karachi-buses-") && key !== CACHE_NAME && key !== TILE_CACHE_NAME)
      .map((key) => caches.delete(key))
  )));
  self.clients.claim();
});
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/")) return;
  // Same-origin tile archive of the licensed offline provider, when enabled.
  if (isOfflineTile(url)) {
    event.respondWith(caches.match(request).then((cached) => cached || fetch(request).then((response) => {
      if (response.ok && response.status === 200) {
        const copy = response.clone();
        caches.open(TILE_CACHE_NAME).then((cache) => cache.put(request, copy));
      }
      return response;
    })));
    return;
  }
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() =>
      caches.match(request).then((cached) => cached || caches.match("/offline"))
    ));
    return;
  }
  event.respondWith(caches.match(request).then((cached) => cached || fetch(request).then((response) => {
    if (response.ok) {
      const copy = response.clone();
      caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
    }
    return response;
  })));
});
