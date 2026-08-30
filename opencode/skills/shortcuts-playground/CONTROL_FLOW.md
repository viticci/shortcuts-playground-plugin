# Control Flow Patterns

How to implement loops, conditionals, and menus in Shortcuts.

## Overview

Control flow actions use two key parameters:
- **GroupingIdentifier**: A UUID that links related actions (start, middle, end)
- **WFControlFlowMode**: An integer indicating the action's role
  - `0` = Start (begin block)
  - `1` = Middle (else, case)
  - `2` = End (close block)

**Important**: `WFControlFlowMode` must be an `<integer>`, not a `<string>`.

---

## Repeat Count

Repeat a block of actions a specific number of times.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Start | Begin repeat, set count |
| 2 | End | Close repeat block |

### Template

```xml
<!-- Repeat Start -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>REPEAT-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFRepeatCount</key>
        <!-- Can be integer or variable reference -->
        <integer>5</integer>
    </dict>
</dict>

<!-- Actions inside the loop go here -->

<!-- Repeat End -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>END-ACTION-UUID</string>
        <key>GroupingIdentifier</key>
        <string>REPEAT-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Accessing Repeat Index

Inside the loop, reference the current index as a **named Variable** (Type=Variable, not ActionOutput):

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{0, 1}</key>
    <dict>
        <key>Type</key>
        <string>Variable</string>
        <key>VariableName</key>
        <string>Repeat Index</string>
    </dict>
</dict>
```

**CRITICAL:** Repeat Index uses `Type: Variable` with `VariableName: "Repeat Index"`, NOT `Type: ActionOutput` referencing the end action's UUID. Using the wrong type causes the variable to appear as "Repeat Results" in the UI and fails at runtime.

---

## Repeat with Each (For Each)

Iterate over each item in a list.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Start | Begin loop, specify input list |
| 2 | End | Close loop |

### Template

```xml
<!-- Repeat Each Start -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.each</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>FOREACH-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>LIST-SOURCE-UUID</string>
                <key>OutputName</key>
                <string>List</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>

<!-- Actions inside the loop go here -->

<!-- Repeat Each End -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.each</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>END-ACTION-UUID</string>
        <key>GroupingIdentifier</key>
        <string>FOREACH-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Accessing Current Item

Reference the current item using a **named Variable** (Type=Variable):

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{0, 1}</key>
    <dict>
        <key>Type</key>
        <string>Variable</string>
        <key>VariableName</key>
        <string>Repeat Item</string>
    </dict>
</dict>
```

**Alternatively** (less common), use the Start action's UUID as an ActionOutput:

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{0, 1}</key>
    <dict>
        <key>OutputUUID</key>
        <string>START-ACTION-UUID</string>
        <key>OutputName</key>
        <string>Repeat Item</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
</dict>
```

**Preferred approach:** Use `Type: Variable` with `VariableName: "Repeat Item"` for consistency and UI stability.

---

## Conditional (If/Otherwise/Otherwise If)

Execute different actions based on a condition.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | If | Start conditional, define condition |
| 1 | Otherwise / Otherwise If | Else branch, or a conditional middle branch when condition fields are present |
| 2 | End If | Close conditional |

### Template (single-condition If)

```xml
<!-- If -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFCondition</key>
        <integer>4</integer>
        <key>WFConditionalActionString</key>
        <string>Yes</string>
        <key>WFInput</key>
        <dict>
            <key>Type</key>
            <string>Variable</string>
            <key>Variable</key>
            <dict>
                <key>Value</key>
                <dict>
                    <key>OutputName</key>
                    <string>Text</string>
                    <key>OutputUUID</key>
                    <string>VALUE-TO-TEST-UUID</string>
                    <key>Type</key>
                    <string>ActionOutput</string>
                </dict>
                <key>WFSerializationType</key>
                <string>WFTextTokenAttachment</string>
            </dict>
        </dict>
    </dict>
</dict>

<!-- Actions for the "If" branch go here -->

<!-- Otherwise -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
    </dict>
</dict>

