(() => {
  "use strict";

  if (!window.L) return;

  function initializePicker(element) {
    if (element.dataset.mapInitialized === "true") return;
    const form = element.closest("form");
    if (!form) return;

    const latInput = form.querySelector('input[name="latitude"]');
    const lngInput = form.querySelector('input[name="longitude"]');
    if (!latInput || !lngInput) return;

    const readCoordinate = (value, fallback) => {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : fallback;
    };

    const defaultLat = readCoordinate(element.dataset.defaultLat, 24.8607);
    const defaultLng = readCoordinate(element.dataset.defaultLng, 67.0011);
    const initialLat = readCoordinate(latInput.value, defaultLat);
    const initialLng = readCoordinate(lngInput.value, defaultLng);
    const initialZoom = Number(element.dataset.defaultZoom || 11);

    const map = L.map(element, { scrollWheelZoom: true }).setView(
      [initialLat, initialLng],
      initialZoom
    );

    const tileUrl = element.dataset.tileUrl
      || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    const tileAttribution = element.dataset.tileAttribution
      || '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>';

    L.tileLayer(tileUrl, {
      maxZoom: Number(element.dataset.tileMaxZoom || 19),
      attribution: tileAttribution
    }).addTo(map);

    let marker = L.marker([initialLat, initialLng], {
      draggable: true,
      autoPan: true
    }).addTo(map);

    function setPoint(lat, lng, updateInputs = true) {
      const point = L.latLng(lat, lng);
      marker.setLatLng(point);
      if (updateInputs) {
        latInput.value = point.lat.toFixed(7);
        lngInput.value = point.lng.toFixed(7);
        latInput.dispatchEvent(new Event("input", { bubbles: true }));
        lngInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }

    map.on("click", (event) => setPoint(event.latlng.lat, event.latlng.lng));
    marker.on("dragend", () => {
      const point = marker.getLatLng();
      setPoint(point.lat, point.lng);
    });

    function syncFromInputs() {
      if (!latInput.value || !lngInput.value) return;
      const lat = Number(latInput.value);
      const lng = Number(lngInput.value);
      if (
        Number.isFinite(lat) && Number.isFinite(lng)
        && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180
      ) {
        marker.setLatLng([lat, lng]);
        map.panTo([lat, lng]);
      }
    }

    latInput.addEventListener("change", syncFromInputs);
    lngInput.addEventListener("change", syncFromInputs);
    element.dataset.mapInitialized = "true";
    element._stopPickerMap = map;
    element._stopPickerResize = () => map.invalidateSize();
  }

  function initializeVisiblePickers(root = document) {
    root.querySelectorAll("[data-stop-map]").forEach((element) => {
      if (element.closest("details") && !element.closest("details").open) return;
      initializePicker(element);
      if (element._stopPickerResize) {
        window.requestAnimationFrame(element._stopPickerResize);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initializeVisiblePickers();

    document.querySelectorAll("details.stop-edit-details").forEach((details) => {
      details.addEventListener("toggle", () => {
        if (details.open) {
          initializeVisiblePickers(details);
        }
      });
    });
  });
})();