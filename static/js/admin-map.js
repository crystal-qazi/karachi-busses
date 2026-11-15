(() => {
  "use strict";
  const el = document.getElementById("route-map");
  if (!el || !window.L || !L.Control.Draw) return;
  const map = L.map(el).setView([24.8607, 67.0011], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);

  const drawn = new L.FeatureGroup().addTo(map);
  const existing = JSON.parse(el.dataset.shape || "null");
  if (existing) {
    const layer = L.geoJSON(existing);
    layer.eachLayer((child) => drawn.addLayer(child));
    if (layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), {padding:[20,20]});
  }

  const drawControl = new L.Control.Draw({
    draw: {polyline:{shapeOptions:{color:"#126b50",weight:5}}, polygon:false, rectangle:false, circle:false, circlemarker:false, marker:false},
    edit: {featureGroup:drawn, remove:true}
  });
  map.addControl(drawControl);
  map.on(L.Draw.Event.CREATED, (event) => {
    drawn.clearLayers();
    drawn.addLayer(event.layer);
  });

  document.getElementById("clear-shape")?.addEventListener("click", () => drawn.clearLayers());
  document.getElementById("shape-form")?.addEventListener("submit", (event) => {
    const layers = drawn.getLayers();
    if (!layers.length) {
      event.preventDefault();
      alert("Draw a route line before saving.");
      return;
    }
    const feature = layers[0].toGeoJSON();
    if (feature.geometry.type !== "LineString" || feature.geometry.coordinates.length < 2) {
      event.preventDefault();
      alert("Route geometry must be a line with at least two points.");
      return;
    }
    document.getElementById("shape-json").value = JSON.stringify(feature.geometry);
  });
})();
