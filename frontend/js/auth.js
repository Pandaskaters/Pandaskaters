// ── Auth Logic ─────────────────────────────────────────────────

async function handleLogin() {
  const btn = document.getElementById('loginBtn');
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;

  if (!email || !password) {
    showToast('Completa todos los campos', 'warning');
    return;
  }

  setLoading(btn, true);
  try {
    const res = await api.post('/auth/login', { email, password });
    localStorage.setItem('ps_token', res.access_token);
    localStorage.setItem('ps_user',  JSON.stringify(res.user));

    // Load extra driver profile if needed
    if (res.user.role === 'driver') {
      try {
        const driver = await api.get('/drivers/me');
        localStorage.setItem('ps_driver', JSON.stringify(driver));
      } catch(_) {}
    }

    showToast(`¡Bienvenido, ${res.user.name}!`, 'success');
    setTimeout(() => redirectByRole(res.user.role), 800);
  } catch(e) {
    showToast(e.message || 'Credenciales incorrectas', 'error');
    setLoading(btn, false);
  }
}

async function handleRegister(role) {
  const btn = document.getElementById('registerBtn');

  const name     = document.getElementById('regName').value.trim();
  const email    = document.getElementById('regEmail').value.trim();
  const phone    = document.getElementById('regPhone').value.trim();
  const password = document.getElementById('regPassword').value;

  if (!name || !email || !phone || !password) {
    showToast('Completa todos los campos requeridos', 'warning');
    return;
  }
  if (password.length < 6) {
    showToast('La contraseña debe tener al menos 6 caracteres', 'warning');
    return;
  }

  setLoading(btn, true);
  try {
    if (role === 'passenger') {
      await api.post('/auth/register/passenger', { name, email, phone, password, role: 'passenger' });
      showToast('¡Cuenta creada! Iniciando sesión...', 'success');
      await api.post('/auth/login', { email, password }).then(res => {
        localStorage.setItem('ps_token', res.access_token);
        localStorage.setItem('ps_user', JSON.stringify(res.user));
        setTimeout(() => redirectByRole(res.user.role), 800);
      });
    } else {
      // Driver registration
      const cedula  = document.getElementById('regCedula').value.trim();
      const license = document.getElementById('regLicense').value.trim();
      const plate   = document.getElementById('regPlate').value.trim().toUpperCase();
      const brand   = document.getElementById('regBrand').value.trim();
      const model   = document.getElementById('regModel').value.trim();
      const year    = parseInt(document.getElementById('regYear').value);
      const color   = document.getElementById('regColor').value.trim();
      const vtype   = document.getElementById('regVehicleType').value;

      if (!cedula || !license || !plate || !brand || !model || !year || !color) {
        showToast('Completa los datos del conductor y vehículo', 'warning');
        setLoading(btn, false);
        return;
      }

      await api.post('/auth/register/driver', {
        name, email, phone, password,
        cedula, license_number: license,
        vehicle: { plate, brand, model, year, color, vehicle_type: vtype },
      });
      showToast('¡Registro enviado! Esperando aprobación.', 'success');
      await api.post('/auth/login', { email, password }).then(res => {
        localStorage.setItem('ps_token', res.access_token);
        localStorage.setItem('ps_user', JSON.stringify(res.user));
        setTimeout(() => redirectByRole(res.user.role), 800);
      });
    }
  } catch(e) {
    showToast(e.message || 'Error en el registro', 'error');
    setLoading(btn, false);
  }
}
