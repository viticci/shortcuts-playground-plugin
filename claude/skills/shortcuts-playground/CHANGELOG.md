# Autoresearch Loop Changelog

## Date: June 13, 2026 - OS 26 to 27 Automators action delta

### Summary

Expanded OS 27-era action support after reviewing the Automators forum thread and cross-checking it against local macOS 27 and hydrated iOS 27 Simulator ToolKit v78 databases.

### Fixes Applied

- Added `data/toolkit-v78-ios27-tool-ids.json` with 1,206 identifiers from the iOS 27.0 Simulator ToolKit database.
- Updated validator snapshot loading so iOS 27 ToolKit identifiers are target-gated and report iOS-specific availability reasons.
- Documented the Automators action and parameter deltas in `ACTIONS.md` and `APPINTENTS.md`, including Messages, Photos, Reminders, Share/Collaborate, stored content, on-screen context, Notes markdown, Maps route options, and Hide/Quit Apps exclusion lists.
- Mapped the reported Toggle Vehicle Motion Cues action to the confirmed macOS 27 `Set Motion Cues` ToolKit entry, documented the confirmed `Set Switch Control` on/off intent and `switchControlSwitches` settings-pane deep link target, and left Set Switch Control Switch Set marked as unresolved pending an exported shortcut or device ToolKit database.
- Added issue-regression coverage for the iOS 27 snapshot and the new reference entries.

## Date: June 12, 2026 - macOS 27 Golden Gate ToolKit v78 review

### Summary

Added early macOS 27 validation support after inspecting the local Shortcuts ToolKit v78 database on macOS 27.0 build 26A5353q.

### Fixes Applied

- Added `data/toolkit-v78-tool-ids.json` with 2,731 identifiers from the local macOS 27 ToolKit database.
- Added `data/macos27-shortpy-grounding.json`, a reviewed static Apple-derived macOS 27 grounding catalog with ToolKit `pythonName`, Apple Shortpy keyword, ToolRenderer utility, and ShortcutsLanguage syntax evidence.
- Added `scripts/lookup_action_grounding.py` to inspect that static catalog without reading live Shortcuts databases or loading private Apple frameworks.
- Updated `validate_shortcut.py` to load packaged `toolkit-v*-tool-ids.json` snapshots by target macOS version instead of hard-coding v63. The default target is `auto`; `--target-macos 27` / `SHORTCUTS_PLAYGROUND_TARGET_MACOS=27` opt into Golden Gate-only IDs.
- Documented `SHORTCUTS_PLAYGROUND_TARGET_MACOS` for explicit macOS 27 validation opt-in on older hosts.
- Documented the eight v78-only classic Shortcuts actions found locally, including `is.workflow.actions.additemtolist` and `is.workflow.actions.getselectedtext`.
- Documented the verified macOS 27 `Otherwise If` control-flow shape and `Add Item to List` serialization from Federico's local samples.
- Added a validator guard and docs for the macOS 27 import bug where list `contains` conditionals lose the comparison value when they test a named list variable that has been repeatedly reassigned from List/Add to List outputs.
- Kept local compatibility-review notes outside the packaged plugin; only the portable metadata and validator behavior ship.
- Added issue-regression coverage proving v78-only actions are target-gated and the macOS 27 `Otherwise If` shape validates.

## Date: June 8, 2026 — 1.1.0 public issue regression release

### Summary

Released the public 1.1.0 package with fixes for Claude output-path configuration, HealthKit blood pressure labels, and Codex sandbox signing diagnostics.

### Fixes Applied

- Resolved Claude `${user_config.output_dir}` and `${user_config.signing_mode}` directly in builder/remixer agents, then passed explicit `--output-dir` and `--mode` flags to `sign-shortcut`.
- Corrected HealthKit blood pressure labels to `Diastolic Blood Pressure` and `Systolic Blood Pressure`.
- Added sandbox-specific guidance when Apple `shortcuts sign` reports the misleading "isn't in the correct format" error under Codex workspace sandboxing.
- Added focused issue-regression tests and HealthKit label assertions in the wiring regression suite.

