# Changelog

## 1.1.0 (2026-11-15)

- Question 0: the language of the questions and of the artifacts is confirmed before anything else and recorded in `meta.lang` and in "Journey state".
- Explainer page in English and Portuguese: `docs/brand-manual.html`.

## 1.0.0 (2026-11-15)

- Seven-phase journey: assessment, intake, reading with evidence, two directions, kit, photo library, brand skill and proof piece.
- Brand kit format: `tokens.json` (colors with origin and checked contrast pairs, type, spacing, radius), `brand.md`, `logos/`, `photos/index.json`.
- `palette.py`: exact colors from SVG, measured colors from raster images, contrast ratio.
- `photo_index.py`: `prep` (clean copies without metadata, measured fields, previews), `rename`, `find` (text search with a closed vocabulary; sensitive photos hidden by default).
- `validate.py` and `build_manual.py`: validated kit, script-free `manual.html` with a hash-pinned stylesheet. Labels in English and Portuguese.
- Optional mapping to a Design System artifact in Claude.
- Fictional example in Portuguese with synthetic inputs; adversarial test in CI.
