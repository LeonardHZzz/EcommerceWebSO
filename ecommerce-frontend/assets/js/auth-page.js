let authMode = 'register';

function applyAuthMode() {
  const isRegister = authMode === 'register';

  document.getElementById('auth-title').textContent = isRegister ? 'Crea tu cuenta' : 'Inicia sesión';
  document.getElementById('auth-subtitle').textContent = isRegister
    ? 'Completa tus datos para empezar a comprar tus entradas.'
    : 'Ingresa tus credenciales para continuar.';

  document.getElementById('extra-fields').style.display = isRegister ? 'block' : 'none';
  document.getElementById('telefono-field').style.display = isRegister ? 'block' : 'none';
  document.querySelectorAll('.register-only').forEach(el => { el.required = isRegister; });

  document.getElementById('submit-btn').textContent = isRegister ? 'Registrarme' : 'Ingresar';

  document.getElementById('toggle-link').textContent = isRegister
    ? '¿Ya tienes cuenta? Inicia sesión aquí'
    : '¿No tienes cuenta? Regístrate aquí';

  document.getElementById('auth-error').classList.remove('show');
}

function wireAuthPage() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('mode') === 'login') authMode = 'login';
  applyAuthMode();

  document.getElementById('toggle-link').addEventListener('click', (e) => {
    e.preventDefault();
    authMode = authMode === 'register' ? 'login' : 'register';
    applyAuthMode();
  });

  document.getElementById('auth-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById('auth-error');
    errorBox.classList.remove('show');

    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;

    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;

    try {
      if (authMode === 'register') {
        const payload = {
          nombre: document.getElementById('auth-nombre').value,
          apellido: document.getElementById('auth-apellido').value,
          email,
          password,
          telefono: document.getElementById('auth-telefono').value || null,
        };
        await Api.registrar(payload);
        await Api.login(email, password); // auto-login tras registrarse, mejor UX
      } else {
        await Api.login(email, password);
      }
      window.location.href = 'index.html';
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.add('show');
      submitBtn.disabled = false;
    }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await initLayout();
  wireAuthPage();
});
