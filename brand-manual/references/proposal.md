# Two directions (phase 4)

Show both directions visually, side by side. A description in text is not a proposal.

## The two directions

| | Faithful | Evolved |
|---|---|---|
| What it does | Organizes what the owner already uses | Keeps what is recognizable (logo, main color) and moves the rest toward the three words from phase 1 |
| Colors | The measured ones, merged where there were near-duplicates, corrected only where contrast fails | May add or replace neutrals and one support color; the main color stays |
| Cost | Keeps today's limitations | Old pieces need to be redone over time |
| Gain | No break with people who already know the brand | Closer to how the owner wants to be seen |

"Admired" references inform the Evolved direction. They are never copied.

## What each direction shows

- Palette of 6 to 10 colors, each with a role: background, text, main, support, emphasis.
- A pair of fonts: one for titles, one for text.
- The **same sample piece in both**: a post cover (1080x1350) and a slide cover (16:9), with the real logo file and a real title from the business.

## Rules

- **Contrast.** Body text needs 4.5:1 on its background; text of 24px or more needs 3:1. Check every pair:

  ```bash
  python scripts/palette.py --contrast "#1F3D36" "#F6F1E8"
  ```

  Without Python: relative luminance L = 0.2126 R + 0.7152 G + 0.0722 B over linearized channels (c/12.92 if c <= 0.03928, else ((c+0.055)/1.055)^2.4), ratio = (L1 + 0.05) / (L2 + 0.05).
- A pair that fails is not offered for text. If a logo color fails as text, keep it for marks and large titles and propose a darker text version of it, labeled "proposed".
- **Fonts** come from Google Fonts or from files the owner sent. Nothing that needs a license the owner does not have.
- **One main color.** A second emphasis color needs a reason.
- Colors that must be told apart differ in lightness, not only in hue.
- No stock AI looks: blue-to-purple gradients, emoji cards, a colored bar on the left of every card.

## No logo, or a weak identity

Propose a **provisional identity**: the brand name set in type (a wordmark), no drawn symbol. Both directions are then two distinct provisional identities. Set `meta.provisional_logo` to `true`; the manual shows a "Provisional logo" notice by itself. Record in `brand.md` the recommendation to hire a designer for the final mark. Do not present a provisional wordmark as a finished logo.

## The decision

Ask: Faithful, Evolved, or a mix (they say what from each). Record the answer in `meta.direction` (`faithful`, `evolved`, `mixed` or `provisional`). One round of adjustments, then build.
