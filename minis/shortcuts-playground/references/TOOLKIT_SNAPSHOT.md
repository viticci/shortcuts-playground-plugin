# Action ID Snapshots

This skill bundles precomputed action-ID allowlists so it can be shared without requiring any extra setup on the user's machine.

## Bundled files

- `data/toolkit-v63-tool-ids.json` - flat list of 1,794 action/intent identifiers from the original ToolKit snapshot.
- `data/toolkit-v78-tool-ids.json` - flat list of 2,731 action/intent identifiers from macOS 27 Golden Gate build 26A5353q.
- `data/toolkit-v78-ios27-tool-ids.json` - flat list of 1,206 action/intent identifiers from an iOS 27.0 Simulator ToolKit v78 database.
- `data/toolkit-v78-first-party-parameter-keys.json` - compact first-party ToolKit v78 parameter-key/name/type catalog with per-parameter platform provenance, used by `lookup_action_grounding.py` for broad AppIntent/schema discovery.
- `data/toolkit-v78-first-party-enum-cases.json` - compact first-party ToolKit v78 enum-case catalog for action and automation-trigger parameter type names.
- `data/toolkit-v78-trigger-parameter-keys.json` - compact ToolKit v78 automation trigger catalog with trigger IDs, Python names, parameter keys, and output type identifiers.
- `data/macos27-workflow-trigger-samples.json` - sanitized exported OS 27 `WFWorkflowTriggers` samples for automation headers that have been observed in real shortcut exports.
- `data/macos27-shortpy-grounding.json` - reviewed static Apple-derived macOS 27 grounding catalog with ToolKit `pythonName`, Apple Shortpy keyword, ToolRenderer utility, and ShortcutsLanguage syntax evidence.

Only the identifiers and compact parameter/enum metadata needed for validation and lookup are bundled. This keeps the plugin lightweight compared with the full ToolKit SQLite metadata.

## Validator behavior

`scripts/validate_shortcut.py` loads packaged `data/toolkit-v*-tool-ids.json` files according to the target OS version and target platform, then augments those snapshots with the markdown references (`ACTIONS.md`, `APPINTENTS.md`, `THIRD_PARTY_ACTIONS.md`). OS 27 snapshots include both macOS 27 and iOS 27 Simulator ToolKit evidence, but iOS-only snapshot rows are rejected for the default macOS platform target. It also target-gates the reviewed Automators OS 26 to 27 parameter deltas, so OS 27-only parameter keys are rejected on macOS 26 targets even when the action identifier itself predates OS 27.

For macOS/iOS 27 targets, the validator also loads `data/toolkit-v78-first-party-parameter-keys.json` as a schema check for first-party `com.apple.*` AppIntent-style actions. If a known AppIntent carries a top-level parameter key that does not appear in the active target's ToolKit v78 schema, validation fails. The catalog is filtered at the parameter level, so a field observed only in the iOS 27 Simulator ToolKit is rejected for the default macOS target even if the action row itself exists on both platforms. The validator also loads `data/toolkit-v78-first-party-enum-cases.json` and rejects invalid simple literal enum values for single-enum AppIntent parameters. It intentionally skips dynamic token values and multi-type parameters, and it does not apply broad unknown-key checks to regular `is.workflow.actions.*` actions because legacy WF actions can include valid plist/UI state keys that are absent from ToolKit parameter metadata.

The default OS target is `auto`: on macOS it reads `sw_vers -productVersion`; when the host cannot be detected it falls back to macOS 26 rather than latest. Override with `--target-macos 26`, `--target-macos 27`, or `--target-macos latest`. The same override is available via `SHORTCUTS_PLAYGROUND_TARGET_MACOS`.

The default platform target is `macos`. Override with `--target-platform ios` / `SHORTCUTS_PLAYGROUND_TARGET_PLATFORM=ios` for iPhone/iPad authoring, or `--target-platform all` only when intentionally validating every packaged platform.

This keeps validation portable and self-contained while avoiding false compatibility on machines that do not have macOS 27 installed.

## macOS 27 scope

