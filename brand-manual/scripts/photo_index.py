#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Photo library for a brand kit: prepare, name and search photos through a small text index.

    python scripts/photo_index.py prep INCOMING_DIR path/to/brand    # needs Pillow
    python scripts/photo_index.py rename path/to/brand
    python scripts/photo_index.py find path/to/brand --type portrait --orientation vertical --text-space good

prep    Copies each new image into brand/photos/ as fNNN.jpg: rotated upright, metadata
        removed (location included), longest side 2400 px. Skips exact duplicates. Measures
        width, height, orientation and dominant color, writes a 768 px preview to
        brand/photos/_preview/ and adds an entry to index.json with the visual fields
        set to "TODO" for the agent to fill after looking at the preview once.
rename  After the visual fields are filled, renames files to
        fNNN_type_who_orientation_trait.jpg so the name alone answers most searches.
find    Filters index.json and prints a few matching lines. Photos with a sensitive
        flag are left out unless --include-sensitive is given. Stdlib only.
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

EXT = {".jpg", ".jpeg", ".png", ".webp"}
SAFE_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,119}$")
SAFE_ID = re.compile(r"^f\d{3,5}$")
TODO = "TODO"


def load(kit):
    p = Path(kit) / "photos" / "index.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"version": 1, "photos": []}


def save(kit, idx):
    p = Path(kit) / "photos" / "index.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(idx, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def slug(text, limit=24):
    plain = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:limit]


def prep(src, kit):
    from PIL import Image, ImageOps
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from palette import image_colors
    idx = load(kit)
    out = Path(kit) / "photos"
    prev = out / "_preview"
    prev.mkdir(parents=True, exist_ok=True)
    seen = {p.get("sha256") for p in idx["photos"]}
    n = max([int(p["id"][1:]) for p in idx["photos"]] or [0])
    added = 0
    for f in sorted(Path(src).iterdir()):
        if not f.is_file() or f.suffix.lower() not in EXT:
            continue
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if h in seen:
            print(f"skip duplicate  {f.name}")
            continue
        seen.add(h)
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im.thumbnail((2400, 2400))
        n += 1
        pid = f"f{n:03d}"
        clean = Image.new("RGB", im.size)
        clean.paste(im)
        clean.save(out / f"{pid}.jpg", "JPEG", quality=85)
        small = clean.copy()
        small.thumbnail((768, 768))
        small.save(prev / f"{pid}.jpg", "JPEG", quality=70)
        w, hgt = clean.size
        orient = "square" if abs(w - hgt) <= 0.05 * max(w, hgt) else ("vertical" if hgt > w else "horizontal")
        dom = image_colors(out / f"{pid}.jpg", 3)
        idx["photos"].append({
            "id": pid, "file": f"{pid}.jpg", "type": TODO, "people": [], "orientation": orient, "width": w, "height": hgt,
            "text_space": TODO, "text_side": TODO, "background": TODO, "light": TODO,
            "dominant_color": dom[0][0] if dom else "#808080", "brand_fit": TODO, "use": [], "quality": TODO,
            "issues": [], "sensitive": [], "desc": TODO, "sha256": h,
        })
        added += 1
        print(f"added {pid}  {w}x{hgt} {orient}  from {f.name}")
    save(kit, idx)
    print(f"{added} photo(s) added, {len(idx['photos'])} in the index. Look at photos/_preview/ once and fill the TODO fields.")


def rename(kit):
    idx = load(kit)
    out = Path(kit) / "photos"
    for p in idx["photos"]:
        if not (SAFE_ID.match(str(p.get("id"))) and SAFE_FILE.match(str(p.get("file")))):
            print(f"{p.get('id')!r}: id or file name is not a plain name inside photos/; skipped")
            continue
        if TODO in (p.get("type"), p.get("background")):
            print(f"{p['id']}: fill the TODO fields first")
            continue
        who = slug(p["people"][0]) if p.get("people") else "nobody"
        trait = "text-" + p["text_side"] if p.get("text_space") == "good" and p.get("text_side") not in (None, "none", TODO) else "bg-" + p["background"]
        new = "_".join(x for x in (p["id"], slug(p["type"]), who, p["orientation"], slug(trait)) if x) + Path(p["file"]).suffix.lower()
        if new != p["file"] and (out / p["file"]).is_file():
            (out / p["file"]).rename(out / new)
            print(f"{p['file']} -> {new}")
            p["file"] = new
    save(kit, idx)


def find(a):
    rows = []
    for p in load(a.kit)["photos"]:
        if p.get("sensitive") and not a.include_sensitive:
            continue
        if a.type and p.get("type") not in a.type:
            continue
        if a.orientation and p.get("orientation") != a.orientation:
            continue
        if a.text_space and p.get("text_space") != a.text_space:
            continue
        if a.use and a.use not in p.get("use", []):
            continue
        if a.person and not any(a.person.lower() in x.lower() for x in p.get("people", [])):
            continue
        if a.text and a.text.lower() not in (p.get("desc", "") + " " + p.get("file", "")).lower():
            continue
        if p.get("quality") == "weak" and not a.include_weak:
            continue
        rows.append(p)
    rows.sort(key=lambda p: (not p.get("best_of_group", False), p.get("quality") != "good", p.get("brand_fit") == "clash", p["id"]))
    for p in rows[:a.limit]:
        flag = "  SENSITIVE: " + ",".join(p["sensitive"]) if p.get("sensitive") else ""
        print(f"{p['id']}  photos/{p['file']}  {p['width']}x{p['height']}  text:{p.get('text_space')}/{p.get('text_side')}  "
              f"fit:{p.get('brand_fit')}  {p.get('desc')}{flag}")
    print(f"{min(len(rows), a.limit)} shown of {len(rows)} match(es)")


def main():
    ap = argparse.ArgumentParser(description="Brand kit photo library")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prep"); s.add_argument("src"); s.add_argument("kit")
    s = sub.add_parser("rename"); s.add_argument("kit")
    s = sub.add_parser("find"); s.add_argument("kit")
    s.add_argument("--type", action="append"); s.add_argument("--orientation"); s.add_argument("--text-space")
    s.add_argument("--use"); s.add_argument("--person"); s.add_argument("--text")
    s.add_argument("--include-sensitive", action="store_true"); s.add_argument("--include-weak", action="store_true")
    s.add_argument("--limit", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(a.src, a.kit)
    elif a.cmd == "rename":
        rename(a.kit)
    else:
        find(a)


if __name__ == "__main__":
    main()
