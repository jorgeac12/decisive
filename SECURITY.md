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

## Reporting

Please open a private security advisory on GitHub (Security → Report a vulnerability) instead of a public issue.
