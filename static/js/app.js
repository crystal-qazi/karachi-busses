(() => {
  "use strict";
  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const map = L.map(mapElement).setView(
    [Number(mapElement.dataset.lat), Number(mapElement.dataset.lng)],
    Number(mapElement.dataset.zoom)
  );
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);

  const status = document.getElementById("location-status");
  const locateButton = document.getElementById("locate-button");
  const resultsElement = document.getElementById("discovery-results");
  const searchInput = document.getElementById("destination-input");
  const searchButton = document.getElementById("search-button");
  const journeyInput = document.getElementById("journey-destination");
  const journeyButton = document.getElementById("journey-button");
  let currentOrigin = null;
  const radiusSelect = document.getElementById("radius-select");
  const userLayer = L.layerGroup().addTo(map);
  const stopsLayer = L.layerGroup().addTo(map);
  const routeLayer = L.layerGroup().addTo(map);

  function setStatus(message) { status.textContent = message; }
  function clearLayers() {
    stopsLayer.clearLayers();
    routeLayer.clearLayers();
  }
  function addUserMarker(lat, lng) {
    userLayer.clearLayers();
    L.circleMarker([lat, lng], {
      radius: 9, color: "#fff", weight: 3, fillColor: "#1769aa", fillOpacity: 1
    }).addTo(userLayer).bindPopup("Your selected location");
  }
  function makeButton(label, onClick, className) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className || "btn btn-sm btn-outline-success text-start";
    button.textContent = label;
    button.addEventListener("click", onClick);
    return button;
  }
  function showEmpty(message) {
    resultsElement.replaceChildren();
    const p = document.createElement("p");
    p.className = "text-secondary small mb-0";
    p.textContent = message;
    resultsElement.append(p);
  }
  async function getJson(url) {
    const response = await fetch(url, {headers: {"Accept": "application/json"}});
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error?.message || "Request failed.");
    }
    return payload.data;
  }
  function renderStopMarker(stop, focus) {
    const marker = L.marker([stop.lat, stop.lng]).addTo(stopsLayer);
    const popup = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = stop.name;
    const detail = document.createElement("div");
    detail.textContent = stop.distance_metres != null
      ? Math.round(stop.distance_metres) + " m from your location"
      : (stop.address || "Bus stop");
    popup.append(title, detail);
    marker.bindPopup(popup);
    if (focus) marker.openPopup();
    return marker;
  }

  async function showDirection(directionId) {
    setStatus("Loading route and stop details…");
    try {
      const data = await getJson("/api/v1/directions/" + directionId);
      routeLayer.clearLayers();
      if (data.shape && data.shape.type === "LineString" && Array.isArray(data.shape.coordinates)) {
        const latlngs = data.shape.coordinates.map((pair) => [pair[1], pair[0]]);
        L.polyline(latlngs, {color: "#126b50", weight: 5, opacity: .9}).addTo(routeLayer);
      }
      const bounds = [];
      data.stops.forEach((stop) => {
        const marker = L.circleMarker([stop.lat, stop.lng], {
          radius: 6, color: "#fff", weight: 2, fillColor: "#e17b27", fillOpacity: 1
        }).addTo(routeLayer);
        const popup = document.createElement("div");
        const heading = document.createElement("strong");
        heading.textContent = stop.sequence + ". " + stop.name;
        popup.append(heading);
        if (stop.address) {
          const address = document.createElement("div");
          address.textContent = stop.address;
          popup.append(address);
        }
        marker.bindPopup(popup);
        bounds.push([stop.lat, stop.lng]);
      });
      if (data.shape && data.shape.coordinates) {
        data.shape.coordinates.forEach((pair) => bounds.push([pair[1], pair[0]]));
      }
      if (bounds.length) map.fitBounds(bounds, {padding: [30, 30], maxZoom: 15});
      setStatus(data.direction.route.code + ": " + data.direction.name + ". " +
        data.stops.length + " active stops shown. Static route only; no live bus tracking.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  function renderNearby(data) {
    clearLayers();
    resultsElement.replaceChildren();
    if (!data.stops.length) {
      showEmpty("No active bus stops with published routes were found within this radius. Try a larger radius or search a route.");
      setStatus("No nearby active routes found.");
      return;
    }
    const summary = document.createElement("p");
    summary.className = "small text-secondary";
    summary.textContent = data.stop_count + " nearby stops within " + data.radius_metres.toLocaleString() + " m";
    resultsElement.append(summary);
    data.stops.forEach((stop) => {
      renderStopMarker(stop, false);
      const card = document.createElement("div");
      card.className = "border rounded-3 p-2 mb-2";
      const name = document.createElement("div");
      name.className = "fw-semibold";
      name.textContent = stop.name;
      const distance = document.createElement("div");
      distance.className = "small text-secondary mb-2";
      distance.textContent = Math.round(stop.distance_metres) + " m away";
      card.append(name, distance);
      stop.directions.forEach((direction) => {
        const route = direction.route;
        const label = route.code + " · " + route.name + " — " + direction.name;
        card.append(makeButton(label, () => showDirection(direction.id),
          "btn btn-sm btn-outline-success w-100 text-start mb-1"));
      });
      resultsElement.append(card);
    });
    setStatus("Found " + data.stop_count + " stops serving published bus routes. Select a route to view its path and stop order.");
  }

  async function discover(lat, lng) {
    currentOrigin = {lat, lng};
    addUserMarker(lat, lng);
    map.setView([lat, lng], 15);
    setStatus("Searching nearby bus stops…");
    showEmpty("Searching published routes…");
    const radius = Number(radiusSelect.value || 1500);
    try {
      const url = "/api/v1/discover/nearby?lat=" + encodeURIComponent(lat) +
        "&lng=" + encodeURIComponent(lng) + "&radius=" + radius + "&limit=60";
      renderNearby(await getJson(url));
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    }
  }

  locateButton.addEventListener("click", () => {
    if (!navigator.geolocation) {
      setStatus("Location is not supported. Tap the map to choose a location manually.");
      return;
    }
    locateButton.disabled = true;
    setStatus("Requesting your location…");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        locateButton.disabled = false;
        discover(position.coords.latitude, position.coords.longitude);
      },
      (error) => {
        locateButton.disabled = false;
        const messages = {
          1: "Location permission denied. Tap the map to choose your location manually.",
          2: "Your location is unavailable. Tap the map to choose a location manually.",
          3: "Location request timed out. Please try again or tap the map."
        };
        setStatus(messages[error.code] || "Could not get your location. Tap the map to choose manually.");
      },
      {enableHighAccuracy: true, timeout: 12000, maximumAge: 30000}
    );
  });

  map.on("click", (event) => {
    discover(event.latlng.lat, event.latlng.lng);
    setStatus("Using the point you selected on the map to find nearby buses…");
  });

  async function search() {
    const query = searchInput.value.trim();
    if (query.length < 2) {
      setStatus("Enter at least 2 characters to search.");
      return;
    }
    clearLayers();
    showEmpty("Searching routes and stops…");
    setStatus("Searching Karachi bus routes and stops…");
    try {
      const data = await getJson("/api/v1/search?q=" + encodeURIComponent(query));
      resultsElement.replaceChildren();
      const summary = document.createElement("p");
      summary.className = "small text-secondary";
      summary.textContent = data.route_count + " routes · " + data.stop_count + " stops";
      resultsElement.append(summary);
      data.routes.forEach((route) => {
        const card = document.createElement("div");
        card.className = "border rounded-3 p-2 mb-2";
        const title = document.createElement("div");
        title.className = "fw-semibold";
        title.textContent = route.code + " · " + route.name;
        card.append(title);
        if (route.operator) {
          const operator = document.createElement("div");
          operator.className = "small text-secondary";
          operator.textContent = route.operator;
          card.append(operator);
        }
        route.directions.forEach((direction) => {
          const label = direction.name + ((direction.start || direction.end)
            ? " · " + (direction.start || "") + " → " + (direction.end || "") : "");
          card.append(makeButton(label, () => showDirection(direction.id),
            "btn btn-sm btn-outline-success w-100 text-start mt-2"));
        });
        resultsElement.append(card);
      });
      data.stops.forEach((stop) => {
        const card = document.createElement("div");
        card.className = "border rounded-3 p-2 mb-2";
        const title = document.createElement("div");
        title.className = "fw-semibold";
        title.textContent = stop.name;
        card.append(title);
        if (stop.address) {
          const address = document.createElement("div");
          address.className = "small text-secondary";
          address.textContent = stop.address;
          card.append(address);
        }
        card.append(makeButton("Show stop on map", () => {
          clearLayers();
          const marker = renderStopMarker(stop, true);
          map.setView([stop.lat, stop.lng], 16);
          marker.openPopup();
          setStatus("Showing " + stop.name + ". Use GPS or choose a map point to discover nearby routes.");
        }));
        resultsElement.append(card);
      });
      if (!data.routes.length && !data.stops.length) {
        showEmpty("No matching active routes or stops. Try another search.");
      }
      setStatus("Search complete. Select a direction to see its mapped path and stops.");
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    }
  }

  searchButton.addEventListener("click", search);
  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") search();
  });


  async function findJourneys() {
    const destination = journeyInput.value.trim();
    if (destination.length < 2) {
      setStatus("Enter at least 2 characters for the destination stop or area.");
      return;
    }
    if (!currentOrigin) {
      setStatus("First use GPS or tap the map to select your starting location.");
      return;
    }
    journeyButton.disabled = true;
    setStatus("Finding direct and one-transfer journeys…");
    showEmpty("Checking published route directions…");
    try {
      const params = new URLSearchParams({
        origin_lat: currentOrigin.lat,
        origin_lng: currentOrigin.lng,
        radius: radiusSelect.value || "1500",
        destination
      });
      const data = await getJson("/api/v1/journeys?" + params.toString());
      resultsElement.replaceChildren();
      if (!data.journeys.length) {
        showEmpty(data.message || "No matching journey found.");
        setStatus(data.message || "No journey found.");
        return;
      }
      const summary = document.createElement("p");
      summary.className = "small text-secondary";
      summary.textContent = data.journey_count + " options found. Routes are based on published stop sequences; times and fares are not available.";
      resultsElement.append(summary);
      data.journeys.forEach((journey, index) => {
        const card = document.createElement("div");
        card.className = "border rounded-3 p-2 mb-2";
        const heading = document.createElement("div");
        heading.className = "fw-semibold";
        heading.textContent = (index + 1) + ". " +
          (journey.type === "direct" ? "Direct bus" : "One transfer");
        const description = document.createElement("div");
        description.className = "small text-secondary mb-2";
        description.textContent = "Board: " + journey.origin_stop.name +
          (journey.transfer_stop ? " · Change at: " + journey.transfer_stop.name : "") +
          " · Get off: " + journey.destination_stop.name;
        card.append(heading, description);
        journey.legs.forEach((leg, legIndex) => {
          const route = leg.direction.route;
          const button = makeButton(
            (legIndex === 0 ? "Leg 1: " : "Leg 2: ") + route.code + " · " +
            route.name + " (" + leg.direction.name + ")",
            () => showDirection(leg.direction.id),
            "btn btn-sm btn-outline-success w-100 text-start mb-1"
          );
          card.append(button);
        });
        resultsElement.append(card);
      });
      setStatus("Found " + data.journey_count + " journey options. Select a leg to display its full route and stop sequence.");
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    } finally {
      journeyButton.disabled = false;
    }
  }

  journeyButton.addEventListener("click", findJourneys);
  journeyInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") findJourneys();
  });


  if ("serviceWorker" in navigator && window.isSecureContext) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/service-worker.js")
        .catch((error) => console.error("Service worker registration failed:", error));
    });
  }
})();
