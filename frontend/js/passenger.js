// ── Passenger Logic ────────────────────────────────────────────
const user = JSON.parse(localStorage.getItem('ps_user') || 'null');
if (!user || user.role === 'driver') location.href = user?.role === 'driver' ? '../driver/home.html' : '../index.html';

// Greet
document.getElementById('greetingName').textContent = user?.name?.split(' ')[0] || 'Pasajero';
const hour = new Date().getHours();
const greet = hour < 12 ? '¡Buenos días!' : hour < 18 ? '¡Buenas tardes!' : '¡Buenas noches!';
document.getElementById('greetingText').textContent = greet;

// State
let originCoords  = null;
let destCoords    = null;
let selectedService = 'economy';
let currentRideId   = null;
let pickingMode     = null; // 'origin' | 'destination'
let estimates       = [];
let wsConn          = null;

// Init map
window.addEventListener('DOMContentLoaded', () => {
  initMap();
  setTimeout(() => {
    if (userLat) {
      originCoords = { lat: userLat, lng: userLng, address: 'Mi ubicación actual' };
      simulateNearbyDrivers(userLat, userLng);
      checkActiveRide();
      setupWebSocket();
    }
  }, 1500);
});

// ── WebSocket ─────────────────────────────────────────────────
function setupWebSocket() {
  if (!user?.id) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  wsConn = new WebSocket(`${proto}://${location.host}/ws/${user.id}`);
  wsConn.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'ride_accepted' && msg.ride_id === currentRideId) {
      handleRideAccepted(msg.driver_id);
    }
    if (msg.type === 'ride_status' && msg.ride_id === currentRideId) {
      updateRideStatusUI(msg.status);
    }
    if (msg.type === 'driver_location') {
      addDriverMarker(msg.driver_id, msg.lat, msg.lng);
    }
  };
  wsConn.onclose = () => setTimeout(setupWebSocket, 5000);
}

// ── Location Modal ────────────────────────────────────────────
function openLocationModal(mode) {
  pickingMode = mode;
  document.getElementById('locationModal').classList.add('open');
  document.getElementById('locationSearchInput').value = '';
  document.getElementById('locationItems').innerHTML = '';
  document.getElementById('locationSearchInput').focus();
}
function closeLocationModal() {
  document.getElementById('locationModal').classList.remove('open');
}

async function searchLocations(query) {
  if (query.length < 3) { document.getElementById('locationItems').innerHTML = ''; return; }
  const items = document.getElementById('locationItems');
  items.innerHTML = '<div style="text-align:center;padding:1rem"><div class="spinner" style="margin:0 auto"></div></div>';
  try {
    const results = await geocode(query);
    if (!results.length) {
      items.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:1rem">Sin resultados</p>';
      return;
    }
    items.innerHTML = results.map((r, i) => `
      <div class="location-item" onclick="selectLocation(${r.lat},${r.lon},'${r.display_name.replace(/'/g, '')}')">
        <div class="location-item-icon"><i class="fa fa-location-dot"></i></div>
        <div class="location-item-text">
          <div class="location-item-name">${r.display_name.split(',')[0]}</div>
          <div class="location-item-addr">${r.display_name.substring(0, 60)}...</div>
        </div>
      </div>`).join('');
  } catch(e) {
    items.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:1rem">Error buscando ubicación</p>';
  }
}

function selectLocation(lat, lng, address) {
  const shortAddr = address.split(',').slice(0, 2).join(',');
  if (pickingMode === 'origin') {
    originCoords = { lat: parseFloat(lat), lng: parseFloat(lng), address: shortAddr };
    document.getElementById('originLabel').textContent = shortAddr;
    document.getElementById('originLabel').style.color = 'var(--text-primary)';
  } else {
    destCoords = { lat: parseFloat(lat), lng: parseFloat(lng), address: shortAddr };
    document.getElementById('destLabel').textContent = shortAddr;
    document.getElementById('destLabel').style.color = 'var(--text-primary)';
  }
  closeLocationModal();
  checkBothSelected();
}

