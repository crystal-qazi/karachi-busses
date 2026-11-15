(() => {
  "use strict";

  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const lat = Number(mapElement.dataset.lat);
  const lng = Number(mapElement.dataset.lng);
  const zoom = Number(mapElement.dataset.zoom);
  const map = L.map(mapElement).setView([lat, lng], zoom);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);

  let userMarker = null;
  const status = document.getElementById("location-status");
  const locateButton = document.getElementById("locate-button");

  locateButton?.addEventListener("click", () => {
    if (!("geolocation" in navigator)) {
      status.textContent = "Location is not supported by this browser. You can still explore the map.";
      return;
    }

    status.textContent = "Finding your location…";
    locateButton.disabled = true;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;
        if (userMarker) map.removeLayer(userMarker);
        userMarker = L.marker([userLat, userLng]).addTo(map).bindPopup("Your current location");
        map.setView([userLat, userLng], 15);
        status.textContent = "Your location is shown. Nearby bus-stop search will be available when route data and discovery APIs are implemented.";
        locateButton.disabled = false;
      },
      (error) => {
        const messages = {
          1: "Location permission was denied. Enable location permission or explore the map manually.",
          2: "Your location is currently unavailable. Try again or explore the map manually.",
          3: "Location request timed out. Please try again."
        };
        status.textContent = messages[error.code] || "Unable to get your location.";
        locateButton.disabled = false;
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 }
    );
  });

  const searchButton = document.getElementById("search-button");
  searchButton?.addEventListener("click", () => {
    status.textContent = "Destination search will be enabled after route and stop data are available.";
  });

  if ("serviceWorker" in navigator && window.isSecureContext) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/static/service-worker.js")
        .catch((error) => console.error("Service worker registration failed:", error));
    });
  }
})();
