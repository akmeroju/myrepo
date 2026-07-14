const N = FRAMES.length;
const imgs = FRAMES.map(src => { const im = new Image(); im.src = src; return im; });

// ── INSTANT HASH SCROLL (back links to #work) ──
(function instantHashScroll() {
  const hash = window.location.hash;
  if (!hash) return;
  const target = document.querySelector(hash);
  if (!target) return;

  history.scrollRestoration = 'manual';
  document.documentElement.style.scrollBehavior = 'auto';
  requestAnimationFrame(() => {
    target.scrollIntoView({ block: 'start' });
    window.setTimeout(() => {
      document.documentElement.style.scrollBehavior = '';
    }, 0);
  });
})();

// ── ELEMENTS ──
const heroSec   = document.getElementById('hero-scroll');
const canvas    = document.getElementById('hero-canvas');
const introText = document.getElementById('intro-text');
const stageLay  = document.getElementById('stage-layer');
const navEl     = document.getElementById('nav');
const cards     = [0,1,2,3].map(i => document.getElementById('sc-'+i));
const dots      = [0,1,2,3].map(i => document.getElementById('dot-'+i));

// Scroll phases (progress 0→1)
const INTRO_EXIT_START = 0.08;
const INTRO_EXIT_END   = 0.16;
const FRAMES_START     = 0.16;
const STAGE_BREAKS     = [0, 11, 28, 42];

let introGone = false, activeCard = -1;
let dispFrame = 0, tgtFrame = 0, rafId = null, lastFi = -1;

function setCard(idx) {
  if (activeCard === idx) return;
  if (activeCard >= 0) {
    cards[activeCard].classList.remove('visible');
    cards[activeCard].classList.add('exit');
    const prev = activeCard;
    setTimeout(() => cards[prev] && cards[prev].classList.remove('exit'), 450);
  }
  activeCard = idx;
  if (idx >= 0) {
    cards[idx].classList.remove('exit');
    requestAnimationFrame(() => cards[idx].classList.add('visible'));
    dots.forEach((d, i) => d.classList.toggle('on', i === idx));
  }
}

function tick() {
  const diff = tgtFrame - dispFrame;
  if (Math.abs(diff) < 0.01) { dispFrame = tgtFrame; rafId = null; return; }
  dispFrame += diff * 0.07;
  const fi = Math.min(N-1, Math.max(0, Math.round(dispFrame)));
  if (fi !== lastFi) { canvas.src = imgs[fi].src; lastFi = fi; }
  rafId = requestAnimationFrame(tick);
}

function onScroll() {
  const rect = heroSec.getBoundingClientRect();
  const p = Math.max(0, Math.min(1, -rect.top / (heroSec.offsetHeight - window.innerHeight)));

  navEl.classList.toggle('solid', p > 0.01 || window.scrollY > window.innerHeight);

  if (p < INTRO_EXIT_START) {
    if (introGone) {
      introGone = false;
      introText.classList.remove('gone');
      stageLay.classList.remove('active');
      setCard(-1);
    }
    introText.style.opacity = '';
    introText.style.transform = '';
  } else if (p < INTRO_EXIT_END) {
    const t = (p - INTRO_EXIT_START) / (INTRO_EXIT_END - INTRO_EXIT_START);
    introText.style.transition = 'none';
    introText.style.opacity    = (1 - t).toString();
    introText.style.transform  = `translateY(${-t * 70}px) scale(${1 - t * 0.04})`;
  } else {
    if (!introGone) {
      introGone = true;
      introText.classList.add('gone');
      stageLay.classList.add('active');
    }
    const fp = (p - FRAMES_START) / (1 - FRAMES_START);
    tgtFrame = Math.max(0, Math.min(N-1, fp * (N-1)));
    const fi = Math.round(tgtFrame);
    let card = 0;
    if (fi >= STAGE_BREAKS[3]) card = 3;
    else if (fi >= STAGE_BREAKS[2]) card = 2;
    else if (fi >= STAGE_BREAKS[1]) card = 1;
    setCard(card);
    if (!rafId) rafId = requestAnimationFrame(tick);
  }
}

canvas.src = imgs[0].src;
window.addEventListener('scroll', onScroll, { passive: true });

// Nav solid when scrolled past hero
window.addEventListener('scroll', () => {
  if (window.scrollY > window.innerHeight * 0.5)
    navEl.classList.add('solid');
}, { passive: true });