<!-- Actions for the "Otherwise" branch go here -->

<!-- End If -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Otherwise If (macOS 27+)

`Otherwise If` is not a new action identifier and does not use a new control-flow mode. It is still `is.workflow.actions.conditional` with `WFControlFlowMode = 1`; the difference from plain Otherwise is that it also carries the same condition fields as an If start (`WFCondition`, `WFInput`, and the required literal field for that condition code).

Plain Otherwise:

```xml
<key>WFControlFlowMode</key>
<integer>1</integer>
```

Otherwise If:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFCondition</key>
        <integer>99</integer>
        <key>WFConditionalActionString</key>
        <string>Four</string>
        <key>WFInput</key>
        <dict>
            <key>Type</key>
            <string>Variable</string>
            <key>Variable</key>
            <dict>
                <key>Value</key>
                <dict>
                    <key>Type</key>
                    <string>Variable</string>
                    <key>VariableName</key>
                    <string>List Variable</string>
                </dict>
                <key>WFSerializationType</key>
                <string>WFTextTokenAttachment</string>
            </dict>
        </dict>
    </dict>
</dict>
```

Place any `Otherwise If` actions after the initial mode 0 If branch and before a final plain Otherwise. Use the same `GroupingIdentifier` for every branch in the block.

### macOS 27 List Contains Import Trap

When checking whether a list contains an item, avoid this pattern:

1. Set `Fruit List` from a List action.
2. Add an item to `Fruit List`.
3. Set `Fruit List` again from the Add to List output.
4. Run `If Fruit List contains "Orange"`.

On macOS 27, imported shortcuts using that repeated-name list pattern can show a blank comparison chip even though the plist contains `WFConditionalActionString`. Use one of these safe shapes instead:

- Reference the final `List`/`Add to List` action output directly in the conditional `WFInput`.
- Or use an intermediate name while mutating (for example `Working Fruit List`) and assign the final list once to a fresh name (`Fruit List`) immediately before the If.

### Condition Codes (DEFINITIVE — verified against an Apple-built sample shortcut)

**ALWAYS use integer codes** for `WFCondition`. String names may import but degrade at runtime.

| Code | UI label | Category | Required extra fields |
|------|----------|----------|------------------------|
| `0`  | is less than | numeric | `WFNumberValue` |
| `1`  | is less than or equal to | numeric | `WFNumberValue` |
| `2`  | is greater than | numeric | `WFNumberValue` |
| `3`  | is greater than or equal to | numeric | `WFNumberValue` |
| `4`  | is (string equals) | string | `WFConditionalActionString` |
| `5`  | is not | string | `WFConditionalActionString` |
| `8`  | begins with | string | `WFConditionalActionString` |
| `9`  | ends with | string | `WFConditionalActionString` |
| `99` | contains | string | `WFConditionalActionString` |
| `100`| has any value | existence | (none) |
| `101`| does not have any value | existence | (none) |
| `999`| does not contain | string | `WFConditionalActionString` |
| `1003` | is between | numeric | `WFNumberValue` (lower) + `WFAnotherNumber` (upper) |

⚠️ **Common confusions to avoid:**
- Code `4` is the string `is` (exact equality). Code `99` is the string `contains` (substring). They are NOT interchangeable.
- Code `0` is `is less than`, NOT `equals`. There is no numeric "equals" code in the modern Shortcuts conditional action — to check equality of two numbers, use `is greater than or equal to` AND `is less than or equal to` (Any-of-two pattern below) or compare via Text equality (code `4`).
- Code `2` is `is greater than`, code `3` is `is greater than or equal to`. They differ by inclusivity — easy to swap by mistake.

### Input rule (uniform across all codes)

**ALL conditional codes require an explicit `WFInput` as a `Type=Variable` wrapper.** There is no "implicit input" mode. The previous documentation that told you numeric conditions (0–3) use implicit input was incorrect — verified against an Apple-built sample where every single `is.workflow.actions.conditional` action sets `WFInput` explicitly.

The wrapper structure:

```xml
<key>WFInput</key>
<dict>
    <key>Type</key>
    <string>Variable</string>
    <key>Variable</key>
    <dict>
        <key>Value</key>
        <dict>
            <key>OutputName</key>
            <string>Text</string>
            <key>OutputUUID</key>
            <string>UPSTREAM-ACTION-UUID</string>
            <key>Type</key>
            <string>ActionOutput</string>
        </dict>
        <key>WFSerializationType</key>
        <string>WFTextTokenAttachment</string>
    </dict>
