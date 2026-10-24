# Install

Every skill in this repository is a folder with a `SKILL.md`, following the open Agent Skills format. Agents that support it read only the name and description at startup and load the full instructions when your request matches.

## Get the files

```bash
git clone https://github.com/jorgeac12/decisive.git
```

or download a single skill folder from the [releases](https://github.com/jorgeac12/decisive/releases) page.

## Claude Code

```bash
# for you, in every project
cp -r decisive/decision-deck ~/.claude/skills/
# or only for one project
cp -r decisive/decision-deck .claude/skills/
```

Start a new session (or reload) and ask for a deck from your documents.

## Claude apps

Zip the `decision-deck` folder and upload it in Claude's settings where custom skills are added. Code execution must be enabled for `assemble.py` and `validate.py` to run; without it the agent follows the manual path in `SKILL.md`.

## pi coding agent

```bash
cp -r decisive/decision-deck ~/.agents/skills/
```

Run `/reload` in an open session. Force the skill with `/skill:decision-deck <your request>`.

## Other agents

Any agent that supports `SKILL.md` folders: copy the folder to its skills directory. Agents without skill support: paste `SKILL.md` as instructions and give the agent access to the `references/`, `assets/` and `scripts/` files.

## Requirements

- Python 3.9+ for `assemble.py` and `validate.py` (standard library only).
- Optional: `pip install playwright && playwright install chromium` for `validate.py --render`.
- A browser to present. Internet access only for the Google Fonts (decks fall back to Arial offline).

## Tested with

| Agent | Model | Result |
|---|---|---|
| Claude Code | Claude Opus | Examples in this repository |

Tried it with another agent or model? Open a pull request adding a row.
