#!/usr/bin/env python3
"""Apply polish fixes with integrity checks."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "tools"))
from portfolio_guard import is_external_mode  # noqa: E402

if is_external_mode():
    sys.exit("BLOCKED: Portfolio is split. Edit assets/portfolio.css / portfolio.js instead.")

HTML = ROOT / "adithya-portfolio.html"

NEW_CSS = """
/* ── CAREER TOGGLE POLISH ── */
.exp-toggle-row{
  padding:14px 18px;border:1px solid #222;border-radius:8px;
  transition:border-color 0.25s,background 0.25s;
}
.exp-toggle-row:hover,.exp-item.is-open .exp-toggle-row{
  border-color:var(--gold);background:rgba(201,168,76,0.06);
}
.exp-toggle-info{flex:1;text-align:left}
.exp-toggle-label{
  font-size:0.62rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
  color:#666;margin-right:10px;white-space:nowrap;transition:color 0.2s;
}
.exp-item.is-open .exp-toggle-label{color:var(--gold)}
.exp-chevron{
  width:32px;height:32px;border:1px solid #333;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  color:var(--gold);transition:transform 0.3s ease,border-color 0.2s;
}
.exp-item.is-open .exp-chevron{transform:rotate(180deg);border-color:var(--gold)}
.exp-details{padding-top:16px}

/* ── APPROACH EQUAL HEIGHT ── */
.pstep{display:flex;flex-direction:column}
.pdesc{min-height:4.8em}

/* ── RECOGNITION CONTROLS ── */
#achievements .gbtn{
  border-color:rgba(255,255,255,0.35);background:rgba(255,255,255,0.1);cursor:pointer;
}
#achievements .gbtn svg{color:#fff;stroke:#fff}
#achievements .gbtn:hover{
  border-color:var(--gold);background:rgba(201,168,76,0.25);transform:scale(1.06);
}

