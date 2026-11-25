const CACHE_NAME = "karachi-buses-shell-v5";
const APP_SHELL = [
  "/", "/offline", "/privacy", "/manifest.json", "/static/css/app.css",
  "/static/js/app.js", "/static/images/bus.svg"
];

// Offline map tiles are intentionally NOT cached by default. The standard
// OSM tile server does not permit offline tile downloads or prefetching.
const OFFLINE_TILE_PROVIDER_HOST = "";
const TILE_CACHE_NAME = "karachi-buses-offline-tiles-v1";
const FORBIDDEN_TILE_HOSTS = new Set([
  "tile.openstreetmap.org",
  "a.tile.openstreetmap.org",
  "b.tile.openstreetmap.org",
  "c.tile.openstreetmap.org"
]);

function isOfflineTile(url) {
  return Boolean(
    OFFLINE_TILE_PROVIDER_HOST &&
    !FORBIDDEN_TILE_HOSTS.has(url.host) &&
    url.host === OFFLINE_TILE_PROVIDER_HOST
  );
}

function isAdminOrAuthPath(pathname) {
  return pathname === "/admin" ||
    pathname.startsWith("/admin/") ||
    pathname === "/login" ||
    pathname.startsWith("/login/") ||
    pathname === "/logout";
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch(() => undefined)
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) =>
        key.startsWith("karachi-buses-") &&
        key !== CACHE_NAME &&
        key !== TILE_CACHE_NAME
      ).map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // Admin pages contain authenticated and frequently changing data. Always
  // let the browser request them directly; never serve them from the SW cache.
  if (isAdminOrAuthPath(url.pathname)) return;

  // API responses are dynamic and must always go to the application server.
  if (url.pathname.startsWith("/api/")) return;

  if (isOfflineTile(url)) {
    event.respondWith((async () => {
      try {
        const cached = await caches.match(request);
        if (cached) return cached;

        const response = await fetch(request);
        if (response.ok && response.status === 200) {
          const copy = response.clone();
          caches.open(TILE_CACHE_NAME)
            .then((cache) => cache.put(request, copy))
            .catch(() => undefined);
        }
        return response;
      } catch (_error) {
        return Response.error();
      }
    })());
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        return await fetch(request);
      } catch (_error) {
        try {
          return (await caches.match(request)) ||
            (await caches.match("/offline")) ||
            Response.error();
        } catch (_cacheError) {
          return Response.error();
        }
      }
    })());
    return;
  }

  // Cache-first for static same-origin assets, with all cache/network failures
  // handled so a rejected promise never escapes the fetch event.
  event.respondWith((async () => {
    try {
      const cached = await caches.match(request);
      if (cached) return cached;

      const response = await fetch(request);
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME)
          .then((cache) => cache.put(request, copy))
          .catch(() => undefined);
      }
      return response;
    } catch (_error) {
      try {
        return (await caches.match(request)) || Response.error();
      } catch (_cacheError) {
        return Response.error();
      }
    }
  })());
});
