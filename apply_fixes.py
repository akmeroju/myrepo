#!/usr/bin/env python3
"""Apply portfolio fixes #1–6 with integrity checks."""
import re
import subprocess
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "tools"))
from portfolio_guard import is_external_mode  # noqa: E402

if is_external_mode():
    sys.exit("BLOCKED: Portfolio is split. Edit assets/portfolio.css / portfolio.js instead.")

HTML = ROOT / "adithya-portfolio.html"

PATCH_CSS = """
/* ── FIX: NAV RESUME ── */
.nav-resume{
  font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;
  color:var(--muted);text-decoration:none;transition:color 0.2s;
  display:inline-flex;align-items:center;gap:6px;
}
.nav-resume:hover{color:var(--text)}
.nav-resume svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2;flex-shrink:0}

/* ── FIX: HERO SCROLL CURSOR ── */
#cursor-label{
  position:fixed;pointer-events:none;z-index:10001;
  font-size:0.58rem;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;
  color:#fff;opacity:0;transition:opacity 0.25s;white-space:nowrap;
  background:rgba(10,10,10,0.88);padding:7px 14px;border-radius:999px;
  transform:translate(-50%,-50%);
  border:1px solid rgba(255,255,255,0.12);
}
body.hero-active #cursor-label{opacity:1}
body.hero-active #cursor{opacity:0!important}
body.hero-active #cursor-ring{width:0;height:0;border:none;opacity:0!important}

/* ── FIX: CAREER ACCORDION (subtle) ── */
.exp-toggle-row{
  padding:14px 0;border:none;border-radius:0;
  transition:opacity 0.2s;
}
.exp-toggle-row:hover{opacity:0.85}
.exp-item.is-open .exp-toggle-row{opacity:1}
.exp-chevron{
  width:28px;height:28px;border:1px solid #ddd;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  color:#888;transition:transform 0.3s ease,border-color 0.2s;
}
.exp-item.is-open .exp-chevron{transform:rotate(180deg);border-color:#bbb;color:#666}

/* ── FIX: APPROACH EQUAL HEIGHT ── */
.pstep{display:flex;flex-direction:column}
.pdesc{flex:1;min-height:5.8em}

/* ── FIX: RECOGNITION CAROUSEL ── */
.ach-carousel .gallery-track{gap:0;width:100%;overflow:visible}
.ach-carousel .gallery-slide{flex:0 0 100%;min-width:100%}
.ach-carousel .gallery-slide img{height:360px;object-fit:cover}
.visuals-track-wrap .gallery-track{gap:0;width:100%}
.visuals-track-wrap .gallery-slide{flex:0 0 100%;min-width:100%}

/* ── FIX: FOOTER FULL IMAGE ── */
.footer-hero-img{width:100%;height:auto;display:block;max-width:100%}
"""

NEW_GO_TO = """  function goTo(idx) {
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
  }"""

NEW_HERO_CURSOR_JS = """// ── HERO SCROLL CURSOR LABEL ─────────────────────────────────────────────
const cursorLabel = document.getElementById('cursor-label');
const heroSticky = document.querySelector('.hero-sticky');
if (cursorLabel && heroSticky) {
  document.addEventListener('mousemove', e => {
    cursorLabel.style.left = e.clientX + 'px';
    cursorLabel.style.top  = e.clientY + 'px';
  });
  const heroObs = new IntersectionObserver(([entry]) => {
    document.body.classList.toggle('hero-active', entry.isIntersecting);
  }, { threshold: 0.4 });
  heroObs.observe(heroSticky);
}"""

NEW_ACCORDION_JS = """// ── EXPERIENCE ACCORDION ─────────────────────────────────────────────────
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
});"""

APPROACH_STEP_03_OLD = (
    '<p class="pdesc">High-fidelity Figma prototypes — accelerated with AI tooling '
    'for faster iteration and stakeholder-ready demos.</p>'
)
APPROACH_STEP_03_NEW = (
    '<p class="pdesc">High-fidelity Figma prototypes with rich interactions — '
    'accelerated using AI tooling (Cursor, Claude, Figma Make) for faster iteration, '
    'stakeholder-ready demos, and sharper handoffs.</p>'
)


def strip_old_fix_css(text: str) -> str:
    patterns = [
        r"/\* ── CAREER TOGGLE POLISH ── \*/[\s\S]*?(?=/\* ── APPROACH EQUAL HEIGHT ── \*/)",
        r"/\* ── APPROACH EQUAL HEIGHT ── \*/[\s\S]*?(?=/\* ── RECOGNITION CONTROLS ── \*/)",
        r"/\* ── RECOGNITION CONTROLS ── \*/[\s\S]*?(?=/\* ── FOOTER HERO IMAGE ── \*/)",
        r"/\* ── FOOTER HERO IMAGE ── \*/[^\n]*\n[^\n]*\n",
        r"/\* ── FIX:[\s\S]*?(?=\n</style>)",
        r"/\* nav-resume moved to PATCH_CSS \*/\n?",
        r"/\* hero cursor moved to PATCH_CSS \*/\n?",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, count=1)
    return text


