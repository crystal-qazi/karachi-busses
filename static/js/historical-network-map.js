(() => {
  "use strict";
  const mapElement = document.getElementById("historical-map");
  if (!mapElement) return;
  const message = document.getElementById("map-message");
  if (!window.L) {
    if (message) {
      message.textContent = "The map library (Leaflet) did not load. Check the browser network tab, CDN access and Content Security Policy.";
      message.classList.add("text-danger");
    }
    return;
  }

  const map = L.map(mapElement).setView([24.8607, 67.0011], 11);
  const tileUrl = mapElement.dataset.tileUrl
    || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const tileAttribution = mapElement.dataset.tileAttribution
    || '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  L.tileLayer(tileUrl, {
    maxZoom: Number(mapElement.dataset.tileMaxZoom || 19),
    attribution: tileAttribution
  }).addTo(map);

  // Keep the QA map usable when the optional MarkerCluster CDN asset is unavailable.
  const hasMarkerCluster = typeof L.markerClusterGroup === "function";
  const stopLayer = hasMarkerCluster
    ? L.markerClusterGroup({ chunkedLoading: true, maxClusterRadius: 42 })
    : L.layerGroup();
  const segmentLayer = L.layerGroup().addTo(map);
  const anomalyLayer = L.layerGroup().addTo(map);
  const collisionLayer = L.layerGroup().addTo(map);
  const routeFilter = document.getElementById("route-filter");
  const showSegments = document.getElementById("show-segments");
  const showCollisions = document.getElementById("show-collisions");
  const showAnomalies = document.getElementById("show-anomalies");
  let dataset = null;

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);

  const coordinateKey = (stop) => Number(stop.lat).toFixed(7) + "," + Number(stop.lng).toFixed(7);
  const routeColor = (code) => {
    let hash = 0;
    for (const char of code) hash = (hash * 31 + char.charCodeAt(0)) | 0;
    return "hsl(" + (Math.abs(hash) % 360) + " 68% 38%)";
  };

  function buildStops() {
    stopLayer.clearLayers();
    collisionLayer.clearLayers();
    const groups = new Map();
    dataset.stops.forEach((stop) => {
      const key = coordinateKey(stop);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(stop);
    });

    groups.forEach((stops) => {
      const first = stops[0];
      const collision = stops.length > 1;
      const popup = collision
        ? "<strong>Shared coordinate · " + stops.length + " source stop names</strong><ul class='mb-0 mt-2'>" +
          stops.map((stop) => "<li>" + escapeHtml(stop.name) + " <small>(ID " + stop.id + ")</small></li>").join("") + "</ul>"
        : "<strong>" + escapeHtml(first.name) + "</strong><br><small>Source stop ID " + first.id + " · " +
          escapeHtml(first.status) + "</small>";
      if (collision && showCollisions.checked) {
        const icon = L.divIcon({
          className: "",
          html: "<span style='display:block;width:17px;height:17px;border:3px solid white;border-radius:50%;background:#e49b19;box-shadow:0 1px 5px #555'></span>",
          iconSize: [17, 17], iconAnchor: [8, 8]
        });
        const marker = L.marker([first.lat, first.lng], { icon }).bindPopup(popup);
        collisionLayer.addLayer(marker);
      } else if (collision) {
        stops.forEach((stop) => {
          stopLayer.addLayer(L.marker([stop.lat, stop.lng]).bindPopup(
            "<strong>" + escapeHtml(stop.name) + "</strong><br><small>Shares coordinates with " +
            (stops.length - 1) + " other source stop(s)</small>"
          ));
        });
      } else {
        const stopIcon = L.divIcon({
          className: "",
          html: "<span style='display:block;width:11px;height:11px;border:2px solid white;border-radius:50%;background:#2478b8;box-shadow:0 1px 4px #555'></span>",
          iconSize: [11, 11], iconAnchor: [5, 5]
        });
        stopLayer.addLayer(L.marker([first.lat, first.lng], { icon: stopIcon }).bindPopup(popup));
      }
    });
    map.addLayer(stopLayer);
    if (showCollisions.checked) map.addLayer(collisionLayer);
    else map.removeLayer(collisionLayer);
    document.getElementById("stat-collisions").textContent =
      Array.from(groups.values()).filter((items) => items.length > 1).length;
  }

  function buildSegments() {
    segmentLayer.clearLayers();
    anomalyLayer.clearLayers();
    if (!showSegments.checked && !showAnomalies.checked) return;
    const selected = routeFilter.value;
    dataset.segments.forEach((segment) => {
      if (selected && segment.route_code !== selected) return;
      const from = [segment.from.lat, segment.from.lng];
      const to = [segment.to.lat, segment.to.lng];
      const detail = "<strong>Route " + escapeHtml(segment.route_code) + "</strong> · segment " +
        segment.sequence + "<br>" + escapeHtml(segment.from.name) + " → " +
        escapeHtml(segment.to.name) +
        "<br><small>Source-listed straight connector; not road geometry.</small>";
      if (segment.self_loop) {
        if (showAnomalies.checked) {
          const marker = L.circleMarker(from, {
            radius: 10, color: "#8e1b16", weight: 3, fillColor: "#e74c3c", fillOpacity: .9
          }).bindPopup(detail + "<br><strong>Review anomaly: self-loop</strong>");
          anomalyLayer.addLayer(marker);
        }
      } else if (showSegments.checked) {
        const line = L.polyline([from, to], {
          color: routeColor(segment.route_code), weight: 2.5, opacity: .72,
          dashArray: "7 6"
        }).bindTooltip(detail, { sticky: true }).bindPopup(detail);
        segmentLayer.addLayer(line);
      }
    });
    if (showAnomalies.checked) map.addLayer(anomalyLayer);
    else map.removeLayer(anomalyLayer);
    map.addLayer(segmentLayer);
  }

  function render() {
    buildStops();
    buildSegments();
    const selected = routeFilter.value;
    const visibleSegments = dataset.segments.filter((segment) => !selected || segment.route_code === selected);
    const stopCount = dataset.stops.length;
    const markerMode = hasMarkerCluster
      ? "Markers are clustered at wider zoom levels."
      : "Marker-cluster library unavailable; displaying individual markers instead.";
    if (stopCount === 0) {
      const reported = dataset.counts && Number.isFinite(Number(dataset.counts.stops))
        ? Number(dataset.counts.stops) : null;
      message.textContent = reported && reported > 0
        ? "The data endpoint reports " + reported + " stops, but returned an empty stop list. Check the historical source_id query and database rows."
        : "No historical stop records were returned. Check that the historical dataset has been imported into this database and that its source name matches the configured research source.";
      message.classList.add("text-danger");
      return;
    }
    message.classList.remove("text-danger");
    message.textContent = (selected ? "Route " + selected + ": " : "All routes: ") +
      visibleSegments.length + " source-listed segments shown when enabled. " +
      stopCount + " unverified historical source stop markers loaded. " + markerMode;
  }

  async function load() {
    try {
      const response = await fetch("/admin/historical-network/data", {
        headers: { "Accept": "application/json" },
        credentials: "same-origin"
      });
      if (!response.ok) throw new Error("Server returned " + response.status);
      dataset = await response.json();
      if (!dataset.success) throw new Error(dataset.error || "Could not load the historical network.");
      if (!Array.isArray(dataset.stops) || !Array.isArray(dataset.routes) || !Array.isArray(dataset.segments)) {
        throw new Error("Historical map response is missing stops, routes or segments.");
      }
      dataset.routes.forEach((route) => {
        const option = document.createElement("option");
        option.value = route.code;
        option.textContent = route.code + " · " + route.segment_count + " segments" +
          (route.self_loop_count ? " · " + route.self_loop_count + " anomaly" : "");
        routeFilter.appendChild(option);
      });
      document.getElementById("stat-stops").textContent = dataset.counts.stops;
      document.getElementById("stat-routes").textContent = dataset.counts.routes;
      document.getElementById("stat-segments").textContent = dataset.counts.segments;
      const bounds = L.latLngBounds(dataset.stops.map((stop) => [stop.lat, stop.lng]));
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [24, 24] });
      render();
    } catch (error) {
      message.textContent = "Could not load historical map data: " + error.message;
      message.classList.add("text-danger");
    }
  }

  [routeFilter, showSegments, showCollisions, showAnomalies].forEach((control) => {
    control.addEventListener("change", () => { if (dataset) render(); });
  });
  load();
})();
