# Reading with evidence (phase 3)

Work only on items tagged **mine**.

## Colors: measure, do not guess

```bash
python scripts/palette.py logo.svg feed.png proposal-page.png
```

- **SVG**: the values printed are exact (read from the file). They win over everything else.
- **PDF**: if you can extract vector colors, treat them as exact. Otherwise rasterize one page and measure it.
- **Screenshots and photos**: approximate, because of compression. Report them as "about #2B5A4E".
- "neutral" marks whites, blacks and grays; "color" marks the rest. The share of pixels tells you what dominates, not what matters: a logo color at 5% can still be the main color.

Look for near-duplicates across pieces: three greens within a short distance are one intended green applied inconsistently. That is a finding.

## Fonts

- **PDF**: `pdffonts file.pdf` lists the embedded fonts. That is a fact.
- **Image only**: a hypothesis. Describe what you see (serif or sans, weight, width, contrast between thick and thin) and name the closest Google Fonts family as an approximation. Never state it as the real font.
- **Logo lettering** is often custom or outlined. Do not assign a font to it unless a file says so.

## Logo

Shape (horizontal, stacked, symbol only), proportions, the colors in the file, whether it works on light and on dark backgrounds, whether light and dark versions exist, and the smallest size at which the smallest text is still readable.

## Photography

Light (bright, dark, mixed), framing, whether people appear, color treatment, how consistent it is across the grid.

## Voice

Read captions and titles in the screenshots: grammatical person, sentence length, emoji use, how they ask for action. Quote at most one short line as an example.

## The report: "What your brand already is"

Short, in the owner's words. Four blocks:

1. **Colors that really appear**: hex, share, where each came from (file or measured from which image).
2. **Fonts**: fact or hypothesis, each one labeled.
3. **Three consistent patterns**: what is already brand.
4. **Inconsistencies, as business risk.** Not "the greens do not match" but "three different greens in nine posts: someone scrolling does not recognize it is the same company". Include contrast failures you measured ("the orange on the cream background is 3.5:1; small text in that pair is hard to read").

End by asking whether the reading matches how they see their own brand. Wait for the ok before proposing anything.
