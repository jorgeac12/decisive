#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Validate a Brand Manual kit folder (stdlib only).

    python scripts/validate.py path/to/brand

Exit code 0 = no errors (warnings may exist), 1 = errors.

Checks
  - tokens.json: shape, token names, 6-digit hex values, a usage note and an
    origin (measured, file or proposed) for every color, font families and
    lengths made only of safe characters
  - contrast: every pair in meta.contrast_pairs reaches 4.5:1 (3:1 if "large")
    in every theme
  - logos/: original files present unless meta.provisional_logo is true;
    SVG files carry no script, event handler or external reference
  - brand.md: present, with sections; em dashes (warning)
  - photos/index.json (if present): closed vocabulary, unique ids, file names
    that start with the id and exist, no path outside photos/, consent recorded
    for photos flagged minor or client-or-patient
  - manual.html (if present): no script, handler or external resource
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,119}$")
FAMILY = re.compile(r"^[A-Za-z0-9 ,\"'-]{1,200}$")
GFONT = re.compile(r"^[A-Za-z0-9 ]{1,40}$")
LENGTH = re.compile(r"^\d+(\.\d+)?(px|rem|em|%)?$")
WEIGHT = re.compile(r"^[1-9]00$")
LANG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
PHOTO_ID = re.compile(r"^f\d{3,5}$")
ORIGIN = re.compile(r"^(measured|file|proposed)\b")

LOGO_EXT = {".svg", ".png", ".pdf", ".jpg", ".jpeg", ".webp"}
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DIRECTIONS = {"faithful", "evolved", "mixed", "provisional"}
VOCAB = {
    "type": {"portrait", "half-body", "full-body", "group", "at-work", "stage", "backstage",
             "space", "storefront", "product", "detail", "screen"},
    "orientation": {"vertical", "horizontal", "square"},
    "text_space": {"none", "some", "good"},
    "text_side": {"none", "left", "right", "top", "bottom", "several"},
    "background": {"clean", "ambient", "busy"},
    "light": {"bright", "dark", "mixed"},
    "brand_fit": {"yes", "neutral", "clash"},
    "quality": {"good", "ok", "weak"},
}
VOCAB_LIST = {
    "use": {"cover", "bio", "authority", "proof", "product", "backstage", "slide-background",
            "carousel", "video-cover"},
    "issues": {"blurry", "eyes-closed", "cropped", "backlit", "low-resolution"},
    "sensitive": {"minor", "client-or-patient", "identifiable-third-party", "third-party-brand",
                  "document-with-data", "private-home"},
}
NEEDS_CONSENT = {"minor", "client-or-patient"}
BAD_TAGS = {"script", "iframe", "object", "embed", "form", "base", "foreignobject"}
URL_ATTRS = {"href", "src", "xlink:href", "action", "formaction", "poster", "data", "srcset", "background"}
SCRIPT_URL = re.compile(r"^\s*(javascript|vbscript|data\s*:\s*text/html)", re.I)
EXTERNAL_URL = re.compile(r"^\s*(https?:)?//", re.I)
FONTS_URL = re.compile(r"^https://fonts\.googleapis\.com/css2\?[A-Za-z0-9+:;@,=&%.-]*$")
RAW_UNSAFE = [
    (re.compile(r"<\s*script", re.I), "script tag"),
    (re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.I), "external resource"),
    (re.compile(r"@import", re.I), "external resource (@import)"),
    (re.compile(r"<!ENTITY", re.I), "entity declaration"),
]


class MarkupScan(HTMLParser):
    """Walks tags and attributes the way a browser tokenizes them, so quotes in text cannot hide a tag."""

    def __init__(self, allow_fonts_link):
        super().__init__(convert_charrefs=True)
        self.allow_fonts_link = allow_fonts_link
        self.found = set()

    def handle_starttag(self, tag, attrs):
        if tag in BAD_TAGS:
            self.found.add("script tag" if tag == "script" else "embedded content")
        for k, v in attrs:
            k, v = (k or "").lower(), v or ""
            if k.startswith("on"):
                self.found.add("event handler")
            if k in URL_ATTRS:
                if SCRIPT_URL.match(v):
                    self.found.add("javascript: URL")
                elif EXTERNAL_URL.match(v) and not (self.allow_fonts_link and tag == "link" and FONTS_URL.match(v)):
                    self.found.add("external resource")


