#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Validate a Decision Deck HTML file.

    python scripts/validate.py deck.html            # static checks (stdlib only)
    python scripts/validate.py deck.html --render   # + browser checks (needs playwright)

Exit code 0 = no errors (warnings may exist), 1 = errors.

Static checks
  - file is complete (ends with </html>) and has at least one <section>
  - runtime script is unchanged (its hash matches the CSP pin)
  - no extra executable scripts, on* handlers, javascript: URLs, iframes/objects
  - no external resources other than Google Fonts
  - every chart has valid JSON, a known type and no "</script" inside the data
  - placeholders left in the template ([DECK TITLE], data-footer)
  - writing: em/en dashes in visible text (warning), [brackets] left (warning)
  - structure: at most one .accent-solid per slide, notes on content slides,
    titles that look like labels instead of action titles (warning)
Render checks (--render)
  - no chart error messages, no JS errors
  - no content overflowing the slide's safe area
"""
import argparse
import base64
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

CHART_TYPES = {"bar", "column", "line", "bullet", "waterfall", "stack", "gantt"}
ALLOWED_EXTERNAL = ("https://fonts.googleapis.com/", "https://fonts.gstatic.com/")
DASHES = ("—", "–")


class Deck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = []          # list of dicts per slide
        self.cur = None
        self.depth = 0
        self.stack = []
        self.scripts = []           # (type, attrs, text, in_chart)
        self._script = None
        self.chart_depth = []
        self.errors = []
        self.text_chunks = []       # visible text, for dash check
        self._skip = 0              # inside script/style/aside
        self.h2 = None
        self.body_attrs = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k, v in attrs:
            if k.lower().startswith("on"):
                self.errors.append(f"inline event handler '{k}' on <{tag}>")
            if v and k in ("href", "src", "action", "formaction", "xlink:href") :
                low = v.strip().lower()
                if low.startswith("javascript:") or low.startswith("vbscript:"):
                    self.errors.append(f"{k}='{v[:40]}' on <{tag}>")
                if low.startswith(("http:", "https:", "//")) and not v.startswith(ALLOWED_EXTERNAL):
                    if tag == "a":
                        warn(f"external link in deck: {v[:60]}")
                    else:
                        self.errors.append(f"external resource on <{tag}>: {v[:60]}")
        style = a.get("style") or ""
        if re.search(r"url\(\s*['\"]?\s*(https?:|//|javascript:)", style, re.I) or "expression(" in style.lower() or "@import" in style.lower():
            self.errors.append(f"line {self.getpos()[0]}: external url()/import in style attribute on <{tag}>")
        if tag in ("iframe", "object", "embed", "form", "base", "frame", "frameset", "svg", "math", "template"):
            self.errors.append(f"forbidden tag <{tag}>")
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            self.errors.append("meta refresh is not allowed")
        if tag == "body":
            self.body_attrs = a
        cls = set((a.get("class") or "").split())
        if tag == "section":
            self.cur = {"classes": cls, "accent_solid": 0, "has_notes": False, "h2": "", "line": self.getpos()[0]}
            self.sections.append(self.cur)
        if self.cur is not None and "accent-solid" in cls:
            self.cur["accent_solid"] += 1
        if tag == "div" and "chart" in cls:
            self.chart_depth.append(len(self.stack))
            if a.get("data-type") not in CHART_TYPES:
                self.errors.append(f"line {self.getpos()[0]}: unknown chart type '{a.get('data-type')}'")
        if tag == "aside" and self.cur is not None:
            self.cur["has_notes"] = True
        if tag in ("script", "style", "aside", "title"):
            self._skip += 1
        if tag == "script":
            self._script = {"type": a.get("type", ""), "text": "", "in_chart": bool(self.chart_depth), "line": self.getpos()[0]}
        if tag == "h2":
            self.h2 = ""
        if tag not in ("br", "img", "hr", "meta", "link", "input", "i"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            self.scripts.append(self._script)
            self._script = None
        if tag in ("script", "style", "aside", "title"):
            self._skip = max(0, self._skip - 1)
        if tag == "h2" and self.h2 is not None and self.cur is not None and not self.cur["h2"]:
            self.cur["h2"] = self.h2.strip()
            self.h2 = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        if tag == "div" and self.chart_depth and len(self.stack) <= self.chart_depth[-1]:
            self.chart_depth.pop()
        if tag == "section":
            self.cur = None

    def handle_data(self, data):
        if self._script is not None:
            self._script["text"] += data
        if self.h2 is not None:
            self.h2 += data
        if not self._skip:
            self.text_chunks.append(data)


WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)


def check_static(html: str):
    errors = []
    if not html.rstrip().endswith("</html>"):
        errors.append("file does not end with </html> (truncated output?)")

    # runtime script pinned by CSP
    runtime = re.findall(r"<script>(.*?)</script>", html, re.S)
    csp = re.search(r"script-src '(sha256-[^']+)'", html)
    if len(runtime) != 1:
        errors.append(f"expected exactly 1 runtime <script> (without type), found {len(runtime)}")
    elif not csp:
        errors.append("CSP meta with a pinned script hash is missing")
    else:
        h = "sha256-" + base64.b64encode(hashlib.sha256(runtime[0].encode()).digest()).decode()
        if h != csp.group(1):
            errors.append("runtime script was modified (hash does not match the CSP); copy the template again")

    n_style = len(re.findall(r"<style\b", html, re.I))
    if n_style != 1:
        errors.append(f"expected exactly 1 <style> block (the template's), found {n_style}")
    if re.search(r"<link\b(?![^>]*https://fonts\.googleapis\.com/)", html, re.I):
        errors.append("<link> to something other than Google Fonts")

    p = Deck()
    p.feed(html)
    errors += p.errors

    if not p.sections:
        errors.append("no <section> slides found")

    for s in p.scripts:
        if s["type"] == "":
            continue  # runtime, checked above
        if s["type"] != "application/json" or not s["in_chart"]:
            errors.append(f"line {s['line']}: <script type='{s['type']}'> outside a chart is not allowed")
            continue
        if "</script" in s["text"].lower():
            errors.append(f"line {s['line']}: chart JSON contains '</script'; escape '<' as \\u003c")
        try:
            json.loads(s["text"])
        except json.JSONDecodeError as e:
            errors.append(f"line {s['line']}: invalid chart JSON ({e.msg} at line {e.lineno} col {e.colno})")

    if "[DECK TITLE]" in html:
        errors.append("<title> still has the [DECK TITLE] placeholder")
    if "data-footer" not in p.body_attrs:
        warn("<body data-footer=\"...\"> not set; slides will have no footer label")

    visible = "".join(p.text_chunks)
    n_dash = sum(visible.count(d) for d in DASHES)
    if n_dash:
        warn(f"{n_dash} em/en dash(es) in visible text; the style guide asks for commas, periods or parentheses")
    brackets = sorted(set(re.findall(r"\[[^\]\n]{1,60}\]", visible)))
    if brackets:
        warn("placeholders left for the author: " + ", ".join(brackets[:15]) + (" ..." if len(brackets) > 15 else ""))

    for i, s in enumerate(p.sections, 1):
        special = s["classes"] & {"cover", "section-break"}
        if s["accent_solid"] > 1:
            errors.append(f"slide {i}: {s['accent_solid']} .accent-solid elements (max 1 per slide)")
        if not special and not s["has_notes"]:
            warn(f"slide {i}: no speaker notes (<aside>)")
        t = s["h2"]
        if t and not special and "ask" not in s["classes"]:
            words = t.split()
            if len(words) <= 3:
                warn(f"slide {i}: title '{t}' looks like a label; write an action title (a claim with a verb)")
            if len(t) > 120:
                warn(f"slide {i}: title has {len(t)} characters; keep it to two lines (~110)")
    return errors, len(p.sections)


def check_render(path: Path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        warn("--render skipped: playwright is not installed (pip install playwright && playwright install chromium)")
        return []
    errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        js_err = []
        pg.on("pageerror", lambda e: js_err.append(str(e)))
        pg.goto(path.resolve().as_uri())
        pg.wait_for_timeout(800)
        errors += [f"JS error: {e}" for e in js_err]
        bad = pg.evaluate("""() => [...document.querySelectorAll('.chart p')].map(p => p.textContent)""")
        errors += [f"chart error: {t}" for t in bad]
        over = pg.evaluate("""() => {
          const out=[]; const S=[...document.querySelectorAll('#stage>section')];
          S.forEach((s,i)=>{ S.forEach(x=>x.classList.remove('active')); s.classList.add('active');
            const sb=s.getBoundingClientRect(), k=sb.width/1920, limit=sb.top+(1080-150)*k, right=sb.left+(1920-120)*k;
            for (const el of s.querySelectorAll('h1,h2,h3,p,table,.card,.chart,.kpi,.field,.item,.ask-item,img')) {
              if (el.closest('.footer')) continue;
              const r=el.getBoundingClientRect(); if(!r.width||!r.height) continue;
              if (r.bottom>limit+1 || r.right>right+1) { out.push(`slide ${i+1}: <${el.tagName.toLowerCase()} class="${el.className}"> overflows the safe area`); break; }
            }});
          return out; }""")
        errors += over
        b.close()
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--render", action="store_true", help="also open the deck in a headless browser")
    args = ap.parse_args()
    path = Path(args.deck)
    html = path.read_text(encoding="utf-8")
    errors, n = check_static(html)
    if args.render and not errors:
        errors += check_render(path)
    print(f"{path}: {n} slides")
    for e in errors:
        print(f"  ERROR   {e}")
    for w in WARNINGS:
        print(f"  warning {w}")
    print("  OK" if not errors else f"  {len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
