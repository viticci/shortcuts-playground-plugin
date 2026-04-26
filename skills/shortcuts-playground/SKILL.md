---
name: shortcuts-playground
description: Build, validate, sign, archive, and REMIX macOS/iOS Shortcuts by creating plist files. Use when asked to create, modify, or remix shortcuts; automate workflows; build .shortcut files; or generate Shortcuts plists. Covers WF actions, AppIntents, third-party actions, variable references, and control flow using bundled ToolKit v63 metadata with optional local ToolKit expansion.
effort: max
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Shortcuts Playground

Generate valid `.shortcut` files that can be signed and imported into Apple's Shortcuts app. The plugin supports two workflows — building new shortcuts from scratch AND remixing existing XML shortcuts with a natural-language diff.

**Two slash commands / two specialized agents:**

| Command | Agent | Purpose |
|---------|-------|---------|
| `/shortcuts-playground:build <brief>` | `shortcut-builder` | Create a new shortcut from scratch based on a natural-language brief. |
| `/shortcuts-playground:remix <path-to-xml> <idea>` | `shortcut-remixer` | Apply a surgical diff to an existing unsigned `.xml` shortcut. Preserves UUIDs, icon, metadata, and every action the user didn't ask to touch. |

Both commands share the same skill docs, the same validator, the same `PostToolUse` auto-validation hook, and the same `sign-shortcut` archive-and-sign pipeline. The only difference is the starting point (empty plist vs. an existing source XML).

**Plugin-provided commands.** When this skill is active, three wrapper commands are on the Bash `PATH`:

| Command | Purpose |
|---------|---------|
| `resolve-icon` | Pick a Shortcuts glyph + color from a natural-language prompt (required step 5 in the build workflow; skipped for remixes, which preserve the source icon). |
| `validate-shortcut` | Run the Craig Loop preflight validator against a `.xml`/`.shortcut` file. |
| `sign-shortcut` | Archive the unsigned XML, sign with `shortcuts sign`, and write the final `.shortcut` to the configured output directory. |

Prefer these wrappers over calling the underlying `python3 scripts/*.py` files directly — they work from any working directory and respect plugin configuration.

**Auto-validation hook.** A `PostToolUse` hook fires on every `Write`/`Edit` that produces a Shortcuts plist file and runs `validate-shortcut` automatically. Do not skip the Craig Loop when the hook reports errors — it already ran the validator for you, so read the errors and fix them before retrying. The hook applies to BOTH the builder and the remixer; neither agent needs to invoke `validate-shortcut` manually for edits it just made.

**Mandatory**: Follow the guidelines in [BEST_PRACTICES.md](BEST_PRACTICES.md) for every shortcut.
If guidance here conflicts with [BEST_PRACTICES.md](BEST_PRACTICES.md), follow `BEST_PRACTICES.md`.

## Recommended Reading Order

1. [BEST_PRACTICES.md](BEST_PRACTICES.md) for mandatory rules and validation expectations
2. [PLIST_FORMAT.md](PLIST_FORMAT.md) for plist structure and serialization details
3. [ACTIONS.md](ACTIONS.md), [APPINTENTS.md](APPINTENTS.md), and [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) for action IDs/parameters
4. [HEALTHKIT.md](HEALTHKIT.md) when building or remixing Health actions
5. [VARIABLES.md](VARIABLES.md), [CONTROL_FLOW.md](CONTROL_FLOW.md), and [FILTERS.md](FILTERS.md) for wiring patterns
6. [ICONS_AND_COLORS.md](ICONS_AND_COLORS.md), [PARAMETER_TYPES.md](PARAMETER_TYPES.md), and [EXAMPLES.md](EXAMPLES.md) for implementation details

## Quick Start

A shortcut is an XML plist that gets signed into a binary package. Generate the XML form:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Actions go here -->
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>61440</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>431817727</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>My Shortcut</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

### Minimal Hello World

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.gettext</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</string>
        <key>WFTextActionText</key>
        <string>Hello World!</string>
    </dict>
</dict>
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.showresult</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>Text</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{0, 1}</key>
                    <dict>
                        <key>OutputName</key>
                        <string>Text</string>
                        <key>OutputUUID</key>
                        <string>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</string>
                        <key>Type</key>
                        <string>ActionOutput</string>
                    </dict>
                </dict>
                <key>string</key>
                <string></string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenString</string>
        </dict>
    </dict>
