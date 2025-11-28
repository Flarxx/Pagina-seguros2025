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
