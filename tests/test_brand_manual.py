#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Regression and security tests for brand-manual.

    python tests/test_brand_manual.py     # needs: pip install pillow; playwright is optional

1. The example kit validates and its manual.html is up to date.
2. Color measuring, the documented tokens example, photo prep (metadata removed,
   duplicates skipped) and photo search (sensitive photos hidden by default).
3. Adversarial kits: values that try to break out of the stylesheet, the font URL,
   file paths or attributes are rejected by the validator, and the builder refuses them.
4. Hostile text in fields that accept free text is escaped: no markup reaches the page.
   With Playwright installed, the page is opened and must run no script and reach no host.
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "brand-manual"
EX = SKILL / "examples" / "studio-pt-BR"
PY = sys.executable
sys.path.insert(0, str(SKILL / "scripts"))

failures = []
PAYLOAD = "<img src=x onerror=\"document.documentElement.id='pwned'\"><script>document.documentElement.id='pwned'</script>"


def check(cond, msg):
    print(("  ok    " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)


def run(script, *args):
    r = subprocess.run([PY, str(SKILL / "scripts" / script), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def kit_copy(tmp, name):
    dst = Path(tmp) / name
    shutil.copytree(EX / "brand", dst)
    return dst


def edit(kit, rel, fn):
    p = kit / rel
    data = json.loads(p.read_text(encoding="utf-8"))
    fn(data)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def rejected(tmp, name, mutate, needle):
    kit = kit_copy(tmp, name)
    mutate(kit)
    code, out = run("validate.py", kit)
    check(code == 1 and needle in out, f"validator rejects: {name}" + ("" if code == 1 and needle in out else f"\n{out}"))
    (kit / "manual.html").unlink()
    code, _ = run("build_manual.py", kit)
    check(code != 0 and not (kit / "manual.html").exists(), f"builder refuses: {name}")


def main():
    from palette import contrast, image_colors, svg_colors
    from validate import check_tokens

    print("example")
    code, out = run("validate.py", EX / "brand")
    check(code == 0 and "0 warning" in out, "example kit validates with no warnings" + (f"\n{out}" if code else ""))
    code, out = run("build_manual.py", EX / "brand", "--check")
    check(code == 0, "manual.html is up to date (re-run build_manual.py)")

    print("measuring")
    check(svg_colors(EX / "input/logo-buriti.svg") == ["#C4673A", "#1F3D36"], "SVG colors are read exactly")
    feed = [h for h, _ in image_colors(EX / "input/feed-instagram.png", 8)]
    check({"#1F3D36", "#2B5A4E", "#3E6B4F", "#C4673A", "#E08A4F"} <= set(feed), "the three greens and two oranges of the feed stay distinct")
    check(contrast("#C4673A", "#F6F1E8") == 3.49 and contrast("#000000", "#FFFFFF") == 21.0, "contrast ratio")
    doc = (SKILL / "references/kit-format.md").read_text(encoding="utf-8")
    block = re.search(r"```json\n(.*?)```", doc, re.S).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "tokens.json").write_text(block, encoding="utf-8")
        errs = []
        check_tokens(Path(tmp), errs, [])
        check(not errs, "tokens example in kit-format.md is a valid tokens.json" + (f"\n{errs}" if errs else ""))

    with tempfile.TemporaryDirectory() as tmp:
        print("photos")
        from PIL import Image
        inc = Path(tmp) / "incoming"
        inc.mkdir()
        exif = Image.Exif()
        exif[0x010F] = "SecretCameraMaker"
        exif[0x8825] = {1: "S", 2: (22.0, 54.0, 0.0), 3: "W", 4: (47.0, 3.0, 0.0)}
        Image.new("RGB", (3000, 2000), "#1F3D36").save(inc / "a.jpg", exif=exif)
        shutil.copy(inc / "a.jpg", inc / "b.jpg")
        kit = Path(tmp) / "newkit"
        code, out = run("photo_index.py", "prep", inc, kit)
        idx = json.loads((kit / "photos/index.json").read_text(encoding="utf-8"))
        check(code == 0 and len(idx["photos"]) == 1 and "skip duplicate" in out, "prep indexes once and skips the exact duplicate")
        made = Image.open(kit / "photos/f001.jpg")
        check(max(made.size) == 2400 and len(made.getexif()) == 0 and b"SecretCameraMaker" not in (kit / "photos/f001.jpg").read_bytes(),
              "prep resizes and removes metadata, location included")
        dom = idx["photos"][0]["dominant_color"]
        near = all(abs(int(dom[i:i + 2], 16) - int("#1F3D36"[i:i + 2], 16)) <= 6 for i in (1, 3, 5))
        check(near and idx["photos"][0]["orientation"] == "horizontal", "prep measures color and orientation")
        code, out = run("photo_index.py", "find", EX / "brand", "--orientation", "horizontal")
        check("f004" in out and "f007" not in out, "find hides sensitive photos by default")
        code, out = run("photo_index.py", "find", EX / "brand", "--type", "group", "--include-sensitive")
        check("f007" in out and "SENSITIVE" in out, "find shows them, flagged, only when asked")
        evil = kit_copy(tmp, "rename-traversal")
        outside = Path(tmp) / "outside.jpg"
        outside.write_bytes(b"x")
        edit(evil, "photos/index.json", lambda d: d["photos"][0].update(file="../../outside.jpg"))
        run("photo_index.py", "rename", evil)
        check(outside.exists(), "rename does not move files from outside photos/")

        print("adversarial kits")
        tok = "tokens.json"
        rejected(tmp, "style break-out in a color",
                 lambda k: edit(k, tok, lambda d: d["color"]["tokens"][0].update(value={"claro": "#fff}</style><script>document.title='PWNED'</script>"})), "6-digit hex")
        rejected(tmp, "css url() in a font family",
                 lambda k: edit(k, tok, lambda d: d["type"]["families"].update(texto="x;} body{background:url(https://attacker.invalid/x)}")), "font family")
        rejected(tmp, "markup in a google font name",
                 lambda k: edit(k, tok, lambda d: d["meta"].update(google_fonts=["Inter&family=x\"><script>alert(1)</script>"])), "google_fonts")
        rejected(tmp, "markup in lang",
                 lambda k: edit(k, tok, lambda d: d["meta"].update(lang="en\"><script>alert(1)</script>")), "meta.lang")
        rejected(tmp, "css in a font size",
                 lambda k: edit(k, tok, lambda d: d["type"]["groups"][0]["styles"][0].update(fontSize="1px;background:url(//attacker.invalid)")), "fontSize")
        rejected(tmp, "contrast below the minimum",
                 lambda k: edit(k, tok, lambda d: d["meta"]["contrast_pairs"].append({"text": "argila", "on": "areia"})), "needs 4.5:1")
        rejected(tmp, "color without origin",
                 lambda k: edit(k, tok, lambda d: d["meta"]["origins"].pop("tinta")), "meta.origins.tinta")
        pix = "photos/index.json"
        rejected(tmp, "path traversal in a photo file",
                 lambda k: edit(k, pix, lambda d: d["photos"][0].update(file="../../../etc/passwd")), "plain image file name")
        rejected(tmp, "external photo URL",
                 lambda k: edit(k, pix, lambda d: d["photos"][0].update(file="https://attacker.invalid/p.jpg")), "plain image file name")
        rejected(tmp, "value outside the vocabulary",
                 lambda k: edit(k, pix, lambda d: d["photos"][0].update(type="selfie")), "type must be one of")
        rejected(tmp, "minor without recorded consent",
                 lambda k: edit(k, pix, lambda d: d["photos"][0].update(sensitive=["minor"])), "consent is not recorded")

        def bad_svg(k):
            (k / "logos/logo-buriti.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>alert(1)</script>'
                '<image href="https://attacker.invalid/x.png"/></svg>', encoding="utf-8")
        rejected(tmp, "SVG logo with script, handler and external image", bad_svg, "script tag")

        def quote_trick(k):
            (k / "logos/logo-buriti.svg").write_text(
                "<svg xmlns='http://www.w3.org/2000/svg'><text>it's</text><g onload=alert(1)></g><text>it's</text>"
                "<style>@import 'https://attacker.invalid/x.css';</style></svg>", encoding="utf-8")
        rejected(tmp, "SVG handler hidden between apostrophes, and @import", quote_trick, "event handler")

        def bad_name(k):
            (k / "logos/logo-buriti.svg").rename(k / "logos" / "x\" onerror=\"alert(1).svg")
        rejected(tmp, "logo file name with quotes", bad_name, "file name or type")

        print("hostile text is escaped")
        kit = kit_copy(tmp, "hostile-text")

        def hostile(d):
            d["name"] = "SAFE " + PAYLOAD[:60]
            d["color"]["tokens"][0]["usage"] = PAYLOAD
            d["color"]["themes"][0]["name"] = PAYLOAD[:40]
            d["meta"]["origins"]["areia"] = "proposed: " + PAYLOAD
            d["type"]["groups"][0]["name"] = PAYLOAD[:40]
            d["spacing"]["tokens"][0]["usage"] = PAYLOAD
        edit(kit, tok, hostile)
        edit(kit, pix, lambda d: d["photos"][0].update(desc=PAYLOAD[:140], people=[PAYLOAD[:60]]))
        (kit / "brand.md").write_text((kit / "brand.md").read_text(encoding="utf-8")
                                      + f"\n\n{PAYLOAD}\n\n- {PAYLOAD}\n\n| a | b |\n|---|---|\n| {PAYLOAD} | [x](javascript:alert(1)) |\n"
                                      + "\n<img src=\"https://attacker.invalid/pixel.png\">\n", encoding="utf-8")
        code, out = run("build_manual.py", kit)
        page = (kit / "manual.html").read_text(encoding="utf-8") if code == 0 else ""
        check(code == 0, "builder accepts free text with markup in it" + (f"\n{out}" if code else ""))
        check("<script" not in page and "<img src=x" not in page and "attacker.invalid/pixel.png\">" not in page
              and "&lt;script&gt;" in page, "markup is rendered as text")
        code, out = run("validate.py", kit)
        check(code == 0, "the built page passes the validator" + (f"\n{out}" if code else ""))

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("  skip  browser check (playwright not installed)")
        else:
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                pg = b.new_page()
                finished, blocked = [], []
                pg.on("requestfinished", lambda q: finished.append(q.url) if "attacker.invalid" in q.url else None)
                pg.on("requestfailed", lambda q: blocked.append(q.url) if "attacker.invalid" in q.url and q.failure == "csp" else None)
                pg.goto((kit / "manual.html").as_uri())
                pg.wait_for_timeout(600)
                check(pg.evaluate("document.documentElement.id") == "", "no injected script ran")
                check(not finished and not blocked, "the built page asks nothing of the attacker host")
                check(pg.evaluate("getComputedStyle(document.querySelector('.c4-0')).backgroundColor") == "rgb(31, 61, 54)",
                      "the hash-pinned stylesheet is applied")
                # a page edited by hand after the build: the CSP must still hold
                tampered = kit / "tampered.html"
                tampered.write_text(page.replace("<main>", "<main><img src=x onerror=\"document.documentElement.id='pwned'\">"
                                                 "<script>document.documentElement.id='pwned'</script>"
                                                 "<p id=\"leak\" style=\"background:url(https://attacker.invalid/leak)\">x</p>"
                                                 "<img src=\"https://attacker.invalid/pixel.png\">"), encoding="utf-8")
                pg.goto(tampered.as_uri())
                pg.wait_for_timeout(600)
                check(pg.evaluate("document.documentElement.id") == "", "CSP blocks script and handlers added to the page by hand")
                check(pg.evaluate("getComputedStyle(document.getElementById('leak')).backgroundImage") == "none",
                      "CSP blocks inline styles added by hand")
                check(not finished and len(blocked) >= 1, f"CSP blocks the external image ({len(blocked)} blocked)")
                code, out = run("validate.py", kit)
                tampered.replace(kit / "manual.html")
                code, out = run("validate.py", kit)
                check(code == 1 and "script tag" in out and "event handler" in out and "external resource" in out,
                      "validator rejects the hand-edited page")
                b.close()

    print("PASSED" if not failures else f"{len(failures)} FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
