/* Subtle mouse-follow ambient glows on case study pages */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const body = document.body;
  if (!body.classList.contains('case-study-page')) return;

  /* ── Global cursor-following layer (behind page content) ── */
  const globalLayer = document.createElement('div');
  globalLayer.className = 'ambient-global';
  globalLayer.setAttribute('aria-hidden', 'true');
  globalLayer.innerHTML = [
    '<div class="ambient-orb ambient-global-a"></div>',
    '<div class="ambient-orb ambient-global-b"></div>',
    '<div class="ambient-orb ambient-global-c"></div>',
  ].join('');
  body.insertBefore(globalLayer, body.firstChild);

  const globalOrbs = globalLayer.querySelectorAll('.ambient-orb');
  const globalOffsets = [
    { x: -140, y: -100 },
    { x: 120, y: 80 },
    { x: 0, y: 40 },
  ];
  let mouseX = window.innerWidth * 0.5;
  let mouseY = window.innerHeight * 0.4;
  const globalPos = globalOffsets.map(() => ({ x: mouseX, y: mouseY }));

  /* ── Per-section orbs (hero excluded — fixed .glow gradient on far right) ── */
  const sections = Array.from(document.querySelectorAll('[data-ambient]:not(.hero)'));
  const sectionStates = sections.map((section, i) => {
    const colors = ['ambient-orb-violet', 'ambient-orb-coral', 'ambient-orb-mint'];
    const orbA = document.createElement('div');
    const orbB = document.createElement('div');
    orbA.className = `ambient-orb ${colors[i % 3]}`;
    orbB.className = `ambient-orb ${colors[(i + 1) % 3]}`;
    section.insertBefore(orbB, section.firstChild);
    section.insertBefore(orbA, section.firstChild);

    return {
      section,
      orbs: [orbA, orbB],
      tx: [0, 0],
      ty: [0, 0],
      cx: [0, 0],
      cy: [0, 0],
      active: false,
    };
  });

  function updatePointer(clientX, clientY) {
    mouseX = clientX;
    mouseY = clientY;
    globalLayer.classList.add('is-active');

    const hero = document.querySelector('.hero');
    if (hero) {
      const hr = hero.getBoundingClientRect();
      const inHero =
        clientX >= hr.left &&
        clientX <= hr.right &&
        clientY >= hr.top &&
        clientY <= hr.bottom;
      globalLayer.classList.toggle('is-hero-active', inHero);
    }

    sectionStates.forEach(state => {
      const r = state.section.getBoundingClientRect();
      const inside =
        clientX >= r.left &&
        clientX <= r.right &&
        clientY >= r.top &&
        clientY <= r.bottom;

      if (inside) {
        const x = clientX - r.left;
        const y = clientY - r.top;
        if (!state.active) {
          state.active = true;
          state.section.classList.add('ambient-active');
          state.tx = [x - 60, x + 90];
          state.ty = [y - 60, y + 40];
        }
        state.cx[0] = x - 60;
        state.cy[0] = y - 60;
        state.cx[1] = x + 90;
        state.cy[1] = y + 40;
      } else if (state.active) {
        state.active = false;
        state.section.classList.remove('ambient-active');
      }
    });
  }

  document.addEventListener('mousemove', e => {
    updatePointer(e.clientX, e.clientY);
  }, { passive: true });

  document.documentElement.addEventListener('mouseleave', () => {
    globalLayer.classList.remove('is-active');
    globalLayer.classList.remove('is-hero-active');
    sectionStates.forEach(state => {
      state.active = false;
      state.section.classList.remove('ambient-active');
    });
  });

  function tick() {
    globalOrbs.forEach((orb, i) => {
      const targetX = mouseX + globalOffsets[i].x;
      const targetY = mouseY + globalOffsets[i].y;
      globalPos[i].x += (targetX - globalPos[i].x) * 0.08;
      globalPos[i].y += (targetY - globalPos[i].y) * 0.08;
      orb.style.transform = `translate3d(${globalPos[i].x}px, ${globalPos[i].y}px, 0)`;
    });

    sectionStates.forEach(state => {
      if (!state.active) return;
      state.orbs.forEach((orb, j) => {
        state.tx[j] += (state.cx[j] - state.tx[j]) * 0.12;
        state.ty[j] += (state.cy[j] - state.ty[j]) * 0.12;
        orb.style.transform = `translate3d(${state.tx[j]}px, ${state.ty[j]}px, 0)`;
      });
    });

    requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
})();