## Date: May 12, 2026 — Calendar date filters and Time Between Dates wiring

### Summary

Closed gaps exposed by a "time until next calendar event" shortcut: invalid Calendar Events date filter operators, Get Time Between Dates UI serialization, and low-signal placeholder range errors.

### Fixes Applied

- Documented the Calendar Events "next event after now" filter: `Start Date is today` plus `Start Date is after Current Date` with date operator `2`; validator now rejects numeric operator `3` on calendar date properties.
- Documented and enforced `WFTextTokenString` placeholder wiring for Get Time Between Dates date inputs. Direct `CurrentDate` magic tokens now produce an explicit "use a Date action first" validator error.
- Improved `attachmentsByRange` diagnostics so placeholder errors report the expected UTF-16 placeholder positions.
- Added regression coverage for valid/invalid calendar event filters, valid/invalid Get Time Between Dates wiring, and placeholder offset failures.
- Added pipeline-first build guidance: validate, sign, and verify before optional comment/prose polish.

## Date: May 12, 2026 — Send Message appended-variable guidance

### Summary

Clarified that Send Message content must use a named variable built from at least two Append Variable actions, including single-type payloads such as photos-only messages.

### Fixes Applied

- Reframed the Send Message guidance so the appended-variable rule is no longer scoped only to mixed text-and-file messages.
- Added the single-type pattern: append the source content, append an empty Text output to the same variable, then reference the named variable with `WFTextTokenString`.
- Updated the validator error to state the exact invariant and added regression coverage for the valid single-type pattern plus invalid one-append, direct ActionOutput, and `WFTextTokenAttachment` variants.

## Date: May 8, 2026 — 1.0 public launch reset and Active Calories correction

### Summary

Reset plugin metadata to `1.0` for public launch and corrected the Active Energy Burned HealthKit label to Shortcuts' `Active Calories` wording.

### Fixes Applied

- Updated HealthKit reference metadata so `HKQuantityTypeIdentifierActiveEnergyBurned` resolves to `Active Calories`.
- Updated guidance to reject `Active Energy` and `Active Energy Burned` in HealthKit actions.
- Added validator regression coverage for stale active-energy labels in Find Health Samples and Log Health Sample.

## Date: May 5, 2026 — Set Name action identity correction

### Summary

Corrected the Set Name guidance after comparing a generated shortcut against an Apple-built skeleton. **Set Name** is `is.workflow.actions.setitemname` and produces a renamed item object; **Rename File** is `is.workflow.actions.file.rename` and renames the original file in place.

### Fixes Applied

- Replaced the incorrect Set Name mapping (`file.rename` + `WFFile`/`WFNewFilename`) with the verified `setitemname` + `WFInput`/`WFName` schema.
- Documented that Rename File mutates the original path and must not be used for save-as/share-copy workflows.
- Updated validator coverage so Set Name validates `WFInput` and `WFName`, while Save/Share consuming Rename File output is rejected.
- Updated regression and random mixed-shortcut fixtures to generate `setitemname`.

## Date: May 4, 2026 — 1.7.5 URL schemes, JavaScript webpage rules, and date recipes

### Summary

Added Apple-documented Shortcuts URL scheme/x-callback guidance, Run JavaScript on Webpage runtime rules, and date/time recipes from Apple's advanced Shortcuts documentation.

### Fixes Applied

- Added `URL_SCHEMES.md` with documented `shortcuts://`, `create-shortcut`, `open-shortcut`, `run-shortcut`, Gallery, and `x-callback-url/run-shortcut` patterns.
- Added `JAVASCRIPT_WEBPAGE.md` covering Safari share-sheet runtime requirements, `completion(...)`, JSON-compatible output, and timeout-prone JavaScript APIs.
- Added `DATE_TIME.md` with UNIX timestamp conversion, built-in date/time styles, ISO 8601, RFC 2822, and Unicode TR35 custom format guidance.
- Updated the validator to reject unsupported Shortcuts URL routes and malformed documented routes.
- Updated the validator to require Safari webpage share-sheet metadata and completion-handler usage for Run JavaScript on Webpage actions.
- Added regression fixtures for valid/invalid Shortcuts URL scheme and JavaScript webpage cases.

