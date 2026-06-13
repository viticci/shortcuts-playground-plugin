# Action ID Snapshots

This skill bundles precomputed action-ID allowlists so it can be shared without requiring any extra setup on the user's machine.

## Bundled files

- `data/toolkit-v63-tool-ids.json` - flat list of 1,794 action/intent identifiers from the original ToolKit snapshot.
- `data/toolkit-v78-tool-ids.json` - flat list of 2,731 action/intent identifiers from macOS 27 Golden Gate build 26A5353q.
- `data/toolkit-v78-ios27-tool-ids.json` - flat list of 1,206 action/intent identifiers from an iOS 27.0 Simulator ToolKit v78 database.
- `data/toolkit-v78-first-party-parameter-keys.json` - compact first-party ToolKit v78 parameter-key catalog used by `lookup_action_grounding.py` for broad AppIntent/schema discovery.
- `data/macos27-shortpy-grounding.json` - reviewed static Apple-derived macOS 27 grounding catalog with ToolKit `pythonName`, Apple Shortpy keyword, ToolRenderer utility, and ShortcutsLanguage syntax evidence.

Only the identifiers needed for validation are bundled. This keeps the plugin lightweight compared with the full ToolKit SQLite metadata.

## Validator behavior

`scripts/validate_shortcut.py` loads packaged `data/toolkit-v*-tool-ids.json` files according to the target macOS version, then augments those snapshots with the markdown references (`ACTIONS.md`, `APPINTENTS.md`, `THIRD_PARTY_ACTIONS.md`). OS 27 snapshots include both macOS 27 and iOS 27 Simulator ToolKit evidence. It also target-gates the reviewed Automators OS 26 to 27 parameter deltas, so OS 27-only parameter keys are rejected on macOS 26 targets even when the action identifier itself predates OS 27.

The default target is `auto`: on macOS it reads `sw_vers -productVersion`; outside macOS it falls back to the latest packaged snapshots. Override with `--target-macos 26`, `--target-macos 27`, or `--target-macos latest`. The same override is available via `SHORTCUTS_PLAYGROUND_TARGET_MACOS`.

This keeps validation portable and self-contained while avoiding false compatibility on machines that do not have macOS 27 installed.

## macOS 27 scope

The v78 snapshot expands validation coverage for shortcuts created on macOS 27. It is only active when the target is macOS 27+ or `latest`. It is an identifier allowlist, not a complete authoring schema. If a v78-only action identifier is present but its parameter serialization is not documented in the reference files or a golden XML, do not guess the payload. Ask for an exported XML sample or use a documented fallback.

OS 27-era parameter keys are also target-gated. Examples include `WFAllowWebSearch` on Use Model, `interpretAsMarkdown` on Notes actions, `WFAvoidTolls`/`WFAvoidHighways` on Maps route actions, `WFAppsExcept` on Hide/Quit App, `imageFile` on Scan QR or Barcode, and `contents` on Safari Create Tab Group.

## iOS 27 simulator scope

The iOS 27 Simulator v78 snapshot adds iOS-only AppIntents that are not present in the macOS ToolKit database, such as `com.apple.HearingApp.MuteVolumeIntent` and iOS Settings/Wallet/Health/Fitness identifiers. These identifiers are included for iOS/iPadOS shortcut authoring and are also target-gated to OS 27+. Do not use them for macOS shortcuts unless a macOS ToolKit snapshot or exported shortcut confirms runtime support.

## Apple-derived grounding catalog

`data/macos27-shortpy-grounding.json` is a portable metadata catalog generated from local macOS 27 Shortcuts ToolKit, ToolRenderer, WorkflowKit source-export, and installed sample evidence. It is static package data: normal validation does not read the user's live Shortcuts database and does not load private frameworks.

Use `scripts/lookup_action_grounding.py` to inspect it:

```bash
python3 scripts/lookup_action_grounding.py --identifier additemtolist --target-macos 27
python3 scripts/lookup_action_grounding.py --python-name com_apple_shortcuts_add_item_to_list --json
```

The grounding catalog can improve authoring confidence, but it does not override target availability. If `validate_shortcut.py --target-macos 26` rejects a v78-only identifier or parameter key, the static grounding entry is only a note that the action or parameter exists in OS 27-era ToolKit metadata.

`lookup_action_grounding.py` computes per-action availability from the packaged ToolKit snapshots, not from the grounding catalog's source OS. Older actions that appear in the macOS 27 grounding catalog still remain available to older targets when they are present in `toolkit-v63`.
