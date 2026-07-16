/* ============================================================
   LANGUAGE
   ============================================================ */
let currentLang = 'pt';

function toggleLanguage() {
  currentLang = currentLang === 'pt' ? 'en' : 'pt';
  document.documentElement.lang = currentLang === 'pt' ? 'pt-BR' : 'en';
  document.getElementById('lang-label').innerText = currentLang === 'pt' ? 'EN' : 'PT';

  const inline = ['A','BUTTON','SPAN','P','H1','H2','H3','H4','H5','LABEL'];
  document.querySelectorAll('[data-pt]').forEach(el => {
    const text = el.getAttribute(`data-${currentLang}`);
    if (text && inline.includes(el.tagName)) el.innerText = text;
  });

  if (window.typedInstance) window.typedInstance.destroy();
  initTyped();
  localStorage.setItem('preferredLang', currentLang);
}

/* ============================================================
   TYPED.JS
   ============================================================ */
function initTyped() {
  const strings = currentLang === 'pt'
    ? ['Desenvolvedor Backend', 'Automação & Agentes de IA', 'Python · FastAPI · LLMs', 'Orquestração Inteligente']
    : ['Backend Developer', 'Automation & AI Agents', 'Python · FastAPI · LLMs', 'Intelligent Orchestration'];

  window.typedInstance = new Typed('#typed', {
    strings,
    typeSpeed: 60,
    backSpeed: 40,
    loop: true,
    showCursor: true,
    cursorChar: '_'
  });
}

/* ============================================================
   CV MODAL
   ============================================================ */
function openCvModal() {
  const modal = document.getElementById('cv-modal');
  const frame = document.getElementById('cv-frame');
  if (!frame.getAttribute('src')) frame.setAttribute('src', 'JonasAugusto_cv_m.pdf');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeCvModal() {
  document.getElementById('cv-modal').classList.add('hidden');
  document.body.style.overflow = '';
}

function openF5Modal() {
  document.getElementById('f5-modal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeF5Modal() {
  document.getElementById('f5-modal').classList.add('hidden');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeCvModal();
    closeF5Modal();
  }
});

/* ============================================================
   DOM READY
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

  /* AOS */
  AOS.init({ duration: 820, once: true, easing: 'ease-out' });

  /* Language init */
  const savedLang = localStorage.getItem('preferredLang');
  if (savedLang && savedLang !== currentLang) {
    toggleLanguage();
  } else {
    initTyped();
  }

  /* Mobile menu */
  const menuBtn = document.getElementById('mobile-menu-button');
  const menu    = document.getElementById('mobile-menu');
  menuBtn?.addEventListener('click', () => menu.classList.toggle('hidden'));
  document.querySelectorAll('.mobile-link').forEach(link =>
    link.addEventListener('click', () => menu.classList.add('hidden'))
  );

  /* Back to top */
  const backToTop = document.getElementById('back-to-top');
  window.addEventListener('scroll', () =>
    backToTop.classList.toggle('visible', window.scrollY > 400)
  );
  backToTop?.addEventListener('click', () =>
    window.scrollTo({ top: 0, behavior: 'smooth' })
  );

  /* Contact form loading state */
  const form      = document.getElementById('contact-form');
  const submitBtn = document.getElementById('submit-btn');
  form?.addEventListener('submit', () => {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="bi bi-arrow-repeat animate-spin"></i> <span>${currentLang === 'pt' ? 'Enviando...' : 'Sending...'}</span>`;
  });
});
