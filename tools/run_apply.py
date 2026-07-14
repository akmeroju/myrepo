#!/usr/bin/env python3
"""Run portfolio apply scripts safely (backup + validate). Monolith mode only."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from portfolio_guard import ValidationError, backup_file, is_external_mode, validate_all  # noqa: E402


def main() -> int:
    if is_external_mode():
        print(
            "Portfolio is in SPLIT mode.\n"
            "Do NOT run apply_*.py — edit these files instead:\n"
            "  assets/portfolio.css   (styles)\n"
            "  assets/portfolio.js    (logic)\n"
            "  adithya-portfolio.html (HTML structure only)\n\n"
            "After edits: python3 tools/portfolio_guard.py validate",
            file=sys.stderr,
        )
        return 1

    scripts = sys.argv[1:] or ["apply_updates.py", "apply_polish.py", "apply_fixes.py"]
    backup_file(ROOT / "adithya-portfolio.html", label="pre-apply-batch")

    for script in scripts:
        path = ROOT / script
        if not path.exists():
            print(f"Missing {script}", file=sys.stderr)
            return 1
        print(f"Running {script}...")
        r = subprocess.run([sys.executable, str(path)], cwd=ROOT)
        if r.returncode != 0:
            print(f"FAILED: {script}", file=sys.stderr)
            return r.returncode

    try:
        validate_all()
        print("All apply scripts OK.")
    except ValidationError as e:
        print(f"Validation failed after apply: {e}", file=sys.stderr)
        print("Restore: python3 tools/portfolio_guard.py restore", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
