#!/usr/bin/env python3
"""Apply all portfolio updates with integrity checks."""
import re
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "tools"))
from portfolio_guard import is_external_mode  # noqa: E402

if is_external_mode():
    sys.exit("BLOCKED: Portfolio is split. Edit assets/portfolio.css / portfolio.js instead.")

HTML = ROOT / "adithya_portfolio_v16_fixed.html"
RESUME = "https://drive.google.com/file/d/1DKPi8jJ2Ji4PxIV6TdTWAtyXx9faUarY/view?usp=drivesdk"

NEW_CSS = r"""
/* ── VISUALS SHOWCASE ── */
#visuals{background:var(--dark);padding:120px 56px;border-top:1px solid #111}
#visuals .sec-eyebrow{color:var(--gold)}
.visuals-header{margin-bottom:48px}
.visuals-h{font-size:clamp(2rem,4vw,3.5rem);font-weight:800;color:#fff;line-height:1.1;letter-spacing:-0.03em;margin-top:12px}
.visuals-carousel-wrap{max-width:1080px;margin:0 auto}
.visuals-track-wrap{overflow:hidden;border-radius:16px}
.visuals-track-wrap .gallery-track,.ach-carousel .gallery-track,#beyond .gallery-track{transition:transform 0.45s cubic-bezier(0.25,0.46,0.45,0.94)}
.visuals-placeholder{padding:80px 24px;text-align:center;color:#555;font-size:0.85rem;border:1px dashed #333;border-radius:16px}

/* ── ACHIEVEMENTS CAROUSEL ── */
.ach-carousel-wrap{position:relative}
.ach-carousel{position:relative;overflow:hidden;border-radius:4px;max-height:360px}
.ach-carousel-track{display:flex;transition:transform 0.45s cubic-bezier(0.25,0.46,0.45,0.94)}
.ach-slide{flex:0 0 100%;min-width:100%}
.ach-slide img{width:100%;height:360px;object-fit:cover;display:block;border-radius:4px}
.ach-carousel-dots{display:flex;gap:8px;justify-content:center;margin-top:16px}
.ach-dot,.ach-carousel-dots .gdot{width:6px;height:6px;border-radius:50%;background:#333;cursor:pointer;transition:background 0.2s,transform 0.2s}
.ach-dot.on,.ach-carousel-dots .gdot.on{background:var(--gold);transform:scale(1.4)}

/* ── EXP ACCORDION ── */
.exp-toggle-row{
  display:flex;align-items:center;justify-content:space-between;gap:16px;
  width:100%;background:none;border:none;padding:0;cursor:pointer;text-align:left;
  color:inherit;font-family:inherit;
}
.exp-toggle-info{flex:1}
.exp-chevron{
  flex-shrink:0;width:28px;height:28px;border:1px solid #333;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:0.55rem;color:var(--gold);transition:transform 0.3s ease;
}
.exp-item.is-open .exp-chevron{transform:rotate(180deg)}
.exp-details{max-height:0;overflow:hidden;transition:max-height 0.4s cubic-bezier(0.22,1,0.36,1)}
.exp-item.is-open .exp-details{max-height:1200px}
.exp-company-sub{color:#888;font-weight:400;text-transform:none;letter-spacing:0}
.exp-tags-wrap{margin-top:14px}

/* ── HERO SCROLL CURSOR ── */
#cursor-label{
  position:fixed;pointer-events:none;z-index:10000;
  font-size:0.58rem;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;
  color:#fff;opacity:0;transition:opacity 0.3s;white-space:nowrap;
  mix-blend-mode:difference;
}
body.hero-active #cursor-label{opacity:1}
body.hero-active #cursor,body.hero-active #cursor-ring{opacity:0}

/* ── INTEREST ACTIVE STATE ── */
.interest-item{cursor:pointer}
.interest-item.is-active{border-color:var(--gold);background:#fdf8ee}
"""

