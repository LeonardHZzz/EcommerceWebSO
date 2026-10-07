let catalogoPorZona = {};  
let itemsCarrito = [];     
let cuponAplicado = null;  

function money(n) { return `S/ ${Number(n).toFixed(2)}`; }

async function cargarCatalogo() {
  const eventos = await Api.eventos();
  const map = {};
  eventos.forEach(ev => (ev.zonas || []).forEach(z => { map[z.id_zona] = { zona: z, evento: ev }; }));
  catalogoPorZona = map;
}

function calcularSubtotal() {
  return itemsCarrito.reduce((acc, item) => {
    const info = catalogoPorZona[item.id_zona];
    const precio = info ? Number(info.zona.precio) : 0;
    return acc + precio * item.cantidad;
  }, 0);
}

function actualizarResumen() {
  const subtotal = calcularSubtotal();
  document.getElementById('summary-subtotal').textContent = money(subtotal);

  const discountRow = document.getElementById('summary-discount-row');
  let total = subtotal;

  if (cuponAplicado) {
    const descuento = (subtotal * Number(cuponAplicado.porcentaje_descuento)) / 100;
    total = subtotal - descuento;
    document.getElementById('summary-discount-label').textContent = `Descuento (${cuponAplicado.codigo})`;
    document.getElementById('summary-discount-value').textContent = `- ${money(descuento)}`;
    discountRow.hidden = false;
  } else {
    discountRow.hidden = true;
  }

  document.getElementById('summary-total').textContent = money(total);
  document.getElementById('checkout-btn').disabled = itemsCarrito.length === 0;
}

function renderItems() {
  const box = document.getElementById('cart-items');

  if (!itemsCarrito.length) {
    box.innerHTML = `
      <div class="cart-empty">
        <p>Tu carrito está vacío.</p>
        <a href="index.html" class="btn btn-primary">Ver eventos disponibles</a>
      </div>`;
    actualizarResumen();
    return;
  }

  box.innerHTML = itemsCarrito.map(item => {
    const info = catalogoPorZona[item.id_zona];
    const nombreZona = info ? info.zona.nombre_zona : `Zona #${item.id_zona}`;
    const nombreEvento = info ? info.evento.titulo : '';
    const precio = info ? Number(info.zona.precio) : 0;
    const subtotal = precio * item.cantidad;
    const stockDisponible = info ? info.zona.capacidad_disponible : 999;

    return `
      <article class="cart-item" data-id="${item.id_carrito}">
        <div class="cart-item-info">
          <span class="ticket-evento">${nombreEvento}</span>
          <h4>${nombreZona}</h4>
          <span class="cart-item-price">${money(precio)} c/u</span>
        </div>
        <div class="cart-item-qty">
          <button class="qty-btn" data-action="decrementar" aria-label="Disminuir">−</button>
          <span class="qty-value">${item.cantidad}</span>
          <button class="qty-btn" data-action="incrementar" aria-label="Aumentar" ${item.cantidad >= stockDisponible ? 'disabled' : ''}>+</button>
        </div>
        <div class="cart-item-subtotal">${money(subtotal)}</div>
        <button class="cart-item-remove" data-action="quitar" aria-label="Quitar">✕</button>
      </article>`;
  }).join('');

  box.querySelectorAll('.cart-item').forEach(card => {
    const idCarrito = Number(card.dataset.id);
    const item = itemsCarrito.find(i => i.id_carrito === idCarrito);

    card.querySelector('[data-action="incrementar"]').addEventListener('click', () => cambiarCantidad(idCarrito, item.cantidad + 1));
    card.querySelector('[data-action="decrementar"]').addEventListener('click', () => {
      if (item.cantidad <= 1) { quitarItem(idCarrito); return; }
      cambiarCantidad(idCarrito, item.cantidad - 1);
    });
    card.querySelector('[data-action="quitar"]').addEventListener('click', () => quitarItem(idCarrito));
  });

  actualizarResumen();
}

async function cambiarCantidad(idCarrito, nuevaCantidad) {
  try {
    await Api.actualizarCantidadCarrito(idCarrito, nuevaCantidad);
    const item = itemsCarrito.find(i => i.id_carrito === idCarrito);
    item.cantidad = nuevaCantidad;
    renderItems();
    await updateCartBadge();
  } catch (err) {
    showToast(err.message);
  }
}

async function quitarItem(idCarrito) {
  try {
    await Api.quitarDelCarrito(idCarrito);
    itemsCarrito = itemsCarrito.filter(i => i.id_carrito !== idCarrito);
    renderItems();
    await updateCartBadge();
    showToast('Entrada quitada del carrito');
  } catch (err) {
    showToast(err.message);
  }
}

/* ---------------- Cupón ---------------- */
function wireCupon() {
  document.getElementById('coupon-apply').addEventListener('click', async () => {
    const codigo = document.getElementById('coupon-input').value.trim();
    const feedback = document.getElementById('coupon-feedback');
    feedback.className = 'coupon-feedback';
    if (!codigo) return;

    try {
      const resp = await Api.validarCupon(codigo);
      if (resp.valido) {
        cuponAplicado = { codigo, porcentaje_descuento: resp.porcentaje_descuento };
        feedback.textContent = `Cupón aplicado: -${resp.porcentaje_descuento}%`;
        feedback.classList.add('ok');
      } else {
        cuponAplicado = null;
        feedback.textContent = resp.mensaje || 'Cupón no válido';
        feedback.classList.add('error');
      }
    } catch (err) {
      cuponAplicado = null;
      feedback.textContent = err.message;
      feedback.classList.add('error');
    }
    actualizarResumen();
  });
}