</dict>
```

For `Type=Variable` referencing a named variable instead of an `ActionOutput`, replace the inner `Value` dict with:

```xml
<key>Value</key>
<dict>
    <key>Type</key>
    <string>Variable</string>
    <key>VariableName</key>
    <string>MyVarName</string>
</dict>
```

**Placement rules:**
- `WFInput` belongs on Mode 0 (If start) and on Mode 1 only when the action is an Otherwise If. Plain Otherwise (mode 1 with no condition fields) and End If (mode 2) carry only `GroupingIdentifier` + `WFControlFlowMode`.
- The `WFInput` field itself is a dict with `Type` = `"Variable"` and a nested `Variable` dict. Bare `WFTextTokenAttachment` (without the `Type`/`Variable` wrapper) imports as blank in the editor.

### "is between" (code 1003)

The between condition needs both a lower bound (`WFNumberValue`, a literal string) and an upper bound (`WFAnotherNumber`, a token attachment that can hold either a literal or a variable reference):

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>IF-BETWEEN-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFCondition</key>
        <integer>1003</integer>
        <key>WFInput</key>
        <dict>
            <!-- Type=Variable wrapper around the value being tested -->
        </dict>
        <key>WFNumberValue</key>
        <string>1</string>
        <key>WFAnotherNumber</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputName</key>
                <string>Number</string>
                <key>OutputUUID</key>
                <string>UPPER-BOUND-UUID</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```

### Multi-condition If (Any are true / All are true)

Apple's modern Shortcuts conditional supports a single If block testing **multiple conditions at once**, joined by either "Any are true" (OR) or "All are true" (AND). This is encoded as `WFConditions` with serialization type `WFContentPredicateTableTemplate`, NOT as a sequence of separate If blocks.

**When to use:** the user explicitly asks for "if A or B", "if any of these are true", "if all of these match", or similar combinatorial logic. Otherwise, chain single-condition Ifs.

**Top-level structure:** The action sets ONLY `WFConditions`, `WFControlFlowMode`, and `GroupingIdentifier`. There is **no** top-level `WFCondition`, `WFInput`, `WFConditionalActionString`, or `WFNumberValue` — those live inside each template. The validator rejects mixing the two patterns.

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.conditional</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MULTI-IF-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFConditions</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>WFActionParameterFilterPrefix</key>
                <integer>0</integer>
                <!--
                  WFActionParameterFilterPrefix:
                    0 = Any are true (OR — at least one row matches)
                    1 = All are true (AND — every row must match)
                -->
                <key>WFActionParameterFilterTemplates</key>
                <array>
                    <!-- Row 1: string is "Yes" -->
                    <dict>
                        <key>WFCondition</key>
                        <integer>4</integer>
                        <key>WFConditionalActionString</key>
                        <string>Yes</string>
                        <key>WFInput</key>
                        <dict>
                            <key>Type</key>
                            <string>Variable</string>
                            <key>Variable</key>
                            <dict>
                                <key>Value</key>
                                <dict>
                                    <key>OutputName</key>
                                    <string>Text</string>
                                    <key>OutputUUID</key>
                                    <string>TEXT-VAR-UUID</string>
                                    <key>Type</key>
                                    <string>ActionOutput</string>
                                </dict>
                                <key>WFSerializationType</key>
                                <string>WFTextTokenAttachment</string>
                            </dict>
                        </dict>
                    </dict>
                    <!-- Row 2: string is not "No" -->
                    <dict>
                        <key>WFCondition</key>
                        <integer>5</integer>
                        <key>WFConditionalActionString</key>
                        <string>No</string>
                        <key>WFInput</key>
                        <dict>
                            <!-- Same Type=Variable wrapper -->
                        </dict>
                    </dict>
                    <!-- Row 3: number is greater than 1 -->
                    <dict>
                        <key>WFCondition</key>
                        <integer>2</integer>
                        <key>WFNumberValue</key>
                        <string>1</string>
                        <key>WFInput</key>
                        <dict>
                            <!-- Type=Variable wrapper pointing at a Number variable -->
                        </dict>
                    </dict>
                </array>
                <key>WFContentPredicateBoundedDate</key>
                <false/>
            </dict>
            <key>WFSerializationType</key>
            <string>WFContentPredicateTableTemplate</string>
        </dict>
    </dict>
