# ToolKit Snapshot Package

This skill bundles a precomputed ToolKit action-ID allowlist so it can be shared without requiring users to extract `~/Library/Shortcuts/ToolKit/*.sqlite` on their own machines.

## Bundled File

- `data/toolkit-v63-tool-ids.json` — flat list of 1,794 action/intent identifiers used by the validator as the primary allowlist

The full ToolKit metadata (tools, types, triggers) is not bundled — only the action IDs needed for validation are included. This keeps the skill lightweight (~98KB vs ~9.5MB).

## Validator Behavior

`scripts/validate_shortcut.py` uses `data/toolkit-v63-tool-ids.json` as the primary allowlist source, then augments with markdown references (`ACTIONS.md`, `APPINTENTS.md`, `THIRD_PARTY_ACTIONS.md`) and optional local ToolKit SQLite reads.

This keeps validation portable for distributed use while preserving optional local expansion when available.

## Regenerating the Snapshot

If ToolKit schema/content changes in a future OS release, re-extract `data/toolkit-v63-tool-ids.json` from the local ToolKit SQLite database and update the bundled file.
