# Shortcuts Playground — a Claude Code plugin

**Turn Claude Code into a full-stack macOS/iOS Shortcuts author.** This plugin bundles a comprehensive Shortcuts knowledge base, a specialized build agent, automatic plist validation on every write, and wrapper commands that handle icon selection, validation, and the archive-and-sign pipeline.

Ask Claude to build a shortcut. Get back a signed `.shortcut` you can import.

## Why this exists

Writing valid Shortcuts plists by hand — even with an LLM — is miserable. The XML format is under-documented, action identifiers change between OS releases, variable wiring breaks in silent ways, and half the rules you need are only documented in Apple's ToolKit binaries. The standalone [`shortcuts-generator` skill](https://www.macstories.net) that this plugin grew out of fixed most of that, but it only ran on the author's machine because every path was hardcoded.

`shortcuts-playground` packages the same knowledge base as a distributable Claude Code plugin. The model-only workflow becomes a model + agent + hook + bin workflow. The Craig Loop (validate → fix → revalidate) happens automatically via a `PostToolUse` hook. The bin/ wrappers work from any directory. The archive path is configurable per user.

## What's in the box

| Component | Path | Purpose |
|-----------|------|---------|
| **Skill** | `skills/shortcuts-playground/` | The complete 12k-line Shortcuts knowledge base: action identifiers, wiring rules, 55 `BEST_PRACTICES.md` entries, golden example XMLs, ToolKit v63 metadata. Claude loads it automatically when you ask for a shortcut. |
| **Agent** | `agents/shortcut-builder.md` | `shortcut-builder` — a specialized agent that owns the full design → build → validate → sign → archive loop. Keeps the main thread free of the knowledge base's context cost. |
| **Hook** | `hooks/hooks.json` + `hooks/auto-validate.sh` | `PostToolUse` hook that runs the Craig Loop validator on every `Write`/`Edit` producing a Shortcuts plist. Exit code 2 + stderr feeds validator output back into Claude's context so the model can iterate. |
| **CLI** | `bin/validate-shortcut`, `bin/resolve-icon`, `bin/sign-shortcut` | Bare commands added to Claude's Bash `PATH` whenever the plugin is enabled. Work from any working directory. |
| **User config** | `plugin.json` → `userConfig` | Prompts at install time for `output_dir` (archive root) and `signing_mode` (`anyone` or `people-who-know-me`). |

## Requirements

- **macOS** with the built-in `shortcuts` CLI (signing only works on macOS).
- **Claude Code** recent enough to support plugins (`/plugin` command).
- **Python 3** (any `/usr/bin/python3` on macOS works out of the box — no pip installs required).

## Installation

### Option A — during development: `--plugin-dir`

```bash
claude --plugin-dir /path/to/shortcuts-playground-plugin
```

Inside the session, ask for a shortcut. Iterate. Run `/reload-plugins` to pick up changes without restarting Claude.

### Option B — install from a marketplace

Once this plugin is published to a marketplace:

```bash
claude plugin install shortcuts-playground@<marketplace-name>
```

Installation scopes (pick one):
- `--scope user` (default): install for your user, available across every project.
- `--scope project`: install for the current project (shared with teammates via `.claude/settings.json`).
- `--scope local`: install for the current project only, gitignored.

At install time Claude Code will prompt for the two userConfig values:
- `output_dir` — where archived unsigned XML and signed `.shortcut` files are written. Example: `/Users/you/Documents/Shortcuts Playground`.
- `signing_mode` — `anyone` (default) or `people-who-know-me`.

Both can be left blank; the plugin falls back to `~/Documents/Shortcuts Playground/` and `anyone`.

## Usage

Just describe what you want:

```
Build me a shortcut that asks for a city, fetches the current weather, and shows a notification.
```

Claude delegates to the `shortcut-builder` agent, which:
1. Reads the skill's `SKILL.md` and the relevant reference files.
2. Designs the action list and picks UUIDs.
3. Runs `resolve-icon --prompt "<your request>"` to choose a glyph + color.
4. Writes the plist XML to your `output_dir/drafts/` folder.
5. The `PostToolUse` hook auto-validates the file and feeds any errors back.
6. The agent edits until the validator passes (max 5 fix iterations).
7. Runs `sign-shortcut` to archive the unsigned XML and produce a signed `.shortcut`.
8. Returns the paths so you can open the signed file in Shortcuts.app.

### Manual commands

When you want to invoke a single step yourself:

```bash
# Validate an existing .xml or .shortcut
validate-shortcut /path/to/MyShortcut.xml

# Resolve an icon + color from free-text
resolve-icon --prompt "a calendar shortcut that pulls today's meetings"

# Archive + sign in one step
sign-shortcut /path/to/MyShortcut.xml --name "My Shortcut"
```

## Directory layout

```
shortcuts-playground-plugin/
├── .claude-plugin/
│   └── plugin.json              # plugin manifest (name, version, userConfig)
├── skills/
│   └── shortcuts-playground/    # complete Shortcuts knowledge base
│       ├── SKILL.md
│       ├── BEST_PRACTICES.md
│       ├── ACTIONS.md
│       ├── APPINTENTS.md
│       ├── PARAMETER_TYPES.md
│       ├── ...                  # 13 reference markdown files total
│       ├── data/                # ToolKit v63 + glyph/color JSON
│       ├── golden-shortcuts/    # 19 curated example XMLs
│       └── scripts/             # Python implementations
├── agents/
│   └── shortcut-builder.md      # specialized build agent
├── hooks/
│   ├── hooks.json               # PostToolUse config
│   └── auto-validate.sh         # Craig Loop hook runner
├── bin/
│   ├── validate-shortcut
│   ├── resolve-icon
│   └── sign-shortcut
├── CHANGELOG.md
├── LICENSE                      # MIT
└── README.md
```

## Hacking on it

- Make your edits under `skills/shortcuts-playground/` — same structure as the original standalone skill.
- Run the bundled regression suites when touching validator logic:
  ```bash
  python3 skills/shortcuts-playground/scripts/test_wiring_regressions.py --write-fixtures /tmp/wiring-regressions
  python3 skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py --count 20 --min-actions 10
  ```
- Run `claude --plugin-dir .` from the plugin root to test in a live session, and `/reload-plugins` inside that session after each change.
- `claude plugin validate` (or `/plugin validate` in an active session) checks `plugin.json`, skill/agent frontmatter, and `hooks.json` for schema errors.

## Credits

- Built by **[Federico Viticci](https://www.macstories.net)** at **MacStories**, with Claude.
- Grew out of the standalone `shortcuts-generator` Claude Code skill, which bundles action identifiers, validator heuristics, and wiring rules derived from Apple's ToolKit v63 database.

## License

[MIT](LICENSE).
