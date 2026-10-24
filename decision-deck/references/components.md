# Component catalog

Use only these patterns. Replace the text in brackets. Do not create classes, CSS, `<style>` or `<script>` (except chart JSON). Inline `style` is allowed only for `width` on table header cells, `color` on a label, and the `font-size`/`max-width`/`margin-top` shown here.

## Color rules

- **Solid accent** (`accent-solid`, `banner`, the `ask` slide): only the central idea. At most one `accent-solid` per slide.
- **Soft accent** (`accent-soft`, `td.hl`, `tr.hl`): supporting items, and one whole table column you want to highlight.
- **Good** (`good-soft`, `lvl-ok`, `top-good`): decided, allowed, adopted, positive.
- **Bad** (`bad-soft`, `lvl-high`, `tr.risk`): forbidden, high risk, discarded. Never decorative.
- Color never speaks alone: always write the word too (High, Not allowed, Adopted).

## Layout rules

- Rows of numbered cards have a short label on the left ("The problem", "The way out") and space between rows.
- Several cards on a slide: all visible, discreet numbering, arrows guiding the reading order.
- A note about a table goes in a `callout`, never in a loose paragraph.
- A story over time goes in a `timeline` split by periods or steps.
- Safe area: 1664 x 792 px. Budget per slide: eyebrow plus a two-line title take ~210 px, leaving ~580 px. Table: ~100 px per two-line row. Card with title and 3 lines: ~230 px. If it does not fit, split the slide; `validate.py --render` reports overflow.

---

## cover
```html
<section class="cover">
  <div class="bars"><i></i><i></i></div>
  <p class="eyebrow">[AREA · MONTH YEAR]</p>
  <h1>[The deck's thesis in one sentence]</h1>
  <p class="muted" style="font-size:32px;max-width:1300px">[What the deck covers and what it asks, two lines at most]</p>
  <p style="color:var(--faint)">[For whom · Presenter · Internal]</p>
</section>
```

## section-break
```html
<section class="section-break">
  <p class="big">01</p>
  <h2>[Section name]</h2>
  <p class="muted" style="font-size:30px">[One-line subtitle]</p>
</section>
```

## cards (up to 3 per row, up to 2 rows)
```html
<section>
  <p class="eyebrow">[Theme]</p>
  <h2>[The slide's claim]</h2>
  <div class="row">
    <p class="row-label">The problem</p>
    <div class="card"><p class="num">1</p><h3>[Short title]</h3><p class="muted">[Up to 3 lines]</p></div>
    <div class="card"><p class="num">2</p><h3>[...]</h3><p class="muted">[...]</p></div>
    <div class="card"><p class="num">3</p><h3>[...]</h3><p class="muted">[...]</p></div>
  </div>
  <div class="row">
    <p class="row-label accent">The way out</p>
    <div class="card accent-solid"><p class="num">4</p><h3>[Central idea]</h3><p>[...]</p></div>
    <div class="card accent-soft"><p class="num">5</p><h3>[...]</h3><p class="muted">[...]</p></div>
    <div class="card accent-soft"><p class="num">6</p><h3>[...]</h3><p class="muted">[...]</p></div>
  </div>
  <aside>[Speaker notes]</aside>
</section>
```

## banner (one-line takeaway in solid accent)
```html
<p class="banner">[The one sentence the audience must remember]</p>
```

## kpis (2 to 4 indicators with a change; the main one highlighted)
The change always says against what (target, previous month, last year) and uses arrow plus words, not color only. `good`, `bad` or `neutral` by business effect, not direction (a cost that falls is `good`).
```html
<div class="kpis">
  <div class="kpi main"><p class="label">[Metric]</p><p class="value">[value]</p><p class="delta good">▼ [change] vs [period]</p></div>
  <div class="kpi"><p class="label">[Metric]</p><p class="value">[value]</p><p class="delta good">▲ [change] vs target</p></div>
  <div class="kpi"><p class="label">[Metric]</p><p class="value">[value]</p><p class="delta bad">▲ [change] vs last month</p></div>
</div>
<p class="source">Source: [origin] · cut-off [date]</p>
```

## big-numbers (2 to 4 large numbers, no deltas)
```html
<div class="big-numbers">
  <div class="main"><p class="value">[42%]</p><p class="muted">[what the number means]</p></div>
  <div><p class="value">[3]</p><p class="muted">[...]</p></div>
</div>
```

## charts (bar, column, line, bullet, waterfall, stack, gantt)
See `charts.md`. One chart per slide, with `chart-caption` before and `source` after. Typical height: 280 to 460 px.

## flow (horizontal steps; for vertical use `class="col"` and `arrow-down`)
```html
<div class="row" style="align-items:center">
  <div class="card good-soft"><h3>[Step 1]</h3><p class="muted">[...]</p></div>
  <div class="arrow"></div>
  <div class="card"><h3>[Step 2]</h3><p class="muted">[...]</p></div>
  <div class="arrow"></div>
  <div class="card accent-soft"><h3>[Main step]</h3><p class="muted">[...]</p></div>
</div>
```

