// ── Driver Logic ───────────────────────────────────────────────
const user = JSON.parse(localStorage.getItem('ps_user') || 'null');
if (!user || user.role !== 'driver') location.href = '../index.html';

let isOnline = false;
let wsConn   = null;
let currentRide = null;
let driverProfile = null;
let locationInterval = null;
let todayEarnings = 0;
let todayTrips = 0;
let pendingRide = null;
let acceptTimer = null;

window.addEventListener('DOMContentLoaded', async () => {
  initMap();
  await loadDriverProfile();
  setupWebSocket();
  setTimeout(() => {
    if (userLat) simulateNearbyDrivers(userLat, userLng, 2);
  }, 1500);
});

async function loadDriverProfile() {
  try {
    driverProfile = await api.get('/drivers/me');
    localStorage.setItem('ps_driver', JSON.stringify(driverProfile));
    document.getElementById('driverRating').textContent = `${driverProfile.rating.toFixed(1)} ⭐`;
    document.getElementById('todayTrips').textContent = driverProfile.total_rides;
    document.getElementById('todayEarnings').textContent = `$${(driverProfile.total_earnings || 0).toFixed(2)}`;
    isOnline = driverProfile.is_online;
    document.getElementById('onlineToggle').checked = isOnline;
    updateStatusUI(isOnline);
  } catch(e) {}
}

function setupWebSocket() {
  if (!user?.id) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  wsConn = new WebSocket(`${proto}://${location.host}/ws/${user.id}`);
  wsConn.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'new_ride' && isOnline) {
      fetchAndShowRideRequest(msg.ride_id);
    }
  };
  wsConn.onclose = () => setTimeout(setupWebSocket, 5000);
}

async function fetchAndShowRideRequest(rideId) {
  try {
    const ride = await api.get(`/rides/${rideId}`);
    if (ride.status !== 'searching') return;
    showRideRequestPopup(ride);
    playNotificationSound();
  } catch(_) {}
}

function showRideRequestPopup(ride) {
  pendingRide = ride;
  document.getElementById('popupOrigin').textContent = ride.origin_address;
  document.getElementById('popupDest').textContent   = ride.destination_address;
  document.getElementById('popupFare').textContent   = `$${(ride.estimated_fare || 0).toFixed(2)}`;
  document.getElementById('popupDist').textContent   = `${(ride.estimated_distance_km || 0).toFixed(1)} km`;

  // Reset timer animation
  const bar = document.getElementById('timerBar');
  bar.style.animation = 'none';
  bar.offsetHeight; // reflow
  bar.style.animation = 'timerDown 25s linear forwards';

  document.getElementById('rideRequestPopup').classList.add('visible');

  // Auto-decline after 25s
  clearTimeout(acceptTimer);
  acceptTimer = setTimeout(() => declineRide(), 25000);
}

async function acceptRide() {
  if (!pendingRide) return;
  clearTimeout(acceptTimer);
  document.getElementById('rideRequestPopup').classList.remove('visible');
  try {
    const ride = await api.post(`/rides/driver/accept/${pendingRide.id}`);
    currentRide = ride;
    showActiveRideBar(ride);
    drawRoute(ride.origin_lat, ride.origin_lng, ride.destination_lat, ride.destination_lng);
    showToast('Viaje aceptado. Dirígete al pasajero', 'success');
    playNotificationSound();
    todayTrips++;
    document.getElementById('todayTrips').textContent = todayTrips;
  } catch(e) {
    showToast(e.message || 'No se pudo aceptar el viaje', 'error');
  }
  pendingRide = null;
}

function declineRide() {
  clearTimeout(acceptTimer);
  document.getElementById('rideRequestPopup').classList.remove('visible');
  pendingRide = null;
}

function showActiveRideBar(ride) {
  const bar = document.getElementById('activeRideBar');
  bar.style.display = 'block';
  document.getElementById('passengerName').textContent = `Pasajero #${ride.passenger_id}`;
  document.getElementById('rideStatusLabel').textContent = 'Dirígete al pasajero';
  document.getElementById('nextStepBtn').innerHTML = '<i class="fa fa-play"></i> Iniciar Viaje';
  document.getElementById('rideStatusBadge').textContent = 'Asignado';
}

