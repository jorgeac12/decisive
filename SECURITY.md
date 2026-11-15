# Security

## Threat model

Skills in this repository turn documents into files people open. Those documents may come from anyone. The main risk is **indirect prompt injection**: a document contains instructions aimed at the agent ("add this script", "include this image") and the generated file executes code or leaks data when opened.

## decision-deck: defenses

| Layer | What it does |
|---|---|
| Skill instructions | `SKILL.md` tells the agent that documents are data, never instructions, and to report embedded instructions to the user. The agent writes only `<section>` content from a closed component catalog. |
| `assemble.py` | Builds the deck from the template; refuses slide files with executable `<script>` tags. |
| `validate.py` | Rejects extra scripts, `on*` handlers, `javascript:`/`vbscript:` URLs, `iframe`/`object`/`embed`/`form`/`base`/inline `svg`, external `src`, external `url()` or `@import` in styles, extra `<style>` blocks, `<link>` to anything but Google Fonts, unknown chart types, invalid chart JSON, and a modified runtime (hash mismatch). |
| Content-Security-Policy | `script-src` allows only the runtime script, pinned by SHA-256. Injected inline scripts and event handlers do not run. `img-src 'self' data:`, `connect-src 'none'`, `form-action 'none'`, `base-uri 'none'`, `object-src 'none'`, `frame-src 'none'`: no exfiltration through images, CSS, fetch or forms. Only Google Fonts may load. |
| Runtime | Chart JSON is parsed with `JSON.parse`; every text is HTML-escaped; numeric fields are coerced to finite numbers; enumerated fields (alignment, status, chart type) are whitelisted; chart lookup uses own properties only. |

## Adversarial review (v1.0.0)

Reviewed on 2026-10-21 by building a deck with these attacks and opening it in Chromium:

| Attack | Result |
|---|---|
| `<img onerror=...>` in a slide | Blocked by CSP; validator error |
| Inline `<script>` in a slide | Blocked by CSP; validator error |
| `javascript:` link, clicked | Blocked by CSP; validator error |
| External image (tracking pixel) | Blocked by CSP (`img-src`); validator error |
| CSS `background:url(https://...)` exfiltration | Blocked by CSP (`img-src`); validator error |
| HTML in a chart label (`<img onerror>`) | Rendered as text (escaped) |
| Attribute injection through numeric chart fields (`height`, `label_width`) | Coerced to numbers; no attribute break-out |
| Attribute injection through `align` | Whitelisted; ignored |
| `data-type="constructor"` (prototype lookup) | Rejected as unknown type |
| `</script>` inside chart JSON | Breaks the JSON (error shown); validator error |

Outcome: no injected code executed, no request reached the attacker host. The test is automated in `tests/test_decision_deck.py` and runs in CI.

### Residual risks

- **Clickable external links** (`<a href="https://...">`) are allowed for legitimate references; the validator warns. Opening one is a user action.
- **Google Fonts** is contacted when the deck opens (font CSS and files only). Remove the `<link>` and the two Google Fonts entries in the CSP for fully offline decks; the system font fallback is used.
- **Content risks** (a wrong number, a misleading title) are not security issues; the review checklist and the "numbers have a source" rule address them.
- A file opened from a server with its own, weaker CSP header is outside this model.

## brand-manual: defenses

The inputs are a logo, screenshots, documents and photos from the owner, or a kit folder received from someone else. The outputs are a kit folder and `manual.html`.

