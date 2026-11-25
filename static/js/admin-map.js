(() => {
  "use strict";
  const el = document.getElementById("route-map");
  if (!el || !window.L || !L.Control.Draw) return;

  const map = L.map(el, { preferCanvas: true }).setView([24.8607, 67.0011], 11);
  const tileUrl = el.dataset.tileUrl || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const tileAttribution = el.dataset.tileAttribution || '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>';
  L.tileLayer(tileUrl, { maxZoom: Number(el.dataset.tileMaxZoom || 19), attribution: tileAttribution }).addTo(map);

  const drawn = new L.FeatureGroup().addTo(map);
  const existing = JSON.parse(el.dataset.shape || "null");
  if (existing) {
    const layer = L.geoJSON(existing);
    layer.eachLayer(child => drawn.addLayer(child));
    if (layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), { padding: [24, 24] });
  }

  const drawControl = new L.Control.Draw({
    draw: { polyline: { shapeOptions: { color: "#126b50", weight: 5 } }, polygon: false, rectangle: false, circle: false, circlemarker: false, marker: false },
    edit: { featureGroup: drawn, remove: true }
  });
  map.addControl(drawControl);

  const pointSelect = document.getElementById("route-point-select");
  const pointCount = document.getElementById("route-point-count");
  const undoButton = document.getElementById("undo-point");
  const redoButton = document.getElementById("redo-point");
  const removeButton = document.getElementById("remove-point");
  const redoStack = [];
  let selectedLocationMarker = null;
  let verifyMode = false;

  function getLine() {
    return drawn.getLayers().find(layer => layer instanceof L.Polyline && !(layer instanceof L.Polygon)) || null;
  }
  function getLatLngs() {
    const line = getLine();
    if (!line) return [];
    const points = line.getLatLngs();
    return Array.isArray(points[0]) ? points[0] : points;
  }
  function replacePoints(points) {
    drawn.clearLayers();
    if (points.length >= 2) drawn.addLayer(L.polyline(points, { color: "#126b50", weight: 5 }));
    refreshPointControls();
  }
  function refreshPointControls() {
    const points = getLatLngs();
    pointSelect.innerHTML = "";
    points.forEach((point, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = `Point ${index + 1} — ${point.lat.toFixed(6)}, ${point.lng.toFixed(6)}`;
      pointSelect.appendChild(option);
    });
    pointCount.textContent = `${points.length} route points`;
    undoButton.disabled = points.length === 0;
    removeButton.disabled = points.length < 2 || !pointSelect.value;
    redoButton.disabled = redoStack.length === 0;
  }

  undoButton.addEventListener("click", () => {
    const points = getLatLngs();
    if (!points.length) return;
    redoStack.push(points[points.length - 1]);
    replacePoints(points.slice(0, -1));
  });
  redoButton.addEventListener("click", () => {
    if (!redoStack.length) return;
    const points = getLatLngs();
    points.push(redoStack.pop());
    replacePoints(points);
  });
  removeButton.addEventListener("click", () => {
    const index = Number(pointSelect.value);
    const points = getLatLngs();
    if (!Number.isInteger(index) || index < 0 || index >= points.length || points.length <= 2) return;
    redoStack.push(points[index]);
    points.splice(index, 1);
    replacePoints(points);
  });
  pointSelect.addEventListener("change", () => {
    const index = Number(pointSelect.value);
    const point = getLatLngs()[index];
    removeButton.disabled = !point || getLatLngs().length <= 2;
    if (point) map.panTo(point);
  });

  map.on(L.Draw.Event.CREATED, event => {
    drawn.clearLayers();
    drawn.addLayer(event.layer);
    redoStack.length = 0;
    refreshPointControls();
  });
  map.on(L.Draw.Event.EDITED, refreshPointControls);
  map.on(L.Draw.Event.DELETED, refreshPointControls);
  document.getElementById("clear-shape")?.addEventListener("click", () => {
    if (!drawn.getLayers().length || !window.confirm("Clear the complete route line?")) return;
    drawn.clearLayers();
    redoStack.length = 0;
    refreshPointControls();
  });

  const geojsonFileInput = document.getElementById("geojson-file");
  const importGeojsonButton = document.getElementById("import-geojson");
  const geojsonUploadStatus = document.getElementById("geojson-upload-status");
  importGeojsonButton?.addEventListener("click", async () => {
    const file = geojsonFileInput?.files?.[0];
    const reportUpload = message => {
      if (geojsonUploadStatus) geojsonUploadStatus.textContent = message;
    };
    if (!file) {
      reportUpload("Choose a .geojson or .json file first.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      reportUpload("GeoJSON file must be 2 MB or smaller.");
      return;
    }
    importGeojsonButton.disabled = true;
    reportUpload("Reading GeoJSON…");
    try {
      const parsed = JSON.parse(await file.text());
      let geometry = parsed;
      if (parsed?.type === "Feature") geometry = parsed.geometry;
      if (parsed?.type === "FeatureCollection") {
        const features = parsed.features || [];
        if (features.length !== 1) {
          throw new Error("FeatureCollection must contain exactly one route feature.");
        }
        geometry = features[0]?.geometry;
      }
      if (!geometry || geometry.type !== "LineString" ||
          !Array.isArray(geometry.coordinates) ||
          geometry.coordinates.length < 2 || geometry.coordinates.length > 20000) {
        throw new Error("Expected a GeoJSON LineString or a Feature containing one, with 2–20,000 points.");
      }
      const points = geometry.coordinates.map(pair => {
        if (!Array.isArray(pair) || pair.length < 2 ||
            !Number.isFinite(Number(pair[0])) || !Number.isFinite(Number(pair[1]))) {
          throw new Error("GeoJSON contains an invalid coordinate pair.");
        }
        const lng = Number(pair[0]);
        const lat = Number(pair[1]);
        if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
          throw new Error("GeoJSON contains coordinates outside valid longitude/latitude ranges.");
        }
        return L.latLng(lat, lng);
      });
      replacePoints(points);
      redoStack.length = 0;
      map.fitBounds(L.latLngBounds(points), { padding: [24, 24] });
      reportUpload("Loaded " + points.length + " route points. Review the line, then click Save route line.");
    } catch (error) {
      reportUpload("Could not load GeoJSON: " + error.message);
    } finally {
      importGeojsonButton.disabled = false;
    }
  });

  const searchForm = document.getElementById("place-search-form");
  const searchInput = document.getElementById("place-search");
  const searchStatus = document.getElementById("place-search-status");
  searchForm?.addEventListener("submit", async event => {
    event.preventDefault();
    const query = searchInput.value.trim();
    if (!query) return;
    searchStatus.textContent = "Searching OpenStreetMap…";
    try {
      const url = new URL("https://nominatim.openstreetmap.org/search");
      url.search = new URLSearchParams({ q: query + ", Karachi, Pakistan", format: "jsonv2", limit: "5", addressdetails: "1" });
      const response = await fetch(url, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("Place search is temporarily unavailable.");
      const results = await response.json();
      if (!results.length) { searchStatus.textContent = "No matching place found. Try another name."; return; }
      searchStatus.textContent = "";
      const first = results[0];
      const latlng = L.latLng(Number(first.lat), Number(first.lon));
      if (selectedLocationMarker) map.removeLayer(selectedLocationMarker);
      selectedLocationMarker = L.marker(latlng).addTo(map).bindPopup(first.display_name).openPopup();
      map.setView(latlng, 16);
      document.getElementById("verified-place").textContent = first.display_name;
      document.getElementById("verified-coordinates").textContent = `${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}`;
    } catch (error) {
      searchStatus.textContent = error.message || "Could not search this place.";
    }
  });

  const verifyButton = document.getElementById("verify-map-point");
  verifyButton?.addEventListener("click", () => {
    verifyMode = !verifyMode;
    verifyButton.classList.toggle("btn-success", verifyMode);
    verifyButton.classList.toggle("btn-outline-success", !verifyMode);
    verifyButton.textContent = verifyMode ? "Click map to verify… (Cancel)" : "Verify a point on map";
    map.getContainer().style.cursor = verifyMode ? "crosshair" : "";
  });
  map.on("click", async event => {
    if (!verifyMode) return;
    verifyMode = false;
    verifyButton.classList.remove("btn-success");
    verifyButton.classList.add("btn-outline-success");
    verifyButton.textContent = "Verify a point on map";
    map.getContainer().style.cursor = "";
    const { lat, lng } = event.latlng;
    document.getElementById("verified-place").textContent = "Looking up nearby landmark…";
    document.getElementById("verified-coordinates").textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    if (selectedLocationMarker) map.removeLayer(selectedLocationMarker);
    selectedLocationMarker = L.marker(event.latlng).addTo(map);
    try {
      const url = new URL("https://nominatim.openstreetmap.org/reverse");
      url.search = new URLSearchParams({ lat: String(lat), lon: String(lng), format: "jsonv2", zoom: "18", addressdetails: "1" });
      const response = await fetch(url, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("Reverse lookup unavailable.");
      const result = await response.json();
      const label = result.display_name || "No named landmark found at this point.";
      document.getElementById("verified-place").textContent = label;
      selectedLocationMarker.bindPopup(label).openPopup();
    } catch (error) {
      document.getElementById("verified-place").textContent = "Landmark lookup unavailable. Coordinates are shown above.";
      selectedLocationMarker.bindPopup("Selected map point").openPopup();
    }
  });

  document.getElementById("map-fullscreen")?.addEventListener("click", async () => {
    const wrapper = document.getElementById("route-map-panel");
    try {
      if (!document.fullscreenElement) await wrapper.requestFullscreen();
      else await document.exitFullscreen();
    } catch (_) { /* Fullscreen may be blocked by the browser. */ }
    setTimeout(() => map.invalidateSize(), 150);
  });
  document.addEventListener("fullscreenchange", () => setTimeout(() => map.invalidateSize(), 150));

  document.getElementById("shape-form")?.addEventListener("submit", event => {
    const layers = drawn.getLayers();
    const line = getLine();
    const points = getLatLngs();
    if (!line || points.length < 2) {
      event.preventDefault();
      alert("Draw a route line with at least two points before saving.");
      return;
    }
    const feature = line.toGeoJSON();
    document.getElementById("shape-json").value = JSON.stringify(feature.geometry);
  });
  refreshPointControls();
  setTimeout(() => map.invalidateSize(), 100);
})();
