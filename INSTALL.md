# Shortcuts Playground — Internal Install Guide

> Internal release. Not production-hardened. If anything looks off, contact the maintainer.

## What this is

A Claude Code plugin that turns any Claude Code session on your Mac into a full-stack Shortcuts author. Ask Claude to build a shortcut in plain English; get back a signed `.shortcut` file you can open in Shortcuts.app. Or point it at an existing unsigned `.xml` and ask for edits — that's "remix mode."

Two slash commands once installed:

- `/shortcuts-playground:build <your idea>` — build a new shortcut from scratch.
- `/shortcuts-playground:remix <absolute-path-to-xml> <your change>` — apply a surgical diff to an existing unsigned XML shortcut.

## Before you start

You need:

1. **macOS.** The signing step uses the built-in `shortcuts` CLI, which is macOS-only. You can still build and validate XML on other OSes, but you won't get a signed `.shortcut`.
2. **Claude Code.** Install from [claude.com/claude-code](https://claude.com/claude-code) and log in (`claude /login`). You need a version recent enough to support plugins — run `claude plugin --help` and make sure you see `install`, `marketplace`, `list` subcommands.
3. **Python 3.10 or newer.** The bundled validator uses syntax that requires 3.10+. Check with:
   ```bash
   python3 --version
   ```
   If you see `Python 3.9.x`, that's macOS's system Python — too old. Install 3.10+ via Homebrew:
   ```bash
   brew install python3
   ```
   If you can't upgrade the default `python3`, point the plugin at a specific interpreter:
   ```bash
   export SHORTCUTS_PLAYGROUND_PYTHON=/opt/homebrew/bin/python3
   ```
4. **A GitHub account with access to the repo.** If the plugin is installed from a private GitHub repo, log in with `gh` or configure Git credentials for HTTPS. If `git clone https://github.com/<owner>/shortcuts-playground-plugin.git` works for you, you're set.

## Install (one time)

Two commands inside any terminal:

```bash
# Step 1: tell Claude Code where the marketplace lives
claude plugin marketplace add https://github.com/<owner>/shortcuts-playground-plugin

# Step 2: install the plugin from that marketplace
claude plugin install shortcuts-playground@shortcuts-playground
```

On first install Claude Code clones the private repo into `~/.claude/plugins/cache/` — you'll see the progress. If the clone fails with a GitHub auth error, fix your Git credentials first and re-run step 1.

Confirm the install worked:

```bash
claude plugin list | grep shortcuts-playground
```

You should see a line like `shortcuts-playground@shortcuts-playground  Version: 1.5.2  ✔ enabled`.

## Verify it works (strongly recommended)

Run the bundled self-test — it validates the interpreter, the `shortcuts` CLI, the plugin root, the bundled data files, and runs an end-to-end archive + sign round trip against a known-good golden shortcut:

```bash
shortcuts-playground-selftest
```

Expected output ends with `✔ All checks passed. Plugin is ready to build shortcuts.` If anything fails, the script prints a specific error pointing at which check broke — most common issue is Python version.

Then try a real build:

```bash
claude -p "/shortcuts-playground:build a shortcut named Hello MacStories that shows a single alert saying 'It works'"
```

When it's done, open `~/Documents/Shortcuts Playground/Hello MacStories.shortcut` in Finder. Shortcuts.app will offer to import it. Done.

## Where your shortcuts go

By default, every build + remix writes to:

```
~/Documents/Shortcuts Playground/
├── Hello MacStories.shortcut              # the final signed file (open to import)
├── drafts/
│   └── Hello MacStories.xml               # the working unsigned draft
└── 2026-04-14/
    └── Hello MacStories-151223.xml        # dated archive of the unsigned XML
```

The plugin creates this directory on first use. If you want your shortcuts somewhere else (e.g., `~/iCloud Drive/Shortcuts Playground/`), add this to your `~/.claude/settings.json`:

```json
{
  "pluginConfigs": {
    "shortcuts-playground@shortcuts-playground": {
      "options": {
        "output_dir": "/Users/you/iCloud Drive/Shortcuts Playground"
      }
    }
  }
}
```

Or set it per-invocation via an environment variable:

```bash
CLAUDE_PLUGIN_OPTION_OUTPUT_DIR="/custom/path" claude -p "/shortcuts-playground:build …"
```

## Day-to-day usage

### Build a new shortcut

```
/shortcuts-playground:build build a shortcut that asks for a city and shows the current weather
```

Anything after `:build ` is a natural-language brief. The more specific you are, the fewer iterations the agent needs. Saying "show a notification" is clearer than "tell me."

### Remix an existing shortcut

You need an **unsigned `.xml`** version of the shortcut (not a signed `.shortcut` — those are encrypted archives). The easiest way to get one: export from Shortcuts.app → Share → Copy → paste into a text editor → save with `.xml` extension. Or use a draft that the plugin itself previously wrote to `~/Documents/Shortcuts Playground/drafts/`.

```
/shortcuts-playground:remix /absolute/path/to/Weather.xml add a Show Notification at the very start saying 'Fetching…'
```

The remix agent preserves every existing UUID, the icon, the workflow name (unless you explicitly rename), and every action you didn't ask to touch. It only applies the diff you described.

If you don't give it a path, it'll ask for one — it won't hunt for a matching file on your disk.

### Getting updates

When a new version ships:

```bash
claude plugin update shortcuts-playground@shortcuts-playground
```

The version bump will show up in `claude plugin list`. You may need to restart your Claude Code session to pick up any changes to the agent or hook.

### Uninstalling

```bash
claude plugin uninstall shortcuts-playground@shortcuts-playground
claude plugin marketplace remove shortcuts-playground
```

Your `~/Documents/Shortcuts Playground/` directory stays intact — the plugin never touches it on uninstall.

## Troubleshooting

**"Python 3.x is too old"** — you need 3.10+. Install via Homebrew or set `SHORTCUTS_PLAYGROUND_PYTHON` to an explicit path.

**"Plugin not loading" after an update** — start a fresh Claude Code session. Plugins load at session start; long-running sessions need a restart to see updates.

**`claude plugin list` shows the plugin but slash commands don't work** — run `/reload-plugins` inside an interactive session, or start a fresh one.

**Validator hook rejects your write** — that's the Craig Loop doing its job. Read the error message, it's specific about which action and what to fix. Let the agent iterate — it usually converges in 1–3 fixes.

**Built shortcut has wrong behavior in Shortcuts.app** — this is the agent getting a parameter wrong. Use `/shortcuts-playground:remix` with the draft XML to fix it, or describe the issue to the maintainer with the failing action's name.

**Signing fails with a "file doesn't exist" error** — a macOS `shortcuts sign` quirk. Try again; it usually retries successfully.

**Anything weirder than the above** — contact the maintainer with the failing command and the output. Include the session ID from `claude plugin list` if you can.

## What you're getting

- **One skill** — the full Shortcuts knowledge base (~12,000 lines of reference material, 56 best-practice rules, verified action identifiers from Apple's ToolKit v63, 19 golden example XMLs). Claude auto-loads it when you ask for a shortcut.
- **Two agents** — `shortcut-builder` (new-from-scratch) and `shortcut-remixer` (diff an existing XML). Each is a specialist with its own system prompt and bounded research budget.
- **One hook** — `PostToolUse` auto-validator that runs the Craig Loop validator on every Write/Edit that produces a Shortcuts plist. Catches structural errors before signing.
- **Four bin commands** — `validate-shortcut`, `resolve-icon`, `sign-shortcut`, `shortcuts-playground-selftest`. All added to Claude's Bash PATH when the plugin is enabled; all also callable from your own terminal for manual debugging.
- **Two slash commands** — `/shortcuts-playground:build` and `/shortcuts-playground:remix`. Both delegate to their respective agents.

## Release notes

You're installing **v1.5.2**. The full CHANGELOG is in the repo. Big recent changes:

- **v1.5.2** — internal release for MacStories team (marketplace manifest co-located with the plugin so one GitHub URL installs everything).
- **v1.5.1** — uuidgen-only UUID generation + validator backstop rejecting repeating-hex placeholders.
- **v1.5.0** — remix command + shortcut-remixer agent (`/shortcuts-playground:remix`).
- **v1.4.0** — Reminders recipes verified against an Apple-built sample; agent anti-reconnaissance hardening; research scoping.
- **v1.3.0** — definitive conditional-block rules verified against an Apple-built sample (all 13 condition codes + multi-condition If).

## Feedback

This is an internal release. If something breaks, works weirdly, or generates a shortcut that doesn't match your intent, report it with:

1. The exact prompt you ran.
2. The output path(s) in `~/Documents/Shortcuts Playground/`.
3. Whether the self-test passes.