</dict>
```

## Core Concepts

### 1. Actions
Every action has:
- **Identifier**: `is.workflow.actions.<name>` (e.g., `is.workflow.actions.showresult`)
- **Parameters**: Action-specific configuration in `WFWorkflowActionParameters`
- **UUID**: Unique identifier for referencing this action's output

### 2. Variable References
To use output from a previous action:
1. The source action needs a `UUID` parameter
2. Reference it using `OutputUUID` in an `attachmentsByRange` dictionary
3. Use `` (U+FFFC) as placeholder in the string where the variable goes
4. Set `WFSerializationType` to `WFTextTokenString`

### 3. Control Flow
Control flow actions (repeat, conditional, menu) use:
- `GroupingIdentifier`: UUID linking start/middle/end actions
- `WFControlFlowMode`: 0=start, 1=middle (else/case), 2=end

## Common Actions Quick Reference

| Action | Identifier | Key Parameters |
|--------|------------|----------------|
| Text | `is.workflow.actions.gettext` | `WFTextActionText` |
| Show Result | `is.workflow.actions.showresult` | `Text` |
| Ask for Input | `is.workflow.actions.ask` | `WFAskActionPrompt`, `WFInputType` |
| Use AI Model | `is.workflow.actions.askllm` | `WFLLMPrompt`, `WFLLMModel`, `WFGenerativeResultType` |
| Comment | `is.workflow.actions.comment` | `WFCommentActionText` |
| URL | `is.workflow.actions.url` | `WFURLActionURL` |
| Get Contents of URL | `is.workflow.actions.downloadurl` | `WFURL`, `WFHTTPMethod` |
| Get Weather | `is.workflow.actions.weather.currentconditions` | (none required) |
| Open App | `is.workflow.actions.openapp` | `WFAppIdentifier` |
| Open URL | `is.workflow.actions.openurl` | `WFInput` |
| Alert | `is.workflow.actions.alert` | `WFAlertActionTitle`, `WFAlertActionMessage` |
| Notification | `is.workflow.actions.notification` | `WFNotificationActionTitle`, `WFNotificationActionBody` |
| Set Variable | `is.workflow.actions.setvariable` | `WFVariableName`, `WFInput` |
| Get Variable | `is.workflow.actions.getvariable` | `WFVariable` |
| Number | `is.workflow.actions.number` | `WFNumberActionNumber` |
| List | `is.workflow.actions.list` | `WFItems` |
| Dictionary | `is.workflow.actions.dictionary` | `WFItems` |
| Repeat (count) | `is.workflow.actions.repeat.count` | `WFRepeatCount`, `GroupingIdentifier`, `WFControlFlowMode` |
| Repeat (each) | `is.workflow.actions.repeat.each` | `WFInput`, `GroupingIdentifier`, `WFControlFlowMode` |
| If/Otherwise | `is.workflow.actions.conditional` | `WFInput`, `WFCondition`, `GroupingIdentifier`, `WFControlFlowMode` |
| Choose from Menu | `is.workflow.actions.choosefrommenu` | `WFMenuPrompt`, `WFMenuItems`, `GroupingIdentifier`, `WFControlFlowMode` |
| Find Photos | `is.workflow.actions.filter.photos` | `WFContentItemFilter` (see FILTERS.md) |
| Delete Photos | `is.workflow.actions.deletephotos` | `photos` (**NOT** `WFInput`!) |

## Detailed Reference Files

For complete documentation, see:
- [PLIST_FORMAT.md](PLIST_FORMAT.md) - Complete plist structure
- [ICONS_AND_COLORS.md](ICONS_AND_COLORS.md) - Icon glyph + color selection (explicit and inferred)
- [ACTIONS.md](ACTIONS.md) - WF*Action identifiers and parameters
- [APPINTENTS.md](APPINTENTS.md) - AppIntent actions (ToolKit + backups)
- [PARAMETER_TYPES.md](PARAMETER_TYPES.md) - All parameter value types and serialization formats
- [HEALTHKIT.md](HEALTHKIT.md) - iOS/iPadOS Health actions, bundled anonymized XML examples, and HealthKit value coverage
- [VARIABLES.md](VARIABLES.md) - Variable reference system
- [CONTROL_FLOW.md](CONTROL_FLOW.md) - Repeat, Conditional, Menu patterns
- [FILTERS.md](FILTERS.md) - Content filters for Find/Filter actions (photos, files, etc.)
- [EXAMPLES.md](EXAMPLES.md) - Complete working examples
- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Mandatory build guidelines
- [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) - Third-party actions (ToolKit + backups)
- [TOOLKIT_SNAPSHOT.md](TOOLKIT_SNAPSHOT.md) - Bundled ToolKit v63 action-ID allowlist
- [CHANGELOG.md](CHANGELOG.md) - Change history: autoresearch findings, documentation updates, and version notes

When you need to verify an unfamiliar action identifier, check `data/toolkit-v63-tool-ids.json`, then `ACTIONS.md`, `APPINTENTS.md`, and `THIRD_PARTY_ACTIONS.md` before inventing anything.

## Golden Example Library (On-Demand)

A curated set of shortcut XMLs is available for on-demand reference. Use the index first; only load XML sources that match the current task.

- Index: `golden-shortcuts/index.jsonl` (token-efficient metadata: title, purpose, tags, xml path)
- XMLs: `golden-shortcuts/xml/<shortcut_id>.xml`
- Note: Golden XMLs are pattern references and may predate current validator/comment standards; treat them as wiring examples, not pass/fail baselines.

Workflow:
1) Read `golden-shortcuts/index.jsonl` to find relevant examples by tags/purpose.
2) Load only the single XML file(s) needed for the current task.
3) Do **not** bulk-load the entire library.

## Icon and Color Resolver (Required)

For every generated shortcut, choose icon and color using the resolver unless the user gave explicit integer values already:

```bash
resolve-icon --prompt "${USER_PROMPT}"
```

Optional explicit overrides:

```bash
resolve-icon --prompt "${USER_PROMPT}" --icon "robot" --color "purple"
```

Then set:
- `WFWorkflowIconGlyphNumber = icon.glyph_number`
- `WFWorkflowIconStartColor = color.value`

The resolver supports natural-language icon requests (e.g. `paper airplane icon`, `terminal icon`, `expense icon`) and automatic icon selection when no icon is requested.

## Preflight Validator — Craig Loop (Required)

After generating a shortcut, run the validator in a **fix loop** (Craig Loop). Each iteration: read the errors, make a targeted fix, re-validate. Do not re-run without changing something. The plugin's `PostToolUse` hook runs this for you automatically after every `Write`/`Edit`, but you may also invoke it manually:

```bash
validate-shortcut /path/to/Shortcut.xml
```

### Craig Loop Protocol

1. **Run the validator.** If it passes, proceed to signing.
2. **Read ALL error messages.** The validator prints every error it finds — fix as many as possible in one pass, not just the first one.
3. **Make targeted fixes** in the plist XML based on the error messages. Each error includes the action index and identifier so you know exactly where to edit.
4. **Re-run the validator.** Repeat from step 1.
5. **Exit conditions** (stop looping and report to the user):
   - **Max 5 iterations.** If the validator still fails after 5 fix attempts, stop. Summarize the remaining errors and ask the user for guidance.
   - **Same errors repeating.** If the same error persists across 2 consecutive iterations despite attempted fixes, stop. The fix approach is wrong — do not keep trying the same thing.
   - **Known validator gaps.** Some valid patterns trigger false failures (see BEST_PRACTICES.md). If the only remaining errors are documented false positives (numeric If implicit input, Notes `markdownContents`), the shortcut is acceptable — note this in your response.

### Anti-patterns (do NOT do these)
- **Chatting the validator**: Running the validator repeatedly without making meaningful code changes between runs. Every re-run must follow a real edit.
- **Cosmetic fixes**: Rearranging comments or renaming variables to "try something" when the error is about wiring or missing parameters.
- **Regenerating from scratch** when only 1-2 specific actions need fixing. Targeted edits preserve working wiring.

### Data sources
The validator uses bundled ToolKit snapshot IDs from [`data/toolkit-v63-tool-ids.json`](data/toolkit-v63-tool-ids.json) by default, then augments with [`ACTIONS.md`](ACTIONS.md), [`APPINTENTS.md`](APPINTENTS.md), and [`THIRD_PARTY_ACTIONS.md`](THIRD_PARTY_ACTIONS.md). It can optionally expand from a local ToolKit SQLite database when available.

### Escape-hatch comments
If a request explicitly requires vCard/VCF formatting or file-based token loading, add a Comment containing `ALLOW_VCARD` or `ALLOW_TOKEN_FILE` so the validator can allow it. Other escape hatches: `ALLOW_MANUAL_UNIT_CONVERSION`, `ALLOW_DATETIME_FORMAT`.

### Wiring Regression Suite (Recommended)

When changing wiring logic or validator rules for Weather/Location actions, run the bulk regression suite:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/shortcuts-playground/scripts/test_wiring_regressions.py" --write-fixtures /tmp/shortcuts-wiring-regressions
```

