# Shortcuts Playground Skill

Codex skill for AI-assisted generation and remixing of macOS/iOS Shortcuts. It produces valid Shortcuts plist XML, validates it with the bundled preflight validator, and can sign it on macOS with Apple's `shortcuts` CLI.

## Documentation Entry Points

- Start with [SKILL.md](SKILL.md) for workflow and high-level rules.
- Treat [BEST_PRACTICES.md](BEST_PRACTICES.md) as mandatory policy.
- Use [ACTIONS.md](ACTIONS.md), [APPINTENTS.md](APPINTENTS.md), and [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) as identifier references.
- Use [HEALTHKIT.md](HEALTHKIT.md) for iOS/iPadOS Health actions.
- Use [EXAMPLES.md](EXAMPLES.md) and `golden-shortcuts/index.jsonl` for working XML patterns.

## Codex Usage

Install the parent Codex plugin, then ask Codex to build or remix a shortcut:

- "Create a shortcut that shows the current weather."
- "Build a shortcut that asks for text input and shows it."
- "Remix `/path/to/Shortcut.xml` to add a notification at the start."

Codex plugins do not provide Claude-style slash commands, agents, hooks, or PATH wrapper bins. This skill uses direct script calls instead:

```bash
SKILL_DIR=/path/to/shortcuts-playground
python3 "$SKILL_DIR/scripts/select_shortcut_icon_color.py" --prompt "Build a weather shortcut"
python3 "$SKILL_DIR/scripts/validate_shortcut.py" /path/to/Shortcut.xml
"$SKILL_DIR/scripts/sign_shortcut.sh" /path/to/Shortcut.xml --name "Shortcut Name"
```

`sign_shortcut.sh` defaults to `SHORTCUTS_PLAYGROUND_OUTPUT_DIR` or `~/Documents/Shortcuts Playground`, and `SHORTCUTS_PLAYGROUND_SIGNING_MODE` or `anyone`.

## What's Included

| File | Description |
|------|-------------|
| [`SKILL.md`](SKILL.md) | Skill definition with Codex workflow rules |
| [`ACTIONS.md`](ACTIONS.md) | WF*Action identifiers and parameters |
| [`APPINTENTS.md`](APPINTENTS.md) | AppIntent actions (macOS ToolKit v63 + backups) |
| [`PARAMETER_TYPES.md`](PARAMETER_TYPES.md) | Parameter value types and serialization formats |
| [`URL_SCHEMES.md`](URL_SCHEMES.md) | Apple-documented Shortcuts URL schemes and x-callback-url patterns |
| [`JAVASCRIPT_WEBPAGE.md`](JAVASCRIPT_WEBPAGE.md) | Run JavaScript on Webpage runtime requirements |
| [`DATE_TIME.md`](DATE_TIME.md) | UNIX timestamp, ISO 8601, RFC 2822, and custom date/time recipes |
| [`VARIABLES.md`](VARIABLES.md) | Variable reference system |
| [`CONTROL_FLOW.md`](CONTROL_FLOW.md) | Repeat, Conditional, Menu patterns |
| [`FILTERS.md`](FILTERS.md) | Content filters for Find/Filter actions |
| [`HEALTHKIT.md`](HEALTHKIT.md) | iOS/iPadOS Health action schemas and bundled anonymized XML examples |
| [`EXAMPLES.md`](EXAMPLES.md) | Complete working examples |
| [`BEST_PRACTICES.md`](BEST_PRACTICES.md) | Mandatory build guidelines |
| [`ICONS_AND_COLORS.md`](ICONS_AND_COLORS.md) | Icon glyph and color selection workflow |
| [`THIRD_PARTY_ACTIONS.md`](THIRD_PARTY_ACTIONS.md) | Third-party actions (ToolKit + backups) |
| [`TOOLKIT_SNAPSHOT.md`](TOOLKIT_SNAPSHOT.md) | Bundled ToolKit v63 metadata package and field coverage |
| `scripts/select_shortcut_icon_color.py` | Natural-language icon/color resolver |
| `scripts/validate_shortcut.py` | Preflight validator |
| `scripts/sign_shortcut.sh` | Codex archive-and-sign helper |
| `scripts/test_wiring_regressions.py` | Deterministic validator regression suite |
| `data/toolkit-v63-tool-ids.json` | Bundled ToolKit v63 action-ID allowlist |
| `data/healthkit-ios26.2-reference.json` | HealthKit types, category values, workout types, and units |

## Requirements

- Python 3.10+ for validation.
- macOS with the built-in `shortcuts` CLI for signing.

## License

MIT
