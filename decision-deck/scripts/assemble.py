#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Assemble a deck from a slides fragment and the template (stdlib only).

    python scripts/assemble.py slides.html -o deck.html \
        --title "Q3 platform review" --lang pt-BR --theme navy --footer "Data · Internal"

slides.html holds only the <section> elements, in order. The template's CSS and
runtime stay untouched, so the CSP pin keeps working and nothing is truncated.
"""
import argparse
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
MARKER = re.compile(r"<!-- SLIDES GO HERE:.*?-->", re.S)
THEMES = {"navy", "light", "graphite"}
LANG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slides", help="file with the <section> elements")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--lang", default="en", help="BCP 47 tag, e.g. en, pt-BR, es")
    ap.add_argument("--theme", default="navy", choices=sorted(THEMES))
    ap.add_argument("--footer", default="", help="left footer text on content slides")
    a = ap.parse_args()

    if not LANG.match(a.lang):
        raise SystemExit(f"invalid --lang '{a.lang}'")
    slides = Path(a.slides).read_text(encoding="utf-8").strip()
    if "<section" not in slides:
        raise SystemExit("slides file has no <section> elements")
    if re.search(r"<script(?![^>]*type=\"application/json\")", slides, re.I):
        raise SystemExit("slides may only contain <script type=\"application/json\"> chart data")

    t = TEMPLATE.read_text(encoding="utf-8")
    t, n = MARKER.subn(lambda _: slides, t, count=1)
    if n != 1:
        raise SystemExit("slides marker not found in template")
    t = t.replace('<html lang="en" data-theme="navy">', f'<html lang="{a.lang}" data-theme="{a.theme}">', 1)
    t = t.replace("<title>[DECK TITLE]</title>", f"<title>{html.escape(a.title)}</title>", 1)
    t = t.replace("<body>", f'<body data-footer="{html.escape(a.footer, quote=True)}">', 1)
    Path(a.out).write_text(t, encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
