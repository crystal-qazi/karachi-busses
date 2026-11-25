(() => {
  "use strict";
  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const map = L.map(mapElement).setView(
    [Number(mapElement.dataset.lat), Number(mapElement.dataset.lng)],
    Number(mapElement.dataset.zoom)
  );
  const tileUrl = mapElement.dataset.tileUrl || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const tileAttribution = mapElement.dataset.tileAttribution
    || '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>';
  L.tileLayer(tileUrl, {
    maxZoom: Number(mapElement.dataset.tileMaxZoom || 19),
    attribution: tileAttribution
  }).addTo(map);

  const status = document.getElementById("location-status");
  const locateButton = document.getElementById("locate-button");
  const resultsElement = document.getElementById("discovery-results");
  const searchInput = document.getElementById("destination-input");
  const searchButton = document.getElementById("search-button");
  const fromInput = document.getElementById("journey-from");
  const toInput = document.getElementById("journey-to");
  const journeyButton = document.getElementById("journey-button");
  const mapLocationInput = document.getElementById("map-location-input");
  const mapLocationButton = document.getElementById("map-location-button");
  let currentOrigin = null;
  const radiusSelect = document.getElementById("radius-select");
  const userLayer = L.layerGroup().addTo(map);
  const destinationLayer = L.layerGroup().addTo(map);
  const stopsLayer = L.layerGroup().addTo(map);
  let activeMapTarget = "from";
  const routeLayer = L.layerGroup().addTo(map);
  const routePalette = [
    "#d73027", "#4575b4", "#1a9850", "#984ea3", "#f46d43",
    "#3288bd", "#66a61e", "#e7298a", "#a6761d", "#00a6a6",
    "#6a3d9a", "#e6ab02", "#1f78b4", "#b15928", "#4daf4a"
  ];

  function setStatus(message) { if (status) status.textContent = message; }
  function clearLayers() {
    stopsLayer.clearLayers();
    routeLayer.clearLayers();
  }
  function routeColor(routeId) {
    let hash = 0;
    String(routeId).split("").forEach((character) => {
      hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
    });
    return routePalette[Math.abs(hash) % routePalette.length];
  }
  function addUserMarker(lat, lng, label) {
    userLayer.clearLayers();
    L.circleMarker([lat, lng], {
      radius: 9, color: "#fff", weight: 3, fillColor: "#1769aa", fillOpacity: 1
    }).addTo(userLayer).bindPopup(label || "Selected starting location");
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
    if (!resultsElement) return;
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
  async function geocodeLocation(query) {
    const data = await getJson("/api/v1/locations/search?q=" + encodeURIComponent(query));
    if (!data.locations.length) throw new Error('No Karachi map location found for "' + query + '". Try a nearby landmark or tap the map.');
    return data.locations[0];
  }
  function renderStopMarker(stop, focus, color) {
    const marker = L.marker([stop.lat, stop.lng]).addTo(stopsLayer);
    const popup = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = stop.name;
    const detail = document.createElement("div");
    detail.textContent = stop.distance_metres != null
      ? Math.round(stop.distance_metres) + " m away"
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
      stopsLayer.clearLayers();
      const color = routeColor(data.direction.route.id);
      if (data.shape && data.shape.type === "LineString" && Array.isArray(data.shape.coordinates)) {
        L.polyline(data.shape.coordinates.map((pair) => [pair[1], pair[0]]),
          {color, weight: 5, opacity: .92}).addTo(routeLayer);
      }
      const bounds = [];
      data.stops.forEach((stop) => {
        L.circleMarker([stop.lat, stop.lng], {
          radius: 6, color: "#fff", weight: 2, fillColor: color, fillOpacity: 1
        }).addTo(stopsLayer).bindPopup(stop.sequence + ". " + stop.name);
        bounds.push([stop.lat, stop.lng]);
      });
      if (data.shape && data.shape.coordinates) data.shape.coordinates.forEach((pair) => bounds.push([pair[1], pair[0]]));
      if (bounds.length) map.fitBounds(bounds, {padding: [30, 30], maxZoom: 15});
      setStatus(data.direction.route.code + ": " + data.direction.name + ". " +
        data.stops.length + " active stops shown. Static route only; no live bus tracking.");
    } catch (error) {
      setStatus(error.message);
    }
  }


  async function showAllPublishedRoutes() {
    setStatus("Loading published bus routes on the map…");
    try {
      const data = await getJson("/api/v1/routes/map");
      routeLayer.clearLayers();
      stopsLayer.clearLayers();
      const bounds = [];
      data.directions.forEach((direction) => {
        const coordinates = direction.shape.coordinates;
        const points = coordinates.map((pair) => [pair[1], pair[0]]);
        L.polyline(points, {
          color: routeColor(direction.route.id),
          weight: 4,
          opacity: 0.78
        }).addTo(routeLayer).bindPopup(
          direction.route.code + " · " + direction.route.name + " — " + direction.name
        );
        bounds.push(...points);
      });
      if (bounds.length) map.fitBounds(bounds, {padding: [24, 24], maxZoom: 13});
      setStatus(data.direction_count
        ? data.direction_count + " published route directions shown. Search and select a route to isolate it on the map."
        : "No published route geometry is available yet. Search for a route or stop.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  function renderNearby(data) {
    // Nearby discovery only refreshes stop markers; keep the published route
    // geometry visible while the user chooses or changes their From point.
    stopsLayer.clearLayers();
    resultsElement.replaceChildren();
    if (!data.stops.length) {
      showEmpty("No active, verified bus stops with published routes were found within this radius. Unverified research candidates are intentionally hidden from the public map.");
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

  async function discover(lat, lng, label) {
    currentOrigin = {lat, lng, label: label || "Selected map point"};
    if (fromInput) fromInput.value = currentOrigin.label;
    addUserMarker(lat, lng, currentOrigin.label);
    map.setView([lat, lng], 15);
    setStatus("Searching nearby bus stops…");
    showEmpty("Searching published routes…");
    const radius = Number(radiusSelect?.value || 1500);
    try {
      const url = "/api/v1/discover/nearby?lat=" + encodeURIComponent(lat) +
        "&lng=" + encodeURIComponent(lng) + "&radius=" + radius + "&limit=60";
      renderNearby(await getJson(url));
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    }
  }

  if (radiusSelect) radiusSelect.addEventListener("change", () => {
    if (currentOrigin) {
      const {lat, lng, label} = currentOrigin;
      const radius = Number(radiusSelect.value || 1500);
      setStatus("Refreshing nearby routes…");
      getJson("/api/v1/discover/nearby?lat=" + lat + "&lng=" + lng + "&radius=" + radius + "&limit=60")
        .then(renderNearby).catch((error) => setStatus(error.message));
      addUserMarker(lat, lng, label);
    }
  });

  if (locateButton) locateButton.addEventListener("click", () => {
    if (!navigator.geolocation) {
      setStatus("Location is not supported. Tap the map to choose a location manually.");
      return;
    }
    locateButton.disabled = true;
    setStatus("Requesting your location…");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        locateButton.disabled = false;
        discover(position.coords.latitude, position.coords.longitude, "My current location");
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

  function setDestination(lat, lng, label) {
    const destinationLabel = label || ("Map point " + lat.toFixed(5) + ", " + lng.toFixed(5));
    if (toInput) {
      toInput.value = destinationLabel;
      toInput.dataset.lat = String(lat);
      toInput.dataset.lng = String(lng);
    }
    destinationLayer.clearLayers();
    L.circleMarker([lat, lng], {
      radius: 9, color: "#fff", weight: 3, fillColor: "#d94841", fillOpacity: 1
    }).addTo(destinationLayer).bindPopup("To: " + destinationLabel).openPopup();
    map.panTo([lat, lng]);
    setStatus("Destination set to " + destinationLabel + ". Click Find buses to see available journeys.");
  }

  if (fromInput) fromInput.addEventListener("focus", () => { activeMapTarget = "from"; });
  if (toInput) toInput.addEventListener("focus", () => { activeMapTarget = "to"; });

  map.on("click", (event) => {
    const {lat, lng} = event.latlng;
    if (activeMapTarget === "to") {
      setDestination(lat, lng);
      return;
    }
    discover(lat, lng,
      "Map point " + lat.toFixed(5) + ", " + lng.toFixed(5));
    setStatus("Using the point you selected on the map as your From location…");
  });

  async function search() {
    const query = searchInput?.value?.trim() || "";
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
        title.style.borderLeft = "5px solid " + routeColor(route.id);
        title.style.paddingLeft = "8px";
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
          setStatus("Showing " + stop.name + ". You can use it as a nearby From or To landmark.");
        }));
        resultsElement.append(card);
      });
      if (!data.routes.length && !data.stops.length) showEmpty("No matching active routes or stops. Try another search.");
      setStatus("Search complete. Select a direction to see its mapped path and stops.");
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    }
  }

  if (searchButton) searchButton.addEventListener("click", search);
  if (searchInput) searchInput.addEventListener("keydown", (event) => { if (event.key === "Enter") search(); });

  async function searchMapLocation() {
    const query = mapLocationInput?.value?.trim() || "";
    if (query.length < 2) { setStatus("Enter at least 2 characters for a map location."); return; }
    if (mapLocationButton) mapLocationButton.disabled = true;
    setStatus("Searching OpenStreetMap locations…");
    try {
      const data = await getJson("/api/v1/locations/search?q=" + encodeURIComponent(query));
      resultsElement.replaceChildren();
      if (!data.locations.length) {
        showEmpty("No Karachi location matched. Try another name or tap the map.");
        setStatus("No matching map location found.");
        return;
      }
      const summary = document.createElement("p");
      summary.className = "small text-secondary";
      summary.textContent = data.locations.length + " location matches. Choose the correct place:";
      resultsElement.append(summary);
      data.locations.forEach((location) => {
        const card = document.createElement("div");
        card.className = "border rounded-3 p-2 mb-2";
        const label = document.createElement("div");
        label.className = "small fw-semibold mb-2";
        label.textContent = location.label;
        card.append(label);
        card.append(makeButton("Show on map", () => {
          map.setView([location.lat, location.lng], 16);
          addUserMarker(location.lat, location.lng, location.label);
          setStatus("Map centred on " + location.label + ".");
        }));
        card.append(makeButton("Use as From", () => {
          currentOrigin = {lat: location.lat, lng: location.lng, label: location.label};
          fromInput.value = location.label;
          discover(location.lat, location.lng, location.label);
        }, "btn btn-sm btn-outline-success w-100 text-start mt-1"));
        card.append(makeButton("Use as To", () => {
          toInput.value = location.label;
          setDestination(location.lat, location.lng, location.label);
        }, "btn btn-sm btn-outline-primary w-100 text-start mt-1"));
        resultsElement.append(card);
      });
      setStatus("Choose a location result, then use it as From or To.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      if (mapLocationButton) mapLocationButton.disabled = false;
    }
  }
  // Map-place search was added after the original public map controls. Keep
  // the shared map script safe on cached/older markup and pages that omit it.
  if (mapLocationButton && mapLocationInput) {
    mapLocationButton.addEventListener("click", searchMapLocation);
    mapLocationInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") searchMapLocation();
    });
  }

  function addJourneyLegToMap(leg, color, fitPoints) {
    if (leg.shape && leg.shape.type === "LineString" && Array.isArray(leg.shape.coordinates)) {
      const points = leg.shape.coordinates.map((pair) => [pair[1], pair[0]]);
      L.polyline(points, {color, weight: 6, opacity: .95}).addTo(routeLayer);
      fitPoints.push(...points);
    }
    (leg.stops || []).forEach((stop, index) => {
      const marker = L.circleMarker([stop.lat, stop.lng], {
        radius: index === 0 || index === leg.stops.length - 1 ? 8 : 5,
        color: "#fff", weight: 2, fillColor: color, fillOpacity: 1
      }).addTo(stopsLayer);
      marker.bindPopup((stop.sequence || index + 1) + ". " + stop.name);
      fitPoints.push([stop.lat, stop.lng]);
    });
  }

  function showJourneyLeg(leg) {
    clearLayers();
    const points = [];
    const color = routeColor(leg.direction.route.id);
    addJourneyLegToMap(leg, color, points);
    if (points.length) map.fitBounds(points, {padding: [35, 35], maxZoom: 16});
    setStatus(leg.direction.route.code + " · " + leg.direction.route.name +
      ": showing only the selected From-to segment. " +
      (leg.shape ? "Saved road geometry displayed." : "No saved road geometry is available for this segment; stops are shown without drawing a straight line."));
  }

  async function findJourneys() {
    if (!fromInput || !toInput || !journeyButton) {
      setStatus("Journey search controls are missing from this page. Refresh the page and try again.");
      return;
    }
    const fromQuery = fromInput.value.trim();
    const toQuery = toInput.value.trim();
    if (!toQuery || toQuery.length < 2) {
      setStatus("Enter a destination in the To field.");
      return;
    }
    journeyButton.disabled = true;
    setStatus("Resolving From and To locations…");
    showEmpty("Searching locations and checking published bus routes…");
    try {
      let origin;
      if (fromQuery && currentOrigin && fromQuery === currentOrigin.label) {
        origin = currentOrigin;
      } else if (fromQuery.length >= 2) {
        origin = await geocodeLocation(fromQuery);
      } else if (currentOrigin) {
        origin = currentOrigin;
      } else {
        throw new Error("Enter a From location, use GPS, or tap the map to select your starting point.");
      }

      let destination;
      if (toInput.dataset.lat && toInput.dataset.lng) {
        destination = {lat: Number(toInput.dataset.lat), lng: Number(toInput.dataset.lng), label: toQuery};
      } else {
        destination = await geocodeLocation(toQuery);
      }
      if (fromQuery) {
        currentOrigin = {lat: origin.lat, lng: origin.lng, label: origin.label || fromQuery};
        addUserMarker(origin.lat, origin.lng, "From: " + (origin.label || fromQuery));
      }
      toInput.dataset.lat = destination.lat;
      toInput.dataset.lng = destination.lng;
      destinationLayer.clearLayers();
      L.circleMarker([destination.lat, destination.lng], {
        radius: 9, color: "#fff", weight: 3, fillColor: "#d94841", fillOpacity: 1
      }).addTo(destinationLayer).bindPopup("To: " + (destination.label || toQuery));

      const params = new URLSearchParams({
        origin_lat: origin.lat, origin_lng: origin.lng,
        destination_lat: destination.lat, destination_lng: destination.lng,
        radius: radiusSelect?.value || "1500"
      });
      const data = await getJson("/api/v1/journeys?" + params.toString());
      resultsElement.replaceChildren();
      if (!data.journeys.length) {
        showEmpty(data.message || "No matching bus journey found.");
        setStatus(data.message || "No journey found.");
        return;
      }

      const summary = document.createElement("p");
      summary.className = "small text-secondary";
      summary.textContent = data.journey_count + " journey options · " +
        data.origin_stop_count + " boarding-area stops · " +
        data.destination_stop_count + " destination-area stops. Each route has its own color.";
      resultsElement.append(summary);

      const colorLegend = document.createElement("div");
      colorLegend.className = "small mb-2";
      colorLegend.textContent = "Colored lines show saved route geometry between the selected stops.";
      resultsElement.append(colorLegend);

      const allPoints = [];
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
          const color = routeColor(route.id);
          const row = document.createElement("div");
          row.className = "d-flex align-items-center gap-2 mb-1";
          const swatch = document.createElement("span");
          swatch.style.cssText = "display:inline-block;width:18px;height:5px;border-radius:4px;flex:0 0 18px;background:" + color;
          const text = document.createElement("span");
          text.className = "small flex-grow-1";
          text.textContent = (journey.legs.length > 1 ? "Leg " + (legIndex + 1) + ": " : "") +
            route.code + " · " + route.name + " (" + leg.direction.name + ")";
          row.append(swatch, text);
          card.append(row);
          card.append(makeButton("Show only " + route.code + " on map",
            () => showJourneyLeg(leg),
            "btn btn-sm btn-outline-success w-100 text-start mb-1"));
          addJourneyLegToMap(leg, color, allPoints);
        });
        resultsElement.append(card);
      });
      if (allPoints.length) map.fitBounds(allPoints, {padding: [35, 35], maxZoom: 14});
      setStatus("Found " + data.journey_count + " journeys from " +
        (origin.label || fromQuery || "selected point") + " to " +
        (destination.label || toQuery) + ". Select a bus to show only its From-to segment.");
    } catch (error) {
      showEmpty(error.message);
      setStatus(error.message);
    } finally {
      journeyButton.disabled = false;
    }
  }

  if (journeyButton) journeyButton.addEventListener("click", findJourneys);

  // Show all published route lines on the initial map; route selection isolates one direction.
  showAllPublishedRoutes();
  [fromInput, toInput].filter(Boolean).forEach((input) => {
    input.addEventListener("input", () => {
      if (input === toInput) {
        delete input.dataset.lat;
        delete input.dataset.lng;
      }
    });
    input.addEventListener("keydown", (event) => { if (event.key === "Enter") findJourneys(); });
  });

  if ("serviceWorker" in navigator && window.isSecureContext) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/service-worker.js")
        .catch((error) => console.error("Service worker registration failed:", error));
    });
  }
})();
