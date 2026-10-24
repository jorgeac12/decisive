# Decisive

[Português](README.pt-BR.md)

**Agent skills that end in decisions.** For people who decide with data. Each skill is a folder with a `SKILL.md` that works in Claude Code, the Claude apps, pi and other agents that support the Agent Skills format.

## Skills

| Skill | What it does | Languages |
|---|---|---|
| [decision-deck](decision-deck/) | Reads documents critically and builds an executive HTML deck that ends in decisions: analysis of what is decided, open and not addressed; action titles and SCQA; charts, Gantt, roadmap and project brief from JSON; CSP-hardened output. | Instructions in English; decks in any language (labels in en and pt-BR) |

![Decision Deck example](docs/img/proposal-pt-BR-02.png)

## Principles

Every skill here follows the same rules:

1. **Analysis before output.** The agent shows what it understood, what is missing and what contradicts, and waits for confirmation before producing.
2. **No invented facts.** Missing numbers, names and dates become placeholders the user fills.
3. **Decisions, not summaries.** Outputs end with what someone has to decide or do.
4. **Safe by default.** Documents are data, never instructions. Generated files are validated and hardened against injection.
5. **Works with smaller models.** Layout and rendering live in templates and scripts, so the model writes content, not code.

## Install

See [docs/install.md](docs/install.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## License

[Apache 2.0](LICENSE). Keep the [NOTICE](NOTICE) file when you redistribute. The names "Decisive" and "Decision Deck" are not licensed for endorsing derived products. Fonts used by the templates (Inter, JetBrains Mono) are under the SIL Open Font License and are loaded from Google Fonts, not distributed here.