## Date: May 4, 2026 — Weather details and superseded Set Name source reuse

### Summary

Fixed the Weather Detail picker labels. The Set Name source-reuse guidance from this entry was superseded by the May 5, 2026 correction: Set Name is `setitemname`, while `file.rename` is Rename File and mutates the original file in place.

### Fixes Applied

- Documented and validated the supported Get Detail of Weather Conditions names, including `Sunrise Time` and `Sunset Time` instead of stale `Sunrise Date` / `Sunset Date`.
- Added sunrise/sunset list handling guidance and validation: use Get Item from List, First Item for sunrise and Last Item for sunset, before formatting the date.
- Added an earlier Set Name source-reuse validator, later replaced by the May 5 Set Name/Rename File distinction.
- Expanded the wiring regression suite with Weather sunrise/sunset and file-renaming cases.

## Date: April 30, 2026 — 1.7.4 Health dashboard labels and duration math

### Summary

Updated Health dashboard guidance after comparing a generated HealthDash shortcut with a partially repaired copy. Find Health Samples needs additional action-specific picker labels: `Sleep`, `Active Calories`, and `Exercise Minutes`. Sleep duration values should not be divided by `60` and labeled as hours.

### Fixes Applied

- Added observed Find Health Samples labels for Sleep, Active Calories, and Exercise Minutes.
- Updated the validator to accept category types such as Sleep in Find Health Samples and reject stale labels such as `Sleep Analysis`, `Active Energy`, `Apple Exercise Time`, and `Exercise Time`.
- Added validation for Sleep duration math that divides by `60` and stores/reports the result as hours; generated shortcuts should divide by `3600` for decimal hours.
- Documented safer Health dashboard guidance for Sleep duration, last-night ranges, and Walking + Running Distance unit conversion.
- Added validation for the generated `Distance Total ÷ 1000` pattern so Health distances are not converted to zero by assuming meter inputs.

## Date: April 28, 2026 — 1.7.3 HealthKit Type picker correction

### Summary

Corrected the 1.7.2 Find Health Samples fix after comparing a shortcut containing a manually created working action and a plugin-generated broken action. The sample-kind row must be `Property = Type` with `Values.Enumeration.WFSerializationType = WFStringSubstitutableState`, `Bounded = true`, and `Removable = false`. The generated `Property = Value` / `Values.String = Step Count` row imports as an editable text filter, not the Health type picker.

### Fixes Applied

- Updated HealthKit docs and examples to use a locked `Type is <Health picker label>` row for Find Health Samples.
- Updated `validate_shortcut.py` to reject legacy `Value` string rows and validate the `Type` enumeration state.
- Added `observed_find_samples_labels` to the generated HealthKit reference so `HKQuantityTypeIdentifierStepCount` uses `Steps` for Find Health Samples, while other Health action contexts can still use `Step Count`.
- Updated regression fixtures so the exact generated failure shape is invalid.

## Date: April 28, 2026 — 1.7.2 HealthKit Value filter correction

### Summary

Superseded by 1.7.3. This release incorrectly changed the Find Health Samples sample-kind row to `Property = Value`, which imported as an editable text filter rather than the Health type picker.

### Fixes Applied

- The 1.7.3 release restores the correct `Type` row and changes the underlying value state to the observed enumeration shape.

## Date: April 27, 2026 — 1.7.1 HealthKit filter correction

### Summary

Corrected Find Health Samples guidance after comparing a generated Health shortcut against a manually created iOS action. The previously documented top-level `WFHealthQuantityType` key is not honored by the iOS Shortcuts editor. This release moved the sample kind into `WFContentItemFilter`; 1.7.3 later corrected the row value state to the locked `Type` enumeration shape.

### Fixes Applied

