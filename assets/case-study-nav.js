/* Minimal portfolio chrome for case study pages (no hero frames bundle). */
const cur = document.getElementById('cursor');
const ring = document.getElementById('cursor-ring');
const navEl = document.getElementById('nav');
const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

if (cur && ring && finePointer) {
  document.addEventListener('mousemove', e => {
    const x = e.clientX;
    const y = e.clientY;
    cur.style.left = x + 'px';
    cur.style.top = y + 'px';
    ring.style.left = x + 'px';
    ring.style.top = y + 'px';
    const overHeader = e.clientY <= 64 || !!e.target.closest('#nav');
    document.body.classList.toggle('nav-hover', overHeader);
  });

  document.querySelectorAll('a, button, .carousel-dot, .reflect-row, .case-back-body, .visuals-tab, .visuals-zoom-btn, .live-link').forEach(el => {
    el.addEventListener('mouseenter', () => {
      cur.style.width = '20px';
      cur.style.height = '20px';
      ring.style.width = '56px';
      ring.style.height = '56px';
    });
    el.addEventListener('mouseleave', () => {
      cur.style.width = '12px';
      cur.style.height = '12px';
      ring.style.width = '40px';
      ring.style.height = '40px';
    });
  });
}

const progressBar = document.getElementById('progress-bar');
if (progressBar) {
  const updateProgress = () => {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    progressBar.style.width = docHeight > 0 ? (window.scrollY / docHeight * 100) + '%' : '0%';
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
}

if (navEl) {
  navEl.classList.add('solid');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 8) navEl.classList.add('solid');
  }, { passive: true });
}

const hamburger = document.getElementById('hamburger');
const mobileNav = document.getElementById('mobile-nav');
if (hamburger && mobileNav) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileNav.classList.toggle('open');
    document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
  });
  mobileNav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

if (finePointer) document.querySelectorAll('.nav-cta').forEach(btn => {
  btn.addEventListener('mousemove', e => {
    const r = btn.getBoundingClientRect();
    const x = (e.clientX - r.left - r.width / 2) * 0.28;
    const y = (e.clientY - r.top - r.height / 2) * 0.28;
    btn.style.transform = `translate(${x}px,${y}px)`;
    btn.style.transition = 'transform 0.1s ease';
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = '';
    btn.style.transition = 'transform 0.6s cubic-bezier(0.25,0.46,0.45,0.94)';
  });
});