## compare (not allowed vs allowed, before vs after)
```html
<div class="row">
  <div class="card bad-soft"><p class="lvl-high">✕ Not allowed: [...]</p><p class="muted">[Why it breaks]</p></div>
  <div class="card good-soft"><p class="lvl-ok">✓ Allowed: [...]</p><p class="muted">[How it works]</p></div>
</div>
<div class="callout"><p>[The rule in one sentence]</p></div>
```

## table (up to 6 data rows, up to 4 columns)
```html
<table>
  <tr><th style="width:26%">[Col]</th><th style="width:30%">[Col]</th><th style="width:12%">Level</th><th style="width:32%">My reading</th></tr>
  <tr class="risk"><td>[...]</td><td>[...]</td><td class="lvl-high">High</td><td class="hl">[...]</td></tr>
  <tr><td>[...]</td><td>[...]</td><td class="lvl-med">Medium</td><td class="hl">[...]</td></tr>
  <tr class="hl"><td>Verdict</td><td>[...]</td><td></td><td class="lvl-ok">[Adopted]</td></tr>
</table>
<div class="callout"><p>[Note about the table]</p></div>
```
`callout good` and `callout bad` change the stripe color.

## timeline (3 or 4 periods or steps)
```html
<div class="timeline">
  <div class="top-neutral"><p class="muted" style="font-weight:700">[Period 1]</p><h3>[...]</h3><p class="muted">[...]</p></div>
  <div class="top-accent"><p style="color:var(--accent-text);font-weight:700">[Period 2]</p><h3>[...]</h3><p class="muted">[...]</p></div>
  <div class="top-good"><p style="color:var(--good-text);font-weight:700">[Period 3]</p><h3>[...]</h3><p class="muted">[...]</p></div>
</div>
```

## highlight-box (criteria, conditions, a short list of 4 to 6 items)
```html
<div class="highlight-box">
  <h3>[List title]</h3>
  <div class="two-col"><p>[item]</p><p>[item]</p><p>[item]</p><p>[item]</p></div>
</div>
```

## status-columns (decided, open, not addressed)
```html
<div class="row">
  <div class="card good-soft top-good"><h3 style="color:var(--good-text)">Decided</h3><p>[item]</p><p>[item]</p></div>
  <div class="card top-neutral"><h3 style="color:var(--muted)">Open (stated)</h3><p>[item]</p></div>
  <div class="card accent-soft top-accent"><h3 style="color:var(--accent-text)">Not addressed</h3><p>[item]</p></div>
</div>
```

## grid-2 (2x2, for inconsistencies; the most serious in `accent-soft`)
```html
<div class="grid-2">
  <div class="card accent-soft"><p class="num">1</p><h3>[Topic]</h3><p class="muted">[A says X. B says Y. Decide Z.]</p></div>
  <div class="card"><p class="num">2</p><h3>[...]</h3><p class="muted">[...]</p></div>
</div>
```

## roadmap (Now, Next, Later: direction without invented dates)
Each item is a problem or outcome, not a task. Only "Now" is a commitment. A real external deadline (contract, regulation) goes in a `deadline` item.
```html
<div class="roadmap">
  <div class="now"><h3>Now<small>committed</small></h3>
    <div class="item"><b>[Initiative]</b><span>Outcome: [result]</span></div>
    <div class="item deadline"><b>[Initiative]</b><span>External deadline: [date]</span></div></div>
  <div class="next"><h3>Next<small>likely</small></h3>
    <div class="item"><b>[...]</b><span>Outcome: [...]</span></div></div>
  <div class="later"><h3>Later<small>open</small></h3>
    <div class="item"><b>[...]</b><span>[condition to come in]</span></div></div>
</div>
```

## brief (a project on one slide)
3-column grid. `wide` spans 2, `full` spans 3. Status with a `pill`, always with a word: green "On track", yellow "At risk", red "Off track", gray "Not started".
```html
<div class="brief">
  <div class="field"><p class="label">Objective</p><p>[outcome in one sentence]</p></div>
  <div class="field"><p class="label">Owner</p><p>[name or role]</p><span class="pill yellow">At risk</span></div>
  <div class="field"><p class="label">Deadline</p><p>[date]</p></div>
  <div class="field wide"><p class="label">Scope</p><p>[what is in]</p></div>
  <div class="field out"><p class="label">Out of scope</p><p>[what is not]</p></div>
  <div class="field full success"><p class="label">Success if</p><p>[measurable criteria]</p></div>
</div>
```
Other useful fields: Problem, Audience, Dependencies, Budget, Main risks. Seven fields at most.

## ask (last slide; up to 5 items, the last one `final`)
```html
<section class="ask">
  <p class="eyebrow">What I need from you</p>
  <h2>[N] decisions to [objective]</h2>
  <div class="ask-item"><p class="n">1</p><p>[Imperative verb + decision]</p></div>
  <div class="ask-item"><p class="n">2</p><p>[...]</p></div>
  <div class="ask-item final"><p class="n">3</p><p>[...]</p></div>
  <aside>[Notes]</aside>
</section>
```

## Utility classes
`muted` (secondary text), `mono` (code or table names), `num` (small accent number), `row`, `col`, `two-col`.
