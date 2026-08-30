# Shortcuts Playground — an OpenCode plugin

**Turn OpenCode into a full-stack macOS/iOS Shortcuts author.** This plugin bundles a comprehensive Shortcuts knowledge base, specialized build agents, automatic plist validation on every write, and wrapper scripts that handle icon selection, validation, and the archive-and-sign pipeline.

Ask OpenCode to build a shortcut. Get back a signed `.shortcut` you can import.

## Why this exists

Writing valid Shortcuts plists by hand — even with an LLM — is miserable. The XML format is under-documented, action identifiers change between OS releases, variable wiring breaks in silent ways, and half the rules you need are only documented in Apple's ToolKit binaries. The standalone [`shortcuts-generator` skill](https://www.macstories.net) that this plugin grew out of fixed most of that, but it only ran on the author's machine because every path was hardcoded.

`shortcuts-playground` packages the same knowledge base as a distributable plugin. The model-only workflow becomes a model + agent + hook workflow. The Craig Loop (validate → fix → revalidate) happens automatically via a `tool.execute.after` hook. The archive path is configurable per user.

OpenCode is an open-source harness a lot of people use — supporting it alongside Claude Code and Codex makes the same Shortcuts knowledge base available to that community using the same logic.

## What's in the box

| Component | Path | Purpose |
|-----------|------|---------|
| **Skill** | `skills/shortcuts-playground/` | The complete Shortcuts knowledge base: action identifiers, wiring rules, curated `BEST_PRACTICES.md` guidance, golden example XMLs, ToolKit v63 and target-gated macOS/iOS 27 v78 ID snapshots, plus reviewed static Apple-derived macOS 27 grounding, parameter-key, enum-case, trigger metadata, and exported `WFWorkflowTriggers` samples for all 42 ToolKit trigger variants. Current Mac-specific External Drive, File Modified, and Folder Changed exports are documented as lossy picker carriers rather than copyable automation headers. OpenCode loads it via `npx skills add` or `.agents/skills` discovery. |
| **Build agent** | `agents/shortcut-builder.md` | `shortcut-builder` — specialized subagent that owns the full design → build → validate → sign → archive loop for new shortcuts. |
| **Remix agent** | `agents/shortcut-remixer.md` | `shortcut-remixer` — specialized agent that applies a surgical natural-language diff to an existing unsigned XML shortcut. Preserves UUIDs, icon, metadata, and every action the user didn't ask to touch. |
| **Hook** | `plugin/validator.ts` | `tool.execute.after` hook that runs the Craig Loop validator on every `write`/`edit` producing a Shortcuts plist — applies to both agents. Throws validator output so the model can iterate. |
| **CLI** | `skills/shortcuts-playground/scripts/validate_shortcut.py`, `select_shortcut_icon_color.py`, `sign_shortcut.sh` | Direct script paths for validation, icon resolution, and archive+sign. No `bin/` PATH wrappers — invoke via `$SKILL_DIR/scripts/...`. |
| **Slash commands** | `commands/build-shortcut.md`, `commands/remix-shortcut.md` | `/build-shortcut <brief>` — create from scratch. `/remix-shortcut <path> <idea>` — diff an existing unsigned `.xml` file. |
| **User config** | env vars | `SHORTCUTS_PLAYGROUND_OUTPUT_DIR` (archive root), `SHORTCUTS_PLAYGROUND_SIGNING_MODE` (`anyone` or `people-who-know-me`), `SHORTCUTS_PLAYGROUND_TARGET_MACOS` (`auto`, `26`, `27`, or `latest`), and `SHORTCUTS_PLAYGROUND_TARGET_PLATFORM` (`macos`, `ios`, or `all`). See [Configuration](#configuration). |

## Requirements

- **macOS** with the built-in `shortcuts` CLI (signing only works on macOS).
- **OpenCode** recent enough to support plugins and skills (`opencode --help` shows `plugin`).
- **Python 3.10+.** The validator uses PEP 604 union syntax (`int | None`) which requires 3.10 or later. `/usr/bin/python3` on older macOS ships Python 3.9.6 and will fail — install Python 3.10+ via Homebrew (`brew install python3`) or [python.org](https://www.python.org/downloads/), or point the plugin at a specific interpreter with `SHORTCUTS_PLAYGROUND_PYTHON=/opt/homebrew/bin/python3`.

## Installation

This repository contains Claude, Codex, and OpenCode packages. The OpenCode plugin lives in `opencode/`, with an npm package `shortcuts-playground` for remote install and `npx skills` for the knowledge base.

### Option A — npm + skills CLI (recommended)

```bash
# 1. validator (Bun installs on next startup)
# add to opencode.json (project or ~/.config/opencode/opencode.jsonc):
# { "plugin": ["shortcuts-playground"] }

# 2. skill (standard open-skills CLI)
npx skills add viticci/shortcuts-playground-plugin -a opencode --skill shortcuts-playground
# or local checkout:
npx skills add ./opencode -a opencode --skill shortcuts-playground

# 3. optional slash commands (if you want /build-shortcut)
mkdir -p .opencode/commands .opencode/agents
cp opencode/commands/*.md .opencode/commands/
cp opencode/agents/*.md .opencode/agents/
```

Restart OpenCode TUI — `/build-shortcut` should appear under `/`.

### Option B — local file plugin (for single session / dev)

```bash
# add to opencode.json for this project:
# { "plugin": ["./opencode/plugin/validator.ts"] }
# then copy skills/commands/agents as above:
mkdir -p .opencode/plugins .opencode/skills .opencode/commands .opencode/agents
cp opencode/plugin/validator.ts .opencode/plugins/shortcuts-playground.ts
cp -R opencode/skills/shortcuts-playground .opencode/skills/
cp opencode/commands/*.md .opencode/commands/
cp opencode/agents/*.md .opencode/agents/
```

Source edits propagate immediately — restart the TUI to pick up changes. For npm installs, `npx skills add` symlinks to `.agents/skills/shortcuts-playground`.

After install, run the health check below.

## Health check

```bash
python3 --version                                     # expect 3.10+
which shortcuts                                       # expect /usr/bin/shortcuts
# check validator directly (no selftest bin in OpenCode)
python3 opencode/skills/shortcuts-playground/scripts/validate_shortcut.py opencode/skills/shortcuts-playground/golden-shortcuts/xml/*.xml | head
```

For a full self-test, run the Python regression suite (below).

## Configuration

The plugin uses four env vars (no `userConfig` UI like Claude):

| Key | Default | Purpose |
|-----|---------|---------|
| `SHORTCUTS_PLAYGROUND_OUTPUT_DIR` | `~/Documents/Shortcuts Playground` | Root directory where unsigned XML archives and signed `.shortcut` files are written. |
| `SHORTCUTS_PLAYGROUND_SIGNING_MODE` | `anyone` | Passed to `shortcuts sign`. Use `anyone` for public distribution or `people-who-know-me` for contacts only. |
| `SHORTCUTS_PLAYGROUND_TARGET_MACOS` | `auto` | Validator OS target. Use `auto` for host detection, `27` for OS 27-era shortcuts that need v78 snapshots, or `latest` to include every packaged OS snapshot. If the host cannot be detected, `auto` falls back to macOS 26. |
| `SHORTCUTS_PLAYGROUND_TARGET_PLATFORM` | `macos` | Validator platform target. Use `macos` for Mac shortcuts, `ios` for iPhone/iPad-only authoring, or `all` only for cross-platform metadata audits. |

You can set these in `opencode.json` via `shell.env` or as plain env vars:

```bash
export SHORTCUTS_PLAYGROUND_OUTPUT_DIR=/custom/dir
export SHORTCUTS_PLAYGROUND_TARGET_MACOS=27  # only when intentionally building OS 27-era shortcuts
```

Or pass `--output-dir` / `--mode` flags directly to `sign_shortcut.sh` to bypass config entirely.

If none are set, the plugin falls back to `~/Documents/Shortcuts Playground/`, `anyone`, and `auto`.

## Usage

Two workflows, two commands: **build** (from scratch) and **remix** (diff an existing XML).

### Build a new shortcut

**Natural language (auto-invocation).** Just describe what you want:

```
Build me a shortcut that asks for a city, fetches the current weather, and shows a notification.
```

OpenCode's skill auto-invocation picks up the Shortcuts intent and delegates to the `shortcut-builder` subagent.

**Explicit slash command.** For a deterministic entry point:

```
/build-shortcut weather lookup that asks for a city and shows a notification
```

Everything after `/build-shortcut` becomes the brief passed to the agent.

Either path does the same thing — the `shortcut-builder` agent:
1. Reads the skill's `SKILL.md` and the relevant reference files.
2. Designs the action list and picks UUIDs.
3. Runs `python3 "$SKILL_DIR/scripts/select_shortcut_icon_color.py" --prompt "<your request>"` to choose a glyph + color.
4. Writes the plist XML to your `output_dir/drafts/` folder.
5. The `tool.execute.after` hook auto-validates the file and feeds any errors back.
6. The agent edits until the validator passes (max 5 fix iterations).
7. Runs `"$SKILL_DIR/scripts/sign_shortcut.sh"` to archive the unsigned XML and produce a signed `.shortcut`.
8. Returns the paths so you can open the signed file in Shortcuts.app.

### Remix an existing shortcut

When you already have a shortcut and want to apply small changes, use `/remix-shortcut`. Pass an **absolute path to an unsigned `.xml` file** (NOT a signed `.shortcut` — those are AEA1 encrypted archives) plus a natural-language description of what to change:

```
/remix-shortcut /Users/you/Documents/Shortcuts Playground/drafts/Weather.xml add a notification at the start saying "Fetching weather"
```

The `shortcut-remixer` agent:
1. Parses the command input into a source path + a remix idea.
2. Validates the source (exists, `.xml` not `.shortcut`, first bytes aren't `AEA1`, contains `WFWorkflowActions`). If any check fails, it escalates with a specific reason — it never guesses.
3. Reads the full source and baselines it against the validator.
4. Loads relevant skill reference files for the diff you asked for.
5. Plans a surgical diff: which actions to add, modify, or remove. Preserves every other action verbatim.
6. Writes the draft to `output_dir/drafts/<source stem> Remix.xml` (or your explicit name).
7. Runs the Craig Loop via the same `tool.execute.after` hook.
8. Archives + signs via `sign_shortcut.sh`, then verifies the signed file exists.
9. Reports: signed path, archive path, source path, and a one-paragraph diff summary.

**Key remix rules:**
- The source is **never overwritten**. The remix writes to a new name so your original stays intact.
- Signed `.shortcut` files **cannot be remixed directly** — export them as unsigned XML first (Shortcuts.app → Share → Copy → paste into a `.xml` file).
- If you don't provide an absolute path, the agent immediately escalates with instructions on how to provide one. It doesn't search your filesystem for "a shortcut that looks like" your intent.

### Manual commands

When you want to invoke a single step yourself:

```bash
# Validate an existing .xml or .shortcut
python3 opencode/skills/shortcuts-playground/scripts/validate_shortcut.py /path/to/MyShortcut.xml

# Resolve an icon + color from free-text
python3 opencode/skills/shortcuts-playground/scripts/select_shortcut_icon_color.py --prompt "a calendar shortcut that pulls today's meetings"

# Archive + sign in one step
opencode/skills/shortcuts-playground/scripts/sign_shortcut.sh /path/to/MyShortcut.xml --name "My Shortcut"
```

## Directory layout

```
shortcuts-playground-plugin/
├── opencode/
│   ├── opencode.json            # OpenCode plugin config (plugin, commands, agents)
│   ├── plugin/
│   │   └── validator.ts         # tool.execute.after Craig Loop validator
│   ├── skills/
│   │   └── shortcuts-playground/ # complete Shortcuts knowledge base (strict mirror of claude/skills)
│   ├── agents/
│   │   ├── shortcut-builder.md  # build-from-scratch subagent (model: opus, steps: 40)
│   │   └── shortcut-remixer.md  # diff-an-existing-XML subagent
│   ├── commands/
│   │   ├── build-shortcut.md    # /build-shortcut slash command
│   │   └── remix-shortcut.md    # /remix-shortcut slash command
│   ├── package.json             # npm package for `shortcuts-playground`
│   └── README.md
```

## Development

### How OpenCode resolves plugin files

- **File-sourced plugins** (via `opencode.json: plugin: ["./opencode/plugin/validator.ts"]` or `npx skills add` symlink) read files directly from the source directory. Edits to `plugin/validator.ts`, `agents/*.md`, `commands/*.md`, or anything under `skills/` propagate immediately to the next TUI restart.
- **npm-sourced plugins** (via `opencode.json: plugin: ["shortcuts-playground"]`) are installed to `~/.cache/opencode` via Bun on startup. After `npm publish`, users get the update on next `opencode` launch (or `npm i shortcuts-playground@latest`).

### Iteration loop

```bash
# 1. Edit source files under opencode/
# 2. Re-run the validator on golden shortcuts
python3 opencode/skills/shortcuts-playground/scripts/validate_shortcut.py opencode/skills/shortcuts-playground/golden-shortcuts/xml/*.xml
# 3. Run a real build in headless OpenCode
opencode run "/build-shortcut a test shortcut that shows the current date" --format json | tail -20
```

### Regression suites

Run these when touching validator logic, wiring rules, or action coverage:

```bash
python3 opencode/skills/shortcuts-playground/scripts/test_wiring_regressions.py --write-fixtures /tmp/wiring-regressions
python3 opencode/skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py --count 20 --min-actions 10
```

The first covers Weather Detail, Location parameter, and Set Name cases. The second generates random multi-action shortcuts and runs the validator against each.

## Credits

- Grew out of the standalone `shortcuts-generator` Claude Code skill, which bundles action identifiers, validator heuristics, and wiring rules derived from Apple's ToolKit snapshots.

## License

[MIT](LICENSE).
