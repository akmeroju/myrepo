#!/usr/bin/env python3
"""
Split monolithic portfolio HTML into safe, editable external files.

After split:
  - assets/portfolio.css       (~30KB)  — edit styles here
  - assets/portfolio.js        (~15KB)  — edit logic here
  - assets/portfolio.frames.js (~17MB)  — DO NOT EDIT (hero frame data)
  - index.html     — HTML shell only (~1-2MB with inline img fallbacks)

Run once after restoring a valid monolith, or when migrating.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
CSS = ROOT / "assets" / "portfolio.css"
JS = ROOT / "assets" / "portfolio.js"
FRAMES = ROOT / "assets" / "portfolio.frames.js"

sys.path.insert(0, str(ROOT / "tools"))
from portfolio_guard import backup_file, validate_all, ValidationError  # noqa: E402


def find_frames_end(js: str) -> int:
    idx = js.find("const FRAMES = ")
    if idx < 0:
        raise ValidationError("Could not find const FRAMES in script block.")
    start = js.find("[", idx)
    depth = 0
    for j in range(start, len(js)):
        if js[j] == "[":
            depth += 1
        elif js[j] == "]":
            depth -= 1
            if depth == 0:
                end = j + 1
                while end < len(js) and js[end] in " \t;\n\r":
                    end += 1
                return end
    raise ValidationError("Unclosed FRAMES array.")


def split(text: str) -> tuple[str, str, str, str]:
    styles = re.findall(r"<style>([\s\S]*?)</style>", text)
    if not styles:
        raise ValidationError("No <style> block found.")
    css = styles[0].strip() + "\n"

    scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", text)
    logic_blocks = [(i, s) for i, s in enumerate(scripts) if len(s) > 1000]
    if not logic_blocks:
        raise ValidationError("No inline script block with portfolio logic found.")
    _, js_block = logic_blocks[0]

    frames_end = find_frames_end(js_block)
    frames_js = js_block[:frames_end].strip() + "\n"
    logic_js = js_block[frames_end:].strip() + "\n"

    if len(frames_js) < 15_000_000:
        raise ValidationError(
            f"FRAMES blob suspiciously small ({len(frames_js):,} chars). Aborting split."
        )
    if len(logic_js) < 5000:
        raise ValidationError("Logic JS too small after split.")

    html = text
    html = re.sub(r"<style>[\s\S]*?</style>", '<link rel="stylesheet" href="assets/portfolio.css">', html, count=1)

    script_pat = r"<script[^>]*>[\s\S]*?</script>"
    matches = list(re.finditer(script_pat, html))
    big = [m for m in matches if len(m.group(0)) > 1000]
    if not big:
        raise ValidationError("Could not locate main script tag in HTML.")
    m = big[0]
    replacement = (
        '<script src="assets/portfolio.frames.js"></script>\n'
        '<script src="assets/portfolio.js"></script>'
    )
    html = html[: m.start()] + replacement + html[m.end() :]

    return html, css, frames_js, logic_js


def main() -> int:
    if not HTML.exists():
        print(f"Missing {HTML}", file=sys.stderr)
        return 1

    text = HTML.read_text(encoding="utf-8")
    if 'href="assets/portfolio.css"' in text:
        print("Already split — nothing to do.")
        try:
            validate_all()
            print("Validation OK.")
        except ValidationError as e:
            print(f"Validation failed: {e}", file=sys.stderr)
            return 1
        return 0

    try:
        html, css, frames_js, logic_js = split(text)
    except ValidationError as e:
        print(f"Split aborted: {e}", file=sys.stderr)
        return 1

    backup_file(HTML, label="pre-split")
    CSS.parent.mkdir(parents=True, exist_ok=True)
    CSS.write_text(css, encoding="utf-8")
    FRAMES.write_text(frames_js, encoding="utf-8")
    JS.write_text(logic_js, encoding="utf-8")
    HTML.write_text(html, encoding="utf-8")

    try:
        validate_all()
    except ValidationError as e:
        print(f"Post-split validation failed: {e}", file=sys.stderr)
        print("Restore with: python3 tools/portfolio_guard.py restore", file=sys.stderr)
        return 1

    print("Split complete:")
    print(f"  {CSS.relative_to(ROOT)} ({CSS.stat().st_size:,} bytes)")
    print(f"  {FRAMES.relative_to(ROOT)} ({FRAMES.stat().st_size:,} bytes)")
    print(f"  {JS.relative_to(ROOT)} ({JS.stat().st_size:,} bytes)")
    print(f"  {HTML.name} ({HTML.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
