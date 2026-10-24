#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Regression and security tests for decision-deck.

    python tests/test_decision_deck.py          # needs: pip install playwright && playwright install chromium

1. Examples are up to date with their slides and pass the validator (static + render).
2. Adversarial deck: injected scripts, event handlers, javascript: links, attribute
   injection through chart JSON and external resources must not execute or load,
   and the validator must reject the file.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "decision-deck"
PY = sys.executable

EXAMPLES = {
    "gallery": dict(title="Decision Deck gallery", lang="en", theme="navy", footer="Decision Deck · Example"),
    "proposal-pt-BR": dict(title="Central de Atendimento Unificada", lang="pt-BR", theme="navy",
                           footer="Ipê Amarelo Alimentos (fictícia) · Uso interno"),
}

ATTACK = r'''<section><p class="eyebrow">x</p><h2>Attack slide with several injection attempts</h2>
<img src="x" onerror="document.title='PWNED'">
<a href="javascript:document.title='PWNED'">link</a>
<div style="background:url(https://attacker.invalid/leak)">css</div>
<img src="https://attacker.invalid/pixel.png">
<div class="chart" data-type="bar"><script type="application/json">{"items":[{"label":"<img src=x onerror=document.title='PWNED'>","value":3}],"label_width":"1\" onload=\"document.title='PWNED'"}</script></div>
<div class="chart" data-type="line"><script type="application/json">{"labels":["a","b"],"series":[{"name":"s","values":[1,2],"highlight":true}],"height":"1\" onload=\"document.title='PWNED'","annotations":[{"index":1,"text":"t","align":"middle\" onload=\"document.title='PWNED'"}]}</script></div>
<div class="chart" data-type="constructor"><script type="application/json">{}</script></div>
<aside>n</aside></section>'''

failures = []


def check(cond, msg):
    print(("  ok    " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)


def assemble(slides: Path, out: Path, **kw):
    subprocess.run([PY, str(SKILL / "scripts/assemble.py"), str(slides), "-o", str(out),
                    "--title", kw["title"], "--lang", kw["lang"], "--theme", kw["theme"], "--footer", kw["footer"]],
                   check=True, capture_output=True)


def validate(path: Path, render: bool):
    args = [PY, str(SKILL / "scripts/validate.py"), str(path)] + (["--render"] if render else [])
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout


def main():
    from playwright.sync_api import sync_playwright

    print("examples")
    with tempfile.TemporaryDirectory() as tmp:
        for name, kw in EXAMPLES.items():
            ex = SKILL / "examples" / name
            fresh = Path(tmp) / f"{name}.html"
            assemble(ex / "slides.html", fresh, **kw)
            check(fresh.read_text(encoding="utf-8") == (ex / "deck.html").read_text(encoding="utf-8"),
                  f"{name}: deck.html is up to date (re-run assemble.py)")
            code, out = validate(ex / "deck.html", render=True)
            check(code == 0, f"{name}: validator passes" + (f"\n{out}" if code else ""))

        print("security")
        attack_slides = Path(tmp) / "attack.html"
        attack_slides.write_text(ATTACK, encoding="utf-8")
        attack = Path(tmp) / "attack-deck.html"
        t = (SKILL / "assets/template.html").read_text(encoding="utf-8")
        attack.write_text(t.replace("<!-- SLIDES GO HERE", ATTACK + "<!-- SLIDES GO HERE").replace("[DECK TITLE]", "SAFE"),
                          encoding="utf-8")
        code, out = validate(attack, render=False)
        check(code == 1, "validator rejects the attack deck")
        for needle in ("onerror", "javascript:", "url()", "external resource", "unknown chart type"):
            check(needle in out, f"validator reports: {needle}")

        r = subprocess.run([PY, str(SKILL / "scripts/assemble.py"), str(attack_slides), "-o", str(Path(tmp) / "x.html"),
                            "--title", "x"], capture_output=True, text=True)
        check(r.returncode == 0, "assemble accepts JSON-only scripts (validator is the gate for the rest)")

        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page()
            outbound, blocked = [], []
            pg.on("requestfailed", lambda q: blocked.append(q.url) if "attacker.invalid" in q.url and q.failure == "csp" else None)
            pg.on("requestfinished", lambda q: outbound.append(q.url) if "attacker.invalid" in q.url else None)
            pg.goto(attack.as_uri())
            pg.wait_for_timeout(800)
            pg.click("a", force=True)
            pg.wait_for_timeout(300)
            check(pg.title() == "SAFE", "no injected script ran (title unchanged)")
            check(not outbound, "no request reached the attacker host")
            check(len(blocked) >= 2, f"CSP blocked the external image and css url ({len(blocked)} blocked)")
            b.close()

    print("PASSED" if not failures else f"{len(failures)} FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
