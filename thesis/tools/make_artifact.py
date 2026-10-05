#!/usr/bin/env python3
"""Turn html/index.html (a complete pandoc document) into html/artifact.html, a page body
for the claude.ai Artifact publisher: <title> + inlined <style> + MathJax scripts + body.
The publisher wraps the fragment in its own doctype/head/body skeleton."""
import re, sys
from pathlib import Path
T = Path(__file__).resolve().parent.parent / 'html'
h = (T / 'index.html').read_text(encoding='utf8')
css = (T / 'style.css').read_text(encoding='utf8')
title = re.search(r'<title>(.*?)</title>', h, re.S).group(1).strip()
title = title.split(' - ')[0].strip() or 'Quantum Computing and Circuit Simulation'
head = re.search(r'<head[^>]*>(.*?)</head>', h, re.S).group(1)
cfg = re.search(r'<script>\s*(window\.MathJax\s*=.*?)</script>', head, re.S)
cfg = cfg.group(1) if cfg else ''
src = re.search(r'<script[^>]*src="(https://cdn\.jsdelivr\.net/npm/mathjax@3[^"]*)"', head)
src = src.group(1) if src else 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'
body = re.search(r'<body[^>]*>(.*)</body>', h, re.S).group(1)
# three-state theme: guard the dark media block and add the explicit data-theme block
m = re.search(r'@media \(prefers-color-scheme: dark\) \{\s*:root \{(.*?)\}\s*\}', css, re.S)
dark_tokens = m.group(1).strip() if m else ''
if m:
    css = css[:m.start()] + ('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { %s color-scheme: dark; } }\n'
                             ':root[data-theme="dark"] { %s color-scheme: dark; }\n' % (dark_tokens, dark_tokens)) + css[m.end():]
extra = """
/* artifact host adjustments */
.topbar { top: env(safe-area-inset-top, 0px); }
body { padding: 0; }
main { min-width: 0; }
table, pre { max-width: 100%; }
"""
out = f"<title>{title}</title>\n<style>\n{css}\n{extra}</style>\n<script>\n{cfg}\n</script>\n<script id=\"MathJax-script\" async src=\"{src}\"></script>\n{body}\n"
(T / 'artifact.html').write_text(out, encoding='utf8')
imgs = sorted(set(re.findall(r'src="(images/[^"]+)"', body)))
print('wrote', T / 'artifact.html', len(out), 'bytes;', len(imgs), 'image refs; title:', title)
