#!/usr/bin/env python3
"""Assemble the nien.ai site from parts/.

Usage:
  python3 build.py                     # emit deployable pages into this dir (relative links)
  python3 build.py --preview OUT MAP   # emit artifact-preview pages into OUT, rewriting
                                       # page links using the JSON url map at MAP
                                       # ({"index.html": "https://...", ...})
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PARTS = ROOT / "parts"

PAGES = [
    # file, nav label, title, meta description
    ("index.html", "Home",
     "Nien — The control plane for autonomous work",
     "Nien is the control plane for autonomous work. Scoped access to your data, rules your team owns, and a track record for every agent."),
    ("platform.html", "Platform",
     "Platform — Nien",
     "How Nien works, in five steps: connect your systems, set your rules, agents work under supervision, agents earn autonomy, everything goes on the record."),
    ("security.html", "Security & Control",
     "Security & Control — Nien",
     "How Nien keeps agents inside the lines: rules checked the same way every time, approval workflows, instant revocation, and a complete signed record of every action."),
    ("solutions.html", "Solutions",
     "Solutions — Nien",
     "What Nien-governed agents do in finance operations: accounts payable, bookkeeping and reconciliation, collections, and treasury oversight."),
    ("demo.html", "Live demo",
     "Live demo — Nien",
     "Watch a synthetic month of finance ops run itself: agents read the inbox, keep parallel books, catch a duplicate invoice and a changed bank account, and route every judgment call to a person."),
    ("pricing.html", "Pricing",
     "Pricing — Nien",
     "Nien is priced for the work agents complete, not per seat and not per conversation. Pilot, Growth, and Enterprise tiers."),
    ("builders.html", "For Agent Builders",
     "For Agent Builders — Nien",
     "Bring your agent to enterprises through Nien. Scoped data access you could never negotiate alone, and a track record that sells for you."),
    ("about.html", "About",
     "About — Nien",
     "Why Nien exists: agents will do real work inside companies, but only if the company stays in control, and control should not cost Fortune-500 money."),
]

LOGO_B64 = (PARTS / "logo96.b64").read_text().strip()
LOGO_URI = f"data:image/png;base64,{LOGO_B64}"
CSS = (PARTS / "shell.css").read_text()

NAV_TMPL = """<header class="nav">
  <div class="wrap nav-inner">
    <a class="wordmark" href="{home}"><img src="{logo}" alt="">Nien</a>
    <nav class="nav-links" aria-label="Pages">
{links}
    </nav>
    <a class="btn btn-primary btn-sm" href="#contact">Book a demo</a>
  </div>
</header>
"""

FOOTER_TMPL = """<footer>
  <div class="wrap">
    <div class="foot-grid">
      <a class="wordmark" href="{home}"><img src="{logo}" alt="">Nien</a>
      <nav aria-label="Footer">
{links}
      </nav>
    </div>
    <div class="foot-contact">
      <span>demos → book a demo</span>
      <span>builders → apply to list your agent</span>
      <span>press → talk to us</span>
    </div>
  </div>
</footer>
"""

SCRIPT = """<script>
  (function () {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var els = document.querySelectorAll(".reveal");
    if (reduce || !("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  })();
</script>
"""


def build_page(fname, title, meta, body, url_map):
    def href(f):
        return url_map.get(f, f)

    nav_links = "\n".join(
        f'      <a href="{href(f)}"{" aria-current=\"page\"" if f == fname else ""}>{label}</a>'
        for f, label, _, _ in PAGES if f != "index.html"
    )
    foot_links = "\n".join(
        f'        <a href="{href(f)}">{label}</a>'
        for f, label, _, _ in PAGES
    )

    # rewrite cross-page links inside the body
    for f, _, _, _ in PAGES:
        body = body.replace(f'href="{f}', f'href="{href(f)}')

    nav = NAV_TMPL.format(home=href("index.html"), logo=LOGO_URI, links=nav_links)
    footer = FOOTER_TMPL.format(home=href("index.html"), logo=LOGO_URI, links=foot_links)

    return (
        f"<title>{title}</title>\n"
        f'<meta name="description" content="{meta}">\n'
        f"<style>\n{CSS}</style>\n\n"
        f"{nav}\n<main>\n{body}\n</main>\n\n{footer}\n{SCRIPT}"
    )


def main():
    preview = "--preview" in sys.argv
    if preview:
        i = sys.argv.index("--preview")
        out_dir = Path(sys.argv[i + 1])
        url_map = json.loads(Path(sys.argv[i + 2]).read_text())
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = ROOT
        url_map = {}

    for fname, label, title, meta in PAGES:
        body = (PARTS / "pages" / f"{fname.removesuffix('.html')}.body.html").read_text()
        if preview:
            html = build_page(fname, title, meta, body, url_map)
            out = out_dir / ("nien-home.html" if fname == "index.html" else f"nien-{fname}")
        else:
            # full standalone document for deployment
            inner = build_page(fname, title, meta, body, {})
            head_part, _, body_part = inner.partition("<header")
            html = (
                "<!doctype html>\n"
                '<html lang="en">\n<head>\n'
                '<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                f'<link rel="icon" type="image/png" href="{LOGO_URI}">\n'
                f"{head_part}</head>\n<body>\n<header{body_part}\n</body>\n</html>\n"
            )
            out = out_dir / fname
        out.write_text(html)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
