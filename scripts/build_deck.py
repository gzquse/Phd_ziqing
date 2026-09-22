#!/usr/bin/env python3
"""Compose a deck from a manifest: reuse slides of the defense deck by data-id, apply per-slide overrides,
and drop in new slide modules — so a variant (the ORNL seminar, a short talk) is a list you edit, not a copy
you maintain.

    python3 scripts/build_deck.py slides-ornl/deck.json          # writes slides-ornl/index.html + artifact.html

deck.json
  {
    "title": "…",                         # <title> and header comment
    "description": "…",                   # <meta name=description>
    "source": "../slides/index.html",     # engine, styles and the slide library (relative to the manifest)
    "sec_map": {"III · Q-GEAR": "Simulation · Q-GEAR", …},    # global renames of the bottom-left .sec labels
    "slides": [
      {"use": "qg-time"},                                     # a defense slide, verbatim
      {"use": "qg-table", "set": {".hd .kicker": "Takeaway", "h1": "42 qubits, program unchanged"},
                          "drop": [".lead"], "notes": "…", "group": "qgear", "title": "Overview title"},
      {"module": "modules/ornl-fit.html"},                    # a new slide: one <section class="slide"> in a file
      {"comment": "anything else is ignored"}
    ]
  }
"set" maps a CSS selector (inside the slide) to new innerHTML; "drop" removes matching elements — an entry may
also be {"selector": ".card", "contains": "COMMITTEE"} to remove only the match whose text contains a string.
Overrides run in headless Chromium, so inline SVG (viewBox, markers, …) survives untouched. Requires playwright."""
import json, re, sys, pathlib, subprocess
from playwright.sync_api import sync_playwright

manifest_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "slides-ornl/deck.json").resolve()
deck_dir = manifest_path.parent
cfg = json.loads(manifest_path.read_text(encoding="utf-8"))
src = (deck_dir / cfg.get("source", "../slides/index.html")).resolve()
out = deck_dir / "index.html"
html = src.read_text(encoding="utf-8")

APPLY_JS = r"""
([spec, secMap]) => {
  const s = document.querySelector(`#stage > .slide[data-id="${spec.use}"]`);
  if (!s) return null;
  const c = s.cloneNode(true);
  c.classList.remove('active', 'leaving');
  c.querySelectorAll('.brand, .pg, [data-x]').forEach(e => e.classList.contains('brand') || e.classList.contains('pg') ? e.remove() : e.removeAttribute('data-x'));
  for (const d of (spec.drop || [])) {
    if (typeof d === 'string') c.querySelectorAll(d).forEach(e => e.remove());
    else c.querySelectorAll(d.selector).forEach(e => { if (!d.contains || e.textContent.includes(d.contains)) e.remove(); });
  }
  for (const [sel, val] of Object.entries(spec.set || {})) { const e = c.querySelector(sel); if (e) e.innerHTML = val; }
  if (spec.notes !== undefined) { let n = c.querySelector('aside.notes'); if (!n) { n = document.createElement('aside'); n.className = 'notes'; c.appendChild(n); } n.innerHTML = spec.notes; }
  if (spec.group) c.setAttribute('data-morph-group', spec.group);
  if (spec.title) c.setAttribute('data-title', spec.title);
  if (spec.id) c.setAttribute('data-id', spec.id);
  const sec = c.querySelector('.sec'); if (sec && secMap && secMap[sec.textContent.trim()] !== undefined) sec.textContent = secMap[sec.textContent.trim()];
  return c.outerHTML;
}"""

sections, report = [], []
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(src.as_uri()); page.wait_for_timeout(500)
    for spec in cfg["slides"]:
        if "use" in spec:
            h = page.evaluate(APPLY_JS, [spec, cfg.get("sec_map", {})])
            if h is None: sys.exit(f"slide {spec['use']!r} not found in {src}")
            sections.append(h); report.append(f"{spec.get('id', spec['use'])}" + (" *" if any(k in spec for k in ("set", "drop", "notes", "group")) else ""))
        elif "module" in spec:
            frag = (deck_dir / spec["module"]).read_text(encoding="utf-8").strip()
            if not re.match(r'<section class="slide', frag): sys.exit(f"{spec['module']}: must start with <section class=\"slide …\">")
            sections.append(frag); report.append(f"{spec['module']} (module)")
    b.close()

m = re.search(r'(?s)^(.*<div id="stage">\n)(.*?)(\n</div>\n</div>\n\n<div id="progress".*)$', html)
if not m: sys.exit("could not find the #stage block in the source deck")
head, _, tail = m.groups()
head = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", head, count=1, flags=re.S)
if cfg.get("description"):
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{cfg["description"]}">', head, count=1)
head = head.replace("<!--\n  Ph.D. defense deck", f"<!--\n  Built by scripts/build_deck.py from {manifest_path.name} — edit the manifest, not this file.\n  Ph.D. defense deck", 1)
out.write_text(head + "\n".join(sections) + tail, encoding="utf-8")
print(f"wrote {out} with {len(sections)} slides:")
for i, r in enumerate(report, 1): print(f"  {i:2d}. {r}")
subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("build_artifact_fragment.py")), str(deck_dir)], check=True)