VISUALS_SECTION = """
<!-- ══ SELECTED FRAMES ══ -->
<section id="visuals">
  <div class="section-inner">
    <div class="visuals-header">
      <p class="sec-eyebrow" data-a="up">Visual Craft</p>
      <h2 class="visuals-h" data-a="up" data-d="1">Selected<br>Frames.</h2>
    </div>
    <div class="visuals-carousel-wrap" data-a="scale" data-d="2">
      <div class="visuals-track-wrap">
        <div class="gallery-track" id="visuals-track">
          <div class="visuals-placeholder" id="visuals-placeholder">Drop mockups &amp; screens into <code>assets/media/visuals/</code> as 01.jpg, 02.png …</div>
        </div>
      </div>
      <div class="gallery-controls" id="visuals-controls" style="display:none">
        <div class="gallery-dots" id="visuals-dots"></div>
        <div class="gallery-btns">
          <button class="gbtn" id="visuals-prev" aria-label="Previous"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg></button>
          <button class="gbtn" id="visuals-next" aria-label="Next"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg></button>
        </div>
      </div>
    </div>
  </div>
</section>

"""

BEYOND_INTERESTS = '''<div class="beyond-interests" data-a="up" data-d="1">
        <div class="interest-item" data-category="gaming">
          <div class="interest-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4M15 11h.01M18 13h.01"/></svg>
          </div>
          <div class="interest-text">
            <div class="interest-name">Gaming</div>
            <div class="interest-desc">Strategy, open-world, and competitive play.</div>
          </div>
        </div>
        <div class="interest-item" data-category="content-creation">
          <div class="interest-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
          </div>
          <div class="interest-text">
            <div class="interest-name">Content creation</div>
            <div class="interest-desc">Photography, videography, DOP.</div>
          </div>
        </div>
        <div class="interest-item" data-category="creative-works">
          <div class="interest-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7L12 16.8 5.7 21l2.3-7-6-4.6h7.6z"/></svg>
          </div>
          <div class="interest-text">
            <div class="interest-name">Creative works</div>
            <div class="interest-desc">Illustration, branding, and side projects.</div>
          </div>
        </div>
        <div class="interest-item" data-category="roadtrips">
          <div class="interest-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
          </div>
          <div class="interest-text">
            <div class="interest-name">Roadtrips</div>
            <div class="interest-desc">Mountains, highways, and new perspectives.</div>
          </div>
        </div>
      </div>
      '''

NEW_JS = r'''
// ── HERO SCROLL CURSOR LABEL ─────────────────────────────────────────────
const cursorLabel = document.getElementById('cursor-label');
const heroSection = document.getElementById('hero-scroll');
if (cursorLabel && heroSection) {
  document.addEventListener('mousemove', e => {
    cursorLabel.style.left = (e.clientX + 14) + 'px';
    cursorLabel.style.top  = (e.clientY - 10) + 'px';
  });
  const heroObs = new IntersectionObserver(([entry]) => {
    document.body.classList.toggle('hero-active', entry.isIntersecting);
  }, { threshold: 0.35 });
  heroObs.observe(heroSection);
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
    const num = String(i).padStart(2, '0');
    for (const ext of exts) {
      const url = `${base}/${num}.${ext}`;
      if (await imageExists(url)) { found.push(url); break; }
    }
  }
  return found;
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

function initCarousel({ trackId, dotsId, prevId, nextId, controlsId }) {
  const track = document.getElementById(trackId);
  if (!track) return null;
  const dotsEl = document.getElementById(dotsId);
  const prev = document.getElementById(prevId);
  const next = document.getElementById(nextId);
  const controls = controlsId ? document.getElementById(controlsId) : null;
  let current = 0;

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
    track.style.transform = `translateX(-${current * 100}%)`;
    track.style.display = 'flex';
    slides.forEach(s => { s.style.flex = '0 0 100%'; s.style.minWidth = '100%'; });
    dotsEl?.querySelectorAll('.gdot').forEach((d, i) => d.classList.toggle('on', i === current));
  }

  prev?.addEventListener('click', () => goTo(current - 1));
  next?.addEventListener('click', () => goTo(current + 1));
  return { refresh, goTo };
}

window.beyondCarousel = null;

(async () => {
  const track = document.getElementById('visuals-track');
  const ph = document.getElementById('visuals-placeholder');
  if (!track) return;
  const urls = await scanFolder('assets/media/visuals');
  if (urls.length) {
    if (ph) ph.remove();
    buildSlides(track, urls, 'Frame');
    const car = initCarousel({ trackId: 'visuals-track', dotsId: 'visuals-dots', prevId: 'visuals-prev', nextId: 'visuals-next', controlsId: 'visuals-controls' });
    car?.refresh(); car?.goTo(0);
  }
})();

(async () => {
  const track = document.getElementById('ach-track');
  if (!track) return;
  let urls = await scanFolder('assets/media/recognition');
  if (!urls.length) {
    track.querySelectorAll('img[data-fallback]').forEach(img => { if (img.getAttribute('src')) urls.push(img.getAttribute('src')); });
    urls = [...new Set(urls)];
  }
  if (urls.length) {
    buildSlides(track, urls, 'Recognition');
    const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next' });
    car?.refresh(); car?.goTo(0);
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

'''


