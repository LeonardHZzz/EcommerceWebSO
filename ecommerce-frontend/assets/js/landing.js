function formatFecha(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short' }).toUpperCase();
}

function renderHeroCarousel(eventos) {
  const track = document.getElementById('hero-track');
  if (!eventos.length) {
    track.innerHTML = `<p class="error-text">Todavía no hay eventos publicados. Vuelve pronto.</p>`;
    return;
  }
  track.innerHTML = eventos.map(ev => `
    <article class="hero-card">
      <span class="hero-card-badge">${formatFecha(ev.fecha_inicio)} – ${formatFecha(ev.fecha_fin)}</span>
      <h2>${ev.titulo}</h2>
      <p>${ev.descripcion || ''}</p>
    </article>
  `).join('');
}

function renderTicketsGrid(eventos) {
  const grid = document.getElementById('tickets-grid');
  const cards = [];
  eventos.forEach(ev => (ev.zonas || []).forEach(z => cards.push({ ev, z })));

  if (!cards.length) {
    grid.innerHTML = `<p class="error-text">No hay entradas disponibles por ahora.</p>`;
    return;
  }

  grid.innerHTML = cards.map(({ ev, z }, i) => `
    <article class="ticket-card ticket-theme-${i % 4}">
      <div class="ticket-card-top">
        <span class="ticket-evento">${ev.titulo}</span>
        <h3>${z.nombre_zona}</h3>
      </div>
      <div class="ticket-card-bottom">
        <span class="ticket-price">S/ ${Number(z.precio).toFixed(2)}</span>
        <button class="btn-add-cart" data-zona="${z.id_zona}" ${z.capacidad_disponible <= 0 ? 'disabled' : ''}>
          ${z.capacidad_disponible <= 0 ? 'Agotado' : 'Agregar'}
        </button>
      </div>
    </article>
  `).join('');

  grid.querySelectorAll('.btn-add-cart').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!Api.isAuthenticated()) { openLoginDrawer(); return; }
      const original = btn.textContent;
      btn.disabled = true;
      try {
        await Api.agregarAlCarrito(Number(btn.dataset.zona), 1);
        await updateCartBadge();
        btn.textContent = 'Agregado ✓';
        showToast('Entrada agregada al carrito');
        setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 1400);
      } catch (err) {
        showToast(err.message);
        btn.disabled = false;
      }
    });
  });
}

async function initLanding() {
  await initLayout();
  initArrowCarousel('hero-track', 'hero-prev', 'hero-next', 360);
  try {
    const eventos = await Api.eventos();
    const activos = eventos.filter(e => e.estado === 'activo');
    renderHeroCarousel(activos.length ? activos : eventos);
    renderTicketsGrid(eventos);
  } catch (err) {
    document.getElementById('hero-track').innerHTML =
      `<p class="error-text">No se pudieron cargar los eventos: ${err.message}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', initLanding);
