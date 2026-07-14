#!/usr/bin/env python3
"""
Portfolio integrity guard — backup, validate, safe write, auto-rollback.

NEVER edit adithya_portfolio_v16_fixed.html with raw search-replace on the
monolith. Edit assets/portfolio.css, assets/portfolio.js, or HTML body markers.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "adithya_portfolio_v16_fixed.html"
CSS = ROOT / "assets" / "portfolio.css"
JS = ROOT / "assets" / "portfolio.js"
FRAMES = ROOT / "assets" / "portfolio.frames.js"
BACKUP_DIR = ROOT / ".portfolio-backups"
MIN_HTML_BYTES = 500_000  # slim shell after split; monolith was ~21M
MIN_MONOLITH_BYTES = 19_000_000
EXTERNAL_MODE_MARKER = 'href="assets/portfolio.css"'


class ValidationError(Exception):
    pass


def is_external_mode(text: str | None = None) -> bool:
    if text is None:
        if not HTML.exists():
            return False
        head = HTML.read_text(encoding="utf-8", errors="replace")[:8000]
        return EXTERNAL_MODE_MARKER in head
    return EXTERNAL_MODE_MARKER in text


def backup_file(path: Path, label: str = "manual") -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"{path.name}.{ts}.{label}.bak"
    shutil.copy2(path, dest)
    _rotate_backups(path.name, keep=8)
    return dest


def _rotate_backups(filename: str, keep: int = 8) -> None:
    files = sorted(BACKUP_DIR.glob(f"{filename}.*.bak"), key=lambda p: p.stat().st_mtime)
    for old in files[:-keep]:
        old.unlink(missing_ok=True)


def _node_check_js(source: str, label: str) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(source)
        tmp = f.name
    try:
        r = subprocess.run(
            ["node", "--check", tmp],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise ValidationError(f"{label} JS syntax error:\n{r.stderr[:800]}")
    finally:
        Path(tmp).unlink(missing_ok=True)


def validate_html(text: str) -> None:
    if not text.strip().endswith("</html>"):
        raise ValidationError("HTML missing closing </html> — file likely truncated.")
    if text.count("<script") != text.count("</script>"):
        raise ValidationError(
            f"Unbalanced script tags: {text.count('<script')} open vs "
            f"{text.count('</script>')} close."
        )
    if "<body" not in text or "</head>" not in text:
        raise ValidationError("HTML missing <body> or </head>.")

    external = is_external_mode(text)
    size = len(text.encode("utf-8"))
    if external:
        if size < MIN_HTML_BYTES:
            raise ValidationError(f"HTML shell too small ({size:,} bytes) — likely truncated.")
    else:
        if size < MIN_MONOLITH_BYTES:
            raise ValidationError(
                f"Monolithic HTML too small ({size:,} bytes, need >={MIN_MONOLITH_BYTES:,}). "
                "Run: python3 tools/split_portfolio.py"
            )
        scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", text)
        logic_blocks = [s for s in scripts if len(s) > 1000]
        if logic_blocks:
            _node_check_js(logic_blocks[-1], "inline")


def validate_external_assets() -> None:
    if not CSS.exists():
        raise ValidationError(f"Missing {CSS.relative_to(ROOT)}")
    if not JS.exists():
        raise ValidationError(f"Missing {JS.relative_to(ROOT)}")
    if not FRAMES.exists():
        raise ValidationError(f"Missing {FRAMES.relative_to(ROOT)}")
    frames = FRAMES.read_text(encoding="utf-8", errors="replace")
    if "const FRAMES" not in frames:
        raise ValidationError("portfolio.frames.js missing FRAMES array.")
    if len(frames.encode("utf-8")) < 15_000_000:
        raise ValidationError("portfolio.frames.js too small — FRAMES blob may be truncated.")
    _node_check_js(JS.read_text(encoding="utf-8"), "portfolio.js")


def validate_all() -> None:
    if not HTML.exists():
        raise ValidationError(f"Missing {HTML.name}")
    text = HTML.read_text(encoding="utf-8", errors="replace")
    validate_html(text)
    if is_external_mode(text):
        validate_external_assets()


def safe_write(path: Path, content: str, *, skip_backup: bool = False) -> None:
    """Write file with pre/post validation and rollback on failure."""
    original = path.read_text(encoding="utf-8") if path.exists() else None
    if not skip_backup and path.exists():
        backup_file(path, label="pre-write")

    path.write_text(content, encoding="utf-8")
    try:
        if path == HTML:
            validate_html(content)
            if is_external_mode(content):
                validate_external_assets()
        elif path == JS:
            _node_check_js(content, "portfolio.js")
        elif path == FRAMES:
            if "const FRAMES" not in content:
                raise ValidationError("FRAMES constant missing after write.")
            if len(content.encode("utf-8")) < 15_000_000:
                raise ValidationError("FRAMES file too small after write.")
        validate_all()
    except Exception:
        if original is not None:
            path.write_text(original, encoding="utf-8")
        elif path.exists():
            path.unlink()
        raise


def restore_latest_backup(filename: str | None = None) -> Path:
    filename = filename or HTML.name
    files = sorted(BACKUP_DIR.glob(f"{filename}.*.bak"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise ValidationError(f"No backups found for {filename} in {BACKUP_DIR}")
    latest = files[-1]
    dest = ROOT / filename if filename else HTML
    shutil.copy2(latest, dest)
    validate_all()
    return latest


def main() -> int:
    parser = argparse.ArgumentParser(description="Portfolio integrity guard")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="Validate portfolio files")
    sub.add_parser("backup", help="Backup main HTML file")

    p_restore = sub.add_parser("restore", help="Restore latest backup")
    p_restore.add_argument("--file", default=HTML.name)

    args = parser.parse_args()
    try:
        if args.cmd == "validate":
            validate_all()
            mode = "external (split)" if is_external_mode() else "monolith"
            print(f"OK — portfolio valid ({mode})")
        elif args.cmd == "backup":
            path = backup_file(HTML)
            print(f"Backed up to {path}")
        elif args.cmd == "restore":
            path = restore_latest_backup(args.file)
            print(f"Restored from {path}")
    except ValidationError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