- Updated `HEALTHKIT.md`, `FILTERS.md`, `PARAMETER_TYPES.md`, `BEST_PRACTICES.md`, and `SKILL.md` to forbid `WFHealthQuantityType` for Find Health Samples.
- Updated `validate_shortcut.py` to reject obsolete `WFHealthQuantityType` and require a sample-kind predicate row.
- Updated `test_wiring_regressions.py` so valid Health sample find/detail cases use `WFContentItemFilter` sample-kind rows and invalid cases catch missing, malformed, or unknown sample-kind rows.
- Updated `data/healthkit-ios26.2-reference.json` metadata so the packaged evidence no longer advertises the obsolete key.

## Date: April 26, 2026 — Codex package

### Summary

Adapted the Shortcuts Playground skill for Codex plugin packaging.

### Fixes Applied

- Removed Claude-only slash command, specialized agent, hook, wrapper-bin, and `userConfig` assumptions from the Codex skill entry point.
- Added direct script invocation instructions for icon resolution, validation, and archive/sign.
- Added `scripts/sign_shortcut.sh` as the Codex signing helper.

## Date: April 26, 2026 — 1.6.1 follow-up

### Summary

Removed user-specific local evidence details from the distributed HealthKit references and sanitized bundled XML examples.

### Fixes Applied

- Replaced exported shortcut filenames and scratch-folder descriptions in `HEALTHKIT.md` with generic evidence descriptions.
- Regenerated `data/healthkit-ios26.2-reference.json` so it stores evidence IDs and parameter shapes, not user-specific source paths.
- Removed personal attribution/sample names from bundled golden XML examples.

## Date: April 26, 2026

### Summary

Added HealthKit support from anonymized iOS Shortcuts XML exports, iPhoneOS 26.2 HealthKit headers, and ActionKit unit constants. The skill now documents and validates Find Health Samples, Get Details of Health Sample, Log Health Sample, and Log Workout.

### Fixes Applied

- Added `HEALTHKIT.md` with bundled anonymized XML examples for Find Health Samples, Log Health Sample quantity/category samples, Get Details of Health Sample, and Log Workout identifier coverage.
- Added `data/healthkit-ios26.2-reference.json`, generated by `scripts/generate_healthkit_reference.py`.
- Updated `validate_shortcut.py` to allow iOS Health actions and validate their required parameters, Health sample detail wiring, Health filters, quantity fields, category values, dates, and workout fields.
- Expanded `test_wiring_regressions.py` to cover all 120 HealthKit quantity types, 70 category types, 61 category enum values, 84 workout activity types, 46 ActionKit Health unit strings, and variable/date-token cases.
- Updated `ACTIONS.md`, `FILTERS.md`, `PARAMETER_TYPES.md`, `BEST_PRACTICES.md`, and `SKILL.md` so agents no longer escalate on Log Health Sample schema gaps.

### Bundled Evidence Findings

- `is.workflow.actions.health.quantity.log` uses `WFQuantitySampleType` plus `WFQuantitySampleQuantity` as `WFQuantityFieldValue`.
- `WFQuantitySampleAdditionalQuantity` can be unit-only.
- Category samples can retain the count-based quantity scaffold even when the editor hides the Value row.
- Category picker values use `WFCategorySampleEnumeration`; observed example: `Cervical Mucus Quality` with `Dry`.
- `is.workflow.actions.filter.health.quantity` uses `WFContentPredicateTableTemplate`; later corrected in 1.7.3 to require the sample kind as a locked `Type is ...` enumeration row plus date filters such as `Start Date` + operator `1002` for "is today".
- `is.workflow.actions.properties.health.quantity` accepts `Type`, `Value`, `Unit`, `Start Date`, `End Date`, `Duration`, `Source`, and `Name`.

## Date: March 26, 2026

### Summary

Applied autoresearch findings from the previous session to two real-world shortcut fixes. Verified all 8 documented findings are present and accurate across skill files. No new documentation gaps found — all rules are correctly represented.

---

### Fixes Applied

#### QuickMath Comment UUIDs Fix
- **Problem:** Comment actions inside the QuickMath shortcut contained UUID references (e.g., `"Uses output from Random Number (UUID: A1B2C3D4-0001...)"`)
- **Root cause:** Violates the mandatory Comment discipline rule — Comments must contain ONLY descriptive natural language, never UUIDs or plist internals
- **Fix:** Replaced all Comment text containing UUID patterns with human-readable descriptions (e.g., `"Pick a random operation: 1=add, 2=subtract, 3=multiply"`)
- **Rule confirmed:** BEST_PRACTICES.md lines 45-48, 219 — "NEVER include UUIDs, OutputUUID references, or any technical plist details in Comment text"