def reorder_sections(text: str) -> str:
    markers = [
        ('experience', '<!-- ══ EXPERIENCE ══ -->', '<!-- ══ WORK ══ -->'),
        ('work', '<!-- ══ WORK ══ -->', '<!-- ══ SKILLS ══ -->'),
        ('skills', '<!-- ══ SKILLS ══ -->', '<!-- ══ ACHIEVEMENTS ══ -->'),
        ('achievements', '<!-- ══ ACHIEVEMENTS ══ -->', '<!-- ══ BEYOND WORK ══ -->'),
        ('beyond', '<!-- ══ BEYOND WORK ══ -->', '<!-- ══ PROCESS ══ -->'),
        ('process', '<!-- ══ PROCESS ══ -->', '<!-- ══ CONTACT ══ -->'),
    ]
    sections = {n: text[text.index(s):text.index(e)] for n, s, e in markers}
    stats_start = text.index('<!-- ══ STATS TICKER ══ -->')
    stats_end = text.index('<!-- ══ EXPERIENCE ══ -->')
    contact_start = text.index('<!-- ══ CONTACT ══ -->')
    return text[:stats_start] + text[stats_start:stats_end] + sections['work'] + sections['skills'] + sections['experience'] + sections['process'] + sections['achievements'] + sections['beyond'] + text[contact_start:]


def replace_logo(html, company, src, alt):
    idx = html.find(f'<div class="exp-company">{company}</div>')
    if idx == -1 and '(Uncode)' not in company:
        idx = html.find(f'<div class="exp-company">{company}')
    assert idx != -1, company
    start = html.rfind('<div class="exp-item"', 0, idx)
    ls = html.find('<div class="exp-logo">', start, idx)
    le = html.find('</div>', ls) + len('</div>')
    return html[:ls] + f'<div class="exp-logo"><img src="{src}" alt="{alt} logo"></div>' + html[le:]


def wrap_exp_accordion(html: str) -> str:
    pat = re.compile(
        r'(<div class="exp-item"[^>]*>.*?<div class="exp-body">\s*)'
        r'(<div class="exp-role">.*?</div>\s*<div class="exp-company">.*?</div>\s*)'
        r'(<ul class="exp-bullets">.*?</ul>\s*)'
        r'((?:<span class="exp-tag">.*?</span>\s*)+)',
        re.DOTALL,
    )
    def repl(m):
        return (m.group(1)
            + f'<button type="button" class="exp-toggle-row" aria-expanded="false">{m.group(2)}<span class="exp-chevron" aria-hidden="true">▼</span></button>'
            + f'<div class="exp-details">{m.group(3)}<div class="exp-tags-wrap">{m.group(4)}</div></div>')
    return pat.sub(repl, html)


