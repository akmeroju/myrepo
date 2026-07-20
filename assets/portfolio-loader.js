(function initPortfolioLoader() {
  const LOADER_KEY = 'akm_portfolio_loaded';
  const FRAMES_URL = 'assets/portfolio.frames.js';
  const APP_URL = 'assets/portfolio.js';
  const THUMBS = [
    'assets/media/work/acko-website-design.png',
    'assets/media/work/adsc-thumbnail.png',
    'assets/media/work/petbuddy-thumbnail.png',
  ];
  const HOLD_AT_100_MS = 480;

  const loader = document.getElementById('page-loader');
  if (!loader) return;

  const bar = loader.querySelector('.loader-bar');
  const pctEl = loader.querySelector('.loader-pct');
  const cur = document.getElementById('cursor');
  const ring = document.getElementById('cursor-ring');
  let finished = false;
  let displayPct = 0;

  const milestones = {
    dom: { weight: 4, done: false, partial: 0 },
    css: { weight: 6, done: false, partial: 0 },
    fonts: { weight: 8, done: false, partial: 0 },
    framesDownload: { weight: 38, done: false, partial: 0 },
    framesParse: { weight: 14, done: false, partial: 0 },
    heroFrame: { weight: 10, done: false, partial: 0 },
    thumbs: { weight: 12, done: false, partial: 0 },
    appJs: { weight: 5, done: false, partial: 0 },
    ready: { weight: 3, done: false, partial: 0 },
  };

  const markLoaderDone = () => {
    window.__portfolioLoaderDone = true;
    window.dispatchEvent(new CustomEvent('portfolio:loader-done'));
  };

  const paint = pct => {
    displayPct = Math.min(100, Math.max(displayPct, Math.round(pct)));
    if (bar) bar.style.width = displayPct + '%';
    if (pctEl) pctEl.textContent = displayPct + '%';
  };

  const recalc = () => {
    let pct = 0;
    Object.values(milestones).forEach(m => {
      pct += m.done ? m.weight : m.weight * (m.partial || 0);
    });
    paint(Math.min(99, pct));
  };

  const setPartial = (key, fraction) => {
    const m = milestones[key];
    if (!m || m.done) return;
    m.partial = Math.max(0, Math.min(1, fraction));
    recalc();
  };

  const complete = key => {
    const m = milestones[key];
    if (!m) return;
    m.done = true;
    m.partial = 1;
    recalc();
  };

  const loadScript = src => new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.body.appendChild(script);
  });

  const waitForCSS = () => new Promise(resolve => {
    const link = document.querySelector('link[href*="portfolio.css"]');
    if (!link) {
      resolve();
      return;
    }
    if (link.sheet) {
      resolve();
      return;
    }
    link.addEventListener('load', () => resolve(), { once: true });
    link.addEventListener('error', () => resolve(), { once: true });
  });

  const waitForFonts = () => {
    if (!document.fonts?.ready) return Promise.resolve();
    return Promise.race([
      document.fonts.ready,
      new Promise(resolve => window.setTimeout(resolve, 5000)),
    ]);
  };

  const waitForImage = src => new Promise(resolve => {
    if (!src) {
      resolve();
      return;
    }
    const img = new Image();
    img.onload = img.onerror = () => resolve();
    img.src = src;
  });

  const fetchFramesWithProgress = async () => {
    const response = await fetch(FRAMES_URL, { cache: 'force-cache' });
    if (!response.ok) throw new Error('Frames fetch failed');

    const total = Number(response.headers.get('content-length')) || 0;

    if (!response.body || !total) {
      const code = await response.text();
      complete('framesDownload');
      await executeFramesCode(code);
      return;
    }

    const reader = response.body.getReader();
    const chunks = [];
    let loaded = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      loaded += value.length;
      setPartial('framesDownload', loaded / total);
    }

    complete('framesDownload');

    const blob = new Blob(chunks, { type: 'application/javascript' });
    const blobUrl = URL.createObjectURL(blob);

    let parsePartial = 0;
    const parseTimer = window.setInterval(() => {
      parsePartial = Math.min(0.92, parsePartial + 0.04);
      setPartial('framesParse', parsePartial);
    }, 40);

    await new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = blobUrl;
      script.onload = () => {
        window.clearInterval(parseTimer);
        URL.revokeObjectURL(blobUrl);
        resolve();
      };
      script.onerror = () => {
        window.clearInterval(parseTimer);
        URL.revokeObjectURL(blobUrl);
        reject(new Error('Frames parse failed'));
      };
      document.body.appendChild(script);
    });

    complete('framesParse');
  };

  const executeFramesCode = code => new Promise((resolve, reject) => {
    let parsePartial = 0;
    const parseTimer = window.setInterval(() => {
      parsePartial = Math.min(0.92, parsePartial + 0.04);
      setPartial('framesParse', parsePartial);
    }, 40);

    const blob = new Blob([code], { type: 'application/javascript' });
    const blobUrl = URL.createObjectURL(blob);
    const script = document.createElement('script');
    script.src = blobUrl;
    script.onload = () => {
      window.clearInterval(parseTimer);
      URL.revokeObjectURL(blobUrl);
      complete('framesParse');
      resolve();
    };
    script.onerror = () => {
      window.clearInterval(parseTimer);
      URL.revokeObjectURL(blobUrl);
      reject(new Error('Frames parse failed'));
    };
    document.body.appendChild(script);
  });

  const loadThumbnails = async () => {
    let done = 0;
    await Promise.all(THUMBS.map(src => waitForImage(src).then(() => {
      done += 1;
      setPartial('thumbs', done / THUMBS.length);
    })));
    complete('thumbs');
  };

  const finish = () => {
    if (finished) return;
    finished = true;
    paint(100);

    window.setTimeout(() => {
      sessionStorage.setItem(LOADER_KEY, '1');
      loader.classList.add('is-done');
      document.body.classList.remove('is-loading');
      const canvasEl = document.getElementById('hero-canvas');
      if (canvasEl && window.FRAMES?.[0]) canvasEl.src = window.FRAMES[0];
      markLoaderDone();
      window.setTimeout(() => loader.remove(), 600);
    }, HOLD_AT_100_MS);
  };

  const runFastPath = async () => {
    loader.remove();
    document.body.classList.remove('is-loading');
    if (!window.FRAMES?.length) await loadScript(FRAMES_URL);
    if (!window.__portfolioAppLoaded) await loadScript(APP_URL);
    markLoaderDone();
  };

  const runFullLoader = async () => {
    document.body.classList.add('is-loading');

    if (cur && ring) {
      document.addEventListener('mousemove', e => {
        cur.style.left = e.clientX + 'px';
        cur.style.top = e.clientY + 'px';
        ring.style.left = e.clientX + 'px';
        ring.style.top = e.clientY + 'px';
      });
    }

    complete('dom');
    paint(2);

    await Promise.all([
      waitForCSS().then(() => complete('css')),
      waitForFonts().then(() => complete('fonts')),
    ]);

    await fetchFramesWithProgress();

    if (window.FRAMES?.[0]) {
      await waitForImage(window.FRAMES[0]);
    }
    complete('heroFrame');

    await loadThumbnails();

    await loadScript(APP_URL);
    window.__portfolioAppLoaded = true;
    complete('appJs');

    if (document.readyState === 'complete') {
      complete('ready');
    } else {
      await new Promise(resolve => {
        window.addEventListener('load', () => {
          complete('ready');
          resolve();
        }, { once: true });
      });
    }

    paint(100);
    finish();
  };

  if (sessionStorage.getItem(LOADER_KEY)) {
    runFastPath().catch(() => {
      loadScript(FRAMES_URL)
        .then(() => loadScript(APP_URL))
        .then(markLoaderDone);
    });
    return;
  }

  runFullLoader().catch(() => {
    paint(100);
    loadScript(FRAMES_URL)
      .then(() => loadScript(APP_URL))
      .then(() => finish());
  });

  window.setTimeout(() => {
    if (!finished) {
      paint(100);
      finish();
    }
  }, 30000);
})();
