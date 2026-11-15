# Kit format (phase 5)

Everything the validator checks is described here. Write the files, run `validate.py`, fix what it reports.

## tokens.json

```json
{
 "name": "Estúdio Buriti",
 "version": 1,
 "meta": {
  "lang": "pt-BR",
  "direction": "evolved",
  "provisional_logo": false,
  "google_fonts": ["Fraunces", "Inter"],
  "origins": {
   "areia": "proposed: feed background lightened one step",
   "verde-buriti": "file: logos/logo-buriti.svg",
   "argila": "file: logos/logo-buriti.svg"
  },
  "contrast_pairs": [
   {"text": "verde-buriti", "on": "areia"},
   {"text": "argila", "on": "areia", "large": true}
  ]
 },
 "color": {
  "themes": [{"id": "light", "name": "Light"}],
  "tokens": [
   {"name": "areia", "value": {"light": "#F6F1E8"}, "usage": "Default background."},
   {"name": "verde-buriti", "value": {"light": "#1F3D36"}, "usage": "Main color: covers and titles."},
   {"name": "argila", "value": {"light": "#C4673A"}, "usage": "Marks and titles of 24px or more."}
  ]
 },
 "type": {
  "families": {"display": "\"Fraunces\", Georgia, serif", "text": "\"Inter\", system-ui, sans-serif"},
  "groups": [
   {"name": "Titles", "family": "display", "styles": [{"name": "title", "fontSize": "56px", "lineHeight": "1.1", "fontWeight": 700}]},
   {"name": "Text", "family": "text", "styles": [
    {"name": "body", "fontSize": "32px", "lineHeight": "1.4", "fontWeight": 400},
    {"name": "label", "fontSize": "22px", "lineHeight": "1.2", "fontWeight": 700}]}
  ]
 },
 "spacing": {"tokens": [{"name": "space-2", "value": "16px", "usage": "Inside cards."}]},
 "radius": {"tokens": [{"name": "radius-md", "value": "12px", "usage": "Cards and photos."}]}
}
```

Rules:

- **Names**: letters, digits, `-`, `_`, `.`; no spaces; each name used once across colors, spacing and radius. Name colors by what the owner would call them, in their language.
- **Colors**: 3 to 40, six-digit hex only, a `usage` note on every one. The first theme is the main one. Add a dark theme only if the brand uses dark pieces.
- **`meta.origins`**: one entry per color, starting with `measured` (from which image), `file` (which file) or `proposed` (why). This is the "no invented facts" rule made checkable.
- **`meta.contrast_pairs`**: every text-on-background pair the brand book allows. The validator fails any pair under 4.5:1, or under 3:1 when `"large": true`.
- **Type**: 3 to 12 text styles in total. Families may contain only letters, digits, spaces, commas, quotes and hyphens. `meta.google_fonts` lists plain family names to load in the manual.
- **Lengths**: a number with `px`, `rem`, `em` or `%`, or a bare number.
- **`meta.direction`**: `faithful`, `evolved`, `mixed` or `provisional`. **`meta.lang`**: the owner's language tag (`en`, `pt-BR`...).

Keep the first version small: 6 to 10 colors, 5 to 7 text styles, 4 spacing steps, 3 radii.

## brand.md

The brand book, in the owner's language, at least four `##` sections. Recommended:

| Section | Content |
|---|---|
| Who the brand is | The paragraph approved in phase 1 |
| Voice | Five rules, each with a real example |
| Colors | Where each color goes and where it does not; which old colors leave use |
| Typography | Which font where; minimum sizes for the pieces they make most |
| Logo | The file, right and wrong backgrounds, clear space, minimum size. If provisional, say so |
| Photography | The look, what to avoid, consent rules, pointer to `photos/index.json` |
| Surfaces | Size and rules for the two or three pieces they make most (from question 2) |
| Journey state | Dated list: language confirmed in question 0 (conversation and artifacts), phases done, direction chosen, photos indexed, what is pending |

Supported in the manual: headings, paragraphs, lists, tables, `**bold**` and `` `code` ``. Links render as plain text. No em dashes.

## logos/

The files exactly as received. Allowed: svg, png, pdf, jpg, webp. File names with letters, digits, `.`, `-`, `_`. The validator rejects an SVG that contains scripts, event handlers or external references: tell the owner and ask for a clean export instead of editing it yourself.

## Build

```bash
python scripts/validate.py brand        # exit 1 on any error
python scripts/build_manual.py brand    # refuses a kit with errors
python scripts/build_manual.py brand --check
```

`manual.html` is generated. Change the source files and rebuild; never edit the page.
