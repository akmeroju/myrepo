#!/usr/bin/env python3
"""Wrap ACKO case study HTML with portfolio nav shell."""
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from portfolio_shell import portfolio_contact, portfolio_footer
SRC = Path("/Users/adithya.meroju/Downloads/acko-enterprise-case-study_8.html")
OUT = ROOT / "case-studies" / "acko-enterprise.html"
HOME = "../"
MEDIA = ROOT / "assets" / "media" / "case-studies"
EXEC_MOCKUP = MEDIA / "execution-mockup.png"
HERO_VIDEO = MEDIA / "hero-video.mp4"
OVERVIEW_DIR = MEDIA / "overview"
LANDING_DIR = MEDIA / "landing-pages"
CAROUSEL_INTERVAL_MS = 1800

LANDING_FILE_ALIASES = {
    "homepage": ["Homepage", "homepage"],
    "group-medical": ["GMC", "group-medical", "gmc"],
    "travel-insurance": ["Travel", "travel-insurance", "travel"],
    "credit-insurance": ["Credit", "credit-insurance", "credit"],
    "gig-worker": ["Gig workers", "Gig Workers", "gig-worker", "gig workers"],
    "electronics": ["Electronics", "electronics"],
}

MOBILE_FILE_ALIASES = ["Mobile", "mobile"]

PORTFOLIO_CONTACT = portfolio_contact()

PORTFOLIO_FOOTER = portfolio_footer("../")

LIVE_LINKS = [
    ("Homepage", "https://www.acko.com/gi/enterprise/"),
    ("GMC", "https://www.acko.com/gi/enterprise/group-health-insurance/"),
    ("Credit", "https://www.acko.com/gi/enterprise/fintech-loan-protection-insurance/"),
    ("Travel", "https://www.acko.com/gi/enterprise/group-travel-insurance/"),
    ("Gig", "https://www.acko.com/gi/enterprise/gig-worker-health-insurance/"),
    ("Electronics", "https://www.acko.com/gi/enterprise/electronic-device-insurance/"),
]

LANDING_PAGES = [
    ("homepage", "Homepage", 1),
    ("group-medical", "Group Medical", 2),
    ("travel-insurance", "Travel", 3),
    ("credit-insurance", "Credit", 4),
    ("gig-worker", "Gig Worker", 5),
    ("electronics", "Electronics", 6),
]

NAV_SHELL = f"""
<div id="progress-bar"></div>
<div id="cursor"></div>
<div id="cursor-ring"></div>

<nav id="nav">
  <a class="nav-logo" href="{HOME}">AKM</a>
  <ul class="nav-links">
    <li><a href="{HOME}#about">About</a></li>
    <li><a href="{HOME}#work">Work</a></li>
    <li><a href="{HOME}#visuals">Visuals</a></li>
    <li><a href="{HOME}#skills">Skills</a></li>
    <li><a href="{HOME}#experience">Experience</a></li>
    <li><a href="{HOME}#contact">Contact</a></li>
  </ul>
  <div style="display:flex;align-items:center;gap:16px">
    <a class="nav-resume" href="https://drive.google.com/file/d/1JrgIl59VBxkMacOEvoJeXqX1KTEBzNjk/view" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Resume</a>
    <a class="nav-cta" href="{HOME}#contact">Hire Me</a>
    <button class="hamburger" id="hamburger" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<div class="mobile-nav" id="mobile-nav">
  <a href="{HOME}#about">About</a>
  <a href="{HOME}#work">Work</a>
  <a href="{HOME}#visuals">Visuals</a>
  <a href="{HOME}#skills">Skills</a>
  <a href="{HOME}#experience">Experience</a>
  <a href="{HOME}#contact">Contact</a>
  <a class="mn-cta" href="mailto:akmeroju@gmail.com">Hire Me</a>
</div>
<div id="stageLabel" hidden aria-hidden="true"></div>
"""

BACK_LINK = f"""<a class="case-back case-back-body" href="{HOME}#work">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
      <span>Back to portfolio</span>
    </a>
"""

