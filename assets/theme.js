(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    initMobileMenu();
    initStickyHeader();
    initScrollAnimations();
    initProductGallery();
    initQuantityControls();
    initAddToCartAjax();
  }

  function initMobileMenu() {
    var toggle = document.querySelector('.menu-toggle');
    var nav = document.querySelector('.main-nav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      toggle.classList.toggle('is-active');
      nav.classList.toggle('is-open');
      document.body.style.overflow = nav.classList.contains('is-open') ? 'hidden' : '';
    });

    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        toggle.classList.remove('is-active');
        nav.classList.remove('is-open');
        document.body.style.overflow = '';
      });
    });
  }

  function initStickyHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;

    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 50);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function initScrollAnimations() {
    var elements = document.querySelectorAll('.animate-in');
    if (!elements.length) return;

    if (!('IntersectionObserver' in window)) {
      elements.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    elements.forEach(function (el) { observer.observe(el); });
  }

  function initProductGallery() {
    var mainImg = document.querySelector('.product-main-image img');
    var thumbs = document.querySelectorAll('.product-thumbnails button');
    if (!mainImg || !thumbs.length) return;

    thumbs.forEach(function (btn) {
      btn.addEventListener('click', function () {
        thumbs.forEach(function (t) { t.classList.remove('is-active'); });
        btn.classList.add('is-active');
        var src = btn.querySelector('img').getAttribute('data-full');
        if (src) {
          mainImg.style.opacity = '0';
          setTimeout(function () {
            mainImg.setAttribute('src', src);
            mainImg.style.opacity = '1';
          }, 200);
        }
      });
    });

    mainImg.style.transition = 'opacity 0.25s ease';
  }

  function initQuantityControls() {
    document.querySelectorAll('.qty-minus, .qty-plus').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var input = btn.closest('.qty-controls').querySelector('input');
        var val = parseInt(input.value) || 1;
        var max = parseInt(input.getAttribute('max')) || 9999;
        if (btn.classList.contains('qty-minus') && val > 1) val--;
        if (btn.classList.contains('qty-plus') && val < max) val++;
        input.value = val;
        input.dispatchEvent(new Event('change'));
      });
    });
  }

  function initAddToCartAjax() {
    var forms = document.querySelectorAll('form[action="/cart/add"]');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var btn = form.querySelector('.btn-add-to-cart');
        if (!btn || btn.disabled) return;

        var originalText = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner"></span>';
        btn.disabled = true;

        var formData = new FormData(form);

        fetch('/cart/add.js', {
          method: 'POST',
          body: formData
        })
        .then(function (res) { return res.json(); })
        .then(function () {
          btn.innerHTML = 'Pridano!';
          btn.style.background = '#22c55e';
          updateCartCount();
          setTimeout(function () {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.disabled = false;
          }, 1800);
        })
        .catch(function () {
          btn.innerHTML = originalText;
          btn.disabled = false;
        });
      });
    });
  }

  function updateCartCount() {
    fetch('/cart.js')
      .then(function (res) { return res.json(); })
      .then(function (cart) {
        var badges = document.querySelectorAll('.cart-count');
        badges.forEach(function (badge) {
          badge.textContent = cart.item_count;
          badge.style.display = cart.item_count > 0 ? 'flex' : 'none';
        });
      })
      .catch(function () {});
  }

})();
