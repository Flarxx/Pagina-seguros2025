document.addEventListener('DOMContentLoaded', function () {
  // Comprobar que Swiper esté disponible
  if (typeof Swiper === 'undefined') {
    console.warn('Swiper no está cargado. Asegúrate de incluir el CDN antes de base.js');
    return;
  }
  const swiper = new Swiper('.my-swiper', {
    loop: true,
    speed: 700,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true
    },
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev'
    },
    lazy: {
      loadPrevNext: true,
      loadPrevNextAmount: 1
    },
    keyboard: {
      enabled: true,
      onlyInViewport: true
    },
    effect: 'slide',
    slidesPerView: 1,
    // callbacks útiles
    on: {
      init: function () {
        // opcional: añadir clase cuando esté listo
        document.querySelector('.my-swiper')?.classList.add('swiper-initialized');
      },
      slideChange: function () {
        // Ejemplo: cargar contenido con HTMX al activar un slide que tenga data-hx-url
        try {
          const active = document.querySelector('.swiper-slide-active [data-hx-url]');
          if (active && active.dataset.loaded === 'false' && window.htmx) {
            const url = active.dataset.hxUrl;
            if (url) {
              htmx.ajax('GET', url, { target: active, swap: 'innerHTML' });
              active.dataset.loaded = 'true';
            }
          }
        } catch (e) {
          console.error('Error al manejar slideChange:', e);
        }
      }
    }
  });

  // Ajuste opcional de altura para que el slider ocupe más del viewport en desktop
  function ajustarAlturaHero() {
    const el = document.querySelector('.my-swiper');
    if (!el) return;
    const vh = window.innerHeight;
    // Ajusta aquí la proporción si quieres (0.65 = 65vh)
    const altura = Math.max(vh * 0.6, Math.min(vh * 0.9, vh * 0.8));
    el.style.minHeight = Math.round(altura) + 'px';
  }
  ajustarAlturaHero();
  window.addEventListener('resize', ajustarAlturaHero);
});