#### Find Notes Filter Fix
- **Problem:** Find Notes action used operator `4` (is/exact match) for Name filter, returning empty results at runtime
- **Root cause:** Notes name matching only supports operator `99` (contains); operator `4` silently returns an empty result set
- **Fix:** Changed `WFFilterOperator` from `<integer>4</integer>` to `<integer>99</integer>` for all Name filters in Find Notes actions
- **Rule confirmed:** FILTERS.md lines 313-334 — "Always use operator 99 when searching notes by name, even when you want an exact title match"

---

### Documentation Audit Results

All 8 autoresearch findings verified as present and correctly documented:

| Finding | Location | Status |
|---------|----------|--------|
| No UUIDs in Comments | BEST_PRACTICES.md §Comment Guidance | ✅ Present |
| Find Notes operator 99 | FILTERS.md §Notes section, §Common Mistakes | ✅ Present |
| WFTextTokenString vs WFTextTokenAttachment | VARIABLES.md §Critical Distinction, PARAMETER_TYPES.md §When to use | ✅ Present |
| shortcuts import silently skips duplicates | BEST_PRACTICES.md §Signing & Install Naming | ✅ Present |
| Condition code table | CONTROL_FLOW.md §Condition Codes, BEST_PRACTICES.md §Preflight | ✅ Present |
| Format Date dual-key rule | PARAMETER_TYPES.md §WFDateFormatStyle, BEST_PRACTICES.md §Actions | ✅ Present |
| Repeat Index/Item Type=Variable | CONTROL_FLOW.md §Accessing Repeat Index, BEST_PRACTICES.md §Critical Variable Wiring | ✅ Present |
| If block WFInput on Mode=0 only | CONTROL_FLOW.md §Implicit vs Explicit Input | ✅ Present |

**Note on Finding 5 (condition code table):** The incoming finding had 100=Does Not Contain and 999=Has Any Value — these are swapped. The existing documentation is correct: 100=Has Any Value, 999=Does Not Contain. The correction was not applied to avoid regressing correct data.

---

## Date: March 24–25, 2026

### Summary

Applied Karpathy's autoresearch methodology to iteratively improve the generate-shortcuts skill through real-world testing. 35+ shortcuts generated and tested, 127 real shortcut XMLs analyzed, multiple fix iterations performed. The master shortcut (54 actions with nested If blocks, menus, Format Date chains, Show Alert wiring, and notifications) **passes runtime** on device.

---

### Findings (in order of discovery)

#### 1. WFDateFormat vs WFDateFormatString
- **Discovered in:** Shortcut #1 (Date Format Alert)
- **Severity:** High — silent runtime failure (raw date object displayed instead of formatted string)
- **Root cause:** The Format Date action reads `WFDateFormat` for the custom format pattern at runtime. `WFDateFormatString` is accepted by the validator and imports without error, but the runtime ignores it.
- **Fix:** Include BOTH `WFDateFormat` AND `WFDateFormatString` with the same pattern for maximum compatibility. 127-shortcut analysis found 23 using only WFDateFormat, 15 using only WFDateFormatString, 8 using both.
- **Runtime confirmed:** ✅ Shortcut #1 correctly displays "March 24, 2026" after fix.

#### 2. Notes action content key (markdownContents)
- **Discovered in:** Shortcut #5 (Create Note)
- **Severity:** High — empty note body at runtime
- **Root cause:** `com.apple.Notes.CreateNoteFromMarkdownLinkAction` uses `markdownContents` (camelCase) as its content parameter, not `markdown`. The validator accepts `markdown` but the runtime produces an empty note.
- **Fix:** Use `markdownContents`. Documented as validator gap (validator's NOTES_CONTENT_KEYS set doesn't include it).
- **Runtime confirmed:** ✅