The suite generates and validates:
- 40 Weather Detail cases (20 valid + 20 invalid)
- 40 Location parameter cases (20 valid + 20 invalid)
- 12 Set Name cases (6 valid + 6 invalid)

It exits non-zero if any case behavior regresses.

### Random Mixed-Action Stress Suite (Recommended)

For broad randomized coverage (brand-new shortcuts, 10+ distinct actions each), run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py" --count 50 --min-actions 10
```

Behavior:
- Generates brand-new random shortcuts under `$CLAUDE_PLUGIN_OPTION_OUTPUT_DIR/<YYYY-MM-DD>/random-mixed-actions-<runid>/` (or `~/Documents/Shortcuts Playground/` if `output_dir` was not set when the plugin was enabled).
- Enforces a minimum distinct action count per shortcut (`--min-actions`, default `10`).
- Runs validate/retry loops per case (`--max-attempts`, default `20`).
- Writes `manifest.json`, `results.json`, and `summary.md` for documentation.

Optional:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py" --count 50 --min-actions 10 --sign
```

Use this suite when you need randomized multi-action regression coverage beyond targeted wiring tests.

## Signing Shortcuts

Shortcuts MUST be signed before they can be imported. The plugin ships a `sign-shortcut` wrapper that combines **archive + sign** into a single command and respects `${user_config.output_dir}`:

