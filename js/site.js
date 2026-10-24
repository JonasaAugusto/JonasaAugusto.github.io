/* Jonas Augusto · portfólio v2. Sem dependências. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  var fine = matchMedia('(hover: hover) and (pointer: fine)');
  var lang = root.lang === 'en' ? 'en' : 'pt';

  /* ---------- idioma ---------- */
  function swap(el, attr, prop, key) {
    var store = 'pt' + key;
    if (el.dataset[store] === undefined) el.dataset[store] = prop === 'html' ? el.innerHTML : (prop === 'text' ? el.textContent : el.getAttribute(prop) || '');
    var val = lang === 'en' ? el.getAttribute(attr) : el.dataset[store];
    if (prop === 'html') el.innerHTML = val;
    else if (prop === 'text') el.textContent = val;
    else el.setAttribute(prop, val);
  }
  function applyLang() {
    root.lang = lang === 'en' ? 'en' : 'pt-BR';
    d.querySelectorAll('[data-en]').forEach(function (el) { swap(el, 'data-en', 'text', 'Text'); });
    d.querySelectorAll('[data-en-html]').forEach(function (el) { swap(el, 'data-en-html', 'html', 'Html'); });
    d.querySelectorAll('[data-en-aria]').forEach(function (el) { swap(el, 'data-en-aria', 'aria-label', 'Aria'); });
    d.querySelectorAll('[data-en-ph]').forEach(function (el) { swap(el, 'data-en-ph', 'placeholder', 'Ph'); });
    d.querySelectorAll('[data-en-title]').forEach(function (el) { swap(el, 'data-en-title', 'title', 'Title'); });
    d.querySelectorAll('[data-en-content]').forEach(function (el) { swap(el, 'data-en-content', 'content', 'Content'); });
    var lbl = d.getElementById('lang-label'); if (lbl) lbl.textContent = lang === 'en' ? 'PT' : 'EN';
    d.querySelectorAll('[data-cv-page]').forEach(function (a) { a.href = lang === 'en' ? 'cv.en.html' : 'cv.html'; });
    d.querySelectorAll('[data-count]').forEach(function (el) { el.textContent = fmt(+el.dataset.count, el); });
  }
  function withTransition(fn, ev) {
    if (!d.startViewTransition || reduce.matches) { fn(); return; }
    if (ev && ev.clientX !== undefined) {
      root.style.setProperty('--vx', ev.clientX + 'px');
      root.style.setProperty('--vy', ev.clientY + 'px');
    }
    d.startViewTransition(fn);
  }
  var langBtn = d.getElementById('lang-btn');
  if (langBtn) langBtn.addEventListener('click', function (e) {
    lang = lang === 'en' ? 'pt' : 'en';
    try { localStorage.setItem('preferredLang', lang); } catch (x) {}
    withTransition(applyLang, e);
  });
  if (lang === 'en') applyLang();

  /* ---------- tema ---------- */
  function syncThemeColor() {
    var m = d.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', root.getAttribute('data-theme') === 'light' ? '#f7f7f6' : '#0b0b0b');
  }
  syncThemeColor();
  var themeBtn = d.getElementById('theme-btn');
  if (themeBtn) themeBtn.addEventListener('click', function (e) {
    var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    try { localStorage.setItem('theme', next); } catch (x) {}
    withTransition(function () { root.setAttribute('data-theme', next); syncThemeColor(); }, e);
  });

  /* ---------- header: borda ao rolar, some ao descer ---------- */
  var header = d.querySelector('.site-header'), lastY = 0, ticking = false;
  function onScroll() {
    var y = scrollY;
    header.classList.toggle('scrolled', y > 8);
    var menuOpen = menu && menu.classList.contains('open');
    header.classList.toggle('hide', !menuOpen && y > 480 && y > lastY + 4);
    if (y < lastY - 4 || y < 480) header.classList.remove('hide');
    lastY = y; ticking = false;
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });

  /* ---------- menu móvel ---------- */
  var menu = d.getElementById('mobile-menu'), menuBtn = d.getElementById('menu-btn');
  function setMenu(open) {
    if (!menu) return;
    if (open) { menu.hidden = false; requestAnimationFrame(function () { menu.classList.add('open'); }); }
    else { menu.classList.remove('open'); setTimeout(function () { if (!menu.classList.contains('open')) menu.hidden = true; }, 400); }
    menuBtn.setAttribute('aria-expanded', String(open));
  }
  if (menuBtn) menuBtn.addEventListener('click', function () { setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'); });
  if (menu) menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });

  /* ---------- nav ativa ---------- */
  var navLinks = d.querySelectorAll('.nav a');
  if ('IntersectionObserver' in window && navLinks.length) {
    var navIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        navLinks.forEach(function (a) { a.setAttribute('aria-current', a.getAttribute('href') === '#' + e.target.id ? 'true' : 'false'); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    d.querySelectorAll('main section[id]').forEach(function (s) { navIO.observe(s); });
  }

  /* ---------- entradas ---------- */
  var revealEls = d.querySelectorAll('[data-reveal], [data-reveal-one], .shot');
  function show(el) { el.classList.add('in'); if (el.querySelector('[data-count]') || el.hasAttribute('data-count')) countUp(el); }
  if ('IntersectionObserver' in window && !reduce.matches) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
    /* rede de segurança: nada fica escondido se o observer falhar */
    setTimeout(function () { revealEls.forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < innerHeight) show(el); }); }, 2500);
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- números que contam ---------- */
  function fmt(v, el) {
    var dec = +(el.dataset.dec || 0);
    var s = v.toFixed(dec);
    if (lang === 'pt') s = s.replace('.', ',');
    return s + (el.dataset.unit || '');
  }
  function countUp(scope) {
    scope.querySelectorAll('[data-count]').forEach(function (el) {
      if (el.dataset.done) return; el.dataset.done = '1';
      var to = +el.dataset.count, from = to === 0 ? 9 : 0, t0 = performance.now(), dur = 1400;
      if (to < 1) from = 73.7; /* 73,7 s → 0,08 s */
      else if (to === 27) from = 900;
      else if (to === 2.25) from = 35;
      else if (to === 100) from = 96;
      (function tick(t) {
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt(from + (to - from) * e, el);
        if (p < 1) requestAnimationFrame(tick); else el.textContent = fmt(to, el);
      })(t0);
    });
  }

  /* ---------- prévia que segue o cursor no ledger ---------- */
  var ledger = d.getElementById('ledger'), peek = d.getElementById('peek');
  if (ledger && peek && fine.matches) {
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = 0, active = false;
    function loop() {
      cx += (tx - cx) * 0.16; cy += (ty - cy) * 0.16;
      peek.style.transform = 'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0)';
      if (active || Math.abs(tx - cx) > .5) raf = requestAnimationFrame(loop); else raf = 0;
    }
    ledger.querySelectorAll('.row').forEach(function (row) {
      row.addEventListener('mouseenter', function (e) {
        var id = row.dataset.peek;
        peek.querySelectorAll('.peek-item').forEach(function (p) { p.classList.toggle('on', p.dataset.id === id); });
        if (!active) { cx = tx = e.clientX + 28; cy = ty = e.clientY - 70; }
        active = true; peek.classList.add('on');
        if (!raf) raf = requestAnimationFrame(loop);
      });
      row.addEventListener('mouseleave', function () { active = false; peek.classList.remove('on'); });
    });
    ledger.addEventListener('mousemove', function (e) {
      var w = peek.offsetWidth || 340;
      tx = Math.min(e.clientX + 28, innerWidth - w - 16);
      ty = e.clientY - 70;
      if (reduce.matches) { cx = tx; cy = ty; }
    });
  }

  /* ---------- diálogos ---------- */
  var CV = {
    pt: { pdf: 'JonasAugusto_cv_m.pdf', page: 'cv.html', dl: 'JonasAugusto_CV_PT.pdf' },
    en: { pdf: 'JonasAugusto_cv_en.pdf', page: 'cv.en.html', dl: 'JonasAugusto_CV_EN.pdf' }
  };
  var cvLang = null, lastFocus = null;
  function setCv(l) {
    cvLang = l;
    var f = CV[l], frame = d.getElementById('cv-frame');
    /* celular não ajusta PDF em iframe: mostra a página HTML do CV (mesmo conteúdo) */
    var small = matchMedia('(max-width: 720px)').matches;
    frame.src = small ? f.page : f.pdf + '#view=FitH&toolbar=0';
    var a = d.getElementById('cv-download'); a.href = f.pdf; a.setAttribute('download', f.dl);
    d.getElementById('cv-lang-label').textContent = l === 'pt' ? 'EN' : 'PT';
  }
  function openDlg(id) {
    var dlg = d.getElementById(id); if (!dlg) return;
    lastFocus = d.activeElement;
    if (id === 'dlg-cv') setCv(cvLang || lang);
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    root.style.overflow = 'hidden';
  }
  d.querySelectorAll('[data-open]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); openDlg(b.dataset.open === 'cv' ? 'dlg-cv' : 'dlg-f5'); });
  });
  d.querySelectorAll('dialog').forEach(function (dlg) {
    dlg.addEventListener('close', function () { root.style.overflow = ''; if (lastFocus) lastFocus.focus(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelectorAll('[data-close]').forEach(function (b) { b.addEventListener('click', function () { dlg.close(); }); });
  });
  var cvLangBtn = d.getElementById('cv-lang-btn');
  if (cvLangBtn) cvLangBtn.addEventListener('click', function () { setCv(cvLang === 'pt' ? 'en' : 'pt'); });

  /* ---------- botões magnéticos (ponteiro fino, sem reduced motion) ---------- */
  if (fine.matches && !reduce.matches) {
    d.querySelectorAll('.hero-actions .btn, .ctrl, .form .btn').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.18, y = (e.clientY - r.top - r.height / 2) * 0.28;
        b.style.translate = x.toFixed(1) + 'px ' + y.toFixed(1) + 'px';
      });
      b.addEventListener('pointerleave', function () { b.style.translate = ''; });
    });
  }

  /* ---------- hora local de Juiz de Fora ---------- */
  var clock = d.getElementById('local-time');
  function tickClock() {
    try {
      var t = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' }).format(new Date());
      clock.textContent = t; clock.setAttribute('datetime', t);
    } catch (e) { clock.parentNode.parentNode && (clock.textContent = ''); }
  }
  if (clock) { tickClock(); setInterval(tickClock, 15000); }

  /* ---------- formulário ---------- */
  var form = d.getElementById('contact-form'), submit = d.getElementById('submit-btn');
  if (form) form.addEventListener('submit', function () {
    submit.disabled = true;
    submit.querySelector('span').textContent = lang === 'pt' ? 'Enviando…' : 'Sending…';
  });
})();