def patch_achievements(html: str) -> str:
    block = re.search(r'<div class="ach-photos">(.*?)</div>\s*</div>\s*</div>\s*</section>', html, re.DOTALL)
    fallbacks = re.findall(r'src="(data:image/[^"]+)"', block.group(1)) if block else []
    imgs = ''.join(f'<img data-fallback src="{s}" alt="" style="display:none">' for s in fallbacks[:2])
    carousel = f'''<div class="ach-carousel-wrap">
        <div class="ach-carousel">
          <div class="gallery-track" id="ach-track" style="display:flex">{imgs}</div>
        </div>
        <div class="ach-carousel-dots" id="ach-dots"></div>
        <div class="gallery-btns" style="justify-content:center;margin-top:12px;display:flex;gap:10px">
          <button class="gbtn" id="ach-prev" aria-label="Previous"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg></button>
          <button class="gbtn" id="ach-next" aria-label="Next"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg></button>
        </div>
      </div>'''
    return re.sub(r'<div class="ach-photos">.*?</div>(\s*</div>\s*</div>\s*</section>)', carousel + r'\1', html, count=1, flags=re.DOTALL)


def patch_case_studies(html: str) -> str:
    cards = {
        'wca': ('Enterprise · Web', 'ACKO Website Design', "Designing ACKO's Enterprise business website — the face of a ₹1000+ Cr business"),
        'wcb': ('Insurance · Automotive', 'ACKO Drive Service Center', '212% conversion uplift · from Fake Door test to scaled V1'),
        'wcc': ('Enterprise · B2B', 'ACKO Enterprise Employer Portal', '90+ entities · design system built from scratch'),
    }
    for cls, (tag, title, sub) in cards.items():
        inner = f'<p class="ctag">{tag}</p>\n          <h3 class="ctitle">{title}</h3>\n          <p class="csubtitle">{sub}</p>'
        html = re.sub(rf'(<div class="wcard {cls}"[^>]*>.*?<div class="cbg-inner">\s*)(.*?)(</div></div>)',
                      rf'\1{inner}\3', html, count=1, flags=re.DOTALL)
    return html


def safe_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing: {label}')
    return text.replace(old, new, 1)


