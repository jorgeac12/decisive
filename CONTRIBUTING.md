# Contributing

Thanks for helping. Issues and pull requests are welcome in English or Portuguese.

## License of contributions

By opening a pull request you agree that your contribution is licensed under the Apache License 2.0, as stated in its section 5. Add yourself to the commit as author; do not edit `NOTICE` except to add a line for substantial third-party material.

## Ground rules

- **No real data.** Examples, tests and screenshots use fictional companies and invented numbers. Never commit documents, names or figures from a real organization.
- **Keep the model's job small.** Prefer a template, a script or a JSON schema over more instructions for the model to follow.
- **Every new output feature needs a validator check and an example.**
- Writing style for slide text and docs: plain words, no em dashes.

## decision-deck

```
decision-deck/
├── SKILL.md            the workflow; keep it under ~150 lines
├── references/         loaded on demand by the agent
├── assets/template.html
├── scripts/
└── examples/<name>/    slides.html (source) + deck.html (assembled)
```

### Changing the runtime or CSS

1. Edit `assets/template.html`.
2. Re-pin the CSP hash: `python decision-deck/scripts/pin_csp.py decision-deck/assets/template.html`.
3. Re-assemble the examples (commands in `tests/test_decision_deck.py`, `EXAMPLES`).
4. Run `python tests/test_decision_deck.py` (needs Playwright).
5. Update `SECURITY.md` if the change touches parsing, attributes or the CSP.

### Adding a chart type

Add it to `R` in the runtime, to `CHART_TYPES` in `validate.py`, document its JSON in `references/charts.md` (with a parseable example) and use it in `examples/gallery/slides.html`. All string fields must go through `X()`, numeric fields through `N()`, and enumerated fields through a whitelist.

### Adding a component

Add the CSS using theme tokens only (no hard-coded colors), document it in `references/components.md` and show it in the gallery.

### Adding a theme

Copy a `[data-theme]` block, change only values, check contrast (4.5:1 for body text) and add the name to `THEMES` in `assemble.py`.

## Adding a new skill to the catalog

Create a folder with `SKILL.md` (`name` in lowercase-with-hyphens, `description` under 1024 characters), a README in English and Portuguese, at least one fictional example, and add a row to both catalog READMEs.
