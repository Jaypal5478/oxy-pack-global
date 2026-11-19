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

  // Quote buttons jump to the form when this page has one
  if (document.getElementById('quote-form')) {
    document.querySelectorAll('[data-quote]').forEach(function (a) {
      a.setAttribute('href', '#quote-form');
      a.addEventListener('click', function () {
        if (nav && nav.classList.contains('open')) { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
      });
    });
  }

  // Product filter (products page)
  var filterBtns = document.querySelectorAll('.pfilter button');
  var pcards = document.querySelectorAll('#pgrid .pcard');
  filterBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filter');
      filterBtns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      pcards.forEach(function (c) { c.hidden = !(f === 'all' || c.getAttribute('data-cat') === f); });
    });
  });

  // Quote form (FormSubmit AJAX endpoint)
  var form = document.getElementById('quote-form');
  // Prefill from a product card link (?product=...&cat=...)
  if (form && 'URLSearchParams' in window) {
    var qs = new URLSearchParams(location.search);
    var product = qs.get('product');
    var catMap = { corrugated: 0, bags: 1, cartons: 2, food: 3, protective: 4 };
    var sel = document.getElementById('category');
    if (sel && catMap.hasOwnProperty(qs.get('cat'))) sel.selectedIndex = catMap[qs.get('cat')];
    var msg = document.getElementById('message');
    if (msg && product && !msg.value) msg.value = 'Product: ' + product.slice(0, 120) + '\n';
  }
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