def luminance(hx):
    v = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def color_value(token, theme_ids):
    """Return {theme_id: hex}; a missing theme inherits the first one."""
    v = token.get("value")
    if isinstance(v, str):
        v = {theme_ids[0]: v}
    if not isinstance(v, dict) or not theme_ids:
        return {}
    first = v.get(theme_ids[0])
    return {t: v.get(t, first) for t in theme_ids}


def scan_markup(text, where, errors, allow_fonts_link=False):
    scan = MarkupScan(allow_fonts_link)
    try:
        scan.feed(text)
        scan.close()
    except Exception:  # a file the parser cannot read is not accepted
        scan.found.add("unreadable markup")
    for rx, label in RAW_UNSAFE:
        if rx.search(text):
            scan.found.add(label)
    for label in sorted(scan.found):
        errors.append(f"{where}: {label} is not allowed")


def is_str(x, max_len=400):
    return isinstance(x, str) and 0 < len(x.strip()) <= max_len


def check_tokens(kit, errors, warnings):
    path = kit / "tokens.json"
    if not path.is_file():
        errors.append("tokens.json is missing")
        return None
    try:
        tk = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        errors.append(f"tokens.json is not valid JSON: {e}")
        return None
    if not isinstance(tk, dict):
        errors.append("tokens.json must be an object")
        return None
    if not is_str(tk.get("name"), 80):
        errors.append("tokens.json: name (the brand name) is required, up to 80 characters")
    meta = tk.get("meta") if isinstance(tk.get("meta"), dict) else {}
    if not isinstance(tk.get("meta"), dict):
        errors.append("tokens.json: meta object is required")
    if not (isinstance(meta.get("lang"), str) and LANG.match(meta["lang"])):
        errors.append("tokens.json: meta.lang must be a language tag such as en or pt-BR")
    if meta.get("direction") not in DIRECTIONS:
        errors.append(f"tokens.json: meta.direction must be one of {sorted(DIRECTIONS)}")
    if not isinstance(meta.get("provisional_logo"), bool):
        errors.append("tokens.json: meta.provisional_logo must be true or false")
    for g in meta.get("google_fonts") or []:
        if not (isinstance(g, str) and GFONT.match(g)):
            errors.append(f"tokens.json: meta.google_fonts entry {g!r} must be a plain family name")

    color = tk.get("color") if isinstance(tk.get("color"), dict) else {}
    themes = color.get("themes") if isinstance(color.get("themes"), list) else []
    theme_ids = [t.get("id") for t in themes if isinstance(t, dict)]
    if not theme_ids or any(not (isinstance(t, str) and NAME.match(t)) for t in theme_ids):
        errors.append("tokens.json: color.themes needs at least one theme with a simple id")
        theme_ids = [t for t in theme_ids if isinstance(t, str) and NAME.match(t)]
    for t in themes:
        if isinstance(t, dict) and not is_str(t.get("name"), 40):
            errors.append("tokens.json: every theme needs a name")
    seen, colors = set(), {}
    origins = meta.get("origins") if isinstance(meta.get("origins"), dict) else {}
    ctokens = color.get("tokens") if isinstance(color.get("tokens"), list) else []
    if not 3 <= len(ctokens) <= 40:
        errors.append("tokens.json: color.tokens must list between 3 and 40 colors")
    for c in ctokens:
        n = c.get("name") if isinstance(c, dict) else None
        if not (isinstance(n, str) and NAME.match(n)):
            errors.append(f"tokens.json: color token name {n!r} is invalid")
            continue
        if n in seen:
            errors.append(f"tokens.json: token name {n} is used twice")
        seen.add(n)
        vals = color_value(c, theme_ids)
        if not vals or any(not (isinstance(v, str) and HEX.match(v)) for v in vals.values()):
            errors.append(f"tokens.json: color {n} must be a 6-digit hex in every theme")
        else:
            colors[n] = vals
        if not is_str(c.get("usage")):
            errors.append(f"tokens.json: color {n} needs a usage note")
        if not (isinstance(origins.get(n), str) and ORIGIN.match(origins[n]) and len(origins[n]) <= 200):
            errors.append(f"tokens.json: meta.origins.{n} must start with measured, file or proposed")

    pairs = meta.get("contrast_pairs") if isinstance(meta.get("contrast_pairs"), list) else []
    if not pairs:
        errors.append("tokens.json: meta.contrast_pairs must list the text/background pairs the brand uses")
    for p in pairs:
        if not isinstance(p, dict) or p.get("text") not in colors or p.get("on") not in colors:
            errors.append(f"tokens.json: contrast pair {p!r} must name two existing color tokens")
            continue
        need = 3.0 if p.get("large") is True else 4.5
        for t in theme_ids:
            r = contrast(colors[p["text"]][t], colors[p["on"]][t])
            if r < need:
                errors.append(f"contrast: {p['text']} on {p['on']} is {r:.2f}:1 in theme {t} (needs {need}:1)")

    typ = tk.get("type") if isinstance(tk.get("type"), dict) else {}
    families = typ.get("families") if isinstance(typ.get("families"), dict) else {}
    if not families:
        errors.append("tokens.json: type.families is required")
    for k, v in families.items():
        if not NAME.match(str(k)) or not (isinstance(v, str) and FAMILY.match(v)):
            errors.append(f"tokens.json: font family {k!r} has characters that are not allowed")
    styles = 0
    for g in typ.get("groups") if isinstance(typ.get("groups"), list) else []:
        if not isinstance(g, dict) or not is_str(g.get("name"), 40) or g.get("family") not in families:
            errors.append("tokens.json: every type group needs a name and an existing family")
            continue
        for s in g.get("styles") if isinstance(g.get("styles"), list) else []:
            n = s.get("name") if isinstance(s, dict) else None
            if not (isinstance(n, str) and NAME.match(n)):
                errors.append(f"tokens.json: text style name {n!r} is invalid")
                continue
            styles += 1
            if not LENGTH.match(str(s.get("fontSize", ""))):
                errors.append(f"tokens.json: text style {n} needs a fontSize such as 18px")
            if "lineHeight" in s and not LENGTH.match(str(s["lineHeight"])):
                errors.append(f"tokens.json: text style {n} has an invalid lineHeight")
            if "fontWeight" in s and not WEIGHT.match(str(s["fontWeight"])):
                errors.append(f"tokens.json: text style {n} has an invalid fontWeight")
    if not 3 <= styles <= 12:
        errors.append("tokens.json: define between 3 and 12 text styles")
    for fam in ("spacing", "radius"):
        block = tk.get(fam) if isinstance(tk.get(fam), dict) else {}
        for s in block.get("tokens") if isinstance(block.get("tokens"), list) else []:
            n = s.get("name") if isinstance(s, dict) else None
            if not (isinstance(n, str) and NAME.match(n)) or n in seen:
                errors.append(f"tokens.json: {fam} token name {n!r} is invalid or repeated")
                continue
            seen.add(n)
            if not LENGTH.match(str(s.get("value", ""))):
                errors.append(f"tokens.json: {fam} token {n} needs a length such as 16px")
    return tk


