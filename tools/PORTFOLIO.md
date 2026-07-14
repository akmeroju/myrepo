# Portfolio tooling

The portfolio was split to stop accidental corruption of the 21MB monolithic HTML file.

## Architecture

```
index.html   ← HTML shell (~3.7MB, has inline carousel fallbacks)
assets/portfolio.css               ← All styles (safe to edit)
assets/portfolio.js                ← All logic (safe to edit)
assets/portfolio.frames.js         ← Hero frame data (DO NOT EDIT)
.portfolio-backups/                ← Auto backups before writes
```

## Commands

```bash
# Validate everything (run after every edit)
python3 tools/portfolio_guard.py validate

# Backup before manual edits
python3 tools/portfolio_guard.py backup

# Restore latest backup if something breaks
python3 tools/portfolio_guard.py restore

# Re-split (only if you restored a monolith backup)
python3 tools/split_portfolio.py
```

## Editing rules

1. **Styles** → `assets/portfolio.css`
2. **JavaScript** → `assets/portfolio.js`
3. **HTML structure** → `index.html` (avoid bulk search-replace)
4. **Never edit** → `assets/portfolio.frames.js`
5. **Never run** → `apply_*.py` after split (they are blocked)

## Why pages kept breaking

Edits used search/replace on the full HTML file. The file contains megabytes of base64
image data — the same strings can appear inside that data, truncating the file mid-script
and causing `SyntaxError` that breaks the entire page.

Splitting CSS and JS into small external files eliminates that risk for 95% of changes.

## Local preview

```bash
python3 -m http.server 8080
# Open http://localhost:8080/
```
