const ESTADO_PAGO_LABEL = { pendiente: 'Pendiente', completado: 'Completado', cancelado: 'Cancelado' };
const ESTADO_INGRESO_LABEL = { valido: 'Válido', usado: 'Usado', anulado: 'Anulado' };

function formatFechaHora(iso) {
  return new Date(iso).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' });
}

/* ---------------- Tabs ---------------- */
const TABS = ['escritorio', 'pedidos', 'detalles', 'entradas'];
const loaded = {}; 

function showTab(tab) {
  if (!TABS.includes(tab)) tab = 'escritorio';

  TABS.forEach(t => {
    document.getElementById(`panel-${t}`).hidden = (t !== tab);
  });
  document.querySelectorAll('#dashboard-nav a[data-tab]').forEach(a => {
    a.classList.toggle('active', a.dataset.tab === tab);
  });

  if (tab === 'pedidos' && !loaded.pedidos) { loaded.pedidos = true; cargarPedidos(); }
  if (tab === 'entradas' && !loaded.entradas) { loaded.entradas = true; cargarEntradas(); }
  if (tab === 'detalles' && !loaded.detalles) { loaded.detalles = true; cargarPerfilEnForm(); }
}

function wireTabs() {
  document.querySelectorAll('[data-tab]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = el.dataset.tab;
      window.location.hash = tab;
      showTab(tab);
    });
  });
  window.addEventListener('hashchange', () => {
    showTab(window.location.hash.replace('#', ''));
  });
}

/* ---------------- Escritorio ---------------- */
async function cargarEscritorio() {
  try {
    const me = await Api.me();
    document.getElementById('dashboard-welcome').innerHTML =
      `Hola <strong>${me.nombre} ${me.apellido}</strong> ` +
      `(<a href="#" id="welcome-logout">¿no eres tú? Cerrar sesión</a>)`;
    document.getElementById('welcome-logout').addEventListener('click', (e) => {
      e.preventDefault();
      cerrarSesion();
    });
  } catch (err) {
    window.location.href = 'index.html';
  }
}

/* ---------------- Pedidos ---------------- */
async function cargarPedidos() {
  const box = document.getElementById('pedidos-list');
  try {
    const ordenes = await Api.misOrdenes();
    if (!ordenes.length) {
      box.innerHTML = `<p>Todavía no tienes pedidos. <a href="index.html">Ver eventos disponibles</a>.</p>`;
      return;
    }
    box.innerHTML = ordenes.map(o => `
      <article class="order-card">
        <div class="order-card-head">
          <span>Pedido #${o.id_orden}</span>
          <span class="status-badge status-${o.estado_pago}">${ESTADO_PAGO_LABEL[o.estado_pago] || o.estado_pago}</span>
        </div>
        <div class="order-card-body">
          <span>${formatFechaHora(o.fecha_compra)}</span>
          <span class="order-total">S/ ${Number(o.monto_total).toFixed(2)}</span>
        </div>
        <ul class="order-items">
          ${(o.detalles || []).map(d => `<li>${d.cantidad} × Zona #${d.id_zona} — S/ ${Number(d.subtotal).toFixed(2)}</li>`).join('')}
        </ul>
      </article>
    `).join('');
  } catch (err) {
    box.innerHTML = `<p class="error-text">No se pudieron cargar tus pedidos: ${err.message}</p>`;
  }
}

/* ---------------- Entradas ---------------- */
async function cargarEntradas() {
  const box = document.getElementById('entradas-grid');
  try {
    const boletos = await Api.misBoletos();
    if (!boletos.length) {
      box.innerHTML = `<p>Todavía no tienes entradas. <a href="index.html">Ver eventos disponibles</a>.</p>`;
      return;
    }
    box.innerHTML = boletos.map(b => `
      <article class="boleto-card" data-id="${b.id_boleto}">
        <div class="boleto-qr-wrap"><div class="boleto-qr-loading">Cargando QR...</div></div>
        <div class="boleto-info">
          <span class="status-badge status-boleto-${b.estado_ingreso}">${ESTADO_INGRESO_LABEL[b.estado_ingreso] || b.estado_ingreso}</span>
          <span class="boleto-codigo">${b.codigo_qr}</span>
        </div>
      </article>
    `).join('');

    // Carga cada QR como imagen autenticada (blob), en paralelo
    boletos.forEach(async (b) => {
      const card = box.querySelector(`.boleto-card[data-id="${b.id_boleto}"]`);
      const wrap = card.querySelector('.boleto-qr-wrap');
      try {
        const objectUrl = await Api.qrBoletoObjectUrl(b.id_boleto);
        wrap.innerHTML = `<img src="${objectUrl}" alt="Código QR del boleto ${b.id_boleto}">`;
      } catch (err) {
        wrap.innerHTML = `<div class="boleto-qr-loading">No se pudo cargar</div>`;
      }
    });
  } catch (err) {
    box.innerHTML = `<p class="error-text">No se pudieron cargar tus entradas: ${err.message}</p>`;
  }
}

/* ---------------- Detalles de la cuenta ---------------- */
async function cargarPerfilEnForm() {
  try {
    const me = await Api.me();
    document.getElementById('perfil-nombre').value = me.nombre;
    document.getElementById('perfil-apellido').value = me.apellido;
    document.getElementById('perfil-email').value = me.email;
    document.getElementById('perfil-telefono').value = me.telefono || '';
  } catch (err) {
    document.getElementById('perfil-error').textContent = 'No se pudo cargar tu perfil.';
    document.getElementById('perfil-error').classList.add('show');
  }
}

function wirePerfilForm() {
  document.getElementById('perfil-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById('perfil-error');
    const successBox = document.getElementById('perfil-success');
    errorBox.classList.remove('show');
    successBox.classList.remove('show');

    const payload = {
      nombre: document.getElementById('perfil-nombre').value,
      apellido: document.getElementById('perfil-apellido').value,
      email: document.getElementById('perfil-email').value,
      telefono: document.getElementById('perfil-telefono').value || null,
    };
    const nuevaPassword = document.getElementById('perfil-password').value;
    if (nuevaPassword) payload.password = nuevaPassword;

    const btn = document.getElementById('perfil-submit');
    btn.disabled = true;
    try {
      await Api.actualizarPerfil(payload);
      document.getElementById('perfil-password').value = '';
      successBox.classList.add('show');
      await updateAuthUI(); // refresca "Hola, {nombre}" del header si cambió
      await cargarEscritorio();
      showToast('Perfil actualizado');
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.add('show');
    } finally {
      btn.disabled = false;
    }
  });
}

/* ---------------- Cerrar sesión ---------------- */
function cerrarSesion() {
  Api.logout();
  window.location.href = 'index.html';
}

/* ---------------- Init ---------------- */
document.addEventListener('DOMContentLoaded', async () => {
  if (!Api.isAuthenticated()) {
    window.location.href = 'index.html';
    return;
  }
  await initLayout();

  document.getElementById('sidebar-logout').addEventListener('click', (e) => { e.preventDefault(); cerrarSesion(); });
  document.getElementById('quick-link-logout').addEventListener('click', (e) => { e.preventDefault(); cerrarSesion(); });

  wireTabs();
  wirePerfilForm();
  await cargarEscritorio();
  showTab(window.location.hash.replace('#', '') || 'escritorio');
});