</dict>
```

**Per-template rules** (each entry inside `WFActionParameterFilterTemplates`):

- Each template is an independent condition with its own `WFCondition`, `WFInput`, and the appropriate literal field (`WFConditionalActionString` for codes 4/5/8/9/99/999, `WFNumberValue` for codes 0/1/2/3, `WFNumberValue`+`WFAnotherNumber` for code 1003, no literal for codes 100/101).
- Each template's `WFInput` follows the same `Type=Variable` wrapper rule as the single-condition pattern, and can reference a different upstream variable than other templates in the same block.
- Templates inside the same multi-condition block don't need a `GroupingIdentifier` — the parent action holds it.
- Apple's table-template format may include `WFContentPredicateBoundedDate` (a boolean) for date-aware filters; emit `<false/>` unless the conditions involve dates.

Plain Otherwise / End If actions for a multi-condition block are identical to the single-condition pattern: just `GroupingIdentifier` + `WFControlFlowMode` (1 or 2). A macOS 27+ Otherwise If middle branch can carry condition fields on mode 1.

---

## Choose from Menu

Present a menu of options and execute different actions based on the user's choice.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | Menu | Define menu with items |
| 1 | Case | One case per menu item |
| 2 | End Menu | Close menu |

### Template

```xml
<!-- Menu Definition -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFMenuPrompt</key>
        <string>Choose an option:</string>
        <key>WFMenuItems</key>
        <array>
            <string>Option 1</string>
            <string>Option 2</string>
            <string>Option 3</string>
        </array>
    </dict>
</dict>

<!-- Case 1: Option 1 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 1</string>
    </dict>
</dict>

<!-- Actions for Option 1 go here -->

<!-- Case 2: Option 2 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 2</string>
    </dict>
</dict>

<!-- Actions for Option 2 go here -->

<!-- Case 3: Option 3 -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>1</integer>
        <key>WFMenuItemTitle</key>
        <string>Option 3</string>
    </dict>
</dict>

<!-- Actions for Option 3 go here -->

<!-- End Menu -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.choosefrommenu</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>MENU-GROUP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

### Important Notes (from 127 real shortcuts analysis)

1. **Menu definition mode 0**: Uses `WFMenuItems` array containing all option strings
2. **Case mode 1 for each option**: One mode 1 action per menu item with exact `WFMenuItemTitle` match
3. **WFMenuItemTitle must match exactly** - Each case title must match the corresponding item in WFMenuItems exactly (case-sensitive)
4. **Order must match** - Case (mode 1) actions must appear in the same order as items in the WFMenuItems array
5. **One case per item** - You need exactly one mode 1 action for each menu item
6. **Close with mode 2** - End the menu structure with a mode 2 action (uses same GroupingIdentifier, no additional parameters)

---

## Nesting Control Flow

Control flow blocks can be nested to arbitrary depth. Analysis of 127 real shortcuts confirms nesting up to **depth 7** in production shortcuts (AppRedirect.xml).

**Key rule:** Each nested block needs its own unique GroupingIdentifier:

