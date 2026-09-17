#!/usr/bin/env python3
"""Export slides/index.html to a PDF handout (one slide per landscape page) with headless Chromium."""
import sys, pathlib
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "slides/index.html").resolve()
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "slides/defense-slides.pdf").resolve()
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(src.as_uri())
    page.wait_for_timeout(500)
    page.emulate_media(media="print")
    page.pdf(path=str(out), landscape=True, print_background=True, prefer_css_page_size=True)
    browser.close()
print(f"wrote {out}")
