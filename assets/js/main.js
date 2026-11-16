/* OXY PACK GLOBAL — site scripts */
(function () {
  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('mobile-nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -60px 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Footer year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Quote form (FormSubmit AJAX endpoint)
  var form = document.getElementById('quote-form');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = document.getElementById('form-err');
      var submit = form.querySelector('button[type="submit"]');
      err.style.display = 'none';
      submit.disabled = true;
      submit.textContent = 'Sending…';
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      fetch(form.getAttribute('data-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json(); }).then(function (res) {
        if (res && (res.success === true || res.success === 'true')) {
          form.style.display = 'none';
          document.getElementById('form-ok').classList.add('show');
        } else { throw new Error('failed'); }
      }).catch(function () {
        err.style.display = 'block';
        submit.disabled = false;
        submit.textContent = 'Submit enquiry →';
      });
    });
  }
})();
