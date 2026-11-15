# Brand skill and proof piece (phase 7)

## The brand skill

A small personal skill that every future piece reads before it is designed. Write it to `brand-<slug>/SKILL.md` next to the kit (or propose it through the host's skill mechanism, when there is one). `<slug>` is the brand name in lowercase with hyphens.

Template. Replace everything in brackets; keep it under 80 lines.

```markdown
---
name: brand-[slug]
description: Visual identity and voice of [Brand]. Read before producing any post, carousel, slide, document or video for [Brand].
---

# [Brand]: how every piece looks and sounds

Source of truth: the kit at `[path or link to brand/]`. Read `brand.md`, then `tokens.json`. If this file and the kit disagree, the kit wins.

## Colors
[One line per color: name, hex, where it goes, where it does not]

## Type
[Title font, text font, minimum sizes for the pieces they make most]

## Logo
[File to use, allowed backgrounds, clear space, minimum size. "Provisional" if it is]

## Voice
[Five rules, one example each]

## Photos
Find photos with `photo_index.py find [path]` or by filtering `photos/index.json`. Open at most three finalists. Never use a photo flagged sensitive in a public piece without asking.

## Before delivering
- Only kit colors and fonts. No new hex.
- Text pairs are the ones in `meta.contrast_pairs`.
- The logo is the file, untouched.
- The piece was rendered and looked at.
```

The mirror in the skill is a convenience. Values come from the kit; do not add rules the owner did not approve.

## The proof piece

Make the one piece the owner makes most (from question 2 of phase 1): a post cover, a slide cover or a proposal cover. Use only the kit: its colors, fonts, the logo file and one photo found through the index. Show it and say which photo you chose, which filter found it and why it fits.

If the proof piece looks wrong, the kit is wrong: fix the kit, rebuild, and redo the piece. Do not patch the piece.

## Close

Tell the owner what is still provisional, what is pending in "Journey state", and offer one next step: more photos, another surface, or the first real piece.
