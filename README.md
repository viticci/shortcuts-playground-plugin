# Shortcuts Playground

Create Apple Shortcuts with natural language using Claude Code or Codex.

Shortcuts Playground is a plugin for Claude Code and Codex that lets you turn any idea into a shortcut for Apple's Shortcuts app. Describe what you want in plain English; a few minutes later, you get a real, signed `.shortcut` file ready to import into the Shortcuts app.

Under the hood, shortcuts have always been XML files that get signed and encrypted into Apple's proprietary `.shortcut` format. Shortcuts Playground ships a comprehensive knowledge base that teaches Claude and Codex how Shortcuts actions work, what syntax they use, and how they connect to one another. Agents generate the XML, validate it through a loop, and sign it using Apple's native `shortcuts` CLI. The result is a valid shortcut, built from a sentence.

A project by [Federico Viticci](https://www.macstories.net).

---

## What It Does

You can install Shortcuts Playground in either Claude Code or Codex. At the moment, the Claude Code version of the plugin offers a richer experience thannks to dedicated commands, agents, and hooks.

- **Build from scratch.** In Claude Code, type `/shortcuts-playground:build` followed by a description of the shortcut you want. Claude designs the action list, wires variables, picks an icon, validates the XML through a self-correcting loop, and signs the result.
- **Remix an existing shortcut.** Type `/shortcuts-playground:remix` with a path to an unsigned `.xml` shortcut file and describe what to change. The agent applies a surgical diff — preserving every action, UUID, and icon you didn't ask to touch.
- **Automatic validation.** In Claude Code, a `PostToolUse` hook runs a structural validator on every file write. Errors feed back into the agent's context so it can fix them before signing. This is called a Craig Loop. It adds a few seconds of latency but dramatically improves output quality.

---

## Requirements

- **macOS.** The signing step uses the built-in `shortcuts` CLI, which is macOS-only.
- **Claude Code or Codex.** Install from [claude.com/claude-code](https://claude.com/claude-code) or [openai.com/codex](https://openai.com/codex/). Either the desktop apps or CLIs will work.
- **Python 3.10+.** The bundled validator requires 3.10 or later. The system Python on older macOS versions ships 3.9 and will fail. Install a newer version via Homebrew (`brew install python3`) or set `SHORTCUTS_PLAYGROUND_PYTHON` to point at your interpreter.

---

## Installation in Claude

### In the terminal

Two commands. Run them from any directory:

```bash
# 1. Register the marketplace
claude plugin marketplace add https://github.com/viticci/shortcuts-playground-plugin

# 2. Install the plugin
claude plugin install shortcuts-playground@shortcuts-playground
```

Claude Code clones the repository into its plugin cache on first install. If the clone fails with a GitHub auth error, make sure `git clone https://github.com/viticci/shortcuts-playground-plugin.git` works in your terminal first.

### In the Claude for Mac app

1. Open Claude for Mac and start a new Claude Code session (the terminal panel at the bottom).
2. Click the terminal input area and run the same two commands:
   ```
   claude plugin marketplace add https://github.com/viticci/shortcuts-playground-plugin
   claude plugin install shortcuts-playground@shortcuts-playground
   ```
3. Start a new session to load the plugin.

### Verify the install

Run these four checks to confirm everything is wired up:

```bash
python3 --version                                # expect 3.10+
which shortcuts                                  # expect /usr/bin/shortcuts
claude plugin list | grep shortcuts-playground   # expect "✔ enabled"
shortcuts-playground-selftest                    # expect "✔ All checks passed."
```

`shortcuts-playground-selftest` checks your Python version, the `shortcuts` CLI, the plugin root, bundled data files, the validator, and runs a full sign round trip. If anything fails, it tells you exactly what broke.

## Installation in Codex

//TODO

---

## Quick Start

### Build a shortcut

```
/shortcuts-playground:build a shortcut that asks for a city, fetches the current weather, and shows a notification
```

Or just describe what you want in natural language — Claude's skill auto-invocation will pick up the intent:

```
Build me a shortcut that takes my 5 most recent screenshots and sends them to a contact on iMessage
```

When it's done, open the signed `.shortcut` file from `~/Documents/Shortcuts Playground/` in Finder. Shortcuts.app will offer to import it.

### Remix an existing shortcut

Point it at an unsigned `.xml` file and describe the change:

```
/shortcuts-playground:remix /Users/you/Documents/Shortcuts Playground/drafts/Weather.xml add a notification at the start saying "Fetching weather…"
```

The remix preserves everything you didn't ask to change. Your original file is never overwritten.

---

## What You Should Expect

Shortcuts Playground can take you roughly 90% of the way to a complete, functioning shortcut. The remaining 10% should be checked and refined by you. In testing, it was able to one-shot dozens of simple shortcuts using Apple's built-in actions, as well as complex shortcuts involving web APIs, advanced logic, SSH, shell scripting, and more.

Common things to watch for:

- **Variables.** Occasionally a field will be empty where a variable connection is needed. You'll need to go in there and manually connect that variable or parameter yourself.
- **Repeat loops.** Double-check the wiring inside loops: variable scope can get tricky.
- **Always inspect the result.** Open the shortcut in the Shortcuts app and walk through it before relying on it. This is good friction: you'll learn a lot about how shortcuts work from the inside.

For best results, use Claude Opus 4.6/4.7 or GPT 5.5 as the underlying models. Higher reasoning efforts produce better outputs, but introduce latency.

---

## What's in the Box

| Component | Purpose |
|-----------|---------|
| **Skill** (`skills/shortcuts-playground/`) | The complete Shortcuts knowledge base: ~12,000 lines of reference material, 56 best-practice rules, verified action identifiers from Apple's ToolKit v63, and 19 golden example XMLs. |
| **Build agent** (`agents/shortcut-builder.md`) | Specialized agent that owns the full design, build, validate, sign, and archive loop for new shortcuts. |
| **Remix agent** (`agents/shortcut-remixer.md`) | Specialized agent that applies a surgical diff to an existing unsigned XML shortcut. |
| **Validation hook** (`hooks/`) | `PostToolUse` hook that runs the Craig Loop validator on every file write. Catches structural errors before signing. |
| **CLI wrappers** (`bin/`) | `validate-shortcut`, `resolve-icon`, `sign-shortcut`, `shortcuts-playground-selftest` — added to Claude's PATH when the plugin is enabled. |
| **Slash commands** (`commands/`) | `/shortcuts-playground:build` and `/shortcuts-playground:remix`. |

---

## Configuration

By default, shortcuts are saved to `~/Documents/Shortcuts Playground/`:

```
~/Documents/Shortcuts Playground/
├── My Shortcut.shortcut          # signed file — open to import
├── drafts/
│   └── My Shortcut.xml           # working unsigned draft
└── 2026-05-09/
    └── My Shortcut-151223.xml    # dated archive
```

To change the output directory, edit `~/.claude/settings.json`:

```json
{
  "pluginConfigs": {
    "shortcuts-playground@shortcuts-playground": {
      "options": {
        "output_dir": "/Users/you/Documents/Shortcuts Playground"
      }
    }
  }
}
```

The plugin also supports a `signing_mode` option (`anyone` for public distribution, `people-who-know-me` for contacts only). Default is `anyone`.

---

## Companion Shortcut

A companion Shortcuts shortcut that communicates with Claude Code and Codex over SSH – letting you generate shortcuts from iPhone and iPad – is available exclusively for [Club MacStories](https://club.macstories.net) members.

---

## Updating

```bash
claude plugin update shortcuts-playground@shortcuts-playground
```

Start a new Claude Code session after updating to pick up changes to agents and hooks.

## Uninstalling

```bash
claude plugin uninstall shortcuts-playground@shortcuts-playground
claude plugin marketplace remove shortcuts-playground
```

Your `~/Documents/Shortcuts Playground/` directory stays intact.

---

## Dual-Runtime Support

This repository ships plugins for two agent runtimes:

| Folder | Runtime | Notes |
|--------|---------|-------|
| [`claude/`](claude/) | Claude Code | Full plugin with skill, slash commands, specialized agents, PostToolUse hook, and CLI wrappers. |
| [`codex/`](codex/) | Codex | Codex-compatible plugin with bundled skill and validator/signing scripts. |

The root `.claude-plugin/marketplace.json` installs the Claude Code plugin from `./claude`. The root `.agents/plugins/marketplace.json` installs the Codex plugin from `./codex`.

For detailed technical documentation, see [`claude/README.md`](claude/README.md) and [`claude/INSTALL.md`](claude/INSTALL.md).

---

## Credits

by [Federico Viticci](https://mastodon.macstories.net/@viticci), [MacStories.net](https://www.macstories.net)

## License

[MIT](LICENSE).