#### 3. Condition codes must be integers
- **Discovered in:** Shortcuts #11–12 (Battery Check, Number Size)
- **Severity:** Medium — If blocks silently evaluate wrong branch
- **Root cause:** WFCondition must be `<integer>` tags, not `<string>`. All 127 real shortcuts confirm integer-only usage.
- **Fix:** Always use integer condition codes.

#### 4. Hallucinated condition code in Shortcut #15
- **Discovered in:** Shortcut #15 (Word Detection)
- **Severity:** High — exact match instead of substring match
- **Root cause:** Used `WFCondition=4` (Is/exact match) thinking it was "Contains". Code 4 = "Is" (exact), Code 99 = "Contains" (substring).
- **Fix:** Changed to code 99. Added complete condition code lookup table.

#### 5. Condition code 0 Python truthiness bug
- **Discovered in:** Shortcut #12 (Number Size)
- **Severity:** Medium — validator false positive
- **Root cause:** Python `if not condition` evaluates True when `condition` is integer 0. Code 0 (Equals) triggers false validation errors.
- **Fix:** Documented as validator bug. Workaround: avoid code 0, use alternative logic.

#### 6. Numeric If blocks require implicit input (THE MOST IMPORTANT FINDING)
- **Discovered in:** Complex Shortcut C06 (Date Decision Tree) — 4 iterations to diagnose
- **Severity:** Critical — completely breaks numeric conditionals at runtime
- **Root cause:** For condition codes 0–3, the If action must NOT have a `WFInput` key. The immediately preceding action's output feeds in automatically. Using explicit `WFInput` causes "Please choose a value for each parameter" runtime error.
- **Ordering rule:** Source action must be IMMEDIATELY preceding — even a Comment between them breaks the chain.
- **Otherwise branch rule:** Re-compute the value with a fresh source action; implicit context resets at branch boundaries.
- **Fix iterations:**
  - v1: Explicit WFInput with named variable → FAIL
  - v2: Simplified but still explicit → FAIL
  - v3: Implicit input but Comment between source and If → FAIL
  - v4: Format Date immediately before If, no intervening actions → PASS ✅

#### 7. Position counting errors
- **Discovered in:** Shortcuts #10, #22, #25
- **Severity:** Medium — causes validator failures requiring regeneration
- **Root cause:** `attachmentsByRange` positions require exact 0-based character counting against the `string` value. Off-by-one errors were the single most common reason for regeneration.
- **Fix:** Added position accuracy checklist to VARIABLES.md.

#### 8. WFTextTokenString vs WFTextTokenAttachment for display parameters
- **Discovered in:** MASTER-Test shortcut (Show Alert + Notification actions)
- **Severity:** High — display parameters show default/empty text at runtime
- **Root cause:** Display parameters (Show Alert message, Notification body, Show Result text) MUST use `WFTextTokenString` with `￼` (U+FFFC) placeholder + `attachmentsByRange`, even for a single variable. `WFTextTokenAttachment` is only valid for non-display data-flow parameters (`WFInput`, `WFDate`, etc.).
- **Evidence:** All 46 Show Alert and 41 Notification instances in 127 real shortcuts use `WFTextTokenString` for message/body.
- **Fix:** Converted 3 instances in MASTER-Test from WFTextTokenAttachment → WFTextTokenString.

#### 9. `shortcuts import` silently skips duplicates
- **Discovered in:** MASTER-Test debugging (Show Alert fix appeared to not work)
- **Severity:** High — causes false negatives during testing
- **Root cause:** `shortcuts import` exits with code 0 but does NOT replace an existing shortcut with the same name. The old version persists silently.
- **Fix:** Always run `shortcuts delete "Name"` before `shortcuts import`.