// ── SCROLL REVEAL ──
const revObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); revObs.unobserve(e.target); }});
}, { threshold: 0.05, rootMargin: '0px 0px 60px 0px' });
document.querySelectorAll('[data-a]').forEach(el => revObs.observe(el));

// ── ABOUT SCROLL HIGHLIGHT ──
function initAboutScrollHighlight() {
  const blocks = document.querySelectorAll('.about-typewriter');
  if (!blocks.length) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const allWords = [];

  blocks.forEach(block => {
    const words = block.textContent.trim().split(/\s+/).filter(Boolean);
    block.textContent = '';
    words.forEach((word, i) => {
      const span = document.createElement('span');
      span.className = prefersReduced ? 'tw-word is-typed' : 'tw-word';
      span.textContent = word;
      block.appendChild(span);
      if (i < words.length - 1) block.appendChild(document.createTextNode(' '));
      allWords.push(span);
    });
    if (prefersReduced) block.classList.add('is-done');
  });

  if (prefersReduced) return;

  const update = () => {
    const trigger = window.innerHeight * 0.72;
    allWords.forEach(span => {
      span.classList.toggle('is-typed', span.getBoundingClientRect().top < trigger);
    });
  };

  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
}

initAboutScrollHighlight();

// ── CUSTOM CURSOR (mix-blend-mode:difference handles color inversion automatically) ──
const cur   = document.getElementById('cursor');
const ring  = document.getElementById('cursor-ring');
let mx=0, my=0, rx=0, ry=0;

document.addEventListener('mousemove', e => {
  mx = e.clientX; my = e.clientY;
  cur.style.left = mx + 'px';
  cur.style.top  = my + 'px';
});

// Ring lags behind
(function animRing() {
  rx += (mx - rx) * 0.1;
  ry += (my - ry) * 0.1;
  ring.style.left = rx + 'px';
  ring.style.top  = ry + 'px';
  requestAnimationFrame(animRing);
})();

// Expand cursor on interactive elements
document.querySelectorAll('a, button, .wcard, .skill-tag').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cur.style.width  = '20px';
    cur.style.height = '20px';
    ring.style.width  = '56px';
    ring.style.height = '56px';
  });
  el.addEventListener('mouseleave', () => {
    cur.style.width  = '12px';
    cur.style.height = '12px';
    ring.style.width  = '40px';
    ring.style.height = '40px';
  });
});

// ── GALLERY CAROUSEL handled in media loader below

// ── SCROLL PROGRESS BAR ──
const progressBar = document.getElementById('progress-bar');
function updateProgress() {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  progressBar.style.width = (scrollTop / docHeight * 100) + '%';
}
window.addEventListener('scroll', updateProgress, { passive: true });

// ── MOBILE NAV ──
const hamburger = document.getElementById('hamburger');
const mobileNav = document.getElementById('mobile-nav');
hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  mobileNav.classList.toggle('open');
  document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
});
document.querySelectorAll('.mobile-nav a').forEach(a => {
  a.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileNav.classList.remove('open');
    document.body.style.overflow = '';
  });
});

// ── ACTIVE NAV SECTION ──
const navSections = ['about','work','visuals','skills','experience','contact'];
const navAnchors = {};
navSections.forEach(id => {
  const a = document.querySelector(`.nav-links a[href="#${id}"]`);
  if (a) navAnchors[id] = a;
});
const secObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting && navAnchors[e.target.id]) {
      Object.values(navAnchors).forEach(a => a.classList.remove('nav-active'));
      navAnchors[e.target.id].classList.add('nav-active');
    }
  });
}, { threshold: 0.25 });
navSections.forEach(id => { const el = document.getElementById(id); if (el) secObs.observe(el); });



// ── MAGNETIC BUTTONS ──
document.querySelectorAll('.contact-btn, .nav-cta').forEach(btn => {
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

// ── BACK TO TOP ──
const backTop = document.getElementById('back-top');
window.addEventListener('scroll', () => {
  backTop.classList.toggle('visible', window.scrollY > window.innerHeight);
}, { passive: true });
backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));


