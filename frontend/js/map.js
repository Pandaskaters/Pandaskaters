// ── Map Module (Leaflet + OpenStreetMap) ────────────────────────
let map, userMarker, routeLayer, driverMarkers = {};
let userLat = null, userLng = null;

function initMap(options = {}) {
  const defaultLat = options.lat || 4.711;
  const defaultLng = options.lng || -74.072;
  const zoom = options.zoom || 15;

  map = L.map('map', {
    zoomControl: false,
    attributionControl: false,
  }).setView([defaultLat, defaultLng], zoom);

  // Dark tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
  }).addTo(map);

  getUserLocation();
  return map;
}

function getUserLocation() {
  if (!navigator.geolocation) return;
  navigator.geolocation.watchPosition(
    pos => {
      userLat = pos.coords.latitude;
      userLng = pos.coords.longitude;
      updateUserMarker(userLat, userLng);
    },
    () => {},
    { enableHighAccuracy: true, maximumAge: 5000 }
  );
}

function updateUserMarker(lat, lng) {
  if (!map) return;
  const el = document.createElement('div');
  el.style.cssText = `
    width:20px;height:20px;
    border-radius:50%;
    background:var(--accent);
    border:3px solid white;
    box-shadow:0 0 0 4px rgba(198,241,53,.3);
  `;
  const icon = L.divIcon({ html: el, className: '', iconSize: [20, 20] });

  if (!userMarker) {
    userMarker = L.marker([lat, lng], { icon, zIndexOffset: 1000 }).addTo(map);
  } else {
    userMarker.setLatLng([lat, lng]);
  }
}

function centerMap() {
  if (map && userLat) map.setView([userLat, userLng], 15, { animate: true });
}

function drawRoute(lat1, lng1, lat2, lng2) {
  if (!map) return;
  clearRoute();
  const latlngs = [[lat1, lng1], [lat2, lng2]];
  routeLayer = L.polyline(latlngs, {
    color: '#c6f135',
    weight: 4,
    opacity: .85,
    dashArray: null,
    lineJoin: 'round',
  }).addTo(map);

  // Add origin and destination markers
  addPin([lat1, lng1], '#c6f135', '📍');
  addPin([lat2, lng2], '#ef4444', '🏁');
  map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
}

function addPin(latlng, color, emoji) {
  const el = document.createElement('div');
  el.style.cssText = `
    font-size:1.4rem;
    filter:drop-shadow(0 2px 4px rgba(0,0,0,.5));
    cursor:default;
  `;
  el.textContent = emoji;
  const icon = L.divIcon({ html: el, className: '', iconSize: [28, 28], iconAnchor: [14, 28] });
  return L.marker(latlng, { icon }).addTo(map);
}

function clearRoute() {
  if (routeLayer) { routeLayer.remove(); routeLayer = null; }
}

function addDriverMarker(driverId, lat, lng, type = 'economy') {
  const icons = { economy: '🚗', premium: '🚙', moto: '🏍️' };
  const el = document.createElement('div');
  el.className = 'driver-marker';
  el.textContent = icons[type] || '🚗';

  const icon = L.divIcon({ html: el, className: '', iconSize: [36, 36] });

  if (driverMarkers[driverId]) {
    driverMarkers[driverId].setLatLng([lat, lng]);
  } else {
    driverMarkers[driverId] = L.marker([lat, lng], { icon }).addTo(map);
  }
}

function removeDriverMarker(driverId) {
  if (driverMarkers[driverId]) {
    driverMarkers[driverId].remove();
    delete driverMarkers[driverId];
  }
}

// Simulate a few nearby driver markers
function simulateNearbyDrivers(centerLat, centerLng, count = 4) {
  const types = ['economy', 'premium', 'moto', 'economy'];
  for (let i = 0; i < count; i++) {
    const lat = centerLat + (Math.random() - .5) * 0.02;
    const lng = centerLng + (Math.random() - .5) * 0.02;
    addDriverMarker('sim_' + i, lat, lng, types[i % types.length]);
  }
}

// Animate a marker along a path (for active ride)
function animateMarker(marker, fromLat, fromLng, toLat, toLng, steps = 60) {
  const dlat = (toLat - fromLat) / steps;
  const dlng = (toLng - fromLng) / steps;
  let step = 0;
  const interval = setInterval(() => {
    step++;
    marker.setLatLng([fromLat + dlat * step, fromLng + dlng * step]);
    if (step >= steps) clearInterval(interval);
  }, 100);
  return interval;
}

// Nominatim geocoding (OpenStreetMap)
async function geocode(query) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'es' } });
  return res.json();
}

async function reverseGeocode(lat, lng) {
  const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'es' } });
  const data = await res.json();
  return data.display_name || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
}