#### 10. 127-XML corpus analysis findings
- **Discovered in:** Phase 2 ground-truth analysis
- **Key findings:**
  - Magic variables are OutputUUID-based (OutputName is cosmetic)
  - Aggrandizements enable multi-step property chains (coerce → extract)
  - Accumulator pattern: Append Variable inside Repeat Each, retrieve with Type=Variable
  - Dictionary-based configuration pattern for data-driven shortcuts
  - Content item filter operators have separate number space from If condition codes
  - 8 variable types confirmed: ActionOutput, Variable, CurrentDate, Clipboard, Ask, ExtensionInput, DeviceDetails, CurrentApp
  - Nested conditionals confirmed working up to depth 7 (AppRedirect.xml)
  - Does Not Contain = code 999 (previously undocumented)

---

### Files Modified

#### BEST_PRACTICES.md
- Updated Format Date rule to always include BOTH WFDateFormat AND WFDateFormatString
- Added "Critical Variable Wiring Rules" section with WFTextTokenString vs WFTextTokenAttachment display parameter rule
- Added `shortcuts import` silent duplicate behavior warning to Signing section
- Added complete condition code table with companion parameters and input modes
- Documented implicit vs explicit If input pattern
- Added Repeat Index/Item must use Type=Variable rule
- Added markdownContents for Notes as validator gap
- Added Comment actions before control flow blocks requirement

#### CONTROL_FLOW.md
- Replaced string condition names table with complete integer code table (all 12 codes)
- Added frequency counts from 127-shortcut analysis
- Added full implicit vs explicit input documentation with XML examples
- Added Type=Variable double-wrapper pattern for string If inputs
- Documented WFInput placement rules (only on Mode 0)
- Expanded Common Mistakes section with 4 new entries (display params, implicit chain breaking, numeric WFInput error, code 4 vs 99 confusion)
- Added depth 7 nesting confirmation

#### VARIABLES.md
- Added display vs non-display parameter table for WFTextTokenString/WFTextTokenAttachment selection
- Added runtime evidence (46 Show Alert + 41 Notification instances)
- Clarified that WFTextTokenAttachment is for data-flow only

#### PARAMETER_TYPES.md
- Fixed Format Date documentation: dual-key rule (both WFDateFormat AND WFDateFormatString)
- Added WFTextTokenString vs WFTextTokenAttachment decision table
- Added display parameter context guidance

#### SKILL.md
- Updated rule #28 to use WFDateFormat (not WFDateFormatString)

#### validate_shortcut.py
- Multiple bug fixes during autoresearch iterations
- Condition code handling improvements

*The following files were part of the original autoresearch run but are not included in the distributed skill: AUTORESEARCH_FINAL_REPORT.md, AUTORESEARCH_LOG.md, XML_GROUND_TRUTH.md.*

---

### Test Results

| Category | Count | Validator Pass | Runtime Confirmed |
|----------|-------|---------------|-------------------|
| Simple shortcuts | 25 | 25/25 | SC#1 ✅, SC#2 ✅, SC#5 ✅ (+ batch confirmation) |
| Complex shortcuts | 10 | 10/10 | C06 v4 confirmed correct pattern |
| **Master shortcut** | **1** | **✅ PASS** | **✅ RUNTIME PASS** |

**Master shortcut details:** 54 actions including nested If blocks (numeric + string conditions), Choose from Menu, Format Date chains, Show Alert with variable wiring, Notification with variable wiring, math operations, and text template assembly. Validator passes. **Runtime passes on device.**

**Key fix iterations:**
- Format Date (1 iteration to fix)
- Notes content key (1 iteration)
- Condition codes integer (1 iteration)
- If block wiring — implicit vs explicit (4 iterations, most complex)
- Show Alert wiring — WFTextTokenString (2 iterations)
- `shortcuts import` duplicate behavior (1 iteration)

---

### Methodology Notes

The autoresearch loop confirmed two complementary approaches:

1. **Generate → test → fail → fix** excels at finding runtime-specific behaviors that static analysis misses (e.g., implicit input for numeric If, `shortcuts import` duplicate skipping)
2. **XML reverse engineering** of real shortcuts is faster for mapping structural vocabulary (aggrandizements, accumulator patterns, serialization types)

Neither alone is sufficient. The combination produces high-confidence, runtime-verified documentation.

**Anti-cheating principle:** We never modified the validator to make tests pass. When validator and runtime disagreed, we documented the validator gap and fixed the skill docs to target runtime correctness.
