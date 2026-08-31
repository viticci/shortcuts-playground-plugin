# Shortcuts Playground — Minis package

This directory is a portable Minis skill derived from the upstream Shortcuts Playground knowledge
base. It intentionally does not install or require Claude Code, Codex, slash commands, plugin
hooks, or private Apple frameworks.

## Included

- `SKILL.md` — portable Build/Remix/Validate/Sign workflows
- `references/` — on-demand action, plist, HealthKit, variable, control-flow and validation docs
- `tools/` — optional icon, validation and macOS signing wrappers
- `SOURCE.json` — upstream repository/ref/commit provenance
- `LICENSE.upstream` — upstream license

## Platform note

Python and Minis/iSH can generate and validate unsigned plist/XML drafts. Apple signing is
performed only by the native macOS `shortcuts sign` command. A Minis session on iPhone/iSH can
use an authorized SSH/Tailscale Mac bridge to transfer a draft, sign it, retrieve the `.shortcut`,
and verify the `AEA1` header.
