# Shortcuts Playground for Codex

Codex plugin for building, remixing, validating, archiving, and signing Apple Shortcuts.

## Structure

```text
codex/
├── .codex-plugin/plugin.json
├── hooks/
│   ├── hooks.json
│   └── auto-validate.sh
├── assets/
│   ├── icon.png
│   ├── icon-small.png
│   └── logo.png
└── skills/
    └── shortcuts-playground/
```

This package follows the Codex plugin structure: the manifest lives at `.codex-plugin/plugin.json`, skills live under `skills/`, and visual assets live under `assets/`.

## Runtime Differences from Claude

The Codex package intentionally omits Claude-only plugin features:

- Slash commands
- Specialized Claude agents
- PATH wrapper commands under `bin/`
- Claude `userConfig`

Codex now supports plugin-bundled hooks. This package ships a `PostToolUse` hook
that auto-validates changed `.xml`/`.shortcut` files containing
`WFWorkflowActions`. Codex plugin hooks are opt-in in the current Codex release,
so users must enable them in `~/.codex/config.toml`:

```toml
[features]
plugin_hooks = true
```

After enabling plugin hooks, restart Codex and review/trust the hook from
`/hooks` if prompted.

The bundled skill uses direct script paths instead:

```bash
SKILL_DIR=/path/to/codex/skills/shortcuts-playground
python3 "$SKILL_DIR/scripts/select_shortcut_icon_color.py" --prompt "weather shortcut"
python3 "$SKILL_DIR/scripts/validate_shortcut.py" /path/to/Shortcut.xml
"$SKILL_DIR/scripts/sign_shortcut.sh" /path/to/Shortcut.xml --name "Shortcut Name"
```

Set `SHORTCUTS_PLAYGROUND_OUTPUT_DIR` and `SHORTCUTS_PLAYGROUND_SIGNING_MODE` to customize signing output.

If `scripts/sign_shortcut.sh` fails with `Error: The file couldn't be opened because it isn't in the correct format.` while `validate_shortcut.py` and `plutil -lint` pass, retry signing outside Codex `workspace-write` sandbox restrictions or with Codex filesystem sandboxing set to full access. Apple's `shortcuts sign` can surface that misleading format error when the sandbox blocks what it needs.