```bash
# Archives the unsigned XML under $output_dir/$(date +%F)/ and writes a signed .shortcut to $output_dir.
sign-shortcut /path/to/MyShortcut.xml --name "My Shortcut"

# Override the signing mode (default is the plugin's signing_mode config, falling back to 'anyone').
sign-shortcut /path/to/MyShortcut.xml --name "My Shortcut" --mode people-who-know-me
```

The underlying pipeline is still the macOS `shortcuts` CLI:

```bash
shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut.shortcut
```

The signing process:
1. Write your plist as XML to a `.shortcut` file (do not pre-convert with `plutil -convert binary1`).
2. Run `sign-shortcut` (or `shortcuts sign` directly) to add the cryptographic signature (~19KB added).
3. Keep the signed output filename equal to the intended display name (no `_signed` suffix).
4. The signed file can be opened/imported into Shortcuts.app.

Signing gotchas:
- If `shortcuts sign` reports `Error: The file doesn't exist.` but the file exists, copy the XML plist directly to a clean `.shortcut` path and retry (example: `cp source.xml /tmp/MyShortcut.shortcut`).
- `ERROR: Unrecognized attribute string flag '?'` warnings are noisy but can be non-fatal if the output file is produced.
- The `shortcuts` CLI supports `run`, `list`, `view`, and `sign`; do not assume `delete`, `rename`, or `import` subcommands.

## Archive Raw XML (Required)

Before signing, **archive the unsigned XML** in a date/time folder for inspection. The plugin's `sign-shortcut` wrapper does this for you — but the rules below still apply when you invoke `shortcuts sign` directly.

