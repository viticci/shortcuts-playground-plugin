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

## Conditional (If/Otherwise)

Execute different actions based on a condition.

### Structure
| Mode | Action | Description |
|------|--------|-------------|
| 0 | If | Start conditional, define condition |
| 1 | Otherwise | Else branch |
| 2 | End If | Close conditional |

### Template

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
        <string>Equals</string>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>VALUE-TO-TEST-UUID</string>
                <key>OutputName</key>
                <string>Text</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
        <key>WFConditionalActionString</key>
        <string>expected value</string>
    </dict>
</dict>

<!-- Actions for "If" branch go here -->

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

<!-- Actions for "Otherwise" branch go here -->

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

### Condition Codes (DEFINITIVE — from 127 real shortcuts + runtime testing)

**ALWAYS use integer codes** for `WFCondition`. String names may import but degrade at runtime.

| Code | Condition | Category | Companion Parameter | Input Mode | Count in 127 XMLs |
|------|-----------|----------|-------------------|------------|-------------------|
| 0 | Equals (number) | Numeric | WFNumberValue | Implicit | — |
| 1 | Does Not Equal | Numeric | WFNumberValue | Implicit | — |
| 2 | Is Greater Than | Numeric | WFNumberValue | Implicit | 19 |
| 3 | Is Less Than | Numeric | WFNumberValue | Implicit | 1 |
| 4 | Is (exact string match) | String | WFConditionalActionString | Explicit | 32 |
| 5 | Is Not | String | WFConditionalActionString | Explicit | 3 |
| 8 | Begins With | String | WFConditionalActionString | Explicit | — |
| 9 | Ends With | String | WFConditionalActionString | Explicit | — |
| 99 | Contains (substring) | String | WFConditionalActionString | Explicit | 29 |
| 100 | Has Any Value | Existence | (none needed) | Explicit | 31 |
| 101 | Does Not Have Any Value | Existence | (none needed) | Explicit | 9 |
| 999 | Does Not Contain | String | WFConditionalActionString | Explicit | 1 |

⚠️ **Common confusion:** Code 4 = "Is" (exact match), Code 99 = "Contains" (substring). Do NOT confuse them — code 4 for substring matching will only match exact strings.

⚠️ **Python validator bug:** Code 0 is falsy in Python (`if not 0` evaluates as True). The validator may report false positives for Equals conditions. This is a validator bug, not a Shortcuts bug.

### Implicit vs Explicit Input (CRITICAL — runtime-verified, 4 iterations to diagnose)

**Numeric conditions (codes 0–3): IMPLICIT input — do NOT set `WFInput`.**

The action immediately before the If block provides the input automatically. The structure must be:
```
[source action (e.g., Format Date)] → [If block (no WFInput key)]
```

**CRITICAL ordering rule:** No intervening actions are allowed between the source and the If — not even a Comment action. A Comment between them breaks the implicit chain because Shortcuts passes the Comment's nil output to the If instead of the source value.

When a numeric If needs the same value in the Otherwise branch, **re-compute it** with a fresh source action (e.g., a second Format Date). The implicit input context resets at branch boundaries.

**String/existence conditions (codes 4, 5, 8, 9, 99, 100, 101, 999): EXPLICIT `WFInput` required.**

Use the `Type=Variable` double-wrapper pattern:
```xml
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
            <string>MyVar</string>
        </dict>
        <key>WFSerializationType</key>
        <string>WFTextTokenAttachment</string>
    </dict>
</dict>
```

Named variables via Set Variable work reliably. ActionOutput references also work when wrapped in the same structure.

**WFInput placement rules:**
- ONLY on Mode 0 (If start) — never on Mode 1 (Otherwise) or Mode 2 (End If)
- For bare `WFTextTokenAttachment` on If actions: frequently imports as blank/empty on iOS — always use the `Type=Variable` wrapper

**Known validator gap:** The validator requires explicit `WFInput` for all If blocks and rejects implicit input. Shortcuts using numeric If with implicit input will fail validation but work correctly at runtime.

### Compound Conditionals (Advanced)

WorkflowKit supports AND/OR compound conditions via `WFCompoundType` and the `WFConditionalAction.ParameterKey` enum (`conditions`, `compoundType`, `singleRowConditions`). These use the same table-template system as Find/Filter actions.

**Do NOT use compound conditionals in generated shortcuts.** The simple single-condition format above is what the validator supports and is reliable on import. If you need multiple conditions, chain separate If blocks or compute a boolean variable before the conditional.

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

7. **Putting actions between source and numeric If block**
   - Even a Comment action between Format Date and a numeric If breaks the implicit input chain
   - The source action must be the IMMEDIATELY PRECEDING action

8. **Using explicit WFInput for numeric conditions (codes 0–3)**
   - Causes "Please choose a value for each parameter" runtime error
   - Only string/existence conditions (codes 4+) use explicit WFInput

9. **Confusing condition code 4 (Is) with code 99 (Contains)**
   - Code 4 = exact string equality, Code 99 = substring match
   - Using code 4 when you mean "contains" will only match the exact string