function useMapSelection() {
  closeLocationModal();
  showToast(`Toca en el mapa para seleccionar ${pickingMode === 'origin' ? 'origen' : 'destino'}`, 'info');
  map.once('click', async (e) => {
    const { lat, lng } = e.latlng;
    const addr = await reverseGeocode(lat, lng).catch(() => `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    selectLocation(lat, lng, addr);
  });
}

function checkBothSelected() {
  const btn = document.getElementById('requestBtn');
  if (originCoords && destCoords) {
    btn.disabled = false;
    loadFareEstimates();
  }
}

// ── Fare Estimates ────────────────────────────────────────────
async function loadFareEstimates() {
  if (!originCoords || !destCoords) return;
  try {
    estimates = await api.get(
      `/rides/estimate?origin_lat=${originCoords.lat}&origin_lng=${originCoords.lng}&dest_lat=${destCoords.lat}&dest_lng=${destCoords.lng}`
    );
    estimates.forEach(e => {
      const type = e.service_type;
      const fareEl = document.getElementById(`fare_${type}`);
      const etaEl  = document.getElementById(`eta_${type}`);
      if (fareEl) fareEl.textContent = `$${e.fare.toFixed(2)}`;
      if (etaEl)  etaEl.textContent  = `~${Math.ceil(e.duration_min)} min`;
    });
    const selected = estimates.find(e => e.service_type === selectedService);
    if (selected) {
      document.getElementById('routeDist').textContent = `${selected.distance_km.toFixed(1)} km`;
      document.getElementById('routeTime').textContent = `~${Math.ceil(selected.duration_min)} min`;
      document.getElementById('routeFare').textContent = `$${selected.fare.toFixed(2)}`;
    }
  } catch(e) {}
}

// ── Ride Sheet ────────────────────────────────────────────────
function showRideSheet() {
  if (!originCoords || !destCoords) {
    showToast('Selecciona origen y destino primero', 'warning');
    return;
  }
  drawRoute(originCoords.lat, originCoords.lng, destCoords.lat, destCoords.lng);
  openSheet('rideSheet');
}

function openSheet(id) {
  document.getElementById(id).classList.add('open');
}
function closeSheet(id) {
  document.getElementById(id).classList.remove('open');
}

function selectService(el, type) {
  document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  selectedService = type;
  const est = estimates.find(e => e.service_type === type);
  if (est) {
    document.getElementById('routeDist').textContent = `${est.distance_km.toFixed(1)} km`;
    document.getElementById('routeTime').textContent = `~${Math.ceil(est.duration_min)} min`;
    document.getElementById('routeFare').textContent = `$${est.fare.toFixed(2)}`;
  }
}

// ── Confirm Ride ──────────────────────────────────────────────
async function confirmRide() {
  const btn = document.getElementById('confirmBtn');
  if (!originCoords || !destCoords) return;

  setLoading(btn, true);
  try {
    const ride = await api.post('/rides/request', {
      origin_address:     originCoords.address,
      origin_lat:         originCoords.lat,
      origin_lng:         originCoords.lng,
      destination_address: destCoords.address,
      destination_lat:    destCoords.lat,
      destination_lng:    destCoords.lng,
      service_type:       selectedService,
    });
    currentRideId = ride.id;
    closeSheet('rideSheet');
    openSheet('activeRideSheet');
    document.getElementById('searchingState').style.display = 'block';
    document.getElementById('driverAssigned').style.display = 'none';
    updateStepUI('searching');
    playNotificationSound();
    showToast('Buscando conductor...', 'info');
    pollRideStatus();
  } catch(e) {
    showToast(e.message || 'Error al solicitar viaje', 'error');
    setLoading(btn, false);
  }
}

// ── Poll ride status (fallback when no WS) ────────────────────
let pollInterval;
function pollRideStatus() {
  clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    if (!currentRideId) return;
    try {
      const ride = await api.get(`/rides/${currentRideId}`);
      updateRideStatusUI(ride.status);
      if (ride.status === 'assigned' || ride.status === 'driver_arriving') {
        handleRideAccepted(ride.driver_id);
      }
      if (['completed', 'cancelled'].includes(ride.status)) {
        clearInterval(pollInterval);
      }
    } catch(_) {}
  }, 5000);
}

function handleRideAccepted(driverId) {
  document.getElementById('searchingState').style.display = 'none';
  document.getElementById('driverAssigned').style.display = 'block';
  document.getElementById('activeDriverName').textContent = 'Conductor Asignado';
  document.getElementById('activeDriverVehicle').textContent = 'Vehículo en camino';
  updateStepUI('assigned');
  showToast('¡Conductor asignado!', 'success');
  playNotificationSound();
}

function updateRideStatusUI(status) {
  const stepMap = {
    searching: 'searching',
    assigned: 'assigned',
    driver_arriving: 'arriving',
    in_progress: 'progress',
    completed: 'done',
  };
  const step = stepMap[status];
  if (step) updateStepUI(step);

  if (status === 'completed') {
    showToast('¡Viaje completado! Gracias por usar PandaSkaters 🎉', 'success');
    clearInterval(pollInterval);
    setTimeout(() => {
      closeSheet('activeRideSheet');
      clearRoute();
      currentRideId = null;
    }, 2000);
  }
  if (status === 'cancelled') {
    showToast('Viaje cancelado', 'error');
    clearInterval(pollInterval);
    closeSheet('activeRideSheet');
    clearRoute();
    currentRideId = null;
  }
}

function updateStepUI(active) {
  const steps = ['searching', 'assigned', 'arriving', 'progress', 'done'];
  const idx = steps.indexOf(active);
  steps.forEach((s, i) => {
    const el = document.getElementById('step_' + s);
    if (!el) return;
    el.classList.remove('done', 'active');
    if (i < idx) el.classList.add('done');
    else if (i === idx) el.classList.add('active');
  });
}

async function cancelRide() {
  if (!currentRideId || !confirm('¿Cancelar el viaje?')) return;
  try {
    await api.patch(`/rides/${currentRideId}/status`, { status: 'cancelled', cancellation_reason: 'Cancelado por usuario' });
    showToast('Viaje cancelado', 'info');
    closeSheet('activeRideSheet');
    clearRoute();
    currentRideId = null;
    clearInterval(pollInterval);
  } catch(e) {
    showToast('Error al cancelar', 'error');
  }
}

async function checkActiveRide() {
  try {
    const rides = await api.get('/rides/active');
    if (rides.length) {
      currentRideId = rides[0].id;
      openSheet('activeRideSheet');
      updateRideStatusUI(rides[0].status);
      pollRideStatus();
    }
  } catch(_) {}
}

function callDriver() { showToast('Función disponible en la app nativa', 'info'); }
function openChat()   { showToast('Chat próximamente disponible', 'info'); }

function playNotificationSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [523, 659, 784].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      osc.type = 'sine';
      gain.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.2);
      osc.start(ctx.currentTime + i * 0.12);
      osc.stop(ctx.currentTime + i * 0.12 + 0.3);
    });
  } catch(_) {}
}
