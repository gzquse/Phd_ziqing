#!/usr/bin/env python3
"""Derive slides/artifact.html (no doctype/html/head/body — the claude.ai Artifact host adds its own
skeleton) from the standalone slides/index.html. Run after editing index.html, then republish."""
import re, pathlib
src = pathlib.Path("slides/index.html").read_text(encoding="utf-8")
title = re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip()
head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
styles = "\n".join(re.findall(r"<style>.*?</style>", head, re.S))
body = re.search(r"<body[^>]*>(.*?)</body>", src, re.S).group(1)
out = f"<title>{title}</title>\n{styles}\n{body}\n"
pathlib.Path("slides/artifact.html").write_text(out, encoding="utf-8")
print(f"wrote slides/artifact.html ({len(out)//1024} KB), title: {title}")
