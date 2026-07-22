"""Shared portfolio chrome for case study pages."""
from __future__ import annotations

import re

CONTACT_CSS_MARKER = "case-study-contact.css"
CONTACT_MARKER = "portfolio-contact"
FOOTER_CSS_MARKER = "case-study-footer.css"
FOOTER_PATTERN = re.compile(r"<footer[^>]*>.*?</footer>", re.DOTALL)


def portfolio_contact() -> str:
    return """
<section id="contact" class="portfolio-contact">
  <div class="contact-glow"></div>
  <p class="contact-lbl">Available for opportunities</p>
  <h2 class="contact-h">Let's <em>Talk.</em></h2>
  <p class="contact-sub">Open to full-time roles and freelance projects.</p>
  <div class="contact-actions">
    <a class="contact-btn" href="mailto:akmeroju@gmail.com">akmeroju@gmail.com</a>
    <a class="contact-btn-outline" href="https://linkedin.com/in/adithyameroju" target="_blank" rel="noopener noreferrer">LinkedIn &rarr;</a>
  </div>
  <div class="contact-info">
    <div class="cinfo-item">
      <div class="cinfo-label">Phone</div>
      <div class="cinfo-val"><a href="tel:+919700562332">+91 97005 62332</a></div>
    </div>
    <div class="cinfo-item">
      <div class="cinfo-label">Email</div>
      <div class="cinfo-val"><a href="mailto:akmeroju@gmail.com">akmeroju@gmail.com</a></div>
    </div>
    <div class="cinfo-item">
      <div class="cinfo-label">Location</div>
      <div class="cinfo-val">Bengaluru, India</div>
    </div>
  </div>
</section>
""".strip()


def portfolio_footer(asset_prefix: str) -> str:
    return f"""
<footer class="portfolio-site-footer">
  <div class="footer-illustration">
    <div class="footer-hero-wrap">
      <img src="{asset_prefix}assets/media/footer-illustration-v2.png" alt="Designer workspace" class="footer-hero-img" loading="lazy" decoding="async">
      <p class="footer-hero-caption">Still designing. Still learning. <span class="caption-gold">Still curious.</span></p>
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


def contact_css_link(asset_prefix: str) -> str:
    return f'<link rel="stylesheet" href="{asset_prefix}assets/case-study-contact.css">'


def footer_css_link(asset_prefix: str) -> str:
    return f'<link rel="stylesheet" href="{asset_prefix}assets/case-study-footer.css">'


def apply_portfolio_contact(text: str) -> str:
    if CONTACT_MARKER in text:
        return text

    contact = portfolio_contact()
    footer_match = FOOTER_PATTERN.search(text)
    if footer_match:
        pos = footer_match.start()
        return text[:pos] + contact + "\n\n" + text[pos:]

    return text.replace("</body>", f"{contact}\n</body>", 1)


def apply_portfolio_footer(text: str, asset_prefix: str) -> str:
    footer = portfolio_footer(asset_prefix)
    if FOOTER_PATTERN.search(text):
        return FOOTER_PATTERN.sub(footer, text, count=1)
    return text.replace("</body>", f"{footer}\n</body>", 1)


def ensure_contact_css(text: str, asset_prefix: str) -> str:
    if CONTACT_CSS_MARKER in text:
        return text
    return text.replace("</head>", f"{contact_css_link(asset_prefix)}\n</head>", 1)


def ensure_footer_css(text: str, asset_prefix: str) -> str:
    if FOOTER_CSS_MARKER in text:
        return text
    return text.replace("</head>", f"{footer_css_link(asset_prefix)}\n</head>", 1)