HEAD_INJECT = """
<link rel="stylesheet" href="../assets/case-study-nav.css">
<link rel="stylesheet" href="../assets/case-study-shell.css">
<link rel="stylesheet" href="../assets/case-study-visuals.css">
<link rel="stylesheet" href="../assets/case-study-ambient.css">
<link rel="stylesheet" href="../assets/case-study-contact.css">
<link rel="stylesheet" href="../assets/case-study-footer.css">
"""

FOOT_INJECT = """
<script src="../assets/case-study-ambient.js"></script>
<script src="../assets/case-study-visuals.js"></script>
<script src="../assets/case-study-nav.js"></script>
"""

TOPNAV_PATTERN = re.compile(
    r'<div class="topnav">\s*'
    r'<div class="mark">[^<]*</div>\s*'
    r'<div class="stage" id="stageLabel">[^<]*</div>\s*'
    r'</div>\s*',
    re.DOTALL,
)

CAROUSEL_SLIDE_IMG = '<div class="carousel-slide"><img src="data:image'
GRID_BODY_IMG = '<div class="browser-body"><img src="data:image'
HERO_VIDEO_MARKER = '<video class="screen-video"'
HERO_VIDEO_REPLACEMENT = (
    '<video class="screen-video" autoplay muted loop playsinline preload="metadata" '
    'poster="../assets/media/case-studies/hero-video-poster.jpg"></video>'
)
HERO_VIDEO_INIT = """
  // Hero device video — mobile-optimized src + reliable autoplay
  (function () {
    const video = document.querySelector('.device-mockup .screen-video');
    if (!video) return;
    const isMobile = window.matchMedia('(max-width: 900px)').matches;
    video.src = isMobile
      ? '../assets/media/case-studies/hero-video-mobile.mp4'
      : '../assets/media/case-studies/hero-video.mp4';
    const tryPlay = () => video.play().catch(() => {});
    video.addEventListener('loadeddata', tryPlay, { once: true });
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) tryPlay();
        });
      }, { threshold: 0.25 });
      io.observe(video);
    } else {
      tryPlay();
    }
  })();
"""

OVERVIEW_ALTS = [
    "ACKO Enterprise homepage",
    "Group Medical Insurance landing page",
    "Travel Insurance landing page",
    "Credit Insurance landing page",
    "Gig Worker Insurance landing page",
    "Electronics Protection landing page",
]


def replace_data_uri_img(text: str, container_marker: str, new_src: str, alt: str) -> Tuple[str, bool]:
    start = text.find(container_marker)
    if start == -1:
        return text, False
    img_start = text.find("<img", start)
    if img_start == -1:
        return text, False
    src_start = text.find('src="', img_start)
    if src_start == -1:
        return text, False
    src_start += len('src="')
    src_end = text.find('"', src_start)
    if src_end == -1:
        return text, False
    img_end = text.find(">", src_end)
    if img_end == -1:
        return text, False
    img_end += 1
    replacement = f'<img src="{new_src}" alt="{alt}">'
    return text[:img_start] + replacement + text[img_end:], True


def replace_hero_video(text: str) -> str:
    if not HERO_VIDEO.exists():
        print(f"Note: {HERO_VIDEO.name} not found — keeping embedded hero video")
        return text
    start = text.find(HERO_VIDEO_MARKER)
    if start == -1:
        raise SystemExit("Hero screen video not found")
    end = text.find("</video>", start)
    if end == -1:
        raise SystemExit("Hero video end tag not found")
    end += len("</video>")
    text = text[:start] + HERO_VIDEO_REPLACEMENT + text[end:]
    if HERO_VIDEO_INIT.strip() not in text:
        text = text.replace("  })();\n</script>", "  })();\n" + HERO_VIDEO_INIT + "</script>", 1)
    print(f"Using hero video: {HERO_VIDEO.name} (+ mobile + poster)")
    return text


def find_landing_file(names: List[str]) -> Optional[Path]:
    for name in names:
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = LANDING_DIR / f"{name}{ext}"
            if candidate.exists():
                return candidate
    return None