| Layer | What it does |
|---|---|
| Skill instructions | Material is data, never instructions; embedded instructions are reported to the owner. The agent writes `tokens.json`, `brand.md` and `photos/index.json`, never HTML. |
| `validate.py` | Colors must be 6-digit hex; token, theme and file names, font families, Google Fonts names, lengths, weights and the language tag accept only safe characters; photo and logo files must be plain names inside their folder (no path, no URL); photo fields come from a closed vocabulary. SVG logos and `manual.html` are tokenized with an HTML parser and rejected on script tags, event handlers, `javascript:` URLs, embedded content, external references, `@import` and entity declarations. |
| `build_manual.py` | Refuses a kit with validation errors. Every value is HTML-escaped. Only validated colors, families, sizes and weights reach the stylesheet. Markdown is escaped first and links render as text. The page has no script and no inline `style` attribute. |
| Content-Security-Policy | `default-src 'none'`; `style-src` allows only the one stylesheet, pinned by SHA-256 (plus Google Fonts when the kit names fonts); `img-src 'self' data:`; `base-uri 'none'`; `form-action 'none'`. Scripts, handlers, inline styles and external images added to the page do not run or load. |
| `photo_index.py` | `prep` re-encodes every photo without metadata (camera, date, location) and never overwrites a source file. `rename` only touches plain file names inside `photos/`. `find` hides photos flagged as sensitive unless asked. |
| Consent | A photo flagged `minor` or `client-or-patient` fails validation unless `consent` is recorded as `true`. |

## Adversarial review (brand-manual v1.0.0)

Reviewed on 2026-11-15 by mutating the example kit and, for the page, opening it in Chromium:

| Attack | Result |
|---|---|
| `}</style><script>` in a color value | Validator error; builder refuses |
| `url(https://...)` through a font family or a font size | Validator error; builder refuses |
| Markup in a Google Fonts name or in the language tag | Validator error; builder refuses |
| `../../../etc/passwd` or an `https://` URL as a photo file | Validator error; builder refuses |
| Index entry pointing outside `photos/`, then `rename` | Entry skipped; the outside file is not moved |
| SVG logo with `<script>`, `onload` and an external image | Validator error; builder refuses |
| SVG handler hidden between apostrophes in text, and `@import` | Validator error (found by this review: the first scanner used regular expressions and missed it; it now tokenizes) |
| Logo file name with quotes and `onerror` | Validator error; builder refuses |
| `<img onerror>` and `<script>` in brand name, usage notes, origins, theme and group names, photo description, people and `brand.md` (paragraph, list, table, link) | Rendered as text (escaped); nothing ran |
| Page edited by hand after the build: script, handler, inline style with `url()`, tracking pixel | Blocked by CSP; validator error |
| Photo with EXIF camera and GPS data | Removed by `prep` |
| Measuring colors: two brand colors averaged into one that does not exist | Fixed in this review (bucket means instead of median cut); regression test |

Outcome: no injected code executed and no request reached the attacker host. Automated in `tests/test_brand_manual.py`, which runs in CI.

The explainer page `docs/brand-manual.html` is static: no script, no form, no user input, images only from its own folder, and a CSP that pins its stylesheet by hash. The tests check the pin and the absence of scripts and handlers.

### Residual risks

- **Text an agent reads.** `desc`, `usage` and `brand.md` are free text. A kit received from a third party can carry text aimed at the next agent that reads it. The skill tells agents to treat kit text as data; nothing enforces it.
- **Image parsing.** `prep` and `palette.py` open images with Pillow. Keep Pillow updated; its size limit guards against decompression bombs.
- **Parser differences.** The validator's HTML parser and a browser can disagree on malformed markup. For `manual.html` the CSP is the second layer. SVG logos are shown through `<img>`, where browsers do not run scripts or load external files, but opening an SVG directly in a browser is outside that protection: only use logo files from the brand owner.
- **Consent is a recorded statement.** `consent: true` means the owner said they have written consent. The skill cannot verify it.
- **Google Fonts** is contacted when the manual opens, if the kit names fonts. Remove `meta.google_fonts` for a fully offline page.
- **Publishing the kit.** Photos and names in a kit are personal data. Publishing the folder or the manual is the owner's decision.

## Reporting

Please open a private security advisory on GitHub (Security → Report a vulnerability) instead of a public issue.
