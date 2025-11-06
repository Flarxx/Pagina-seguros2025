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