def replace_js_section(text: str, marker: str, replacement: str) -> str:
    start = text.index(marker)
    # Find end: next section comment at same indent level
    rest = text[start + len(marker):]
    m = re.search(r"\n// ── [A-Z]", rest)
    end = start + len(marker) + (m.start() if m else len(rest))
    return text[:start] + replacement + text[end:]


def main():
    text = HTML.read_text(encoding="utf-8")
    orig_len = len(text)
    assert "</html>" in text

    # 3. Remove "View details" labels
    text = re.sub(r'\s*<span class="exp-toggle-label">View details</span>', "", text)

    # 4. Approach step 03 copy
    text = text.replace(APPROACH_STEP_03_OLD, APPROACH_STEP_03_NEW, 1)

    # JS: accordion
    text = replace_js_section(text, NEW_ACCORDION_JS.split("\n")[0], NEW_ACCORDION_JS)

    # JS: hero cursor
    text = replace_js_section(text, NEW_HERO_CURSOR_JS.split("\n")[0], NEW_HERO_CURSOR_JS)

    # JS: goTo pixel-based
    old_go_to = """  function goTo(idx) {
    const slides = track.querySelectorAll('.gallery-slide');
    const total = slides.length;
    if (!total) return;
    current = (idx + total) % total;
    track.style.transform = `translateX(-${current * 100}%)`;
    track.style.display = 'flex';
    slides.forEach(s => { s.style.flex = '0 0 100%'; s.style.minWidth = '100%'; });
    dotsEl?.querySelectorAll('.gdot').forEach((d, i) => d.classList.toggle('on', i === current));
  }"""
    assert old_go_to in text
    text = text.replace(old_go_to, NEW_GO_TO, 1)

    # Carousel: expose current + ach ref + pause on wrap
    text = text.replace(
        "  track?.addEventListener('mouseenter', stopAutoplay);\n  track?.addEventListener('mouseleave', startAutoplay);",
        "  const pauseEl = track.closest('.ach-carousel-wrap, .visuals-carousel-wrap, .gallery-wrap') || track;\n  pauseEl?.addEventListener('mouseenter', stopAutoplay);\n  pauseEl?.addEventListener('mouseleave', startAutoplay);",
        1,
    )
    text = text.replace(
        "  return { refresh, goTo, startAutoplay, stopAutoplay };",
        "  return { refresh, goTo, startAutoplay, stopAutoplay, get current() { return current; } };",
        1,
    )
    text = text.replace(
        "const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next', autoplay: true, interval: 5500 });\n    car?.refresh(); car?.goTo(0);",
        "const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next', autoplay: true, interval: 5500 });\n    window.achCarousel = car;\n    car?.refresh(); car?.goTo(0); car?.startAutoplay();",
        1,
    )

    # CSS cleanup
    text = re.sub(
        r"\.nav-resume\{[^}]+\}\s*\.nav-resume:hover\{[^}]+\}\s*\.nav-resume svg\{[^}]+\}",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"/\* ── HERO SCROLL CURSOR ── \*/\s*#cursor-label\{[^}]+\}\s*body\.hero-active #cursor-label\{[^}]+\}\s*body\.hero-active #cursor,body\.hero-active #cursor-ring\{[^}]+\}",
        "",
        text,
        count=1,
    )
    text = re.sub(r"\.exp-toggle-label\{[^}]+\}\s*\.exp-item\.is-open \.exp-toggle-label\{[^}]+\}", "", text, count=1)
    text = strip_old_fix_css(text)
    text = text.replace(
        ".footer-hero-img{width:100%;height:auto;display:block;object-fit:cover;object-position:center bottom;min-height:240px;max-height:90vh}\n",
        "",
        1,
    )

    if "FIX: NAV RESUME" not in text:
        text = text.replace("</style>", PATCH_CSS + "\n</style>", 1)

    assert "</html>" in text
    assert text.count("<script") == text.count("</script>")
    assert "View details" not in text
    assert "exp-toggle-label" not in text
    assert len(text) > orig_len * 0.95

    scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", text)
    js = scripts[1]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(js)
        path = f.name
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    os.unlink(path)
    assert r.returncode == 0, f"JS syntax error: {r.stderr}"

    HTML.write_text(text, encoding="utf-8")
    print(f"OK — {len(text):,} bytes")


if __name__ == "__main__":
    main()
