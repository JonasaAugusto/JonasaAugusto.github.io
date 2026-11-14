/* Jonas Augusto · portfólio. Sem dependências. Tema, menu móvel, diálogos. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  var lang = root.lang === 'en' ? 'en' : 'pt';
  var base = root.getAttribute('data-base') || '';
  /* O idioma é uma página estática por idioma (/ e /en/); o alternador é um link comum. */

  function withTransition(fn, ev) {
    if (!d.startViewTransition || reduce.matches) { fn(); return; }
    if (ev && ev.clientX !== undefined) {
      root.style.setProperty('--vx', ev.clientX + 'px');
      root.style.setProperty('--vy', ev.clientY + 'px');
    }
    d.startViewTransition(fn);
  }

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

  /* ---------- diálogos ---------- */
  var CV = {
    pt: { pdf: base + 'JonasAugusto_cv_m.pdf', page: base + 'cv.html', dl: 'JonasAugusto_CV_PT.pdf' },
    en: { pdf: base + 'JonasAugusto_cv_en.pdf', page: base + 'cv.en.html', dl: 'JonasAugusto_CV_EN.pdf' }
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
  function openDlg(id, anchor) {
    var dlg = d.getElementById(id); if (!dlg) return;
    lastFocus = d.activeElement;
    if (id === 'dlg-cv') setCv(cvLang || lang);
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    root.style.overflow = 'hidden';
    if (anchor) { var t = dlg.querySelector(anchor); if (t) t.scrollIntoView(); }
  }
  d.querySelectorAll('[data-open]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); openDlg('dlg-' + b.dataset.open, b.dataset.anchor); });
  });
  d.querySelectorAll('dialog').forEach(function (dlg) {
    dlg.addEventListener('close', function () { root.style.overflow = ''; if (lastFocus) lastFocus.focus(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelectorAll('[data-close]').forEach(function (b) { b.addEventListener('click', function () { dlg.close(); }); });
  });
  var cvLangBtn = d.getElementById('cv-lang-btn');
  if (cvLangBtn) cvLangBtn.addEventListener('click', function () { setCv(cvLang === 'pt' ? 'en' : 'pt'); });

})();
