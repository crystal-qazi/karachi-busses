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

  // Admin-only, click-to-preview road routing. The public OSRM demo is best-effort
  // and limited to one request per second; never bulk-route the historical graph.
  let lastRoadRequestAt = 0;
  let roadRequestInFlight = false;

  async function previewRoadPath(segment, line, sourceDetail) {
    if (roadRequestInFlight) {
      line.setPopupContent(sourceDetail + "<br><strong>Another road preview is already running. Please wait.</strong>");
      return;
    }
    const now = Date.now();
    if (now - lastRoadRequestAt < 1100) {
      line.setPopupContent(sourceDetail + "<br><strong>Please wait at least one second between road-preview requests.</strong>");
      return;
    }
    if (!segment.from || !segment.to ||
        !Number.isFinite(Number(segment.from.lat)) || !Number.isFinite(Number(segment.from.lng)) ||
        !Number.isFinite(Number(segment.to.lat)) || !Number.isFinite(Number(segment.to.lng))) {
      line.setPopupContent(sourceDetail + "<br><strong>Road preview unavailable: stop coordinates are invalid.</strong>");
      return;
    }

    roadRequestInFlight = true;
    lastRoadRequestAt = now;
    line.setPopupContent(sourceDetail + "<br><small>Requesting a road-following candidate from OSRM / OpenStreetMap…</small>");
    try {
      const coordinates = [
        Number(segment.from.lng) + "," + Number(segment.from.lat),
        Number(segment.to.lng) + "," + Number(segment.to.lat)
      ].join(";");
      const url = "https://router.project-osrm.org/route/v1/driving/" +
        coordinates + "?overview=full&geometries=geojson&steps=false&alternatives=false";
      const response = await fetch(url, {
        headers: { "Accept": "application/json" },
        credentials: "omit",
        mode: "cors"
      });
      if (!response.ok) throw new Error("Routing service returned HTTP " + response.status + ".");
      const payload = await response.json();
      if (payload.code !== "Ok" || !Array.isArray(payload.routes) ||
          !payload.routes[0] || !payload.routes[0].geometry ||
          !Array.isArray(payload.routes[0].geometry.coordinates) ||
          payload.routes[0].geometry.coordinates.length < 2) {
        throw new Error("No drivable road path was returned for these stop coordinates.");
      }
      const route = payload.routes[0];
      const latLngs = route.geometry.coordinates.map((point) => [Number(point[1]), Number(point[0])]);
      if (latLngs.some((point) => !Number.isFinite(point[0]) || !Number.isFinite(point[1]))) {
        throw new Error("The routing service returned invalid geometry.");
      }
      line.setLatLngs(latLngs);
      line.setStyle({ color: "#1769aa", weight: 4, opacity: .92, dashArray: null });
      const km = (Number(route.distance) / 1000).toFixed(2);
      const roadDetail = sourceDetail +
        "<hr><strong>Road-routing candidate: " + km + " km</strong>" +
        "<br><small>Generated from OpenStreetMap road data by OSRM. This is a drivable-road candidate, NOT proof that the bus uses this road or that the stop boarding points are verified. Preview only; not saved.</small>" +
        "<br><small>Routing: OSRM · Map data: © OpenStreetMap contributors.</small>";
      line.setPopupContent(roadDetail).openPopup();
      line.unbindTooltip();
      line.bindTooltip("OSRM road candidate · " + km + " km · not a verified bus path", { sticky: true });
    } catch (error) {
      line.setPopupContent(sourceDetail + "<br><strong>Road preview unavailable:</strong> " +
        escapeHtml(error.message) + "<br><small>The original straight connector remains visible. No data was changed.</small>");
    } finally {
      roadRequestInFlight = false;
    }
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
        segment.sequence + "<br>" + escapeHtml(segment.from.name) + " (stop " + segment.from.id + ") → " +
        escapeHtml(segment.to.name) + " (stop " + segment.to.id + ")" +
        "<br><small>Source-listed connector. Click the line to request a temporary OSM road-routing candidate; this is not verified bus alignment.</small>";
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
        line.on("click", () => previewRoadPath(segment, line, detail));
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

  // Admin-only snap preview. Proposes geometric OSM road snap candidates for
  // one stop via the server endpoint. Each candidate is a preview only, never
  // proof of the bus stop location; nothing is saved and no coordinates change.
  const snapPreviewLayer = L.layerGroup().addTo(map);
  const showSnapPreview = document.getElementById("show-snap-preview");
  const snapPreviewBtn = document.getElementById("snap-preview-btn");
  const snapStopId = document.getElementById("snap-stop-id");
  const snapCandidateSelect = document.getElementById("snap-candidate");
  let snapPreviewInFlight = false;
  let snapCandidates = [];
  let snapOriginal = null;

  function clearSnapPreview() {
    snapPreviewLayer.clearLayers();
  }

  function candidateLabel(candidate, index) {
    return "#" + (index + 1) + " · " +
      (candidate.road_name || "(unnamed)") +
      (candidate.highway ? " (" + candidate.highway + ")" : "") +
      " · " + candidate.distance_m + " m";
  }

  function populateCandidateSelect() {
    snapCandidateSelect.innerHTML = "";
    snapCandidateSelect.disabled = snapCandidates.length === 0;
    if (snapCandidates.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "No road candidate";
      snapCandidateSelect.appendChild(opt);
      return;
    }
    snapCandidates.forEach((candidate, index) => {
      const opt = document.createElement("option");
      opt.value = String(index);
      opt.textContent = candidateLabel(candidate, index);
      snapCandidateSelect.appendChild(opt);
    });
    snapCandidateSelect.value = "0";
  }

  function renderSnapPreview(payload) {
    clearSnapPreview();
    snapCandidates = [];
    snapOriginal = null;
    snapCandidateSelect.disabled = true;
    if (!payload || payload.success !== true) {
      message.textContent = payload && payload.note
        ? payload.note.message
        : (payload && payload.error ? payload.error.message : "Snap preview unavailable.");
      message.classList.add("text-danger");
      return;
    }
    const original = payload.stop;
    snapOriginal = original;
    const candidates = Array.isArray(payload.candidates) ? payload.candidates : [];
    snapCandidates = candidates;
    populateCandidateSelect();

    const originalLatLng = L.latLng(original.latitude, original.longitude);
    snapPreviewLayer.addLayer(L.marker(originalLatLng, {
      icon: L.divIcon({ className: "", html: "<span style='display:block;width:13px;height:13px;border:3px solid white;border-radius:50%;background:#2478b8;box-shadow:0 1px 4px #555'></span>", iconSize: [13, 13], iconAnchor: [6, 6] })
    }).bindPopup("<strong>" + escapeHtml(original.name) + "</strong><br><small>Original stop " + original.id + " · " + escapeHtml(original.status) + "</small>"));

    // Draw every candidate's snap marker and connector; the selected candidate
    // additionally gets its road geometry highlighted.
    candidates.forEach((candidate, index) => {
      const latLng = L.latLng(candidate.latitude, candidate.longitude);
      const isSelected = index === Number(snapCandidateSelect.value);
      if (isSelected) {
        snapPreviewLayer.addLayer(L.marker(latLng, {
          icon: L.divIcon({ className: "", html: "<span style='display:block;width:14px;height:14px;border:3px solid white;border-radius:50%;background:#d35400;box-shadow:0 1px 4px #555'></span>", iconSize: [14, 14], iconAnchor: [7, 7] })
        }).bindPopup("<strong>Selected snap candidate</strong><br><small>Road: " + escapeHtml(candidate.road_name || "(unnamed)") + " · " + escapeHtml(candidate.highway || "") + "<br>OSM way " + escapeHtml(candidate.osm_way_id || "") + "<br>Distance: " + candidate.distance_m + " m</small>"));

        const connector = L.polyline([originalLatLng, latLng], {
          color: "#d35400", weight: 2, dashArray: "4 5", opacity: .9
        });
        connector.bindPopup("<strong>Proposed OSM snap</strong><br><small>" +
          escapeHtml(original.name) + " (stop " + original.id + ")</small><br>" +
          "<small>Distance: <strong>" + candidate.distance_m + " m</strong></small><br>" +
          "<small>Road: " + escapeHtml(candidate.road_name || "(unnamed)") + " (" + escapeHtml(candidate.highway || "?") + ")</small><br>" +
          "<small>OSM way " + escapeHtml(candidate.osm_way_id || "") + "</small><br>" +
          "<small class='text-danger'>Candidate only – not proof of the bus stop location. Nothing saved.</small>");
        snapPreviewLayer.addLayer(connector);

        // Highlight the exact road geometry of the selected candidate.
        if (Array.isArray(candidate.way_geometry) && candidate.way_geometry.length) {
          const coords = candidate.way_geometry.map((pair) => L.latLng(pair[1], pair[0]));
          const roadLine = L.polyline(coords, { color: "#8e44ad", weight: 4, opacity: 0.85 });
          roadLine.bindPopup("<strong>Candidate road</strong><br><small>OSM way " +
            escapeHtml(candidate.osm_way_id || "") + " · " +
            escapeHtml(candidate.road_name || "(unnamed)") + " (" +
            escapeHtml(candidate.highway || "?") + ")</small>");
          snapPreviewLayer.addLayer(roadLine);
        }
      } else {
        // Non-selected candidates render as muted markers for comparison.
        snapPreviewLayer.addLayer(L.marker(latLng, {
          icon: L.divIcon({ className: "", html: "<span style='display:block;width:11px;height:11px;border:2px solid white;border-radius:50%;background:#9a9a9a;box-shadow:0 1px 3px #555'></span>", iconSize: [11, 11], iconAnchor: [5, 5] })
        }).bindPopup("<strong>Alternative candidate</strong><br><small>Road: " + escapeHtml(candidate.road_name || "(unnamed)") + " · " + escapeHtml(candidate.highway || "") + "<br>OSM way " + escapeHtml(candidate.osm_way_id || "") + "<br>Distance: " + candidate.distance_m + " m</small>"));
      }
    });

    if (showSnapPreview.checked) map.addLayer(snapPreviewLayer);
    message.classList.remove("text-danger");
    if (candidates.length) {
      message.textContent = "Snap preview for stop " + original.id + ": " + candidates.length +
        " road candidate(s) · top: " + (candidates[0].road_name || "(unnamed)") +
        " · candidate only, not verified.";
    } else {
      message.textContent = "Snap preview for stop " + original.id + ": " +
        (payload.note ? payload.note.message : "No road candidate within range.");
    }
  }

  async function previewSnap() {
    const raw = snapStopId.value.trim();
    if (!/^\d+$/.test(raw)) {
      message.textContent = "Enter a numeric stop ID to preview a snap.";
      message.classList.add("text-danger");
      return;
    }
    if (snapPreviewInFlight) {
      message.textContent = "A snap preview is already running. Please wait.";
      return;
    }
    snapPreviewInFlight = true;
    message.textContent = "Requesting geometric OSM road snap candidates for stop " + raw + "…";
    message.classList.remove("text-danger");
    try {
      const response = await fetch("/admin/historical-network/snap?stop_id=" + encodeURIComponent(raw), {
        headers: { "Accept": "application/json" },
        credentials: "same-origin"
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok || !payload) {
        message.textContent = payload && payload.error ? payload.error.message : ("Server returned " + response.status);
        message.classList.add("text-danger");
        return;
      }
      renderSnapPreview(payload);
    } catch (error) {
      message.textContent = "Could not preview snap: " + error.message;
      message.classList.add("text-danger");
    } finally {
      snapPreviewInFlight = false;
    }
  }

  if (snapPreviewBtn) snapPreviewBtn.addEventListener("click", previewSnap);
  if (snapStopId) snapStopId.addEventListener("keydown", (event) => {
    if (event.key === "Enter") previewSnap();
  });
  // Refreshing the preview on candidate change re-highlights the selected
  // road geometry without re-fetching from the server.
  if (snapCandidateSelect) snapCandidateSelect.addEventListener("change", () => {
    if (snapOriginal && snapCandidates.length) {
      renderSnapPreview({ success: true, stop: snapOriginal, candidates: snapCandidates });
    }
  });
  if (showSnapPreview) showSnapPreview.addEventListener("change", () => {
    if (showSnapPreview.checked) map.addLayer(snapPreviewLayer);
    else map.removeLayer(snapPreviewLayer);
  });

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