def resolve_landing_asset(slug: str, overview_index: int) -> Optional[Tuple[str, str]]:
    aliases = LANDING_FILE_ALIASES.get(slug, [slug])
    path = find_landing_file(aliases)
    if path:
        return (
            f"../assets/media/case-studies/landing-pages/{path.name}",
            path.name,
        )
    for ext in (".png", ".webp", ".jpg", ".jpeg"):
        fallback = OVERVIEW_DIR / f"overview-{overview_index}{ext}"
        if fallback.exists():
            return (
                f"../assets/media/case-studies/overview/{fallback.name}",
                fallback.name,
            )
    return None


def resolve_mobile_asset() -> str:
    path = find_landing_file(MOBILE_FILE_ALIASES)
    if path:
        return f"../assets/media/case-studies/landing-pages/{path.name}"
    return ""


def build_visuals_section() -> str:
    pages: List[Tuple[str, str, str]] = []
    for slug, label, idx in LANDING_PAGES:
        resolved = resolve_landing_asset(slug, idx)
        if resolved:
            pages.append((label, resolved[0], slug))

    if not pages:
        return ""

    mobile_src = resolve_mobile_asset()
    if mobile_src:
        pages.append(("Mobile", mobile_src, "mobile"))

    tabs = []
    for i, (label, src, _slug) in enumerate(pages):
        active = " active" if i == 0 else ""
        tabs.append(
            f'      <button type="button" class="visuals-tab{active}" '
            f'data-src="{src}">{label}</button>'
        )

    first_src = pages[0][1]
    first_label = pages[0][0]

    return f"""
<!-- ============ VISUALS ============ -->
<div class="section-divider"><div class="divider"></div></div>
<section id="case-visuals" class="wrap-wide reveal" data-ambient>
  <div class="eyebrow c-mint">Visuals</div>
  <h2 class="section-title">Explore the full landing pages.</h2>
  <p class="body-text">Drag to pan, scroll to zoom — explore each page freely, like Figma.</p>
  <div class="visuals-tabs" id="visualsTabs">
{chr(10).join(tabs)}
  </div>
  <div class="visuals-controls">
    <button type="button" class="visuals-zoom-btn" id="visualsZoomOut" aria-label="Zoom out">&minus;</button>
    <button type="button" class="visuals-zoom-btn" id="visualsZoomReset" aria-label="Reset view">Reset</button>
    <button type="button" class="visuals-zoom-btn" id="visualsZoomIn" aria-label="Zoom in">+</button>
  </div>
  <div class="visuals-viewport" id="visualsViewport">
    <div class="visuals-canvas" id="visualsCanvas">
      <img id="visualsImage" src="{first_src}" alt="{first_label} landing page design">
    </div>
  </div>
  <p class="visuals-hint">Drag to pan &middot; Scroll to zoom &middot; Double-click to reset</p>
</section>
"""


def build_live_links_section() -> str:
    links = []
    for label, url in LIVE_LINKS:
        links.append(
            f'    <a class="live-link" href="{url}" target="_blank" rel="noopener noreferrer">'
            f"{label}<span>&rarr;</span></a>"
        )
    return f"""
<!-- ============ LIVE LINKS ============ -->
<section id="case-live-links" class="wrap-wide reveal" data-ambient>
  <div class="eyebrow c-violet">Live</div>
  <h2 class="section-title">View the <span class="grad-live">live</span> enterprise pages.</h2>
  <p class="body-text">Six experiences shipped — explore them on acko.com.</p>
  <div class="live-links-grid">
{chr(10).join(links)}
  </div>
</section>
"""


def strip_progress_rail(text: str) -> str:
    text, removed = re.subn(
        r'<div class="progress-rail">\s*<div class="progress-fill" id="progressFill"></div>\s*</div>\s*',
        "",
        text,
        count=1,
    )
    if removed != 1:
        print("Warning: progress-rail block not found — skipping removal")
    return text


