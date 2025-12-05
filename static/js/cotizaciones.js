document.addEventListener('DOMContentLoaded', () => {
        const cotizarButtons = document.querySelectorAll('.btn-quote');

        cotizarButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault(); 
                
                // Obtiene el título del seguro (SALUD, VIDA, etc.)
                const card = event.target.closest('.card-shadow');
                const tipoSeguro = card.querySelector('h3').textContent;

                // **TODO:** Reemplaza esta alerta con la lógica para mostrar tu formulario dinámico.
                console.log(`Click en: ${tipoSeguro}`);
                alert(`¡Preparando cotización para ${tipoSeguro}! Aquí se cargará la tarjeta dinámica/modal.`);
            });
        });
    });


document.addEventListener('DOMContentLoaded', () => {
    const cotizarButtons = document.querySelectorAll('.btn-quote');
    const modal = document.getElementById('modalCotizaciones');
    const btnCancelar = document.getElementById('btnCancelarCotizacion');
    const btnAceptar = document.getElementById('btnAceptarCotizacion');
    const checkbox = document.getElementById('aceptoCotizaciones');

    cotizarButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); 

            const card = event.target.closest('.card-shadow');
            const tipoSeguro = card.querySelector('h3').textContent;

            // Muestra el modal
            modal.classList.remove('hidden');

            // Opcional: Cambiar título dentro del modal dinámicamente
            modal.querySelector('h2').textContent = `Términos y Condiciones de la Cotización de ${tipoSeguro}`;
        });
    });

    // Cerrar modal con "Cancelar"
    btnCancelar.addEventListener('click', () => {
        modal.classList.add('hidden');
        checkbox.checked = false;
        btnAceptar.disabled = true;
        btnAceptar.classList.add('opacity-50', 'cursor-not-allowed');
    });

    // Habilitar botón "Aceptar" solo si se acepta el checkbox
    checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
            btnAceptar.disabled = false;
            btnAceptar.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            btnAceptar.disabled = true;
            btnAceptar.classList.add('opacity-50', 'cursor-not-allowed');
        }
    });

    // Acción al aceptar
    btnAceptar.addEventListener('click', () => {
        modal.classList.add('hidden');
        alert(`Cotización aceptada. Aquí iría tu formulario para ${modal.querySelector('h2').textContent}`);
    });
});


modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.add('hidden');
        checkbox.checked = false;
        btnAceptar.disabled = true;
        btnAceptar.classList.add('opacity-50', 'cursor-not-allowed');
    }
});
