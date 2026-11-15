# Optional target: a Design System artifact in Claude

Use this only when the session lists a **Design System** artifact type. The local kit stays the source you validate; the artifact is a hosted copy the owner can open, share and point other agents to.

## Order

1. Build and validate the kit locally first (phases 5 and 6). Never publish a kit that fails `validate.py`.
2. Create the artifact from the Design System type with the brand name as title, and follow the instructions the type returns. They decide file paths, size limits and the order of writes. If they conflict with this page, they win.
3. Map the kit:

| Kit | Design system |
|---|---|
| `tokens.json` | `project/tokens.json`. The shapes match: color tokens as a list with `name`, `value` per theme and `usage`; `type.families` and `type.groups`; `spacing` and `radius` lists |
| `brand.md` | `project/README.md` |
| `logos/*` | Uploads in the asset group `Logos`, with a short `README.md` for the group |
| `photos/*.jpg` | Uploads in the asset group `Photos` |
| `photos/index.json` | A text file in the `Photos` group, plus a group `README.md` with the vocabulary and the search recipe from `photos.md` |

4. Add each upload's returned address to its photo entry as `url`, in the copy of `index.json` you publish, so an agent can fetch a photo by id.
5. Write the type's index last, as its instructions say.

## After publishing

- Put the artifact link in the brand skill as the first place to read.
- New photos: run phase 6 locally, then upload only the new files and the updated index.
- To the owner this is "your brand manual, saved". Do not explain the mechanism.

If the type is not available, skip this page. The kit and `manual.html` are the deliverable.