```xml
<!-- Outer Repeat -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>OUTER-LOOP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>0</integer>
        <key>WFRepeatCount</key>
        <integer>3</integer>
    </dict>
</dict>

    <!-- Inner Conditional -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>0</integer>
            <!-- condition params -->
        </dict>
    </dict>

    <!-- Inner Otherwise -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>1</integer>
        </dict>
    </dict>

    <!-- Inner End If -->
    <dict>
        <key>WFWorkflowActionIdentifier</key>
        <string>is.workflow.actions.conditional</string>
        <key>WFWorkflowActionParameters</key>
        <dict>
            <key>GroupingIdentifier</key>
            <string>INNER-IF-UUID</string>
            <key>WFControlFlowMode</key>
            <integer>2</integer>
        </dict>
    </dict>

<!-- Outer End Repeat -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.repeat.count</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>GroupingIdentifier</key>
        <string>OUTER-LOOP-UUID</string>
        <key>WFControlFlowMode</key>
        <integer>2</integer>
    </dict>
</dict>
```

---

## Nothing and Exit Actions

Two special control flow actions have no parameters:

- **Nothing** (`is.workflow.actions.nothing`): Produces no output. Use as a placeholder inside branches that should intentionally return no result.
- **Exit Shortcut** (`is.workflow.actions.exit`): Immediately stops the shortcut. Empty parameters dict.

Both need only `WFWorkflowActionIdentifier` and an empty `WFWorkflowActionParameters` dict (no UUID needed).

---

## Common Mistakes

1. **Using string instead of integer for WFControlFlowMode**
   - Wrong: `<string>0</string>`
   - Right: `<integer>0</integer>`

2. **Mismatched GroupingIdentifier**
   - All parts of a control flow block must share the same GroupingIdentifier
   - Nested blocks MUST have distinct GroupingIdentifiers per level
   - Confirmed working up to depth 7 (from AppRedirect.xml in 127-shortcut analysis)

3. **Missing End action**
   - Every start (mode 0) must have a corresponding end (mode 2)

4. **Wrong order in menu cases**
   - Cases must appear in the same order as WFMenuItems

5. **Referencing wrong UUID for loop items**
   - Repeat Item uses the **start** action's UUID (OR `Type=Variable` with `VariableName="Repeat Item"` — preferred)
   - Repeat Index uses `Type=Variable` with `VariableName="Repeat Index"` — NOT ActionOutput

6. **Using WFTextTokenAttachment for display parameters in control flow branches**
   - Show Alert message, Notification body, and Show Result text MUST use `WFTextTokenString` (with `￼` placeholder + `attachmentsByRange`)
   - Using `WFTextTokenAttachment` for these causes default/empty text at runtime

7. **Omitting `WFInput` on conditional codes 0–3**
   - All conditional codes — numeric, string, and existence — require an explicit `WFInput` as a `Type=Variable` wrapper. The earlier "implicit input for numeric conditions" rule was wrong; an Apple-built sample shortcut has explicit `WFInput` on every conditional, including codes 0, 1, 2, 3, and 1003.

8. **Confusing condition code semantics**
   - Code `0` = `is less than` (NOT equals). Code `1` = `is less than or equal to`. Code `2` = `is greater than`. Code `3` = `is greater than or equal to`.
   - Code `4` = string `is` (exact equality). Code `99` = string `contains` (substring). Using code 4 when you mean "contains" will only match the exact string.

9. **Mixing single-condition and multi-condition fields on one If**
   - If you set `WFConditions` (multi-condition `WFContentPredicateTableTemplate`), do NOT also set top-level `WFCondition`, `WFInput`, or any literal field. The validator rejects this.
   - Conversely, if you set top-level `WFCondition` + `WFInput`, do NOT set `WFConditions`. Pick one pattern per If.

10. **Forgetting `WFAnotherNumber` on `is between` (code 1003)**
    - Code 1003 needs both `WFNumberValue` (lower bound, literal string) and `WFAnotherNumber` (upper bound, token attachment). Missing `WFAnotherNumber` imports as an empty upper-bound field.

11. **Treating Otherwise If as a separate action**
    - macOS 27 serializes Otherwise If as `is.workflow.actions.conditional` with `WFControlFlowMode = 1` plus condition fields. Plain Otherwise is the same mode with no condition fields.
