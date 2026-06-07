# Shortcuts Playground Skill

Claude Code skill for AI-assisted generation and remixing of macOS/iOS Shortcuts. It produces valid Shortcuts plist XML, validates it with the bundled preflight validator, and signs it on macOS with Apple's `shortcuts` CLI through plugin-provided wrapper commands.

## Documentation Entry Points

- Start with [SKILL.md](SKILL.md) for workflow and high-level rules.
- Treat [BEST_PRACTICES.md](BEST_PRACTICES.md) as mandatory policy.
- Use [ACTIONS.md](ACTIONS.md), [APPINTENTS.md](APPINTENTS.md), and [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) as identifier references.
- Use [HEALTHKIT.md](HEALTHKIT.md) for iOS/iPadOS Health actions.
- Use [EXAMPLES.md](EXAMPLES.md) and `golden-shortcuts/index.jsonl` for working XML patterns.

## Claude Code Usage

Install the parent Claude Code plugin, then use either slash command:

- `/shortcuts-playground:build <brief>` creates a new shortcut from scratch.
- `/shortcuts-playground:remix <absolute-path-to-xml> <change>` applies a surgical diff to an existing unsigned XML shortcut.

The Claude package provides slash commands, specialized agents, a PostToolUse validation hook, and PATH wrapper commands:

```bash
resolve-icon --prompt "Build a weather shortcut"
validate-shortcut /path/to/Shortcut.xml
sign-shortcut /path/to/Shortcut.xml --name "Shortcut Name"
```

`sign-shortcut` defaults to `CLAUDE_PLUGIN_OPTION_OUTPUT_DIR` or `~/Documents/Shortcuts Playground`, and `CLAUDE_PLUGIN_OPTION_SIGNING_MODE` or `anyone`.

If `shortcuts sign` reports that a validator-clean plist "isn't in the correct format", retry outside Codex `workspace-write` sandbox restrictions before assuming the XML is malformed.

## What's Included

| File | Description |
|------|-------------|
| [SKILL.md](SKILL.md) | Skill definition with Claude Code workflow rules |
| [ACTIONS.md](ACTIONS.md) | WF*Action identifiers and parameters |
| [APPINTENTS.md](APPINTENTS.md) | AppIntent actions (macOS ToolKit v63 + backups) |
| [PARAMETER_TYPES.md](PARAMETER_TYPES.md) | Parameter value types and serialization formats |
| [PLIST_FORMAT.md](PLIST_FORMAT.md) | Complete plist structure |
| [BEST_PRACTICES.md](BEST_PRACTICES.md) | Mandatory generation guidelines |
| [HEALTHKIT.md](HEALTHKIT.md) | HealthKit action schemas and examples |
| [CONTROL_FLOW.md](CONTROL_FLOW.md) | Repeat, conditional, and menu patterns |
| [FILTERS.md](FILTERS.md) | Filter action predicates |
| [VARIABLES.md](VARIABLES.md) | Variable reference patterns |
| [ICONS_AND_COLORS.md](ICONS_AND_COLORS.md) | Icon glyph and color selection |
| [EXAMPLES.md](EXAMPLES.md) | Complete working examples |
| [URL_SCHEMES.md](URL_SCHEMES.md) | Shortcuts URL scheme and x-callback-url guidance |
| [JAVASCRIPT_WEBPAGE.md](JAVASCRIPT_WEBPAGE.md) | Run JavaScript on Webpage rules |
| [DATE_TIME.md](DATE_TIME.md) | Date/time recipes and custom format guidance |
| [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) | Third-party actions (ToolKit + backups) |
| [TOOLKIT_SNAPSHOT.md](TOOLKIT_SNAPSHOT.md) | Bundled ToolKit v63 metadata package and field coverage |
| `scripts/select_shortcut_icon_color.py` | Natural-language icon/color resolver |
| `scripts/validate_shortcut.py` | Preflight validator |
| `scripts/test_wiring_regressions.py` | Deterministic validator regression suite |
| `scripts/test_random_mixed_shortcuts.py` | Random mixed-action validator suite |
| `data/toolkit-v63-tool-ids.json` | Bundled ToolKit v63 action-ID allowlist |
| `data/healthkit-ios26.2-reference.json` | HealthKit types, category values, workout types, and units |

## Requirements

- Python 3.10+ for validation.
- macOS with the built-in `shortcuts` CLI for signing.
- Claude Code with plugin support.

## License

MIT
