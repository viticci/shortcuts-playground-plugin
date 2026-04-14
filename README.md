# Shortcuts Playground — a Claude Code plugin

**Turn Claude Code into a full-stack macOS/iOS Shortcuts author.** This plugin bundles a comprehensive Shortcuts knowledge base, a specialized build agent, automatic plist validation on every write, and wrapper commands that handle icon selection, validation, and the archive-and-sign pipeline.

Ask Claude to build a shortcut. Get back a signed `.shortcut` you can import.

## Why this exists

Writing valid Shortcuts plists by hand — even with an LLM — is miserable. The XML format is under-documented, action identifiers change between OS releases, variable wiring breaks in silent ways, and half the rules you need are only documented in Apple's ToolKit binaries. The standalone [`shortcuts-generator` skill](https://www.macstories.net) that this plugin grew out of fixed most of that, but it only ran on the author's machine because every path was hardcoded.

`shortcuts-playground` packages the same knowledge base as a distributable Claude Code plugin. The model-only workflow becomes a model + agent + hook + bin workflow. The Craig Loop (validate → fix → revalidate) happens automatically via a `PostToolUse` hook. The bin/ wrappers work from any directory. The archive path is configurable per user.

## What's in the box

| Component | Path | Purpose |
|-----------|------|---------|
| **Skill** | `skills/shortcuts-playground/` | The complete 12k-line Shortcuts knowledge base: action identifiers, wiring rules, 56 `BEST_PRACTICES.md` entries, golden example XMLs, ToolKit v63 metadata. Claude loads it automatically when you ask for a shortcut. |
| **Build agent** | `agents/shortcut-builder.md` | `shortcut-builder` — specialized agent that owns the full design → build → validate → sign → archive loop for new shortcuts. |
| **Remix agent** | `agents/shortcut-remixer.md` | `shortcut-remixer` — specialized agent that applies a surgical natural-language diff to an existing unsigned XML shortcut. Preserves UUIDs, icon, metadata, and every action the user didn't ask to touch. |
| **Hook** | `hooks/hooks.json` + `hooks/auto-validate.sh` | `PostToolUse` hook that runs the Craig Loop validator on every `Write`/`Edit` producing a Shortcuts plist — applies to BOTH agents. Exit code 2 + stderr feeds validator output back into Claude's context so the model can iterate. |
| **CLI** | `bin/validate-shortcut`, `bin/resolve-icon`, `bin/sign-shortcut`, `bin/shortcuts-playground-selftest` | Bare commands added to Claude's Bash `PATH` whenever the plugin is enabled. Work from any working directory. |
| **Slash commands** | `commands/build.md`, `commands/remix.md` | `/shortcuts-playground:build <brief>` — create from scratch. `/shortcuts-playground:remix <path> <idea>` — diff an existing unsigned `.xml` file. |
| **User config** | `plugin.json` → `userConfig` | `output_dir` (archive root) and `signing_mode` (`anyone` or `people-who-know-me`). See [Configuration](#configuration) for how to set these. |

## Requirements

- **macOS** with the built-in `shortcuts` CLI (signing only works on macOS).
- **Claude Code** recent enough to support plugins (`/plugin` command).
- **Python 3.10+.** The validator uses PEP 604 union syntax (`int | None`) which requires 3.10 or later. `/usr/bin/python3` on older macOS ships Python 3.9.6 and will fail — install Python 3.10+ via Homebrew (`brew install python3`) or [python.org](https://www.python.org/downloads/), or point the plugin at a specific interpreter with `SHORTCUTS_PLAYGROUND_PYTHON=/opt/homebrew/bin/python3`. The `shortcuts-playground-selftest` command (below) will tell you immediately if your interpreter is too old.

## Installation

This repo contains **only the plugin** (manifest + skill + agent + commands + hooks + bin). To install it, you'll add it to a Claude Code marketplace that references this directory, then install from that marketplace. Three options, ordered from quickest to most-durable:

### Option A — quickest: `--plugin-dir` (for a single session)

```bash
claude --plugin-dir /path/to/shortcuts-playground-plugin
```

Inside the session, ask for a shortcut or run `/shortcuts-playground:build <brief>`. Run `/reload-plugins` after source edits. The plugin only exists for the life of that session.

### Option B — local dev marketplace (for ongoing local development)

Create a separate marketplace directory that references this plugin repo via a symlink. The marketplace is its own git repo and points at `./shortcuts-playground-plugin` (which is a symlink to wherever you cloned this repo):

```bash
mkdir -p ~/Projects/shortcuts-playground-dev-marketplace/.claude-plugin
cd ~/Projects/shortcuts-playground-dev-marketplace

# Symlink the plugin into the marketplace directory
ln -s /path/to/shortcuts-playground-plugin shortcuts-playground-plugin

# Write marketplace.json
cat > .claude-plugin/marketplace.json <<'JSON'
{
  "name": "shortcuts-playground-dev",
  "owner": { "name": "Your Name" },
  "metadata": {
    "description": "Local dev marketplace for the Shortcuts Playground plugin.",
    "version": "1.0.0"
  },
  "plugins": [
    { "source": "./shortcuts-playground-plugin" }
  ]
}
JSON

# Register + install
claude plugin marketplace add ~/Projects/shortcuts-playground-dev-marketplace
claude plugin install shortcuts-playground@shortcuts-playground-dev
```

Source edits propagate through the symlink — Claude Code reads files in-place for directory-sourced marketplaces, so iteration is instant. Run `claude plugin update shortcuts-playground@shortcuts-playground-dev` only when you want the cache to resync (e.g., after a version bump).

### Option C — install from a public git-backed marketplace

Once a marketplace referencing this plugin is published (e.g., as a separate git repo):

```bash
claude plugin marketplace add https://github.com/<owner>/<marketplace-repo>
claude plugin install shortcuts-playground@<marketplace-name>
```

Installation scopes (for either Option B or C):
- `--scope user` (default): install for your user, available across every project.
- `--scope project`: install for the current project (shared with teammates via `.claude/settings.json`).
- `--scope local`: install for the current project only, gitignored.

After install, run the health check below to confirm everything's wired up.

## Health check

```bash
python3 --version                                     # expect 3.10+
which shortcuts                                       # expect /usr/bin/shortcuts
claude plugin list | grep shortcuts-playground        # expect "✔ enabled"
shortcuts-playground-selftest                         # expect "✔ All checks passed."
```

`shortcuts-playground-selftest` is a bundled bin command that runs six checks in order: Python version, `shortcuts` CLI presence, plugin-root resolution, bundled data files, validator-on-golden, and a full archive + sign round trip to a temporary directory. It exits 0 on pass and prints a specific error message for every failure. Run it once after install and any time you update the plugin.

For CI environments without the macOS `shortcuts` CLI, set `SHORTCUTS_PLAYGROUND_SELFTEST_SKIP_SIGN=1` to skip the sign round trip and only run the validator checks.

## Configuration

The plugin exposes two `userConfig` values in `plugin.json`:

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `output_dir` | `directory` | `~/Documents/Shortcuts Playground` | Root directory where unsigned XML archives and signed `.shortcut` files are written. |
| `signing_mode` | `string` | `anyone` | Passed to `shortcuts sign`. Use `anyone` for public distribution or `people-who-know-me` for contacts only. |

You can set these in three ways, from most to least explicit:

1. **Interactive plugin TUI.** Inside a live Claude Code session, run `/plugin` and pick `shortcuts-playground`. If prompts are available in your Claude Code build, they'll appear here.
2. **`settings.json`.** Edit `~/.claude/settings.json` directly. Non-sensitive values live under `pluginConfigs`:
   ```json
   {
     "pluginConfigs": {
       "shortcuts-playground@shortcuts-playground": {
         "options": {
           "output_dir": "/Users/you/Documents/Shortcuts Playground",
           "signing_mode": "anyone"
         }
       }
     }
   }
   ```
   Claude Code exports each value as `CLAUDE_PLUGIN_OPTION_<KEY_UPPERCASED>` (e.g. `CLAUDE_PLUGIN_OPTION_OUTPUT_DIR`) when it spawns bin wrappers, hook scripts, and MCP servers.
3. **Environment variable override.** If both above fail, you can always set the env var directly for a one-off build:
   ```bash
   CLAUDE_PLUGIN_OPTION_OUTPUT_DIR=/custom/dir sign-shortcut draft.xml --name "My Shortcut"
   ```
   Or pass `--output-dir` / `--mode` flags directly to `sign-shortcut` to bypass config entirely.

If none of these are set, the plugin falls back to `~/Documents/Shortcuts Playground/` and `anyone`. Those defaults exist so first-time install just works.

## Usage

Two workflows, two commands: **build** (from scratch) and **remix** (diff an existing XML).

### Build a new shortcut

**Natural language (auto-invocation).** Just describe what you want:

```
Build me a shortcut that asks for a city, fetches the current weather, and shows a notification.
```

Claude's skill auto-invocation picks up the Shortcuts intent and delegates to the `shortcut-builder` agent.

**Explicit slash command.** For a deterministic entry point:

```
/shortcuts-playground:build weather lookup that asks for a city and shows a notification
```

Everything after `:build` becomes the brief passed to the agent. Useful when you want to make sure the agent is invoked (for example, inside a long conversation where Claude might not auto-route).

Either path does the same thing — the `shortcut-builder` agent:
1. Reads the skill's `SKILL.md` and the relevant reference files.
2. Designs the action list and picks UUIDs.
3. Runs `resolve-icon --prompt "<your request>"` to choose a glyph + color.
4. Writes the plist XML to your `output_dir/drafts/` folder.
5. The `PostToolUse` hook auto-validates the file and feeds any errors back.
6. The agent edits until the validator passes (max 5 fix iterations).
7. Runs `sign-shortcut` to archive the unsigned XML and produce a signed `.shortcut`.
8. Returns the paths so you can open the signed file in Shortcuts.app.

### Remix an existing shortcut

When you already have a shortcut and want to apply small changes, use `/shortcuts-playground:remix`. Pass an **absolute path to an unsigned `.xml` file** (NOT a signed `.shortcut` — those are AEA1 encrypted archives) plus a natural-language description of what to change:

```
/shortcuts-playground:remix /Users/you/Documents/Shortcuts Playground/drafts/Weather.xml add a notification at the start saying "Fetching weather"
```

The `shortcut-remixer` agent:
1. Parses the command input into a source path + a remix idea.
2. Validates the source (exists, `.xml` not `.shortcut`, first bytes aren't `AEA1`, contains `WFWorkflowActions`). If any check fails, it escalates with a specific reason — it never guesses.
3. Reads the full source and baselines it against the validator (pre-existing issues in the source are informational, not fixed unless they block signing).
4. Loads relevant skill reference files for the diff you asked for.
5. Plans a surgical diff: which actions to add, modify, or remove. Preserves every other action verbatim. Preserves UUIDs, `WFWorkflowIcon`, client-version fields, and `WFWorkflowName` (unless you explicitly renamed it).
6. Writes the draft to `output_dir/drafts/<source stem> Remix.xml` (or your explicit name).
7. Runs the Craig Loop via the same `PostToolUse` hook that the builder uses.
8. Archives + signs via `sign-shortcut`, then verifies the signed file exists.
9. Reports: signed path, archive path, source path, and a one-paragraph diff summary of what changed.

**Key remix rules:**
- The source is **never overwritten**. The remix writes to a new name so your original stays intact.
- Signed `.shortcut` files **cannot be remixed directly** — export them as unsigned XML first (Shortcuts.app → Share → Copy → paste into a `.xml` file).
- If you don't provide an absolute path, the agent immediately escalates with instructions on how to provide one. It doesn't search your filesystem for "a shortcut that looks like" your intent.
- The remix output carries the "Shortcuts generated by Shortcuts Playground" disclaimer Comment in its leading actions — your source's existing top-level comments are preserved below.

### Manual commands

When you want to invoke a single step yourself:

```bash
# Validate an existing .xml or .shortcut
validate-shortcut /path/to/MyShortcut.xml

# Resolve an icon + color from free-text
resolve-icon --prompt "a calendar shortcut that pulls today's meetings"

# Archive + sign in one step
sign-shortcut /path/to/MyShortcut.xml --name "My Shortcut"

# End-to-end post-install self test
shortcuts-playground-selftest
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
│   ├── shortcut-builder.md      # build-from-scratch agent
│   └── shortcut-remixer.md      # diff-an-existing-XML agent
├── commands/
│   ├── build.md                 # /shortcuts-playground:build slash command
│   └── remix.md                 # /shortcuts-playground:remix slash command
├── hooks/
│   ├── hooks.json               # PostToolUse config
│   └── auto-validate.sh         # Craig Loop hook runner
├── bin/
│   ├── validate-shortcut
│   ├── resolve-icon
│   ├── sign-shortcut
│   └── shortcuts-playground-selftest
├── CHANGELOG.md
├── LICENSE                      # MIT
└── README.md
```

## Development

### How Claude Code resolves plugin files

This matters when you're iterating on the source:

- **Directory-sourced marketplaces** (added via `claude plugin marketplace add /local/path`) read plugin files **directly from the source directory**. Edits to `hooks/auto-validate.sh`, `agents/shortcut-builder.md`, `bin/*`, `commands/build.md`, or anything under `skills/` propagate **immediately** to the next session — no `claude plugin update` needed. Verified by tracing hook execution paths.
- **Git-sourced marketplaces** (added via `claude plugin marketplace add https://github.com/owner/repo`) copy the plugin to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` at install time and read from there. After pushing a source change to the git remote, run `claude plugin update shortcuts-playground` to sync the cache.

Both variants expose `${CLAUDE_PLUGIN_ROOT}` as the absolute path to whichever location Claude Code is reading from. All bundled commands and hooks use that variable (with a self-resolution fallback) so source-directory and cache installs behave identically from the script's point of view.

### Iteration loop

```bash
# 1. Edit source files under ~/Projects/shortcuts-playground-plugin/
# 2. Re-run the self test to catch regressions
shortcuts-playground-selftest
# 3. Re-run manifest validation
claude plugin validate ~/Projects/shortcuts-playground-plugin
# 4. Run a real build in a headless Claude session
claude -p --dangerously-skip-permissions "/shortcuts-playground:build a test shortcut that shows the current date"
```

Inside an interactive Claude Code session, use `/reload-plugins` after each change to pick up edits without restarting the session.

### Regression suites

Run these when touching validator logic, wiring rules, or action coverage:

```bash
python3 skills/shortcuts-playground/scripts/test_wiring_regressions.py --write-fixtures /tmp/wiring-regressions
python3 skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py --count 20 --min-actions 10
```

The first covers 40 Weather Detail cases, 40 Location parameter cases, and 12 Set Name cases. The second generates random multi-action shortcuts and runs the validator against each.

## Credits

- Built by **[Federico Viticci](https://www.macstories.net)** at **MacStories**, with Claude.
- Grew out of the standalone `shortcuts-generator` Claude Code skill, which bundles action identifiers, validator heuristics, and wiring rules derived from Apple's ToolKit v63 database.

## License

[MIT](LICENSE).
