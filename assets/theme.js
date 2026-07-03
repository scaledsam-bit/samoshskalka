document.addEventListener('DOMContentLoaded', function () {

  // Mobile menu toggle
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('is-open');
    });
  }

  // Product page: thumbnail gallery
  var mainImg = document.querySelector('.product-main-image img');
  var thumbs = document.querySelectorAll('.product-thumbnails button');
  thumbs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      thumbs.forEach(function (t) { t.classList.remove('is-active'); });
      btn.classList.add('is-active');
      var src = btn.querySelector('img').getAttribute('data-full');
      if (mainImg && src) mainImg.setAttribute('src', src);
    });
  });

  // Quantity controls
  document.querySelectorAll('.qty-minus, .qty-plus').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = btn.closest('.qty-controls').querySelector('input');
      var val = parseInt(input.value) || 1;
      if (btn.classList.contains('qty-minus') && val > 1) val--;
      if (btn.classList.contains('qty-plus')) val++;
      input.value = val;
    });
  });

});