// ── HERO SCROLL CURSOR LABEL ─────────────────────────────────────────────
const cursorLabel = document.getElementById('cursor-label');
const heroSticky = document.querySelector('.hero-sticky');
if (cursorLabel) {
  document.addEventListener('mousemove', e => {
    cursorLabel.style.left = e.clientX + 'px';
    cursorLabel.style.top  = e.clientY + 'px';
    const overHeader = e.clientY <= 64 || !!e.target.closest('#nav');
    document.body.classList.toggle('nav-hover', overHeader);
  });
}
if (cursorLabel && heroSticky) {
  const heroObs = new IntersectionObserver(([entry]) => {
    document.body.classList.toggle('hero-active', entry.isIntersecting);
  }, { threshold: 0.4 });
  heroObs.observe(heroSticky);
}
// ── EXPERIENCE ACCORDION ─────────────────────────────────────────────────
document.querySelectorAll('.exp-item').forEach((item, i) => {
  const btn = item.querySelector('.exp-toggle-row');
  if (!btn) return;
  if (i === 0) { item.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); }
  btn.addEventListener('click', () => {
    const open = item.classList.contains('is-open');
    document.querySelectorAll('.exp-item').forEach(el => {
      el.classList.remove('is-open');
      el.querySelector('.exp-toggle-row')?.setAttribute('aria-expanded', 'false');
    });
    if (!open) {
      item.classList.add('is-open');
      btn.setAttribute('aria-expanded', 'true');
    }
  });
});
// ── IMAGE FOLDER SCANNER ─────────────────────────────────────────────────
async function imageExists(url) {
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url + '?t=' + Date.now();
  });
}

async function scanFolder(base, max = 24) {
  const exts = ['jpg', 'jpeg', 'png', 'webp'];
  const found = [];
  for (let i = 1; i <= max; i++) {
    const names = [String(i).padStart(2, '0'), String(i)];
    let matched = false;
    for (const num of names) {
      for (const ext of exts) {
        const url = `${base}/${num}.${ext}`;
        if (await imageExists(url)) { found.push(url); matched = true; break; }
      }
      if (matched) break;
    }
  }
  return found;
}

function buildVisualsMarquee(track, urls) {
  track.innerHTML = '';
  const items = urls.map((src, i) => {
    const item = document.createElement('div');
    item.className = 'visuals-marquee-item';
    item.innerHTML = `<img src="${src}" alt="Visual craft frame ${i + 1}" loading="lazy" decoding="async">`;
    return item;
  });
  items.forEach(item => track.appendChild(item));
  items.forEach(item => track.appendChild(item.cloneNode(true)));
  const duration = Math.max(28, urls.length * 7);
  track.style.setProperty('--visuals-duration', `${duration}s`);
}

async function scanFolders(bases) {
  const all = [];
  for (const b of bases) all.push(...(await scanFolder(b)));
  return all;
}

function buildSlides(track, urls, captionPrefix = '') {
  track.innerHTML = '';
  urls.forEach((src, i) => {
    const slide = document.createElement('div');
    slide.className = 'gallery-slide';
    const cap = captionPrefix ? `${captionPrefix} ${String(i + 1).padStart(2, '0')}` : `Slide ${i + 1}`;
    slide.innerHTML = `<img src="${src}" alt="${cap}" loading="lazy"><div class="gallery-slide-caption">${cap}</div>`;
    track.appendChild(slide);
  });
}

function initCarousel({ trackId, dotsId, prevId, nextId, controlsId, autoplay = false, interval = 5500 }) {
  const track = document.getElementById(trackId);
  if (!track) return null;
  const dotsEl = document.getElementById(dotsId);
  const prev = document.getElementById(prevId);
  const next = document.getElementById(nextId);
  const controls = controlsId ? document.getElementById(controlsId) : null;
  let current = 0;
  let timer = null;

  function refresh() {
    const slides = track.querySelectorAll('.gallery-slide');
    const total = slides.length;
    if (!total) return null;
    if (controls) controls.style.display = total > 1 ? 'flex' : 'none';
    if (dotsEl) {
      dotsEl.innerHTML = '';
      slides.forEach((_, i) => {
        const d = document.createElement('div');
        d.className = 'gdot' + (i === current ? ' on' : '');
        d.addEventListener('click', () => goTo(i));
        dotsEl.appendChild(d);
      });
    }
    return total;
  }

  function goTo(idx) {
    const slides = track.querySelectorAll('.gallery-slide');
    const total = slides.length;
    if (!total) return;
    current = (idx + total) % total;
    const viewport = track.parentElement || track;
    const slideW = viewport.offsetWidth || track.offsetWidth;
    track.style.transform = slideW ? `translateX(-${current * slideW}px)` : `translateX(-${current * 100}%)`;
    track.style.display = 'flex';
    slides.forEach(s => { s.style.flex = '0 0 100%'; s.style.minWidth = '100%'; });
    dotsEl?.querySelectorAll('.gdot').forEach((d, i) => d.classList.toggle('on', i === current));
  }

  function startAutoplay() {
    if (!autoplay) return;
    stopAutoplay();
    timer = setInterval(() => goTo(current + 1), interval);
  }
  function stopAutoplay() {
    if (timer) { clearInterval(timer); timer = null; }
  }

  prev?.addEventListener('click', () => { goTo(current - 1); startAutoplay(); });
  next?.addEventListener('click', () => { goTo(current + 1); startAutoplay(); });
  const pauseEl = track.closest('.ach-carousel-wrap, .gallery-wrap') || track;
  pauseEl?.addEventListener('mouseenter', stopAutoplay);
  pauseEl?.addEventListener('mouseleave', startAutoplay);

  startAutoplay();
  return { refresh, goTo, startAutoplay, stopAutoplay, get current() { return current; } };
}

