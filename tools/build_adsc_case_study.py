#!/usr/bin/env python3
"""Inject portfolio nav shell + back link into ADSC case study."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case-studies" / "adsc.html"
HOME = "../adithya_portfolio_v16_fixed.html"

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
<link rel="stylesheet" href="../assets/case-study-nav.css">
<link rel="stylesheet" href="../assets/case-study-adsc-shell.css">
"""

FOOT_INJECT = """
<script src="../assets/case-study-nav.js"></script>
"""

NAV_MARKER = '<div id="progress-bar"></div>'
BACK_MARKER = 'class="case-back case-back-body"'
HEAD_MARKER = 'case-study-adsc-shell.css'
FOOT_MARKER = 'case-study-nav.js'

TRACKER_CSS = re.compile(
    r"\n  #tracker\{[^}]+\}\n"
    r"  #tracker \.wrap\{[^}]+\}\n"
    r"  #tracker \.wrap::-webkit-scrollbar\{[^}]+\}\n"
    r"  \.brand-mini\{[^}]+\}\n"
    r"  \.brand-mini span\{[^}]+\}\n"
    r"  \.stages\{[^}]+\}\n"
    r"  \.stage\{[^}]+\}\n"
    r"  \.stage \.dot\{[^}]+\}\n"
    r"  \.stage\.active\{[^}]+\}\n"
    r"  \.stage\.active \.dot\{[^}]+\}\n"
    r"  \.stage\.done \.dot\{[^}]+\}\n"
    r"  \.stage-track\{[^}]+\}\n"
    r"  \.stage-track\.filled\{[^}]+\}\n"
    r"  #progressbar\{[^}]+\}\n",
    re.DOTALL,
)
TRACKER_NAV = re.compile(r"\n<nav id=\"tracker\">.*?</nav>\n", re.DOTALL)
STAGE_SCRIPT = re.compile(
    r"\n<script>\n  const stageDefs = \[.*?</script>\n(?=<script src=\"\.\./assets/case-study-nav\.js\">)",
    re.DOTALL,
)


def strip_adsc_tracker(text: str) -> str:
    text, _ = TRACKER_CSS.subn("\n", text)
    text, _ = TRACKER_NAV.subn("\n", text)
    text, _ = STAGE_SCRIPT.subn("\n", text)
    return text


def build() -> None:
    text = OUT.read_text(encoding="utf-8")

    text = strip_adsc_tracker(text)

    if HEAD_MARKER not in text:
        text = text.replace("</head>", f"{HEAD_INJECT.strip()}\n</head>", 1)

    text = re.sub(r"<body(\s[^>]*)?>", '<body class="case-study-page adsc-page">', text, count=1)

    if NAV_MARKER not in text:
        text = text.replace("<body class=\"case-study-page adsc-page\">", f'<body class="case-study-page adsc-page">{NAV_SHELL.strip()}\n', 1)

    if BACK_MARKER not in text:
        text = text.replace(
            '<section id="hero">\n  <div class="wrap">',
            f'<section id="hero">\n  <div class="wrap">\n    {BACK_LINK.strip()}\n',
            1,
        )

    if FOOT_MARKER not in text:
        text = text.replace("</body>", f"{FOOT_INJECT.strip()}\n</body>", 1)

    OUT.write_text(text, encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