/* ==========================================================
   Pasarela de pago SIMULADA
   No es un cobro real: solo imita visualmente el flujo (form ->
   procesando -> éxito) y, por debajo, llama al checkout real de
   la API + al endpoint de demo que marca la orden como pagada.
   ========================================================== */

function camposPasarela(metodo) {
  if (metodo === 'tarjeta') {
    return `
      <div class="field">
        <label for="pasarela-num-tarjeta">Número de tarjeta</label>
        <input type="text" id="pasarela-num-tarjeta" inputmode="numeric" maxlength="19" placeholder="4242 4242 4242 4242" required>
      </div>
      <div class="field">
        <label for="pasarela-nombre-tarjeta">Nombre en la tarjeta</label>
        <input type="text" id="pasarela-nombre-tarjeta" placeholder="Como figura en la tarjeta" required>
      </div>
      <div class="form-row">
        <div class="field">
          <label for="pasarela-venc">Vencimiento</label>
          <input type="text" id="pasarela-venc" placeholder="MM/AA" maxlength="5" required>
        </div>
        <div class="field">
          <label for="pasarela-cvv">CVV</label>
          <input type="text" id="pasarela-cvv" inputmode="numeric" maxlength="4" placeholder="123" required>
        </div>
      </div>`;
  }
  // Yape / Plin: solo se pide el número de celular asociado
  const nombre = metodo === 'yape' ? 'Yape' : 'Plin';
  return `
    <div class="field">
      <label for="pasarela-celular">Número de celular (${nombre})</label>
      <input type="text" id="pasarela-celular" inputmode="numeric" maxlength="9" placeholder="9XXXXXXXX" required>
    </div>
    <p class="pasarela-demo-note">Se simula la confirmación desde tu app de ${nombre}.</p>`;
}

function wireFormatoTarjeta() {
  const input = document.getElementById('pasarela-num-tarjeta');
  if (!input) return;
  input.addEventListener('input', () => {
    const digits = input.value.replace(/\D/g, '').slice(0, 16);
    input.value = digits.replace(/(.{4})/g, '$1 ').trim();
  });
}

function mostrarPasoPasarela(paso) {
  ['form', 'procesando', 'exito', 'error'].forEach(p => {
    document.getElementById(`pasarela-step-${p}`).hidden = (p !== paso);
  });
}

function abrirPasarela() {
  const total = document.getElementById('summary-total').textContent;
  document.getElementById('pasarela-total').textContent = total;

  const metodo = document.getElementById('metodo-pago').value;
  document.getElementById('pasarela-campos').innerHTML = camposPasarela(metodo);
  wireFormatoTarjeta();

  document.getElementById('pasarela-error').classList.remove('show');
  mostrarPasoPasarela('form');

  document.getElementById('pasarela-overlay').classList.add('open');
  document.getElementById('pasarela-modal').classList.add('open');
}

function cerrarPasarela() {
  document.getElementById('pasarela-overlay').classList.remove('open');
  document.getElementById('pasarela-modal').classList.remove('open');
}

async function procesarPagoSimulado() {
  mostrarPasoPasarela('procesando');

  const metodoPago = document.getElementById('metodo-pago').value;
  const codigoCupon = cuponAplicado ? cuponAplicado.codigo : null;

  // Pausa artificial para que se sienta como un pago real procesándose.
  await new Promise(r => setTimeout(r, 1500));

  try {
    const orden = await Api.checkout(metodoPago, codigoCupon);
    await Api.simularPago(orden.id_orden); // SOLO DEMO — ver api.js

    document.getElementById('exito-numero-pedido').textContent = `#${orden.id_orden}`;
    mostrarPasoPasarela('exito');

    itemsCarrito = [];
    cuponAplicado = null;
    await updateCartBadge();
  } catch (err) {
    document.getElementById('pasarela-error-mensaje').textContent = err.message;
    mostrarPasoPasarela('error');
  }
}

function wireCheckout() {
  document.getElementById('checkout-btn').addEventListener('click', abrirPasarela);
  document.getElementById('pasarela-close').addEventListener('click', cerrarPasarela);
  document.getElementById('pasarela-overlay').addEventListener('click', cerrarPasarela);

  document.getElementById('pasarela-pagar-btn').addEventListener('click', (e) => {
    e.preventDefault();
    procesarPagoSimulado();
  });

  document.getElementById('pasarela-reintentar-btn').addEventListener('click', () => {
    mostrarPasoPasarela('form');
  });
}

/* ---------------- Init ---------------- */
document.addEventListener('DOMContentLoaded', async () => {
  if (!Api.isAuthenticated()) {
    window.location.href = 'index.html';
    return;
  }
  await initLayout();
  wireCupon();
  wireCheckout();

  try {
    await cargarCatalogo();
    itemsCarrito = await Api.carrito();
    renderItems();
  } catch (err) {
    document.getElementById('cart-items').innerHTML =
      `<p class="error-text">No se pudo cargar tu carrito: ${err.message}</p>`;
  }
});
