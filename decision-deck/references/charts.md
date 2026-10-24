# Charts: which one and how to declare it

The template has a runtime that draws charts from JSON. You do NOT draw SVG. You choose the type, write the data and mark the highlight.

```html
<p class="chart-caption">[What is measured, unit]</p>
<div class="chart" data-type="bar">
<script type="application/json">{ ...data... }</script>
</div>
<p class="source">Source: [origin] · cut-off [date] · [estimate, validate before quoting]</p>
```

The slide title states the conclusion. The `chart-caption` says what is measured. The `source` says where it came from.

JSON rules: double quotes, no trailing commas, numbers as numbers (not strings). Never put `<` inside the JSON; write `<` instead.

## Which chart (by the question the data answers)

| The question is... | Use | Avoid |
|---|---|---|
| How did it change over time? | `line` (many points) or `column` (up to ~8 periods) | horizontal bars |
| Who is biggest, ranking? | `bar` (sorted) | pie, columns with long labels |
| Are we on target? | `bullet` (one row per metric) or `kpis` | speedometer, gauge |
| From value A to value B, what explains the gap? | `waterfall` | two loose columns |
| What is the composition of a total? | `stack` (up to 5 parts) | pie with more than 3 slices |
| When does each thing happen? | `gantt` | a table of dates |
| What comes now and later, without firm dates? | `roadmap` (HTML component) | a Gantt with invented dates |
| What are the 3 numbers of the moment? | `kpis` (HTML component) | a table |

Correlation, distribution and maps are not in the runtime. If the material needs them, state the finding in text with `big-numbers` or `callout` and tell the user the chart must be made separately.

## Common fields

- `unit`: suffix after the number ("%", "k", " h", " days").
- `prefix`: before the number ("$", "R$ ", "€").
- `decimals`: fixed decimal places (default: 0 for integers, 1 otherwise).
- `highlight`: list of indexes (0, 1, 2...) or labels drawn in the accent color. Everything else is gray. Highlight ONE thing, two at most.

Numbers are formatted for the deck language (`lang` on `<html>`): `1,234.5` in English, `1.234,5` in Portuguese.

## bar (ranking, magnitude)
```json
{"unit":"%","highlight":["South region"],
 "items":[{"label":"South region","value":38},{"label":"North region","value":24},{"label":"East region","value":17}]}
```
Sorted from largest to smallest (turn off with `"sort":false`). Up to 8 items. Labels up to ~25 characters (or set `label_width`).

## column (few periods or categories)
```json
{"unit":" M","prefix":"$","highlight":[3],
 "items":[{"label":"Q1","value":120},{"label":"Q2","value":135},{"label":"Q3","value":150},{"label":"Q4","value":170}]}
```
Up to 8 columns, short labels. `height` in px (default 440; use 280 to 360 when the slide also has KPIs).

## line (trend over time)
```json
{"unit":"k","labels":["Jan","Feb","Mar","Apr","May","Jun"],
 "series":[{"name":"Actual","values":[42,45,47,52,55,58],"highlight":true,"color":"good"},
           {"name":"Plan","values":[44,46,48,50,52,54]}],
 "target":{"value":60,"label":"Target"},
 "annotations":[{"index":3,"text":"new campaign starts","position":"above"}]}
```
- Up to 4 series; only one with `highlight`. `"color":"good"` makes the highlighted series green when the reading is positive.
- `null` in `values` for a missing point.
- The axis starts at zero by default; use `"zero":false` only when the variation is the point and zero would flatten the line.
- `annotations`: at most 2, text up to ~30 characters. `position`: "above" or "below".

## bullet (actual vs target)
```json
{"items":[
 {"label":"Satisfaction (0 to 10)","actual":8.4,"target":8.5},
 {"label":"Response time (h)","actual":3,"target":4,"higher_is_better":false}]}
```
Green when the target is met, accent when it is not, and the text next to it says so (color never speaks alone). Optional `ranges`: three thresholds [poor, ok, good].

## waterfall (bridge between two totals)
```json
{"unit":"k","positive_is_good":true,"items":[
 {"label":"Start of year","value":500,"type":"total"},
 {"label":"New customers","value":120},{"label":"Churn","value":-60},{"label":"Price change","value":40},
 {"label":"End of year","value":600,"type":"total","highlight":true}]}
```
`positive_is_good:true` for revenue (up is good: green). Use `false` for cost (up is bad: red). Check that the final total equals the first total plus the steps.

## stack (composition of 100%)
```json
{"highlight":["Online"],"items":[{"label":"Online","value":52},{"label":"Stores","value":30},{"label":"Partners","value":18}]}
```
Up to 5 parts. Group the rest as "Other".

## gantt (real dates)
```json
{"start":"2027-01","end":"2027-06","today":"2027-02-10",
 "bars":[{"label":"Discovery","start":"2027-01","end":"2027-01","status":"done"},
         {"label":"Build","start":"2027-02","end":"2027-04","status":"active"},
         {"label":"Launch","start":"2027-05","end":"2027-06","status":"planned"}],
 "milestones":[{"date":"2027-03-15","label":"Beta"},{"date":"2027-05-20","label":"Contract deadline","critical":true}]}
```
- Dates as "YYYY-MM" (whole month) or "YYYY-MM-DD".
- `status`: done (green), active (accent), planned (dashed), risk (red). The status word is written on the bar.
- Up to 12 bars, 8 milestones and 36 months. Beyond that, group or split.
- Only dates that are in the documents. Without firm dates, use `roadmap`.

## Visual honesty
- Bars and columns always start at zero (the runtime enforces it).
- Same unit for every item in a chart.
- Do not mix actuals and projections in one series without saying so: put the projection in a separate series named "Projection".
- If the number is an estimate, the `source` line says so.
