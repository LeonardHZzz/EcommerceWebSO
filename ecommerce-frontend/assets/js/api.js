const API_BASE = '/api/v1';
const TOKEN_KEY = 'yumeevent_token';

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }

async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  let data = null;
  const text = await resp.text();
  if (text) { try { data = JSON.parse(text); } catch (_) { data = text; } }

  if (!resp.ok) {
    const detail = data && data.detail ? data.detail : `Error ${resp.status}`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

const Api = {
  // --- Usuarios ---
  registrar(payload) {
    return apiFetch('/usuarios/registro', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async login(email, password) {
    const form = new URLSearchParams();
    form.set('username', email);
    form.set('password', password);
    const resp = await fetch(`${API_BASE}/usuarios/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || 'No se pudo iniciar sesión');
    setToken(data.access_token);
    return data;
  },

  me() { return apiFetch('/usuarios/me'); },

  actualizarPerfil(payload) {
    return apiFetch('/usuarios/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  logout() { clearToken(); },

  isAuthenticated() { return !!getToken(); },

  // --- Catálogo ---
  eventos() { return apiFetch('/eventos'); },
  evento(id) { return apiFetch(`/eventos/${id}`); },
  zona(id) { return apiFetch(`/zonas/${id}`); },

  // --- Carrito ---
  carrito() { return apiFetch('/carrito'); },
  agregarAlCarrito(id_zona, cantidad = 1) {
    return apiFetch('/carrito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_zona, cantidad }),
    });
  },
  actualizarCantidadCarrito(id_carrito, cantidad) {
    return apiFetch(`/carrito/${id_carrito}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cantidad }),
    });
  },
  quitarDelCarrito(id_carrito) {
    return apiFetch(`/carrito/${id_carrito}`, { method: 'DELETE' });
  },

  // --- Cupones ---
  validarCupon(codigo) {
    return apiFetch('/cupones/validar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codigo }),
    });
  },

  // --- Checkout / Pedidos ---
  checkout(metodo_pago, codigo_cupon = null) {
    return apiFetch('/ordenes/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metodo_pago, codigo_cupon }),
    });
  },
  misOrdenes() { return apiFetch('/ordenes'); },

  simularPago(id_orden) {
    return apiFetch(`/ordenes/${id_orden}/simular-pago`, { method: 'POST' });
  },

  // --- Boletos ---
  misBoletos() { return apiFetch('/boletos/mis-boletos'); },
  async qrBoletoObjectUrl(id_boleto) {
    const headers = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const resp = await fetch(`${API_BASE}/boletos/${id_boleto}/qr.png`, { headers });
    if (!resp.ok) throw new Error(`No se pudo cargar el QR (${resp.status})`);
    const blob = await resp.blob();
    return URL.createObjectURL(blob);
  },
};
