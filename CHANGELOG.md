# Changelog

All notable changes to the Shortcuts Playground plugin are documented in this file. The skill-level changelog lives at `skills/shortcuts-playground/CHANGELOG.md`.

## [1.0.0] — 2026-04-13

### Added
- Initial plugin conversion from the standalone `generate-shortcuts-skill` Claude Code skill.
- `skills/shortcuts-playground/` — full knowledge base carried over verbatim, with `SKILL.md` adapted to invoke the new bin wrappers instead of `python3 scripts/*.py` calls. Includes `BEST_PRACTICES.md`, `ACTIONS.md`, `APPINTENTS.md`, `PARAMETER_TYPES.md`, `VARIABLES.md`, `CONTROL_FLOW.md`, `FILTERS.md`, `EXAMPLES.md`, `THIRD_PARTY_ACTIONS.md`, `TOOLKIT_SNAPSHOT.md`, `ICONS_AND_COLORS.md`, `PLIST_FORMAT.md`, the golden-shortcuts reference library, and the ToolKit v63 metadata bundle.
- `agents/shortcut-builder.md` — specialized agent that owns the full design → build → validate → sign → archive loop, keeping the main thread free of the 1.2 MB knowledge base.
- `hooks/hooks.json` + `hooks/auto-validate.sh` — `PostToolUse` hook that auto-runs the Craig Loop validator on every `Write`/`Edit` that produces a Shortcuts plist file. Exits with code 2 + stderr on failure so validator output is injected back into Claude's context for the next iteration.
- `bin/validate-shortcut` — wrapper around `validate_shortcut.py`.
- `bin/resolve-icon` — wrapper around `select_shortcut_icon_color.py`.
- `bin/sign-shortcut` — combines archive + `shortcuts sign` into one command; respects `output_dir` and `signing_mode` userConfig values.
- `userConfig.output_dir` and `userConfig.signing_mode` — prompted at install time; falls back to `~/Documents/Shortcuts Playground` and `anyone` respectively.

### Migration notes from the standalone skill
- The Craig Loop is now **automatic**. Previously the model had to remember to invoke `validate_shortcut.py` after every `Write`; now the hook runs it unconditionally.
- All paths in `SKILL.md` that referenced `python3 scripts/<name>.py` now use the bin wrappers (`validate-shortcut`, `resolve-icon`, `sign-shortcut`) or `${CLAUDE_PLUGIN_ROOT}`-prefixed paths for the dev-only regression scripts.
- The archive directory is configurable via `userConfig.output_dir` instead of the hardcoded `~/Agent/Shortcuts Playground/` path.
- The skill name namespace is now `shortcuts-playground:shortcuts-playground`; the original `shortcuts-generator` name remains available via the parallel `~/.claude/skills/generate-shortcuts-skill/` installation until it is explicitly removed.
