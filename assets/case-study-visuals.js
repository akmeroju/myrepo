/* Figma-style pan/zoom for case study Visuals section */
(function () {
  const viewport = document.getElementById('visualsViewport');
  const canvas = document.getElementById('visualsCanvas');
  const image = document.getElementById('visualsImage');
  const tabs = document.querySelectorAll('.visuals-tab');
  const zoomIn = document.getElementById('visualsZoomIn');
  const zoomOut = document.getElementById('visualsZoomOut');
  const zoomReset = document.getElementById('visualsZoomReset');

  if (!viewport || !canvas || !image) return;

  let activeTab = tabs[0] || null;

  let scale = 1;
  let panX = 0;
  let panY = 0;
  let dragging = false;
  let startX = 0;
  let startY = 0;
  let startPanX = 0;
  let startPanY = 0;

  function clampScale(value) {
    return Math.min(3, Math.max(0.25, value));
  }

  function applyTransform() {
    canvas.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
  }

  function centerView() {
    const vw = viewport.clientWidth;
    const vh = viewport.clientHeight;
    const iw = image.naturalWidth || image.width;
    const ih = image.naturalHeight || image.height;
    if (!iw || !ih) return;
    scale = clampScale(Math.min(vw / iw, vh / ih) * 0.92);
    panX = (vw - iw * scale) / 2;
    panY = 24;
    applyTransform();
  }

  function resetView() {
    centerView();
  }

  function setImageSrc(src, alt) {
    if (!src) return;
    image.src = src;
    image.alt = alt || '';
  }

  image.addEventListener('load', resetView);
  if (image.complete) resetView();

  viewport.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    dragging = true;
    viewport.classList.add('is-dragging');
    startX = e.clientX;
    startY = e.clientY;
    startPanX = panX;
    startPanY = panY;
    viewport.setPointerCapture(e.pointerId);
  });

  viewport.addEventListener('pointermove', e => {
    if (!dragging) return;
    panX = startPanX + (e.clientX - startX);
    panY = startPanY + (e.clientY - startY);
    applyTransform();
  });

  viewport.addEventListener('pointerup', e => {
    dragging = false;
    viewport.classList.remove('is-dragging');
    try { viewport.releasePointerCapture(e.pointerId); } catch (_) { /* noop */ }
  });

  viewport.addEventListener('pointercancel', () => {
    dragging = false;
    viewport.classList.remove('is-dragging');
  });

  viewport.addEventListener('wheel', e => {
    e.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const prevScale = scale;
    const delta = e.deltaY > 0 ? 0.92 : 1.08;
    scale = clampScale(scale * delta);
    panX = mx - (mx - panX) * (scale / prevScale);
    panY = my - (my - panY) * (scale / prevScale);
    applyTransform();
  }, { passive: false });

  viewport.addEventListener('dblclick', resetView);

  zoomIn?.addEventListener('click', () => {
    scale = clampScale(scale * 1.15);
    applyTransform();
  });

  zoomOut?.addEventListener('click', () => {
    scale = clampScale(scale / 1.15);
    applyTransform();
  });

  zoomReset?.addEventListener('click', resetView);

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeTab = tab;
      if (tab.dataset.src) {
        setImageSrc(tab.dataset.src, tab.textContent.trim());
      }
    });
  });

  window.addEventListener('resize', resetView);
})();
