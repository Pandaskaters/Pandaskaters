// ── API Client ─────────────────────────────────────────────────
const BASE_URL = window.location.origin + '/api';

const api = {
  _token() { return localStorage.getItem('ps_token'); },

  async _request(method, path, body, isForm = false) {
    const headers = {};
    const token = this._token();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!isForm && body) headers['Content-Type'] = 'application/json';

    const res = await fetch(BASE_URL + path, {
      method,
      headers,
      body: isForm ? body : (body ? JSON.stringify(body) : undefined),
    });

    if (res.status === 401) {
      localStorage.clear();
      location.href = '/';
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error del servidor' }));
      throw new Error(err.detail || 'Error desconocido');
    }
    if (res.status === 204) return null;
    return res.json();
  },

  get(path)           { return this._request('GET', path); },
  post(path, body)    { return this._request('POST', path, body); },
  patch(path, body)   { return this._request('PATCH', path, body); },
  put(path, body)     { return this._request('PUT', path, body); },
  delete(path)        { return this._request('DELETE', path); },
};

// ── Toast helper ───────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || '💬'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── Role redirect ──────────────────────────────────────────────
function redirectByRole(role) {
  const routes = {
    passenger: '/passenger/home.html',
    driver:    '/driver/home.html',
    admin:     '/admin/dashboard.html',
  };
  location.href = routes[role] || '/';
}

// ── Loading button helper ──────────────────────────────────────
function setLoading(btn, loading, text = '') {
  if (!btn) return;
  if (loading) {
    btn._orig = btn.innerHTML;
    btn.innerHTML = `<span class="spinner" style="width:18px;height:18px;border-width:2px"></span>`;
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._orig || text;
    btn.disabled = false;
  }
}