The v78 snapshot expands validation coverage for shortcuts created on macOS 27. It is only active when the target is macOS 27+ or `latest`. The action-ID snapshots are identifier allowlists, not complete authoring schemas. For first-party `com.apple.*` AppIntent-style actions, the v78 parameter catalog can reject unknown top-level keys, but it does not prove full value serialization, requiredness, picker state, or runtime behavior. If a v78-only action identifier is present but its parameter serialization is not documented in the reference files or a golden XML, do not guess the payload. Ask for an exported XML sample or use a documented fallback.

OS 27-era parameter keys are also target-gated. Examples include `WFAllowWebSearch` and `FollowUp` on Use Model, `interpretAsMarkdown` on Notes actions, `WFAvoidTolls`/`WFAvoidHighways` on Maps route actions, `WFAppsExcept` on Hide/Quit App, `imageFile` on Scan QR or Barcode / Extract from Image, and `contents` on Safari Create Tab Group.

## iOS 27 simulator scope

The iOS 27 Simulator v78 snapshot adds iOS-only AppIntents that are not present in the macOS ToolKit database, such as `com.apple.HearingApp.MuteVolumeIntent` and iOS Settings/Wallet/Health/Fitness identifiers. These identifiers are included for iOS/iPadOS shortcut authoring and are also target-gated to OS 27+. They do not validate for the default macOS target; use `--target-platform ios` only when authoring for iPhone/iPad. Do not use them for macOS shortcuts unless a macOS ToolKit snapshot or exported shortcut confirms runtime support.

## Apple-derived grounding catalog

`data/macos27-shortpy-grounding.json` is a portable metadata catalog generated from local macOS 27 Shortcuts ToolKit, ToolRenderer, WorkflowKit source-export, and installed sample evidence. It is static package data: normal validation does not read the user's live Shortcuts database and does not load private frameworks.

Use `scripts/lookup_action_grounding.py` to inspect it:

```bash
python3 scripts/lookup_action_grounding.py --identifier additemtolist --target-macos 27
python3 scripts/lookup_action_grounding.py --python-name com_apple_shortcuts_add_item_to_list --json
python3 scripts/lookup_action_grounding.py --identifier com.apple.HearingApp.MuteVolumeIntent --target-macos 27 --target-platform ios --json
```

The grounding catalog can improve authoring confidence, but it does not override target availability. `lookup_action_grounding.py` reports the requested target macOS and target platform, including a target-platform availability note when an entry is only observed in the opposite platform's ToolKit rows. If `validate_shortcut.py --target-macos 26` rejects a v78-only identifier or parameter key, the static grounding entry is only a note that the action or parameter exists in OS 27-era ToolKit metadata.

`lookup_action_grounding.py` computes per-action availability from the packaged ToolKit snapshots, not from the grounding catalog's source OS. Older actions that appear in the macOS 27 grounding catalog still remain available to older targets when they are present in `toolkit-v63`.

The lookup helper also reads `data/toolkit-v78-first-party-enum-cases.json` and attaches `enumCases` / `enumTypes` to ToolKit parameter summaries. This exposes concrete picker values such as Add Item to List `Beginning` / `End` / `Index`, Find Places `Relevance` / `Distance`, Set Multitasking Mode `fullScreenApps` / `windowedApps` / `stageManager`, VPN operations, and trigger state values. Dynamic user-local picker cases, such as personal Reminders list names or Contacts groups, are intentionally redacted from the packaged enum catalog. These cases improve authoring and catalog review, but they still do not prove full plist serialization for complex picker states.

## Automation trigger metadata

`data/toolkit-v78-trigger-parameter-keys.json` packages the 42 automation triggers exposed in local macOS 27 and iOS 27 Simulator ToolKit v78 databases. This includes identifiers such as `com.apple.shortcuts.WFTimeOfDayTrigger.at_time_on_recurring_day`, Apple Shortpy-style names such as `when_app_opened`, trigger parameter keys, and raw output type identifiers.

ToolKit trigger metadata is discovery metadata only. Portable automation headers must come from exported shortcut evidence: use `data/macos27-workflow-trigger-samples.json` and [AUTOMATION_TRIGGERS.md](AUTOMATION_TRIGGERS.md) for sanitized `WFWorkflowTriggers` payload shapes. The validator checks top-level `WFWorkflowTriggers` for OS 27 targets, rejects placeholder values, and target-gates automation headers away from macOS 26/iOS 26 output. Do not infer trigger payloads from ToolKit rows alone.
