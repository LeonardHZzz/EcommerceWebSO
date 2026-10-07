function renderHeader() {
  const el = document.getElementById('site-header');
  if (!el) return;
  el.innerHTML = `
    <header class="site-header">
      <div class="header-inner">
        <a href="index.html" class="brand">
          <span class="brand-mark">夢</span>
          <span class="brand-name">Yume<span>Event</span></span>
        </a>
        <nav class="main-nav">
          <a href="faq.html">Preguntas Frecuentes</a>
          <a href="condiciones.html">Condiciones de Compra</a>
          <a href="contacto.html">Contacto</a>
        </nav>
        <div class="header-actions">
          <button class="account-btn" id="account-btn">Mi Cuenta</button>
          <div class="account-menu" id="account-menu">
            <a href="dashboard.html">Dashboard</a>
            <button id="menu-logout">Cerrar sesión</button>
          </div>
          <button class="cart-btn" id="cart-btn">
            <span class="cart-icon">🎟</span>
            <span id="cart-count">0</span> / <span id="cart-total">S/ 0.00</span>
          </button>
        </div>
      </div>
    </header>

    <div class="drawer-overlay" id="drawer-overlay"></div>
    <aside class="drawer" id="login-drawer" aria-hidden="true">
      <div class="drawer-head">
        <h3>Ingresar</h3>
        <button class="drawer-close" id="drawer-close">✕ Cerrar</button>
      </div>

      <div class="form-error" id="login-error"></div>

      <form id="login-form">
        <div class="field">
          <label for="login-email">Nombre de usuario o correo electrónico</label>
          <input type="email" id="login-email" required autocomplete="username">
        </div>
        <div class="field">
          <label for="login-password">Contraseña</label>
          <input type="password" id="login-password" required autocomplete="current-password">
        </div>
        <button type="submit" class="btn btn-primary btn-block">Ingresar</button>
      </form>

      <p class="drawer-switch">
        ¿No estás registrado? <a href="register.html">Crear Cuenta</a>
      </p>
    </aside>
  `;
}

function renderFooter() {
  const el = document.getElementById('site-footer');
  if (!el) return;
  el.innerHTML = `
    <footer class="site-footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="brand" style="margin-bottom:12px;">
              <span class="brand-mark">夢</span>
              <span class="brand-name">Yume<span>Event</span></span>
            </div>
            <p>Tu entrada a los eventos recreativos y convenciones geek más esperados.</p>
          </div>
          <div class="footer-col">
            <h4>Atención General</h4>
            <a href="faq.html">Preguntas Frecuentes</a>
            <a href="condiciones.html">Condiciones de Compra</a>
            <a href="contacto.html">Contacto</a>
          </div>
          <div class="footer-col">
            <h4>Acerca de Nosotros</h4>
            <a href="#">Quiénes Somos</a>
            <a href="#">Galería de Eventos</a>
            <a href="contacto.html">Contacto</a>
          </div>
          <div class="footer-col">
            <h4>Transparencia</h4>
            <a href="#">Términos y Condiciones</a>
            <a href="#">Políticas de Privacidad</a>
            <a href="register.html">Mi Cuenta</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© ${new Date().getFullYear()} YumeEvent. Todos los derechos reservados.</span>
          <div class="social-links">
            <a href="#" aria-label="Instagram">IG</a>
            <a href="#" aria-label="Facebook">FB</a>
            <a href="#" aria-label="Twitter">X</a>
          </div>
        </div>
      </div>
    </footer>
  `;
}

/* ---------------- Drawer de login ---------------- */
function openLoginDrawer() {
  document.getElementById('login-drawer').classList.add('open');
  document.getElementById('drawer-overlay').classList.add('open');
}
function closeLoginDrawer() {
  document.getElementById('login-drawer').classList.remove('open');
  document.getElementById('drawer-overlay').classList.remove('open');
  document.getElementById('login-error').classList.remove('show');
}

function wireDrawerEvents() {
  document.getElementById('drawer-overlay').addEventListener('click', closeLoginDrawer);
  document.getElementById('drawer-close').addEventListener('click', closeLoginDrawer);

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById('login-error');
    errorBox.classList.remove('show');
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
      await Api.login(email, password);
      closeLoginDrawer();
      await updateAuthUI();
      await updateCartBadge();
      showToast('Sesión iniciada correctamente');
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.add('show');
    }
  });
}

/* ---------------- Cuenta / sesión ---------------- */
async function updateAuthUI() {
  const btn = document.getElementById('account-btn');
  const menu = document.getElementById('account-menu');
  if (!btn) return;

  if (!Api.isAuthenticated()) {
    btn.textContent = 'Mi Cuenta';
    btn.onclick = () => openLoginDrawer();
    menu.classList.remove('open');
    return;
  }

  try {
    const me = await Api.me();
    btn.textContent = `Hola, ${me.nombre}`;
    btn.onclick = (e) => { e.stopPropagation(); menu.classList.toggle('open'); };
  } catch (_) {
    // token vencido o inválido
    Api.logout();
    btn.textContent = 'Mi Cuenta';
    btn.onclick = () => openLoginDrawer();
  }
}

function wireAccountMenu() {
  document.addEventListener('click', (e) => {
    const menu = document.getElementById('account-menu');
    const btn = document.getElementById('account-btn');
    if (menu && menu.classList.contains('open') && !menu.contains(e.target) && e.target !== btn) {
      menu.classList.remove('open');
    }
  });
  document.getElementById('menu-logout').addEventListener('click', async () => {
    Api.logout();
    await updateAuthUI();
    await updateCartBadge();
    document.getElementById('account-menu').classList.remove('open');
    showToast('Sesión cerrada');
  });
}

/* ---------------- Carrito ---------------- */
async function updateCartBadge() {
  const countEl = document.getElementById('cart-count');
  const totalEl = document.getElementById('cart-total');
  if (!countEl) return;

  if (!Api.isAuthenticated()) {
    countEl.textContent = '0';
    totalEl.textContent = 'S/ 0.00';
    return;
  }

  try {
    const items = await Api.carrito();
    let count = 0, total = 0;
    for (const item of items) {
      count += item.cantidad;
      try {
        const zona = await Api.zona(item.id_zona);
        total += Number(zona.precio) * item.cantidad;
      } catch (_) { /* zona pudo haberse borrado; se ignora en el total */ }
    }
    countEl.textContent = String(count);
    totalEl.textContent = `S/ ${total.toFixed(2)}`;
  } catch (_) {
    countEl.textContent = '0';
    totalEl.textContent = 'S/ 0.00';
  }
}

/* ---------------- Toast simple ---------------- */
let toastTimer = null;
function showToast(mensaje) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = mensaje;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}

/* ---------------- Inicialización de layout ---------------- */
async function initLayout() {
  renderHeader();
  renderFooter();
  wireDrawerEvents();
  wireAccountMenu();
  document.getElementById('cart-btn').addEventListener('click', () => {
    if (!Api.isAuthenticated()) { openLoginDrawer(); return; }
    window.location.href = 'carrito.html';
  });
  await updateAuthUI();
  await updateCartBadge();
}
