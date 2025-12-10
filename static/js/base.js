// ...existing code...
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Swiper === 'undefined') {
        console.warn('Swiper no está cargado. Incluye swiper-bundle.min.js antes de este script.');
        return;
    }

    const commonOpts = {
        loop: true,
        slidesPerView: 1,
        spaceBetween: 16,
        autoplay: { delay: 5000, disableOnInteraction: false }, // autoplay cada 5s
        pagination: { clickable: true },
        breakpoints: {
            768: { slidesPerView: 1, spaceBetween: 24 },
            1024: { slidesPerView: 1, spaceBetween: 32 }
        }
    };

    // Slider 1
    new Swiper('.my-swiper-1', Object.assign({}, commonOpts, {
        pagination: Object.assign({}, commonOpts.pagination, { el: '.swiper-pagination-1' }),
        navigation: { nextEl: '.swiper-button-next-1', prevEl: '.swiper-button-prev-1' }
    }));

});


// cierre de poliza 

document.addEventListener('click', function(event) {
          const dropdown = document.getElementById('polizas-mega-menu');
          const button = document.getElementById('polizas-dropdown-button');
          
          if (dropdown && button && !button.contains(event.target) && !dropdown.contains(event.target)) {
              dropdown.classList.add('hidden');
          }
      });

// hamburger para el mobile 

document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    const menuCuenta = document.getElementById('mobile-menu');

    const iconOpen = document.getElementById('icon-open');
    const iconClose = document.getElementById('icon-close');

    if (menuToggle && menuCuenta) {
        menuToggle.addEventListener('click', function () {

            // Animación del menú
            menuCuenta.classList.toggle('opacity-0');
            menuCuenta.classList.toggle('-translate-y-4');
            menuCuenta.classList.toggle('pointer-events-none');

            // Cambiar iconos
            iconOpen.classList.toggle('hidden');
            iconClose.classList.toggle('hidden');

            // Cerrar mega menú si está abierto
            const megaMenu = document.getElementById('polizas-mega-menu');
            if (megaMenu && !megaMenu.classList.contains('hidden')) {
                megaMenu.classList.add('hidden');
            }
        });
    }
});

