#!/usr/bin/env python3
"""Build local-only preview for new ADSC case study (does not touch live adsc.html)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from portfolio_shell import (
    apply_portfolio_contact,
    apply_portfolio_footer,
    ensure_contact_css,
    ensure_footer_css,
)
DRAFTS = ROOT / "case-studies" / "_drafts"
SRC = DRAFTS / "adsc-new.source.html"
OUT = DRAFTS / "adsc-new.html"
HOME = "../../"

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
    <a class="nav-resume" href="https://drive.google.com/file/d/1DKPi8jJ2Ji4PxIV6TdTWAtyXx9faUarY/view?usp=drivesdk" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Resume</a>
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
"""

BACK_LINK = f"""<a class="case-back case-back-body" href="{HOME}#work">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
      <span>Back to portfolio</span>
    </a>
"""

HEAD_INJECT = """
<link rel="stylesheet" href="../../assets/case-study-nav.css">
<link rel="stylesheet" href="adsc-new-shell.css">
"""

FOOT_INJECT = """
<script src="../../assets/case-study-nav.js"></script>
"""

NAV_MARKER = '<div id="progress-bar"></div>'
BACK_MARKER = 'class="case-back case-back-body"'
HEAD_MARKER = 'adsc-new-shell.css'
FOOT_MARKER = 'case-study-nav.js'
PROGRESS_RAIL = '<div class="progress-rail"><div class="progress-fill" id="progressFill"></div></div>'
HERO_OPEN = '<header class="hero" id="top">\n  <div class="wrap">'


def build() -> None:
    if not SRC.exists():
        raise SystemExit(
            f"Source not found: {SRC}\n"
            "Copy acko-drive-case-study_3.html to case-studies/_drafts/adsc-new.source.html"
        )

    text = SRC.read_text(encoding="utf-8")

    text = text.replace(f"{PROGRESS_RAIL}\n\n", "")
    text = text.replace(PROGRESS_RAIL, "")

    if HEAD_MARKER not in text:
        text = text.replace("</head>", f"{HEAD_INJECT.strip()}\n</head>", 1)

    text = re.sub(
        r"<body(\s[^>]*)?>",
        '<body class="case-study-page adsc-new-page">',
        text,
        count=1,
    )

    if NAV_MARKER not in text:
        text = text.replace(
            '<body class="case-study-page adsc-new-page">',
            f'<body class="case-study-page adsc-new-page">{NAV_SHELL.strip()}\n',
            1,
        )

    if BACK_MARKER not in text and HERO_OPEN in text:
        text = text.replace(
            HERO_OPEN,
            f"{HERO_OPEN}\n    {BACK_LINK.strip()}\n",
            1,
        )

    text = ensure_contact_css(text, HOME)
    text = ensure_footer_css(text, HOME)
    text = apply_portfolio_contact(text)
    text = apply_portfolio_footer(text, HOME)

    if FOOT_MARKER not in text:
        text = text.replace("</body>", f"{FOOT_INJECT.strip()}\n</body>", 1)

    OUT.write_text(text, encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)} (local draft — not linked from live site)")


if __name__ == "__main__":
    build()
