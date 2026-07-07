# nien.ai website

Marketing site for Nien, the control plane for autonomous work.

Static HTML, no framework. Pages are generated from shared parts:

- `parts/shell.css` — shared styles (light + dark theme)
- `parts/pages/*.body.html` — per-page content
- `build.py` — assembles the final pages

To rebuild after editing content:

```
python3 build.py
```

Content source of truth: `website-content-v1.org` (internal).
