#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Draws the synthetic inputs of this example (needs Pillow). No real photo or brand is used.

    python make_inputs.py      # writes feed-instagram.png and fotos/*.png next to this file
"""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SAND, GREEN, CLAY, INK = "#F4EDE2", "#1F3D36", "#C4673A", "#1C2422"


def feed():
    """A 3x3 profile grid with a planted inconsistency: three greens and two oranges."""
    tiles = ["#1F3D36", "#F4EDE2", "#2B5A4E", "#E08A4F", "#3E6B4F", "#F4EDE2", "#C4673A", "#1F3D36", "#2B5A4E"]
    im = Image.new("RGB", (1080, 1080), "#FFFFFF")
    d = ImageDraw.Draw(im)
    for i, c in enumerate(tiles):
        x, y = 6 + (i % 3) * 358, 6 + (i // 3) * 358
        d.rectangle([x, y, x + 352, y + 352], fill=c)
        fg = SAND if c != SAND else GREEN
        d.rectangle([x + 40, y + 250, x + 240, y + 262], fill=fg)
        d.rectangle([x + 40, y + 280, x + 180, y + 290], fill=fg)
    im.save(HERE / "feed-instagram.png")


def person(d, cx, top, scale, color):
    r = int(60 * scale)
    d.ellipse([cx - r, top, cx + r, top + 2 * r], fill=color)
    d.rounded_rectangle([cx - int(130 * scale), top + int(2.3 * r), cx + int(130 * scale), top + int(2.3 * r) + int(420 * scale)],
                        radius=int(90 * scale), fill=color)


def photos():
    out = HERE / "fotos"
    out.mkdir(exist_ok=True)
    im = Image.new("RGB", (1200, 1500), "#E9E1D3"); d = ImageDraw.Draw(im)      # portrait, clean wall, space on top
    person(d, 600, 620, 1.5, "#3B4A45"); im.save(out / "retrato-parede.png")
    im = Image.new("RGB", (1600, 1000), "#D9D2C4"); d = ImageDraw.Draw(im)      # horizontal, person on the left
    person(d, 380, 260, 1.2, "#2E3A36"); d.rectangle([0, 820, 1600, 1000], fill="#B9A58A"); im.save(out / "retrato-horizontal.png")
    im = Image.new("RGB", (1600, 1000), "#CFC6B6"); d = ImageDraw.Draw(im)      # at work: desk and drawing sheets
    d.rectangle([0, 620, 1600, 1000], fill="#8C7357"); person(d, 1150, 180, 1.0, "#3B4A45")
    for i in range(3):
        d.polygon([(200 + i * 230, 700), (400 + i * 230, 680), (430 + i * 230, 860), (220 + i * 230, 880)], fill="#F7F3EA")
    im.save(out / "mesa-de-projeto.png")
    im = Image.new("RGB", (1200, 1500), "#BFD3D6"); d = ImageDraw.Draw(im)      # storefront
    d.rectangle([150, 380, 1050, 1500], fill="#EFE7DA"); d.rectangle([150, 380, 1050, 470], fill=GREEN)
    d.rectangle([260, 620, 560, 1500], fill="#2A2F2D"); d.rectangle([660, 620, 940, 980], fill="#7FA3A8"); im.save(out / "fachada.png")
    im = Image.new("RGB", (1600, 1000), "#EDE6DA"); d = ImageDraw.Draw(im)      # space: room with a large window
    d.rectangle([0, 760, 1600, 1000], fill="#A88D6E"); d.rectangle([900, 140, 1480, 700], fill="#CFE1E3")
    d.rectangle([180, 520, 620, 760], fill=CLAY); im.save(out / "sala-de-reuniao.png")
    im = Image.new("RGB", (1200, 1200), "#F1ECE3"); d = ImageDraw.Draw(im)      # product: scale model
    d.polygon([(250, 820), (600, 640), (950, 820), (600, 1000)], fill="#D8CDBB")
    d.polygon([(420, 760), (600, 520), (780, 760)], fill="#FFFFFF"); d.rectangle([470, 760, 730, 860], fill="#FBF8F2"); im.save(out / "maquete.png")
    im = Image.new("RGB", (1600, 1000), "#3A3F3D"); d = ImageDraw.Draw(im)      # dark, busy: site visit with two people
    for i in range(9):
        d.rectangle([i * 180, 0, i * 180 + 40, 1000], fill="#59605D")
    person(d, 500, 300, 1.0, "#C9B08A"); person(d, 900, 330, 0.95, "#8FA39E"); im.save(out / "visita-obra.png")


if __name__ == "__main__":
    feed()
    photos()
