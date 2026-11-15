# Photo library (phase 6)

Goal: any agent finds the right photo by reading a small text file, without opening images. Looking at an image is expensive; the index pays that cost once.

## Ask

20 to 60 photos, in batches of up to 10. Cover: portraits of the owner (vertical and horizontal, clean background), the owner at work, the space (storefront, reception, rooms), product or result, backstage, team, stage or event. As batches arrive, say which types are still missing.

Before accepting photos, agree on three things:

1. **Who appears.** Names and roles, said by the owner. You never identify anyone by their face.
2. **Clients, patients or children.** Whether any photo shows them, and whether there is written consent.
3. **Originals stay with the owner.** The library keeps an optimized copy.

## Prepare (by code, without looking)

```bash
python scripts/photo_index.py prep incoming/ brand
```

Each new image becomes `brand/photos/fNNN.jpg`: upright, metadata removed (location included), longest side 2400 px. Exact duplicates are skipped. Width, height, orientation and dominant color are measured. A 768 px preview goes to `brand/photos/_preview/`. Ids continue from the last one and are never reused.

## Look once

Open each preview one time and fill the `TODO` fields in `brand/photos/index.json`. After this the photo is not opened again for search. Delete `_preview/` when you finish.

| Field | Values |
|---|---|
| `type` | `portrait`, `half-body`, `full-body`, `group`, `at-work`, `stage`, `backstage`, `space`, `storefront`, `product`, `detail`, `screen` |
| `people` | Names or roles given by the owner; `[]` if nobody |
| `text_space` | `none`, `some`, `good` |
| `text_side` | `none`, `left`, `right`, `top`, `bottom`, `several` |
| `background` | `clean`, `ambient`, `busy` |
| `light` | `bright`, `dark`, `mixed` |
| `brand_fit` | `yes`, `neutral`, `clash` (does the photo's color sit well with the brand palette) |
| `use` | One or more of `cover`, `bio`, `authority`, `proof`, `product`, `backstage`, `slide-background`, `carousel`, `video-cover` |
| `quality` | `good`, `ok`, `weak` |
| `issues` | Any of `blurry`, `eyes-closed`, `cropped`, `backlit`, `low-resolution` |
| `group`, `best_of_group` | Similar photos share a group name; one is the best |
| `sensitive` | Any of `minor`, `client-or-patient`, `identifiable-third-party`, `third-party-brand`, `document-with-data`, `private-home` |
| `consent` | `true` only when the owner confirmed written consent. Required for `minor` and `client-or-patient` |
| `desc` | One line, up to 140 characters: what is seen and the mood, in the owner's language |

Measured by `prep`, do not edit: `id`, `width`, `height`, `orientation` (`vertical`, `horizontal`, `square`), `dominant_color`, `sha256`.

The vocabulary is closed. A value outside the lists fails validation. If nothing fits, choose the nearest and put the nuance in `desc`.

## Name

```bash
python scripts/photo_index.py rename brand
```

Files become `f012_portrait_ana_vertical_text-top.jpg`: id, type, who, orientation, one useful trait. The name alone answers half the searches.

## Search

```bash
python scripts/photo_index.py find brand --type portrait --orientation vertical --text-space good
python scripts/photo_index.py find brand --use slide-background --person ana --limit 3
python scripts/photo_index.py find brand --text obra
```

Results come best first: best of group, good quality, palette fit. Sensitive photos are hidden unless `--include-sensitive`; weak ones unless `--include-weak`. Open at most three finalists to confirm the image matches its description. Without Python: read `index.json` and filter the same fields by hand.

Picking by piece:

| Piece | Filter |
|---|---|
| Post or carousel cover | `--orientation vertical --text-space good` |
| Slide background | `--orientation horizontal --use slide-background` |
| Bio, speaker card, video cover | `--type portrait --use bio` |
| Proof and backstage | `--use proof` or `--use backstage`, check `sensitive` |

## Care

- A photo flagged `minor` or `client-or-patient` enters only with `consent: true`, stays flagged, and is never recommended for public use without telling the owner.
- Before-and-after photos of patients or clients: say that professional bodies have their own advertising rules and that publishing is the owner's decision.
- A `weak` photo enters only if it is the only one of its type. Say which photo should be retaken.
- Do not send photos to external services unless the owner asks.

## Close the phase

Counts by type, the five strongest photos with a reason each, and the gaps ("no horizontal portrait with room for a title"). Rebuild the manual and update "Journey state".
