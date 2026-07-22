"""Shared portfolio chrome for case study pages."""
from __future__ import annotations

import re

FOOTER_CSS_MARKER = "case-study-footer.css"
FOOTER_PATTERN = re.compile(r"<footer[^>]*>.*?</footer>", re.DOTALL)


def portfolio_footer(asset_prefix: str) -> str:
    return f"""
<footer class="portfolio-site-footer">
  <div class="footer-illustration">
    <div class="footer-hero-wrap">
      <img src="{asset_prefix}assets/media/footer-illustration-v2.png" alt="Designer workspace" class="footer-hero-img" loading="lazy" decoding="async">
    </div>
  </div>
  <div class="footer-bottom">
    <p class="footer-copy">&copy; 2026 Adithya Kumar Meroju &mdash; Product Designer</p>
    <p class="footer-tagline">Crafted with curiosity, strategy &amp; a lot of Figma.</p>
    <div class="footer-links">
      <a href="https://linkedin.com/in/adithyameroju" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a href="mailto:akmeroju@gmail.com">Email</a>
    </div>
  </div>
</footer>
""".strip()


def footer_css_link(asset_prefix: str) -> str:
    return f'<link rel="stylesheet" href="{asset_prefix}assets/case-study-footer.css">'


def apply_portfolio_footer(text: str, asset_prefix: str) -> str:
    footer = portfolio_footer(asset_prefix)
    if FOOTER_PATTERN.search(text):
        return FOOTER_PATTERN.sub(footer, text, count=1)
    return text.replace("</body>", f"{footer}\n</body>", 1)


def ensure_footer_css(text: str, asset_prefix: str) -> str:
    if FOOTER_CSS_MARKER in text:
        return text
    return text.replace("</head>", f"{footer_css_link(asset_prefix)}\n</head>", 1)