def main():
    text = HTML.read_text(encoding='utf-8')
    orig = len(text)
    assert '</html>' in text

    text = reorder_sections(text)

    patches = [
        ('about-links', '.about-links{display:flex;gap:16px;margin-top:32px;flex-wrap:wrap}',
         '.about-links{display:flex;gap:12px;margin-top:32px;flex-wrap:nowrap}'),
        ('about-link-pad', '.about-link{\n  display:inline-flex;align-items:center;gap:8px;\n  padding:10px 20px;border:1.5px solid var(--border);',
         '.about-link{\n  display:inline-flex;align-items:center;gap:8px;\n  padding:10px 14px;border:1.5px solid var(--border);white-space:nowrap;'),
        ('exp-bullets', '.exp-bullets li{\n  font-size:0.82rem;line-height:1.8;color:#666;font-weight:300;',
         '.exp-bullets li{\n  font-size:0.88rem;line-height:1.75;color:#b8b8b8;font-weight:400;'),
        ('exp-company', '.exp-company{font-size:0.8rem;font-weight:500;color:#666;',
         '.exp-company{font-size:0.8rem;font-weight:500;color:#888;'),
        ('beyond-grid', '.beyond-grid{display:grid;grid-template-columns:5fr 7fr;gap:56px;margin-bottom:72px;align-items:start}',
         '.beyond-grid{display:grid;grid-template-columns:5fr 7fr;gap:56px;margin-bottom:72px;align-items:stretch}'),
        ('beyond-interests', '.beyond-interests{display:flex;flex-direction:column;gap:24px}',
         '.beyond-interests{display:flex;flex-direction:column;gap:12px;justify-content:space-between;height:100%;overflow:visible;padding-top:6px}'),
        ('interest-item', '.interest-item{display:flex;align-items:flex-start;gap:20px;padding:24px;',
         '.interest-item{display:flex;align-items:center;gap:20px;padding:16px 20px;'),
        ('interest-desc', '.interest-desc{font-size:0.8rem;font-weight:300;color:#777;line-height:1.7}',
         '.interest-desc{font-size:0.78rem;font-weight:300;color:#777;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'),
        ('interest-hover', '.interest-item:hover{border-color:var(--gold);transform:translateY(-2px)}',
         '.interest-item:hover{border-color:var(--gold);box-shadow:0 4px 20px rgba(0,0,0,0.06)}'),
        ('gallery-wrap', '.gallery-wrap{position:relative;overflow:hidden}',
         '.gallery-wrap{position:relative;overflow:visible}'),
        ('gallery-track', '.gallery-track{\n  display:flex;gap:16px;\n  overflow-x:auto;',
         '.gallery-track{\n  display:flex;gap:16px;\n  overflow:hidden;\n  border-radius:4px;'),
        ('gallery-controls', '.gallery-controls{\n  display:flex;align-items:center;justify-content:space-between;\n  margin-top:20px;\n}',
         '.gallery-controls{\n  display:flex;align-items:center;justify-content:space-between;\n  margin-top:20px;\n  padding-bottom:4px;\n}'),
        ('wcard-radius', '.wcard{position:relative;overflow:hidden;cursor:pointer;border-radius:6px;',
         '.wcard{position:relative;overflow:hidden;cursor:pointer;border-radius:16px;'),
        ('hero-grad', '#hero-grad{\n  position:absolute;bottom:0;left:0;width:55%;height:28%;\n  background:linear-gradient(to top,rgba(245,244,242,0.7) 0%,rgba(245,244,242,0.25) 60%,transparent 100%);\n  z-index:5;pointer-events:none;\n}',
         '#hero-grad{display:none}'),
        ('exp-logo', '.exp-logo{margin-bottom:16px;height:26px;display:flex;align-items:center}\n.exp-logo svg{height:26px;width:auto;max-width:130px;display:block;filter:brightness(0)}\n.exp-logo img{height:26px;width:auto;max-width:130px;object-fit:contain;display:block;filter:brightness(0)}',
         '.exp-logo{margin-bottom:16px;height:28px;display:flex;align-items:center}\n.exp-logo img{height:28px;width:auto;max-width:140px;object-fit:contain;display:block;filter:none}'),
        ('ach-photos', '.ach-photos{display:flex;flex-direction:column;gap:12px}\n.ach-photo{width:100%;border-radius:4px;object-fit:cover;display:block}\n.ach-photo-main{aspect-ratio:16/9;object-position:center}\n.ach-photo-sub{aspect-ratio:4/3;object-position:top}',
         '/* ach-photos replaced by carousel */'),
        ('pdesc-ai', '<p class="pdesc">High-fidelity prototypes in Figma — pixel-perfect, interaction-rich, and ready for stakeholder review.</p>',
         '<p class="pdesc">High-fidelity prototypes in Figma — augmented with AI tooling (Cursor, Claude, Figma Make) for faster iteration, richer interactions, and stakeholder-ready demos.</p>'),
    ]
    for label, old, new in patches:
        text = safe_replace(text, old, new, label)

    if '  .about-links{flex-wrap:wrap}\n' not in text:
        text = safe_replace(text, '  .beyond-grid{grid-template-columns:1fr;gap:40px}',
                            '  .about-links{flex-wrap:wrap}\n  .beyond-grid{grid-template-columns:1fr;gap:40px}', 'responsive-about')

    text = text.replace('</style>', NEW_CSS + '\n</style>', 1)
    text = text.replace('    <div id="hero-grad"></div>\n', '')
    text = text.replace('<div id="cursor-ring"></div>', '<div id="cursor-ring"></div>\n<div id="cursor-label">Scroll</div>')

    text = re.sub(r'<a class="nav-resume" href="#" target="_blank" id="nav-resume-link"',
                  f'<a class="nav-resume" href="{RESUME}" target="_blank" rel="noopener noreferrer" id="nav-resume-link"', text, 1)
    text = re.sub(r'<a class="about-link" href="#" target="_blank" id="resume-link"',
                  f'<a class="about-link" href="{RESUME}" target="_blank" rel="noopener noreferrer" id="resume-link"', text, 1)
    text = re.sub(r'<a class="about-link" href="/cdn-cgi/l/email-protection#[^"]+"',
                  '<a class="about-link" href="mailto:akmeroju@gmail.com"', text, 1)

    text = safe_replace(text,
        """    <li><a href="#about">About</a></li>
    <li><a href="#experience">Experience</a></li>
    <li><a href="#work">Work</a></li>
    <li><a href="#skills">Skills</a></li>
    <li><a href="#contact">Contact</a></li>""",
        """    <li><a href="#about">About</a></li>
    <li><a href="#work">Work</a></li>
    <li><a href="#visuals">Visuals</a></li>
    <li><a href="#skills">Skills</a></li>
    <li><a href="#experience">Experience</a></li>
    <li><a href="#contact">Contact</a></li>""", 'nav')

    text = safe_replace(text,
        """  <a href="#about">About</a>
  <a href="#experience">Experience</a>
  <a href="#work">Work</a>
  <a href="#skills">Skills</a>
  <a href="#contact">Contact</a>""",
        """  <a href="#about">About</a>
  <a href="#work">Work</a>
  <a href="#visuals">Visuals</a>
  <a href="#skills">Skills</a>
  <a href="#experience">Experience</a>
  <a href="#contact">Contact</a>""", 'mobile-nav')

    text = text.replace("const navSections = ['about','experience','work','skills','contact'];",
                        "const navSections = ['about','work','visuals','skills','experience','contact'];")

    for company, src, alt in [
        ('ACKO', 'assets/logos/acko.png', 'ACKO'),
        ('AJR Infosystems', 'assets/logos/uncode.png', 'Uncode'),
        ('Tech Mahindra', 'assets/logos/tech-mahindra.png', 'Tech Mahindra'),
        ('Lit-Athleto (Mobile App) — Entrepreneurial', 'assets/logos/lit-athleto.png', 'Lit-Athleto'),
    ]:
        text = replace_logo(text, company, src, alt)

    text = text.replace('<div class="exp-company">AJR Infosystems</div>',
                        '<div class="exp-company">AJR Infosystems <span class="exp-company-sub">(Uncode)</span></div>')

    # Beyond interests block
    bi_start = text.index('<div class="beyond-interests"')
    bi_end = text.index('<div data-a="scale" data-d="2">', bi_start)
    text = text[:bi_start] + BEYOND_INTERESTS + text[bi_end:]

    # Gallery fallback URLs
    slides = re.findall(r'<img src="(data:image/[^"]+|assets/[^"]+)"', text[text.index('id="gallery-track"'):text.index('gallery-controls', text.index('id="gallery-track"'))])
    if slides:
        fb = json.dumps(slides[:8])
        text = text.replace('<div class="gallery-track" id="gallery-track">',
                            f"<div class=\"gallery-track\" id=\"gallery-track\" data-fallback='{fb}'>", 1)

    text = patch_case_studies(text)
    text = patch_achievements(text)
    text = wrap_exp_accordion(text)

    if '<section id="visuals">' not in text:
        text = text.replace('<!-- ══ SKILLS ══ -->', VISUALS_SECTION + '<!-- ══ SKILLS ══ -->', 1)

    # Remove old gallery scroll JS, inject new JS
    old_gallery = text[text.index('// ── GALLERY CAROUSEL'):text.index('// ── SCROLL PROGRESS BAR')]
    text = text.replace(old_gallery, '// ── GALLERY CAROUSEL handled in media loader below\n\n')

    anchor = '// Contact section reveal'
    if 'HERO SCROLL CURSOR LABEL' not in text:
        text = text.replace(anchor, NEW_JS + '\n' + anchor)

    assert '</html>' in text
    assert text.count('<script') == text.count('</script>')
    assert len(text) > orig * 0.95

    HTML.write_text(text, encoding='utf-8')
    print(f'OK — {len(text):,} bytes')


if __name__ == '__main__':
    main()
