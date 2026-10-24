# Deck spines by type

Every spine opens with `cover` and an executive summary in SCQA (situation, complication, question, answer; see `storytelling.md`) and closes with the `ask` slide. Wherever there are numbers, replace text cards with `kpis` or a chart (see `charts.md`). Use `section-break` to separate parts when the deck has more than 10 slides.

## Proposal (architecture, project, process change)

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary (what changes, what is at stake, the decisions announced) | `cover`, `cards` + `banner` |
| 01 The proposal | Overall map; central rule or principle; one slide per relevant component; accepted trade-off | `flow`, `compare`, `table`, `cards` |
| 02 How it works | Governance or operating model; evolution over time; discarded alternatives | `flow`, `timeline`, `table` with a highlighted column |
| 03 Risks and decisions | Decided / open / not addressed; risks; inconsistencies; next steps with exit criteria; ask | `status-columns`, `table`, `grid-2`, `timeline` + `highlight-box`, `ask` |

## Project brief (kickoff, charter, initiative pitch)

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; SCQA summary | `cover`, `cards` + `banner` |
| 01 The project | Brief; the problem with the number that justifies it; what changes for whom | `brief`, `kpis` or chart, `compare` (before and after) |
| 02 How we will do it | Schedule with milestones; workstreams and owners; roadmap of what comes after | `gantt`, `table`, `roadmap` |
| 03 Conditions | Success metrics with targets; assumptions and dependencies; risks; ask | `bullet` or `kpis`, `status-columns`, `table`, `ask` |

## Metrics review (data-driven)

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary with the 3 numbers of the period and the reading in one sentence | `cover`, `kpis` + `banner` |
| 01 What the numbers say | Main trend; actual vs target; ranking or mix; bridge explaining the change | `line`, `bullet`, `bar` or `stack`, `waterfall` |
| 02 Why | Causes (observation, implication, recommendation per slide) | `cards`, `compare`, `callout` |
| 03 What to do | Actions with owner and date; risks; ask | `table`, `roadmap`, `ask` |

Rule for this type: at most one chart per slide, and every chart has an action title, a caption of what it measures, and a source.

## Status report

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary (result in one sentence, 3 numbers that matter, what I need) | `cover`, `big-numbers` + `banner` |
| 01 Where we are | Plan vs actual; schedule with the status of each workstream; what got stuck and why | `bullet` or `table`, `gantt`, `cards` |
| 02 What changed | Timeline of the period; lessons | `timeline`, `callout` |
| 03 From here | Risks; next milestones; ask | `table`, `timeline`, `ask` |

## Plan (roadmap, 90-day plan, budget)

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary (goal, deadline, cost or effort) | `cover`, `cards` + `banner` |
| 01 Why | Problem; what happens if nothing is done | `cards`, `callout` |
| 02 The plan | Schedule with milestones (or roadmap without firm dates); workstreams and owners; success metrics | `gantt` or `roadmap`, `table`, `bullet` or `kpis` |
| 03 Conditions | Assumptions and dependencies; risks; ask | `status-columns`, `table`, `ask` |

## Post-mortem or incident

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary (what happened, impact, root cause in one sentence) | `cover`, `big-numbers` + `banner` |
| 01 What happened | Incident timeline; business impact | `timeline`, `big-numbers` |
| 02 Why | Causal chain; what worked and what did not | `flow`, `compare` |
| 03 What changes | Actions with owner and date; remaining risks; ask | `table`, `ask` |

## Options comparison (vendor, tool, path)

| Part | Slides | Components |
|---|---|---|
| Opening | Cover; Summary (the question, the recommendation, the cost of not deciding) | `cover`, `cards` + `banner` |
| 01 Criteria | What matters and why | `cards` |
| 02 Options | Comparison table with the recommended option highlighted; one slide per finalist | `table` with `td.hl`, `compare` |
| 03 Decision | Risks of the recommended option; adoption plan; ask | `table`, `timeline`, `ask` |

## Content rules

- **Eyebrow:** 1 to 4 words naming the theme.
- **Title:** a complete claim, two lines at most. Strong: "Teams never read each other's data: that is what prevents deadlock". Weak: "Dependency rules".
- **Detail:** at most 3 lines per card. If it does not fit, split the slide. Never shrink the font.
- **Speaker notes** (`<aside>`) on every content slide: 2 to 4 sentences with the argument that does not fit on the slide.