def inject_ambient_markers(text: str) -> str:
    def add_ambient(match: re.Match) -> str:
        tag = match.group(0)
        if "data-ambient" in tag:
            return tag
        return tag[:-1] + " data-ambient>"

    text = re.sub(r'<section class="section(?:-tight)?"[^>]*>', add_ambient, text)
    text = text.replace(
        'class="case-closing reveal"',
        'class="case-closing reveal" data-ambient',
        1,
    )
    text = text.replace(
        'class="portfolio-contact"',
        'class="portfolio-contact" data-ambient',
        1,
    )
    return text


def inject_visuals_and_links(text: str) -> str:
    closing_marker = "<!-- ============ CLOSING ============ -->"
    pos = text.find(closing_marker)
    if pos == -1:
        raise SystemExit("Closing marker not found for visuals injection")
    block = build_visuals_section() + build_live_links_section()
    return text[:pos] + block + "\n" + text[pos:]


def apply_execution_mockup(text: str) -> str:
    if not EXEC_MOCKUP.exists():
        print(f"Warning: {EXEC_MOCKUP} not found — keeping source Execution image")
        return text
    text, ok = replace_data_uri_img(
        text,
        '<div class="exec-hero-mockup">',
        "../assets/media/case-studies/execution-mockup.png",
        "ACKO Enterprise device mockup",
    )
    if not ok:
        raise SystemExit("Failed to replace Execution section mockup image")
    print(f"Using Execution mockup: {EXEC_MOCKUP.name}")
    return text


def apply_overview_slides(text: str) -> str:
    replaced = 0
    search_from = 0
    for i in range(1, 7):
        path = None
        for ext in (".png", ".webp", ".jpg", ".jpeg"):
            candidate = OVERVIEW_DIR / f"overview-{i}{ext}"
            if candidate.exists():
                path = candidate
                break
        if not path:
            continue

        marker = CAROUSEL_SLIDE_IMG
        pos = text.find(marker, search_from)
        if pos == -1:
            break

        alt = OVERVIEW_ALTS[i - 1] if i - 1 < len(OVERVIEW_ALTS) else f"Overview slide {i}"
        rel = f"../assets/media/case-studies/overview/{path.name}"
        chunk_start = pos
        text_part, ok = replace_data_uri_img(text[chunk_start:], marker, rel, alt)
        if not ok:
            break
        text = text[:chunk_start] + text_part
        replaced += 1
        search_from = chunk_start + len(f'<div class="carousel-slide"><img src="{rel}"')

    if replaced:
        print(f"Replaced {replaced} carousel slide(s) with files from {OVERVIEW_DIR}")
    else:
        print("No overview/*.png slides found — keeping embedded carousel images")
    return text


def apply_grid_slides(text: str) -> str:
    replaced = 0
    search_from = text.find('<div class="grid-6">')
    if search_from == -1:
        return text

    for i in range(1, 7):
        path = None
        for ext in (".png", ".webp", ".jpg", ".jpeg"):
            candidate = OVERVIEW_DIR / f"overview-{i}{ext}"
            if candidate.exists():
                path = candidate
                break
        if not path:
            continue

        marker = GRID_BODY_IMG
        pos = text.find(marker, search_from)
        if pos == -1:
            break

        alt = OVERVIEW_ALTS[i - 1] if i - 1 < len(OVERVIEW_ALTS) else f"Landing page {i}"
        rel = f"../assets/media/case-studies/overview/{path.name}"
        chunk_start = pos
        text_part, ok = replace_data_uri_img(text[chunk_start:], marker, rel, alt)
        if not ok:
            break
        text = text[:chunk_start] + text_part
        replaced += 1
        search_from = chunk_start + len(f'<div class="browser-body"><img src="{rel}"')

    if replaced:
        print(f"Replaced {replaced} grid landing page image(s) from {OVERVIEW_DIR}")
    return text


def strip_grid_inline_heights(text: str) -> str:
    return text.replace('class="browser-body" style="height:260px;"', 'class="browser-body"')