window.beyondCarousel = null;

(async () => {
  const track = document.getElementById('visuals-track');
  const ph = document.getElementById('visuals-placeholder');
  if (!track) return;
  const urls = await scanFolder('assets/media/visuals', 48);
  if (urls.length) {
    if (ph) ph.remove();
    buildVisualsMarquee(track, urls);
  }
})();

(async () => {
  const track = document.getElementById('ach-track');
  if (!track) return;
  let urls = await scanFolder('assets/media/recognition');
  if (!urls.length) {
    track.querySelectorAll('img[data-fallback]').forEach(img => { if (img.src) urls.push(img.src); });
    urls = [...new Set(urls)];
  }
  if (urls.length) {
    buildSlides(track, urls, 'Recognition');
    const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next', autoplay: true, interval: 5500 });
    window.achCarousel = car;
    car?.refresh(); car?.goTo(0); car?.startAutoplay();
  }
})();

const BEYOND_MAP = {
  gaming: ['assets/media/beyond/gaming'],
  'content-creation': ['assets/media/beyond/content-creation/photography','assets/media/beyond/content-creation/videography','assets/media/beyond/content-creation/dop'],
  'creative-works': ['assets/media/beyond/creative-works/movies','assets/media/beyond/creative-works/short-films','assets/media/beyond/creative-works/publicity','assets/media/beyond/creative-works/logos','assets/media/beyond/creative-works/flyers'],
  roadtrips: ['assets/media/beyond/roadtrips']
};

(async () => {
  const items = document.querySelectorAll('.interest-item[data-category]');
  const track = document.getElementById('gallery-track');
  const gControls = document.querySelector('#beyond .gallery-controls');
  if (!items.length || !track) return;

  async function loadCategory(cat) {
    let urls = await scanFolders(BEYOND_MAP[cat] || []);
    if (!urls.length && track.dataset.fallback) urls = JSON.parse(track.dataset.fallback);
    if (!urls.length) return;
    buildSlides(track, urls, cat.replace(/-/g, ' '));
    if (gControls) gControls.style.display = urls.length > 1 ? 'flex' : 'none';
    window.beyondCarousel = initCarousel({ trackId: 'gallery-track', dotsId: 'gallery-dots', prevId: 'g-prev', nextId: 'g-next' });
    window.beyondCarousel?.refresh();
    window.beyondCarousel?.goTo(0);
  }

  items.forEach((item, i) => {
    if (i === 0) item.classList.add('is-active');
    item.addEventListener('click', () => {
      items.forEach(el => el.classList.remove('is-active'));
      item.classList.add('is-active');
      loadCategory(item.dataset.category);
    });
  });
  loadCategory(items[0].dataset.category);
})();


// Contact section reveal
const contactSection = document.getElementById('contact');
if(contactSection){
  const contactObs = new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting) { contactSection.classList.add('revealed'); contactObs.disconnect(); }
    });
  },{threshold:0.05});
  contactObs.observe(contactSection);
}

// ── NDA MODAL (Enterprise Portal) ──
function openNdaModal() {
  const modal = document.getElementById('nda-modal');
  if (!modal) return;
  modal.classList.add('is-open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  document.body.classList.add('nda-modal-open');
}

function closeNdaModal() {
  const modal = document.getElementById('nda-modal');
  if (!modal) return;
  modal.classList.remove('is-open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  document.body.classList.remove('nda-modal-open');
}

window.openNdaModal = openNdaModal;

document.querySelectorAll('[data-nda-close]').forEach(el => {
  el.addEventListener('click', closeNdaModal);
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeNdaModal();
});