/* ── FOOTER HERO IMAGE ── */
.footer-illustration{background:#000;width:100%;padding:0;margin:0;overflow:hidden;border-top:1px solid #111;line-height:0}
.footer-hero-img{width:100%;height:auto;display:block;object-fit:cover;object-position:center bottom;min-height:240px;max-height:90vh}
"""

NEW_INIT_CAROUSEL = """function initCarousel({ trackId, dotsId, prevId, nextId, controlsId, autoplay = false, interval = 5500 }) {
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
    track.style.transform = `translateX(-${current * 100}%)`;
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
  track?.addEventListener('mouseenter', stopAutoplay);
  track?.addEventListener('mouseleave', startAutoplay);

  startAutoplay();
  return { refresh, goTo, startAutoplay, stopAutoplay };
}"""


def fix_exp_toggles(html: str) -> str:
    pat = re.compile(
        r'<button type="button" class="exp-toggle-row" aria-expanded="[^"]*">\s*'
        r'<div class="exp-role">(.*?)</div>\s*'
        r'<div class="exp-company">(.*?)</div>\s*'
        r'<span class="exp-chevron" aria-hidden="true">▼</span>\s*</button>',
        re.DOTALL,
    )

    def repl(m):
        role = m.group(1).strip()
        company = m.group(2).strip()
        return (
            '<button type="button" class="exp-toggle-row" aria-expanded="false">\n'
            '          <div class="exp-toggle-info">\n'
            f'            <div class="exp-role">{role}</div>\n'
            f'            <div class="exp-company">{company}</div>\n'
            '          </div>\n'
            '          <span class="exp-toggle-label">View details</span>\n'
            '          <span class="exp-chevron" aria-hidden="true">'
            '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">'
            '<path d="M6 9l6 6 6-6"/></svg></span>\n'
            '        </button>'
        )

    return pat.sub(repl, html)


def main():
    text = HTML.read_text(encoding="utf-8")
    orig = len(text)
    assert "</html>" in text

    # Footer: replace SVG with full-width image
    text = re.sub(
        r'(<div class="footer-illustration">\s*)<svg[^>]*class="footer-svg"[\s\S]*?</svg>',
        r'\1<img src="assets/media/footer-illustration.png" alt="Designer workspace — Still designing. Still learning. Still curious." class="footer-hero-img" loading="lazy" decoding="async">',
        text,
        count=1,
    )

    # Remove old footer-svg max-width rule
    text = text.replace(
        ".footer-svg{width:100%;max-width:900px;display:block;margin:0 auto;height:auto;opacity:0.9}\n",
        "",
        1,
    )

    # Shorten approach step 03
    text = text.replace(
        "<p class=\"pdesc\">High-fidelity prototypes in Figma — augmented with AI tooling (Cursor, Claude, Figma Make) for faster iteration, richer interactions, and stakeholder-ready demos.</p>",
        "<p class=\"pdesc\">High-fidelity Figma prototypes — accelerated with AI tooling for faster iteration and stakeholder-ready demos.</p>",
        1,
    )

    text = fix_exp_toggles(text)

    # Replace initCarousel function (include trailing brace so we don't leave a duplicate)
    start = text.index("function initCarousel({ trackId, dotsId, prevId, nextId, controlsId")
    old_end = text.index("return { refresh, goTo };", start) + len("return { refresh, goTo };")
    end = old_end
    while end < len(text) and text[end] in " \t\r\n":
        end += 1
    if end < len(text) and text[end] == "}":
        end += 1
    text = text[:start] + NEW_INIT_CAROUSEL + text[end:]

    # Recognition: fix fallback + autoplay
    text = text.replace(
        "track.querySelectorAll('img[data-fallback]').forEach(img => { if (img.getAttribute('src')) urls.push(img.getAttribute('src')); });",
        "track.querySelectorAll('img[data-fallback]').forEach(img => { if (img.src) urls.push(img.src); });",
        1,
    )
    text = text.replace(
        "const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next' });",
        "const car = initCarousel({ trackId: 'ach-track', dotsId: 'ach-dots', prevId: 'ach-prev', nextId: 'ach-next', autoplay: true, interval: 5500 });",
        1,
    )

    # Accordion label toggle
    text = text.replace(
        """  btn.addEventListener('click', () => {
    const open = item.classList.contains('is-open');
    document.querySelectorAll('.exp-item').forEach(el => {
      el.classList.remove('is-open');
      el.querySelector('.exp-toggle-row')?.setAttribute('aria-expanded', 'false');
    });
    if (!open) {
      item.classList.add('is-open');
      btn.setAttribute('aria-expanded', 'true');
    }
  });""",
        """  btn.addEventListener('click', () => {
    const open = item.classList.contains('is-open');
    document.querySelectorAll('.exp-item').forEach(el => {
      el.classList.remove('is-open');
      const b = el.querySelector('.exp-toggle-row');
      b?.setAttribute('aria-expanded', 'false');
      el.querySelector('.exp-toggle-label') && (el.querySelector('.exp-toggle-label').textContent = 'View details');
    });
    if (!open) {
      item.classList.add('is-open');
      btn.setAttribute('aria-expanded', 'true');
      const lbl = btn.querySelector('.exp-toggle-label');
      if (lbl) lbl.textContent = 'Hide details';
    }
  });""",
        1,
    )

    # First item open label
    text = text.replace(
        "  if (i === 0) { item.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); }",
        "  if (i === 0) { item.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); const lbl = btn.querySelector('.exp-toggle-label'); if (lbl) lbl.textContent = 'Hide details'; }",
        1,
    )

    if "CAREER TOGGLE POLISH" not in text:
        text = text.replace("</style>", NEW_CSS + "\n</style>", 1)

    assert "</html>" in text
    assert text.count("<script") == text.count("</script>")
    assert len(text) > orig * 0.95
    assert "footer-hero-img" in text
    assert "autoplay: true" in text

    HTML.write_text(text, encoding="utf-8")
    print(f"OK — {len(text):,} bytes")


if __name__ == "__main__":
    main()