def apply_portfolio_closing(text: str) -> str:
    closing_marker = "<!-- ============ CLOSING ============ -->"
    footer_open = '<footer class="reveal">'
    start = text.find(closing_marker)
    if start == -1:
        raise SystemExit("Closing section not found")
    footer_start = text.find(footer_open, start)
    if footer_start == -1:
        raise SystemExit("Case study closing footer not found")
    footer_end = text.find("</footer>", footer_start)
    if footer_end == -1:
        raise SystemExit("Case study closing footer end not found")
    footer_end += len("</footer>")

    inner = text[footer_start + len(footer_open):footer_end - len("</footer>")]
    replacement = (
        f"{closing_marker}\n"
        f'<section class="case-closing reveal">{inner}</section>\n'
        f"{PORTFOLIO_CONTACT.strip()}\n"
        f"{PORTFOLIO_FOOTER.strip()}\n"
    )
    return text[:start] + replacement + text[footer_end:]


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    LANDING_DIR.mkdir(parents=True, exist_ok=True)

    text = SRC.read_text(encoding="utf-8")
    assert "</html>" in text

    text = text.replace("<body>", '<body class="case-study-page">', 1)
    text = text.replace("</head>", HEAD_INJECT + "\n</head>", 1)

    text, removed = TOPNAV_PATTERN.subn("", text, count=1)
    if removed != 1:
        raise SystemExit("Failed to remove case study topnav block")

    text = replace_hero_video(text)
    text = apply_execution_mockup(text)
    text = apply_overview_slides(text)
    text = strip_grid_inline_heights(text)
    text = apply_grid_slides(text)
    text = inject_visuals_and_links(text)
    text = apply_portfolio_closing(text)
    text = strip_progress_rail(text)
    text = inject_ambient_markers(text)

    body_idx = text.find("<body")
    body_end = text.index(">", body_idx) + 1
    text = text[:body_end] + NAV_SHELL + text[body_end:]

    hero_inner = '<div class="wrap-wide hero-inner">'
    if hero_inner not in text:
        raise SystemExit("Hero inner container not found")
    text = text.replace(
        hero_inner,
        hero_inner + "\n    " + BACK_LINK.strip() + "\n",
        1,
    )

    text = text.replace(
        "        stageLabel.textContent = e.target.textContent.toUpperCase();",
        "        if (stageLabel) stageLabel.textContent = e.target.textContent.toUpperCase();",
    )
    text = text.replace(
        "    fill.style.height = scrolled + '%';",
        "    if (fill) fill.style.height = scrolled + '%';",
    )

    reveal_fallback = """
  document.querySelectorAll('.reveal').forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.92 && rect.bottom > 0) {
      el.classList.add('is-visible');
    }
  });
"""
    text = text.replace(
        "  document.querySelectorAll('.reveal').forEach(el => io.observe(el));",
        "  document.querySelectorAll('.reveal').forEach(el => io.observe(el));" + reveal_fallback,
    )

    carousel_autoplay = f"""
    let autoplayTimer = setInterval(() => moveCarousel(1), {CAROUSEL_INTERVAL_MS});
    const carouselEl = document.getElementById('overviewCarousel');
    if (carouselEl) {{
      carouselEl.addEventListener('mouseenter', () => clearInterval(autoplayTimer));
      carouselEl.addEventListener('mouseleave', () => {{
        autoplayTimer = setInterval(() => moveCarousel(1), {CAROUSEL_INTERVAL_MS});
      }});
    }}
"""
    marker = "    window.moveCarousel = function(dir){\n      idx = (idx + dir + slides.length) % slides.length;\n      update();\n    };\n  })();"
    replacement = (
        "    window.moveCarousel = function(dir){\n"
        "      idx = (idx + dir + slides.length) % slides.length;\n"
        "      update();\n"
        "    };" + carousel_autoplay + "\n  })();"
    )
    if marker not in text:
        raise SystemExit("Carousel script block not found — autoplay injection failed")
    text = text.replace(marker, replacement)

    text = text.replace("</body>", FOOT_INJECT + "\n</body>", 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"Built {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
