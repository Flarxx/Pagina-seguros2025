document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modalTerminos");
    const checkbox = document.getElementById("aceptoTerminos");
    const btn = document.getElementById("btnContinuar");

    // Mostrar modal
    modal.classList.remove("hidden");
    modal.style.display = "flex"; // forzar display flex

    // Evitar que el usuario cierre modal accidentalmente fuera del botón
    modal.addEventListener("click", function(e) {
        if(e.target === modal) {
            // modal.style.display = "none"; // opcional: permitir cerrar haciendo click fuera
        }
    });

    // Habilitar botón cuando el checkbox esté activo
    if (checkbox && btn) {
        checkbox.addEventListener("change", function () {
            if (this.checked) {
                btn.disabled = false;
                btn.classList.remove("opacity-50", "cursor-not-allowed");
            } else {
                btn.disabled = true;
                btn.classList.add("opacity-50", "cursor-not-allowed");
            }
        });
    } else {
        console.warn("⚠️ Checkbox o botón no encontrados");
    }
});



document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('modalCotizaciones');
  const checkbox = document.getElementById('aceptoCotizaciones');
  const btnAceptar = document.getElementById('btnAceptarCotizacion');
  const btnCancelar = document.getElementById('btnCancelarCotizacion');

  // Mostrar modal al cargar la página o al hacer click en "¡Quiero cotizar!"
  document.querySelectorAll('.btn-quote').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.remove('hidden');
    });
  });

  // Habilitar/deshabilitar botón
  checkbox.addEventListener('change', () => {
    btnAceptar.disabled = !checkbox.checked;
    btnAceptar.classList.toggle('opacity-50', !checkbox.checked);
    btnAceptar.classList.toggle('cursor-not-allowed', !checkbox.checked);
  });

  // Cancelar modal
  btnCancelar.addEventListener('click', () => {
    modal.classList.add('hidden');
    checkbox.checked = false;
    btnAceptar.disabled = true;
    btnAceptar.classList.add('opacity-50', true);
    btnAceptar.classList.add('cursor-not-allowed', true);
  });

  // Aceptar modal (aquí podrías redirigir a la cotización real)
  btnAceptar.addEventListener('click', () => {
    modal.classList.add('hidden');
    // Aquí podrías redirigir a otra página, abrir un formulario, etc.
    alert('¡Cotización iniciada!');
  });
});
