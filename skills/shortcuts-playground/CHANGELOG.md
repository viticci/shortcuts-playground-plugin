# Autoresearch Loop Changelog

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
