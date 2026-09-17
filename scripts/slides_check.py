#!/usr/bin/env python3
"""Walk through every slide of slides/index.html in headless Chromium; fail on console errors / page errors."""
import sys, pathlib
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "slides/index.html").resolve()
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.goto(src.as_uri())
    page.wait_for_timeout(400)
    n = page.evaluate("document.querySelectorAll('.slide').length")
    for _ in range(n + 2):
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(120)
    for _ in range(n + 2):
        page.keyboard.press("ArrowLeft"); page.wait_for_timeout(60)
    browser.close()
print(f"{n} slides walked; {len(errors)} errors")
for e in errors: print("  ", e)
sys.exit(1 if errors else 0)