def check_logos(kit, tk, errors, warnings):
    d = kit / "logos"
    files = sorted(p for p in d.iterdir() if p.is_file()) if d.is_dir() else []
    provisional = bool(tk and tk.get("meta", {}).get("provisional_logo") is True)
    if not files and not provisional:
        errors.append("logos/: no logo file. Add the original file or set meta.provisional_logo to true")
    for p in files:
        if not FILE.match(p.name) or p.suffix.lower() not in LOGO_EXT:
            errors.append(f"logos/{p.name}: file name or type is not allowed")
        elif p.suffix.lower() == ".svg":
            scan_markup(p.read_text(encoding="utf-8", errors="replace"), f"logos/{p.name}", errors)
    return [p.name for p in files if FILE.match(p.name) and p.suffix.lower() in LOGO_EXT]


def check_brand_md(kit, errors, warnings):
    path = kit / "brand.md"
    if not path.is_file():
        errors.append("brand.md is missing")
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 200 or len(re.findall(r"^## ", text, re.M)) < 4:
        errors.append("brand.md: write the brand book (at least four '## ' sections)")
    if "\u2014" in text or "\u2013" in text:
        warnings.append("brand.md: em or en dash found; use plain punctuation")
    return text


def check_photos(kit, errors, warnings):
    d = kit / "photos"
    path = d / "index.json"
    if not path.is_file():
        if d.is_dir() and any(p.suffix.lower() in PHOTO_EXT for p in d.iterdir()):
            errors.append("photos/: there are photos but no index.json")
        return None
    try:
        idx = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        errors.append(f"photos/index.json is not valid JSON: {e}")
        return None
    photos = idx.get("photos") if isinstance(idx, dict) else None
    if not isinstance(photos, list):
        errors.append("photos/index.json: expected {\"version\": 1, \"photos\": [...]}")
        return None
    ids, names, ok = set(), set(), []
    for ph in photos:
        if not isinstance(ph, dict):
            errors.append("photos/index.json: every entry must be an object")
            continue
        pid = ph.get("id")
        w = f"photos/index.json {pid}"
        if not (isinstance(pid, str) and PHOTO_ID.match(pid)) or pid in ids:
            errors.append(f"photos/index.json: id {pid!r} is invalid or repeated")
            continue
        ids.add(pid)
        bad = False
        f = ph.get("file")
        if not (isinstance(f, str) and FILE.match(f) and Path(f).suffix.lower() in PHOTO_EXT):
            errors.append(f"{w}: file must be a plain image file name inside photos/")
            bad = True
        else:
            names.add(f)
            if not f.startswith(pid + "_") and Path(f).stem != pid:
                errors.append(f"{w}: file name must start with the id")
            if not (d / f).is_file():
                errors.append(f"{w}: file {f} does not exist")
        for k, allowed in VOCAB.items():
            if ph.get(k) not in allowed:
                errors.append(f"{w}: {k} must be one of {sorted(allowed)}")
                bad = True
        for k, allowed in VOCAB_LIST.items():
            v = ph.get(k, [])
            if not isinstance(v, list) or any(x not in allowed for x in v):
                errors.append(f"{w}: {k} must be a list with values from {sorted(allowed)}")
                bad = True
        if not isinstance(ph.get("use"), list) or not ph.get("use"):
            errors.append(f"{w}: use needs at least one value")
        people = ph.get("people", [])
        if not isinstance(people, list) or any(not is_str(x, 60) for x in people):
            errors.append(f"{w}: people must be a list of short names or roles given by the user")
            bad = True
        for k in ("width", "height"):
            if not (isinstance(ph.get(k), int) and not isinstance(ph.get(k), bool) and 0 < ph[k] < 100000):
                errors.append(f"{w}: {k} must be a positive integer")
                bad = True
        if not (isinstance(ph.get("dominant_color"), str) and HEX.match(ph["dominant_color"])):
            errors.append(f"{w}: dominant_color must be a measured 6-digit hex")
            bad = True
        if not is_str(ph.get("desc"), 140):
            errors.append(f"{w}: desc is required, one line up to 140 characters")
            bad = True
        if "group" in ph and not (isinstance(ph["group"], str) and NAME.match(ph["group"])):
            errors.append(f"{w}: group must be a simple name")
            bad = True
        if "best_of_group" in ph and not isinstance(ph["best_of_group"], bool):
            errors.append(f"{w}: best_of_group must be true or false")
        sens = ph.get("sensitive", []) if isinstance(ph.get("sensitive", []), list) else []
        if NEEDS_CONSENT & set(sens) and ph.get("consent") is not True:
            errors.append(f"{w}: flagged {sorted(NEEDS_CONSENT & set(sens))} but consent is not recorded as true")
        if not bad:
            ok.append(ph)
    for p in sorted(d.iterdir()):
        if p.is_file() and p.suffix.lower() in PHOTO_EXT and p.name not in names:
            warnings.append(f"photos/{p.name}: file is not in the index")
    return ok


def check_kit(kit):
    """Return (errors, warnings, data). data holds only values that passed the checks."""
    kit = Path(kit)
    errors, warnings = [], []
    if not kit.is_dir():
        return [f"{kit} is not a folder"], [], {}
    tk = check_tokens(kit, errors, warnings)
    logos = check_logos(kit, tk, errors, warnings)
    brand = check_brand_md(kit, errors, warnings)
    photos = check_photos(kit, errors, warnings)
    manual = kit / "manual.html"
    if manual.is_file():
        scan_markup(manual.read_text(encoding="utf-8", errors="replace"), "manual.html", errors, allow_fonts_link=True)
    else:
        warnings.append("manual.html not built yet (run build_manual.py)")
    return errors, warnings, {"tokens": tk, "logos": logos, "brand": brand, "photos": photos}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    errors, warnings, data = check_kit(sys.argv[1])
    for w in warnings:
        print("warning  " + w)
    for e in errors:
        print("ERROR    " + e)
    n = len(data.get("photos") or [])
    print(f"{len(errors)} error(s), {len(warnings)} warning(s), {n} photo(s) indexed")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
