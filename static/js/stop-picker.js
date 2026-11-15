(() => {
  "use strict";
  const element = document.getElementById("stop-picker");
  if (!element || !window.L) return;
  const latInput = document.querySelector('input[name="latitude"]');
  const lngInput = document.querySelector('input[name="longitude"]');
  const map = L.map(element).setView([24.8607, 67.0011], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);
  let marker;
  function setPoint(lat, lng) {
    latInput.value = lat.toFixed(7);
    lngInput.value = lng.toFixed(7);
    if (marker) marker.setLatLng([lat, lng]);
    else marker = L.marker([lat, lng]).addTo(map);
  }
  map.on("click", (event) => setPoint(event.latlng.lat, event.latlng.lng));
  function syncFromInputs() {
    const lat = Number(latInput.value), lng = Number(lngInput.value);
    if (latInput.value && lngInput.value && Number.isFinite(lat) && Number.isFinite(lng)) {
      setPoint(lat, lng);
    }
  }
  latInput.addEventListener("change", syncFromInputs);
  lngInput.addEventListener("change", syncFromInputs);
})();