Folder structure rule:
- The archive root is `${user_config.output_dir}` (falls back to `~/Documents/Shortcuts Playground/` when the plugin's `output_dir` userConfig is unset).
- Inside the archive root, create a **date folder** for the current day (`YYYY-MM-DD`) if it doesn't exist.
- Copy the unsigned XML into that date folder with a time-stamped filename.

Example (output dir = `~/Documents/Shortcuts Playground`):
- Archive folder: `~/Documents/Shortcuts Playground/2026-02-03/`
- Archive file: `My Shortcut-142355.xml`

Command pattern (the one-liner `sign-shortcut` wraps):
```bash
OUTPUT_DIR="${CLAUDE_PLUGIN_OPTION_OUTPUT_DIR:-$HOME/Documents/Shortcuts Playground}"
ARCHIVE_ROOT="$OUTPUT_DIR/$(date +%F)"
mkdir -p "$ARCHIVE_ROOT"
cp "/path/to/My Shortcut.xml" "$ARCHIVE_ROOT/My Shortcut-$(date +%H%M%S).xml"
```

The archive copy must be the **unsigned, raw XML** (not the signed `.shortcut`).

## Workflow for Creating Shortcuts

0. **Research external APIs** - For complex/unfamiliar APIs, read the latest official docs before drafting request code.
1. **Define actions** - List what the shortcut should do
2. **Generate UUIDs** - Each action that produces output needs a unique UUID
3. **Build action array** - Create each action dictionary with identifier and parameters
4. **Wire variable references** - Connect outputs to inputs using `OutputUUID`
5. **Resolve icon and color** - Run `resolve-icon` with the full user prompt (plus any explicit icon/color hints) and use the returned values
6. **Wrap in plist** - Add the root structure with icon, name, version
7. **Write to file** - Save as `.shortcut` (XML plist format is fine)
8. **Preflight validation** - Run the Craig Loop (see above): validate → fix → re-validate, max 5 iterations. The `PostToolUse` hook auto-runs `validate-shortcut` whenever you write a Shortcuts plist file; read its errors before iterating.
9. **Archive + Sign (required)** - Run `sign-shortcut /path/to/file.xml --name "Final Name"`. This wrapper archives the unsigned XML to `${user_config.output_dir}/$(date +%F)/` and writes the signed `.shortcut` alongside it. Never leave the signing output filename with a `_signed` suffix.

## Comment Blocks (Repair-Oriented)

Because variable wiring can require manual fixes, add a **concise Comment before each major block** with a **bulleted list** describing which variables must be connected. Keep it short, specific, and focused on wiring (e.g., “Use Repeat Item 2 inside inner loop”).
Write comments with Shortcuts UI wording (for example, `Input`, `Date`, `Provided Input`, `Repeat Item`, `Text`) and readable action names (`Ask for Input`, `Text`, `Save File`). Do **not** use plist key jargon like `WFInput` / `WFDate` / `WFImage` in Comment text. **NEVER include UUIDs, OutputUUID references, or technical plist details in Comment text** — comments must be descriptive natural language only.
Prefer wording like `- Input uses the text output from the Text action above` and `• Date uses the user's answer from Ask for Input` instead of `WF*` field names or UUID references.

## Key Rules

1. **UUIDs must be uppercase and generated via `uuidgen`, not hand-picked.** Before emitting a shortcut, run a single Bash call to generate all the UUIDs you'll need:
    ```bash
    for i in $(seq 1 <N>); do uuidgen | tr '[:lower:]' '[:upper:]'; done
    ```
    Where `<N>` is the number of action UUIDs the shortcut requires (one per action that produces output or is referenced by downstream actions). Assign each output line to a specific action in your working map, then paste them into the plist. **Never use sequential placeholders** like `11111111-1111-1111-1111-111111111111`, `AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA`, or any other pattern where every hex character is the same — the validator rejects repeating-hex UUIDs as a hard error. Valid example shape: `7F3A4E91-C2D8-4B56-BE5A-0242AC120002`.
2. **WFControlFlowMode is an integer**: Use `<integer>0</integer>` not `<string>0</string>`
3. **Range keys use format**: `{position, length}` - e.g., `{0, 1}` for first character
4. **The placeholder character**: `` (U+FFFC) marks where variables are inserted
5. **Control flow needs matching ends**: Every repeat/if/menu start needs an end action with same `GroupingIdentifier`
6. **Match placeholder positions**: `attachmentsByRange` must point to the exact index of each `` in the final string
7. **No out-of-bounds ranges**: `attachmentsByRange` positions beyond string length can crash Shortcuts on import
8. **Avoid empty placeholders**: Omit unused keys or fields; do not leave empty values where the action expects data
9. **WFURL serialization**: For `WFURL` parameters (especially `downloadurl`), use `WFTextTokenString` with `` placeholders even when the URL is entirely a variable; reserve `WFTextTokenAttachment` for parameters that are explicitly variable-only (e.g., `WFVariable`, `WFRequestVariable`)
10. **Form file fields and WFRequestVariable**: For `WFHTTPBodyType = Form`, file fields (`WFItemType = 5`) must wrap the file reference in `WFTokenAttachmentParameterState` with an inner `WFTextTokenAttachment` so the UI shows the connected file variable. Set `WFRequestVariable` only when body type is `File` (JSON Text fallback pattern)
11. **Array fields**: For `WFDictionaryFieldValue` items with `WFItemType = 2`, use `WFArrayParameterState` with a list of items (`WFItemType` + `WFValue`), not numeric keys inside another dictionary
12. **Format Date input**: Set `WFDate` (not `WFInput`) as a `WFTextTokenString` placeholder wired to a Date output; never leave `WFDate` empty
13. **Repeat loops**: Inside **Repeat with Each**, use **Repeat Item** for per-item extraction; avoid **Repeat Results** inside the loop
14. **Reuse extractions**: If you extract multiple fields from a dictionary/API response, reuse each value later or remove the unused extraction
15. **Variable placeholders**: When composing strings or URLs with variables (Ask for Input, Track/Artist, etc.), insert a placeholder for every variable and align `attachmentsByRange` positions
16. **Dictionary dot notation**: Use dot notation (with 1-based indexes) in `WFDictionaryKey` to access nested keys (e.g., `results.tracks.items`, `artists.1.name`), but guard optional parents first (avoid direct `error.message` on raw API responses)
17. **Conditional inputs (verified against an Apple-built sample)**: For `is.workflow.actions.conditional` with `WFControlFlowMode = 0`, **every** condition code requires an explicit `WFInput` set as `{ Type: "Variable", Variable: { Value: <ActionOutput or Variable>, WFSerializationType: "WFTextTokenAttachment" } }`. There is no implicit-input mode. Per-code literal field requirements: string codes `4`/`5`/`8`/`9`/`99`/`999` need `WFConditionalActionString`; numeric codes `0`/`1`/`2`/`3` need `WFNumberValue`; numeric `1003` (`is between`) needs both `WFNumberValue` (lower) and `WFAnotherNumber` (upper, attachment); existence codes `100`/`101` need neither literal field. Code `0` is `is less than` (NOT equals); codes `0`–`3` are inequalities. Multi-condition Ifs use `WFConditions` with `WFContentPredicateTableTemplate` serialization; do not mix `WFConditions` with top-level `WFCondition`. Modes 1 (Otherwise) and 2 (End If) carry only `GroupingIdentifier` + `WFControlFlowMode`. For JSON booleans, compare numerically (`1`/`0`); treat JSON `null` as empty. See `CONTROL_FLOW.md` "Condition Codes" and "Multi-condition If" for the complete reference and templates.
18. **Workflow icon keys are mandatory**: Always set both `WFWorkflowIconGlyphNumber` and `WFWorkflowIconStartColor` in `WFWorkflowIcon` (use resolver output)
19. **Runtime file picking**: If the user needs to choose a file, use `is.workflow.actions.file.select` and connect its output
20. **Text token validation**: Run a final validation pass over every `WFTextTokenString` and refuse to output if any `attachmentsByRange` key does not map to a placeholder position or if counts mismatch
21. **No unrequested services**: Do not introduce third-party APIs, external CDNs, or extra import questions unless the user explicitly requests them
22. **Notion image uploads**: Default to Notion `file_uploads` + `file_upload` block type; avoid `external` image blocks unless the user supplies a URL or asks for external hosting
23. **Notion title filters**: Use the Notion `title` property name unless the user explicitly says their database uses a different title property name (e.g., `Name`)
24. **API research and endpoint accuracy**: For complex or unfamiliar external APIs, verify auth, endpoints, parameters, and payload formats against the latest official docs before assembling the shortcut. Validate endpoint strings exactly (underscore vs hyphen matters)
25. **API string sanity checks**: Before output, scan API strings for `//` (beyond protocol) and empty JSON fields where variables are expected (e.g., `equals:””`, `id:””`, `url:””`, `filename:””`), and fix them
26. **JSON request bodies**: For `WFHTTPBodyType = JSON`, use `WFJSONValues` for flat key/value payloads so the body is preserved in Shortcuts UI
27. **Format Date custom style**: When `WFDateFormatStyle` is `Custom`, put the format pattern in `WFDateFormat` (not `WFDateFormatString`). The runtime-verified schema: `WFDateFormatStyle=Custom` + `WFDateFormat=<pattern>` (e.g., `MMMM d, yyyy`, `EEEE`, `HH`). Using `WFDateFormatString` passes validation but the runtime ignores it and outputs the raw unformatted date
28. **Complex JSON fallback**: If the JSON body includes arrays of objects or deep nesting and the UI renders it as `Number 0`/empty rows, use a JSON Text action and set `WFRequestVariable` to that text with `WFHTTPBodyType = File` and `Content-Type: application/json`
29. **Filename extensions**: When using **Get Name** for file uploads, append the correct extension in the JSON payload (e.g., `.png`) and do not rely on the base name alone
30. **Count input visibility**: For `is.workflow.actions.count`, set both `WFInput` and `Input` to the same variable so the UI shows the selected list
31. **Get Name web titles**: For file names, set **Get Web Page Title** to **Off** in **Get Name** so the action returns the file name, not a URL title
32. **String If workaround**: If validator rules conflict on string conditionals, use `Match Text` + `Count` + numeric `If` instead of direct string `If`
33. **Replace Text empty replacement**: For delete-match patterns, prefer omitting `WFReplaceTextReplace`; an explicit empty string is allowed, but omission is cleaner and more portable
34. **Base64 input wiring**: Always set `WFInput` for `is.workflow.actions.base64encode`; implicit input can import as an empty field and break runtime
35. **Replace Text input visibility**: For `is.workflow.actions.text.replace`, use a `WFTextTokenString` placeholder (or wrapped variable input), not a bare `WFTextTokenAttachment`
36. **Adjust Date reliability**: Use `WFDate` + non-empty `WFDuration` for `is.workflow.actions.adjustdate` (optionally mirror with `WFInput`); include `WFAdjustOperation` when explicit Add/Subtract is required. Offset-picker-only payloads can import as `Add 0 seconds` on iOS
37. **Convert Image wiring**: For `is.workflow.actions.image.convert`, always set `WFInput` explicitly; do not rely on implicit input chaining
38. **Weather detail wiring**: For `is.workflow.actions.properties.weather.conditions`, set both `WFInput` and `WFContentItemPropertyName`, keep `WFContentItemPropertyName` concrete (never placeholder `Detail`), and wire `WFInput` directly to an ActionOutput from `is.workflow.actions.weather.currentconditions` / `is.workflow.actions.weather.forecast` (no named-variable hop)
39. **Time Between Dates input wiring**: For `is.workflow.actions.gettimebetweendates`, set `WFInput` and exactly one non-empty date operand (`WFDate` or `WFTimeUntilCustomDate` or `WFTimeUntilFromDate`); `WFTimeUntilUnit` may be omitted only when intentionally using the default unit. Never emit empty unused date keys
40. **Extract Text from Image input wiring**: For `is.workflow.actions.extracttextfromimage`, set exactly one non-empty image input key (`WFImage` preferred, `WFInput` only when intentionally required)
41. **API error extraction safety**: Do not read `error.message` directly from a raw response; extract `error`, guard it with `If Has Any Value`, then read `message`
42. **Continuation JSON array closure**: When appending to a JSON array via `Replace Text` on `\]$`, the replacement must end with `]`; missing the closing bracket corrupts JSON and causes `Detect Dictionary` to return empty
43. **No raw object/list tokens inside JSON text**: Do not inject Dictionary/List outputs (for example, raw API `content` arrays) directly into JSON Text templates; Shortcuts may stringify them as newline-separated blocks rather than valid JSON
44. **Continuation payload safe pattern**: For multi-turn handoff payloads, append assistant text from a plain text variable (for example, `Response Text`) and keep `messages_json` as valid JSON before rerunning the shortcut
45. **JSON string interpolation safety**: Before inserting freeform text into JSON Text templates (`”content”:””`), sanitize it first (at minimum handle backslashes, double quotes, and control whitespace/newlines) or the next `Detect Dictionary` step will fail
46. **API response parse stability**: For `downloadurl` JSON APIs, keep `ShowHeaders` off unless explicitly needed and run `Detect Dictionary` on `Contents of URL` before any `Get Dictionary Value` extraction
47. **Action input keys matter**: `Replace Text` uses `WFInput`, while `Change Case` and `Split Text` use `text`; wrong keys import but show empty inputs in the editor
48. **Split Text custom separator**: If `WFTextSeparator` is `Custom`, always include `WFTextCustomSeparator` (a single space `” “` is valid)
49. **Find Notes filter state**: `WFContentItemFilter` must be `WFContentPredicateTableTemplate` with non-empty templates; for `Folder` filters use `WFLinkDynamicOptionSubstitutableState` wrapping a tokenized variable
50. **Direct variable wiring**: Prefer inserting named variables directly into action input fields; avoid redundant `Get Variable → next action` hops unless there is a clear transformation need
51. **Location parameter wiring**: Never emit empty location parameters. For `WFLocation`, `WFWeatherCustomLocation`, and `WFWeatherLocation`, use `WFTextTokenAttachment` (not token strings) and reference a Get Current Location/Location output (directly or via a variable sourced from those outputs). `is.workflow.actions.location` must include a non-empty `WFLocation` attachment; missing/blank payloads import as empty “Location” fields
52. **Set Name best practice**: Use `is.workflow.actions.file.rename` with both `WFFile` and `WFNewFilename` (for example, `Test.txt`) so downstream actions receive a renamed file object
53. **⚠️ WFMathOperation syntax (verified against Shortcuts app)**: For `is.workflow.actions.math`: (a) **Addition**: OMIT the `WFMathOperation` key entirely — no key means addition; (b) **Subtraction**: `-` (ASCII minus, U+002D); (c) **Multiplication**: `×` (U+00D7, ord 215, Unicode MULTIPLICATION SIGN) — NEVER `*`; (d) **Division**: `÷` (U+00F7, ord 247, Unicode DIVISION SIGN) — NEVER `/`; (e) **Scientific ops** (Modulus, Power, etc.): `WFMathOperation='…'` (U+2026 horizontal ellipsis) as placeholder, with real op in `WFScientificMathOperation` and operand in `WFScientificMathOperand`. **Literal operands** (`WFMathOperand`) must be plain strings like `"10"`, not wrapped dicts. Shortcuts silently renders ASCII `/` as `+` in the UI with no error. See PARAMETER_TYPES.md "Math and Counting Operations" for verified examples.
54. **Never inspect the user's local system for authoring discovery unless the user explicitly asks for that local evidence.** If an action identifier is allowlisted in `data/toolkit-v63-tool-ids.json` but its parameter schema is not documented in the bundled reference files (`ACTIONS.md`, `APPINTENTS.md`, `PARAMETER_TYPES.md`, `FILTERS.md`, `EXAMPLES.md`, `BEST_PRACTICES.md`, `HEALTHKIT.md`, or the `golden-shortcuts/` library), **stop and ask the user** — do not try to reverse-engineer the schema by reading local databases, inspecting system binaries, querying Shortcuts.app internals, or searching cloud-backup folders without explicit permission. Escalate to the user with three options: (a) best-effort guess + iterate after they import, (b) use a simpler alternative action you propose, or (c) they paste a working example for you to mirror. When the user explicitly supplies or requests local exported XML, prefer that evidence over web references.
55. **Bottom-align in Combine Images via the flip trick**: `is.workflow.actions.image.combine` in horizontal mode top-aligns images. To bottom-align without transparent canvas padding: (1) flip each input image upside-down before Combine, (2) run Combine (now "top" is the original bottom), (3) flip the combined result upside-down. ⚠️ **`is.workflow.actions.image.flip` behaves OPPOSITELY on iOS vs macOS — this is a genuine Apple bug across platforms**: on **iOS/iPadOS**, `WFImageFlipDirection='Vertical'` produces upside-down (direction-of-motion naming); on **macOS**, `WFImageFlipDirection='Horizontal'` produces upside-down (axis-of-reflection naming). The same plist value renders differently. **Workaround**: wrap the flip in an If block checking `Device Model is Mac` → Flip Horizontally / Otherwise → Flip Vertically. Do this for BOTH flips in the trick (per-image and combined result). Proven on Apple Frames 4 proportional scaling — worked on iOS but silently failed on macOS until the device check was added
56. **Reminders: always use `is.workflow.actions.setters.reminders` for editing, never `UpdateReminderAppIntent`.** For every property of an existing reminder (Due Date, Title, Notes, Priority, Is Completed, Is Flagged, List, Subtasks, URL, Tags, Images, Parent Reminder, When Messaging Person), use one `setters.reminders` action per property with `Mode="Set"`, `WFContentItemPropertyName=<property name>`, and the matching `WFReminderContentItem<CamelCaseProperty>` value key. Chain multiple setters by pointing each one's `WFInput` at the previous setter's `ActionOutput` (`OutputName="Edited Reminder"`) so the "Edited Reminder" variable propagates. The `List` property is the only one that takes a plain string (the list name), not a token attachment. For date filtering in `filter.reminders`, operator `1002` ("is today") takes empty `Values`, operator `1003` ("is between") takes `Values.Date` (literal ISO `<date>`) + `Values.AnotherDate` (token attachment, typically `{Type: "CurrentDate"}`). See [PARAMETER_TYPES.md → Reminders — Filter & Setter Schemas](PARAMETER_TYPES.md#reminders--filter--setter-schemas-definitive) for the complete verified schema, the per-property value-key table, and verbatim templates.
57. **HealthKit actions are iOS/iPadOS-only and must use `HEALTHKIT.md`.** For `filter.health.quantity`, `properties.health.quantity`, `health.quantity.log`, and `health.workout.log`, use the bundled anonymized iOS XML examples and `data/healthkit-ios26.2-reference.json`. Do not guess the Log Health Sample schema: use `WFQuantitySampleType` plus `WFQuantitySampleQuantity` (`WFQuantityFieldValue`), allow unit-only `WFQuantitySampleAdditionalQuantity`, and add `WFCategorySampleEnumeration` only when a category picker value is needed. Do not run Health-writing shortcuts just to test syntax.
