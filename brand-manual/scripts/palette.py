#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Measure the colors a brand really uses, instead of guessing them by eye.

    python scripts/palette.py logo.svg feed.png proposal-page.png
    python scripts/palette.py --contrast "#1F3D36" "#F6F1E8"

SVG files: exact hex values read from the file (stdlib only).
Raster images (png, jpg, webp): dominant colors by share of pixels (needs Pillow).
Screenshots are compressed, so their values are approximate; a logo file wins.
"""
import colorsys
import re
import sys
from pathlib import Path

HEX = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")


def luminance(hx):
    v = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def role(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, s, v = colorsys.rgb_to_hsv(r, g, b)
    return "neutral" if s < 0.12 or v < 0.12 else "color"


def svg_colors(path):
    """Exact colors written in an SVG, in order of first use. The file is read as text, never rendered."""
    out = []
    for m in HEX.findall(Path(path).read_text(encoding="utf-8", errors="replace")):
        h = m.upper()
        if len(h) == 4:
            h = "#" + "".join(c * 2 for c in h[1:])
        if h not in out:
            out.append(h)
    return out


def image_colors(path, n=6):
    """[(hex, percent of pixels)] for a raster image, most used first.

    Pixels are grouped in coarse buckets and each bucket reports the mean of its own
    pixels, so two distinct brand colors are never averaged into a third that does not exist.
    """
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    im.thumbnail((400, 400))
    data = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    buckets, total = {}, 0
    for r, g, b, a in data:
        if a <= 200:
            continue
        total += 1
        k = (r >> 4, g >> 4, b >> 4)
        c = buckets.setdefault(k, [0, 0, 0, 0])
        c[0] += 1; c[1] += r; c[2] += g; c[3] += b
    groups = []
    for cnt, r, g, b in sorted(buckets.values(), reverse=True):
        mean = (r / cnt, g / cnt, b / cnt)
        for grp in groups:
            if sum((x - y) ** 2 for x, y in zip(mean, grp[1])) < 24 ** 2:
                grp[0] += cnt
                break
        else:
            groups.append([cnt, mean])
    out = []
    for cnt, mean in sorted(groups, key=lambda x: -x[0])[:n]:
        pct = round(100 * cnt / total)
        if pct >= 1:
            out.append(("#%02X%02X%02X" % tuple(round(x) for x in mean), pct))
    return out


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "--contrast":
        r = contrast(args[1], args[2])
        print(f"{args[1]} on {args[2]}: {r}:1  body text {'pass' if r >= 4.5 else 'FAIL'}  large text {'pass' if r >= 3 else 'FAIL'}")
        return
    if not args:
        print(__doc__)
        sys.exit(2)
    for a in args:
        print(a)
        if a.lower().endswith(".svg"):
            for h in svg_colors(a):
                print(f"  {h}  exact    {role(h):7}  on white {contrast(h, '#FFFFFF')}  on black {contrast(h, '#000000')}")
        else:
            for h, pct in image_colors(a):
                print(f"  {h}  {pct:>3}%     {role(h):7}  on white {contrast(h, '#FFFFFF')}  on black {contrast(h, '#000000')}")


if __name__ == "__main__":
    main()