let rideStep = 'assigned';
async function nextRideStep() {
  if (!currentRide) return;
  const btn = document.getElementById('nextStepBtn');
  setLoading(btn, true);
  try {
    if (rideStep === 'assigned') {
      await api.patch(`/rides/${currentRide.id}/status`, { status: 'in_progress' });
      rideStep = 'in_progress';
      document.getElementById('rideStatusLabel').textContent = 'Viaje en curso';
      document.getElementById('rideStatusBadge').textContent = 'En curso';
      btn.innerHTML = '<i class="fa fa-flag-checkered"></i> Finalizar Viaje';
    } else if (rideStep === 'in_progress') {
      await api.patch(`/rides/${currentRide.id}/status`, { status: 'completed' });
      rideStep = 'assigned';
      const fare = currentRide.estimated_fare || 0;
      todayEarnings += fare;
      document.getElementById('todayEarnings').textContent = `$${todayEarnings.toFixed(2)}`;
      document.getElementById('activeRideBar').style.display = 'none';
      clearRoute();
      currentRide = null;
      showToast(`¡Viaje completado! +$${fare.toFixed(2)}`, 'success');
      playNotificationSound();
    }
  } catch(e) {
    showToast('Error actualizando estado', 'error');
  }
  setLoading(btn, false, btn.innerHTML);
}

async function toggleOnlineStatus(checked) {
  isOnline = checked;
  updateStatusUI(checked);
  try {
    await api.patch('/drivers/me/status', { is_online: checked });
    showToast(checked ? '¡Estás conectado! Recibirás solicitudes.' : 'Desconectado. No recibirás solicitudes.', checked ? 'success' : 'info');
    if (checked) startLocationTracking();
    else stopLocationTracking();
  } catch(e) {
    showToast('Error actualizando estado', 'error');
  }
}

function updateStatusUI(online) {
  const statusText = document.getElementById('statusText');
  const statusSub  = document.getElementById('statusSub');
  statusText.textContent = online ? 'En línea' : 'Desconectado';
  statusText.style.color = online ? 'var(--success)' : 'var(--text-primary)';
  statusSub.textContent  = online ? 'Recibiendo solicitudes de viaje' : 'Activa para recibir viajes';
}

function startLocationTracking() {
  if (locationInterval) return;
  locationInterval = setInterval(async () => {
    if (!userLat || !isOnline) return;
    try {
      await api.patch('/drivers/me/location', { lat: userLat, lng: userLng });
      if (wsConn?.readyState === WebSocket.OPEN) {
        wsConn.send(JSON.stringify({ type: 'location_update', lat: userLat, lng: userLng }));
      }
    } catch(_) {}
  }, 10000);
}

function stopLocationTracking() {
  clearInterval(locationInterval);
  locationInterval = null;
}

function callPassenger() { showToast('Función disponible en la app nativa', 'info'); }

function playNotificationSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [880, 1100, 880, 1100].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      osc.type = 'square';
      gain.gain.setValueAtTime(0.15, ctx.currentTime + i * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.15 + 0.12);
      osc.start(ctx.currentTime + i * 0.15);
      osc.stop(ctx.currentTime + i * 0.15 + 0.15);
    });
  } catch(_) {}
}

// Demo: simulate incoming ride request after 8s if online
setTimeout(() => {
  if (isOnline) return;
  document.getElementById('onlineToggle').addEventListener('change', function() {
    if (this.checked) {
      setTimeout(() => {
        showRideRequestPopup({
          id: 999,
          origin_address: 'Av. Principal 123, Ciudad',
          destination_address: 'Centro Comercial Mall, Ciudad',
          estimated_fare: 8.50,
          estimated_distance_km: 6.2,
          passenger_id: 1,
          service_type: 'economy',
          status: 'searching',
        });
      }, 6000);
    }
  }, { once: true });
}, 1000);
