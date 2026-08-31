# Variable Reference System

How to pass data between actions in Shortcuts.

## Overview

Shortcuts uses a UUID-based system for referencing output from previous actions:

1. **Source action** has a `UUID` parameter identifying its output
2. **Consuming action** references that UUID via `OutputUUID` in `attachmentsByRange`
3. The placeholder character `￼` (U+FFFC) marks where variables are inserted in text

## UUID Format

UUIDs must be:
- **Uppercase** letters
- Standard UUID format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

Example: `A1B2C3D4-E5F6-7890-ABCD-EF1234567890`

Generate with any UUID generator, just ensure uppercase.

---

## WFSerializationType Values

The `WFSerializationType` key indicates the type of value:

| Type | Description | Usage |
|------|-------------|-------|
| `WFTextTokenString` | Text with embedded variable references | Text fields with variables mixed in; uses `￼` placeholders |
| `WFTextTokenAttachment` | Single variable reference (no surrounding text) | When parameter IS purely a variable/output; no text wrapper |
| `WFContentPredicateTableTemplate` | Filter/predicate definition | For filter actions |
| `WFDictionaryFieldValueItems` | Dictionary entries | For dictionary creation |
| `WFQuantityFieldValue` | Measurement with unit (duration, size, etc.) | For durations: Magnitude + Unit |

**CRITICAL DISTINCTION (from analysis of 127 real shortcuts + runtime testing):**

- **WFTextTokenAttachment = Single variable reference for data-flow parameters** — use when the parameter IS just a variable with no text around it AND the parameter is a non-display data input (e.g., `WFInput`, `WFDate`, `WFVariable`)
- **WFTextTokenString = Text containing embedded variables OR display parameters** — use when there's text that contains one or more variables inserted via `￼` placeholders, OR when the parameter is a display parameter (shown to the user in UI)

**Display vs Non-Display Parameter Rule (runtime-verified):**

| Parameter Type | Serialization | Example Parameters |
|----------------|--------------|-------------------|
| **Display** (user-visible text) | MUST use `WFTextTokenString` even for single variable | `WFAlertActionMessage`, `WFAlertActionTitle`, `WFNotificationActionBody`, `WFNotificationActionTitle`, `Text` (Show Result) |
| **Non-display** (data flow) | Can use `WFTextTokenAttachment` for single variable | `WFInput`, `WFDate`, `WFVariable`, `WFDictionary`, `WFFile` |

Using `WFTextTokenAttachment` for display parameters causes the field to appear as default/empty text at runtime. This was confirmed across all 46 Show Alert and 41 Notification instances in the 127-shortcut corpus — every one uses `WFTextTokenString` for message/body fields.

---

## attachmentsByRange Format

The `attachmentsByRange` dictionary maps character positions to variable references:

```xml
<key>attachmentsByRange</key>
<dict>
    <key>{position, length}</key>
    <dict>
        <key>OutputUUID</key>
        <string>SOURCE-ACTION-UUID</string>
        <key>OutputName</key>
        <string>Display Name</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
</dict>
```

### Range Key Format

`{position, length}` where:
- **position**: Character index in the string (0-based)
- **length**: Always `1` (the placeholder is 1 character)

Examples:
- `{0, 1}` - Variable at start of string
- `{5, 1}` - Variable at position 5
- `{10, 1}` - Variable at position 10

---

## The Placeholder Character

The Object Replacement Character `￼` (U+FFFC, Unicode code point 65532) serves as a placeholder in the `string` value where variables are inserted.

In XML, represent it as:
- Direct character: `￼`
- Or escaped: `&#xFFFC;` or `&#65532;`

Example string with two variables:
```xml
<key>string</key>
<string>Hello ￼, the weather is ￼</string>
```

With attachments at positions 6 and 24.

---

## Position Accuracy Checklist

- Compute `attachmentsByRange` positions from the final string (0-based) by locating each `￼` placeholder.
- Recompute positions if the surrounding text changes (including emoji or added characters).
- For multiple placeholders, create one `attachmentsByRange` entry per `￼` and verify each key points to the exact position.
- If a placeholder exists but no matching range, the variable will not render.
- If a range points past the end of the string, Shortcuts can crash on import.
- For JSON strings, do not leave required fields as empty quotes (`""`); use a placeholder with an attachment or explicitly document the missing value.

---

## Complete Variable Reference Structure

### WFTextTokenString (Text with Variables)

Use when the parameter is text that may contain variable references:

```xml
<key>ParameterName</key>
<dict>
    <key>Value</key>
    <dict>
        <key>string</key>
        <string>The result is: ￼</string>
        <key>attachmentsByRange</key>
        <dict>
            <key>{16, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
                <key>OutputName</key>
                <string>Result</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

### WFTextTokenAttachment (Single Variable)

Use when the parameter is just a variable reference with no surrounding text:

```xml
<key>ParameterName</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputUUID</key>
        <string>11111111-1111-1111-1111-111111111111</string>
        <key>OutputName</key>
        <string>Text</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

---

## Type Values

The `Type` key in attachment dictionaries indicates the variable source.

**Complete list of Variable Types (from XML ground truth analysis of 127 real shortcuts):**

| Type | Description | Usage |
|------|-------------|-------|
| `ActionOutput` | Output from a previous action | Most common; requires OutputUUID + OutputName |
| `Variable` | Named variable (from Set Variable) | For referencing named variables by VariableName |
| `CurrentDate` | Current date/time | No additional parameters |
| `Clipboard` | System clipboard contents | No additional parameters |
| `Ask` | Ask When Run prompt response | No additional parameters |
| `ExtensionInput` | Shortcut input (share sheet) | Magic variable for shortcut input |
| `DeviceDetails` | Device information | No additional parameters |
| `CurrentApp` | Currently active application | No additional parameters |

Example with CurrentDate:
```xml
<dict>
    <key>Type</key>
    <string>CurrentDate</string>
</dict>
```

---

## Set Variable and Append Variable Patterns

### Set Variable (is.workflow.actions.setvariable)

Creates or updates a named variable:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.setvariable</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>VARIABLE-ACTION-UUID</string>
        <key>WFVariableName</key>
        <string>myVariableName</string>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>SOURCE-ACTION-UUID</string>
                <key>OutputName</key>
                <string>Text</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```

**Key parameters:**
- `WFVariableName`: Name of the variable being set (appears in Variable picker)
- `WFInput`: The value to store (action output, text, etc.)

### Get Variable (WFVariable token attachment)

Reference a named variable later with:

```xml
<key>WFVariable</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>Variable</string>
        <key>VariableName</key>
        <string>myVariableName</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Append Variable (is.workflow.actions.appendvariable)

Accumulator pattern: adds items to a named variable inside loops.

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.appendvariable</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>APPEND-ACTION-UUID</string>
        <key>WFVariableName</key>
        <string>myList</string>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputUUID</key>
                <string>REPEAT-ITEM-UUID</string>
                <key>OutputName</key>
                <string>Repeat Item</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```

**Common pattern (accumulator inside Repeat Each loop):**
1. Start a Repeat Each loop over a list
2. Inside the loop, use Append Variable to add items (or properties of items) to a named variable
3. After the loop ends, the named variable contains all accumulated items
4. Reference it with `Type: Variable` / `VariableName: "myList"`

---

## Aggrandizements (Property Access)

Aggrandizements modify how a variable is accessed, like getting a property or coercing type:

```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>PropertyName</key>
        <string>Name</string>
        <key>Type</key>
        <string>WFPropertyVariableAggrandizement</string>
    </dict>
</array>
```

### Common Aggrandizement Types

#### Property Access
```xml
<dict>
    <key>PropertyName</key>
    <string>Name</string>
    <key>Type</key>
    <string>WFPropertyVariableAggrandizement</string>
</dict>
```

#### Dictionary Key Access
```xml
<dict>
    <key>DictionaryKey</key>
    <string>keyName</string>
    <key>Type</key>
    <string>WFDictionaryValueVariableAggrandizement</string>
</dict>
```

#### Type Coercion
```xml
<dict>
    <key>CoercionItemClass</key>
    <string>WFStringContentItem</string>
    <key>Type</key>
    <string>WFCoercionVariableAggrandizement</string>
</dict>
```

#### Date Format
Format a date variable inline (without a separate Format Date action):
```xml
<dict>
    <key>DateFormat</key>
    <string>Short</string>
    <key>Type</key>
    <string>WFDateFormatVariableAggrandizement</string>
</dict>
```

Possible `DateFormat` values: `Short`, `Medium`, `Long`, `Relative`, or a custom format string.

#### Chaining Multiple Aggrandizements

Aggrandizements can chain to perform multi-step property access in a single variable reference. For example, coercing a calendar event to a Location, then extracting its Street address:

```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>CoercionItemClass</key>
        <string>WFLocationContentItem</string>
        <key>Type</key>
        <string>WFCoercionVariableAggrandizement</string>
    </dict>
    <dict>
        <key>PropertyName</key>
        <string>Street</string>
        <key>PropertyUserInfo</key>
        <string>street</string>
        <key>Type</key>
        <string>WFPropertyVariableAggrandizement</string>
    </dict>
</array>
```

This eliminates the need for intermediate actions — a single variable reference can coerce and extract in one step. Confirmed in the Calendar Locations golden shortcut.

#### Unit Extraction
Extract numeric value or unit string from a measurement variable:
```xml
<dict>
    <key>PropertyName</key>
    <string>Value</string>
    <key>Type</key>
    <string>WFUnitVariableAggrandizement</string>
</dict>
```

---

## WFQuantityFieldValue (Duration and Measurement)

Used for durations and measurements with units (delays, file sizes, etc.):

```xml
<key>WFDuration</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <real>5.0</real>
        <key>Unit</key>
        <string>min</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

**Structure:**
- `Magnitude`: The numeric value (e.g., 5.0 for 5 minutes)
- `Unit`: The unit abbreviation (e.g., "min", "hr", "days", "sec")

**Common duration units:**
- `sec` = seconds
- `min` = minutes
- `hr` = hours
- `days` = days
- `wk` = weeks
- `mon` = months
- `yr` = years

---

## Common Output Names

When referencing action outputs, use these common `OutputName` values:

| Action | OutputName |
|--------|------------|
| Text (gettext) | `Text` |
| Ask for Input | `Provided Input` |
| Ask LLM | `Response` |
| Get Weather | `Weather Conditions` |
| Get Current Location | `Current Location` |
| URL | `URL` |
| Get Contents of URL | `Contents of URL` |
| Number | `Number` |
| Date | `Date` |
| List | `List` |
| Dictionary | `Dictionary` |
| Repeat Each | `Repeat Item` |
| Repeat Count | `Repeat Index` |

---

## Example: Chaining Three Actions

```xml
<!-- Action 1: Get Text -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.gettext</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>11111111-1111-1111-1111-111111111111</string>
        <key>WFTextActionText</key>
        <string>Hello World</string>
    </dict>
</dict>

<!-- Action 2: Ask LLM (references Action 1) -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.askllm</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>22222222-2222-2222-2222-222222222222</string>
        <key>WFLLMPrompt</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>string</key>
                <string>Translate this to French: ￼</string>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{26, 1}</key>
                    <dict>
                        <key>OutputUUID</key>
                        <string>11111111-1111-1111-1111-111111111111</string>
                        <key>OutputName</key>
                        <string>Text</string>
                        <key>Type</key>
                        <string>ActionOutput</string>
                    </dict>
                </dict>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenString</string>
        </dict>
    </dict>
</dict>

<!-- Action 3: Show Result (references Action 2) -->
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
                        <key>OutputUUID</key>
                        <string>22222222-2222-2222-2222-222222222222</string>
                        <key>OutputName</key>
                        <string>Response</string>
                        <key>Type</key>
                        <string>ActionOutput</string>
                    </dict>
                </dict>
                <key>string</key>
                <string>￼</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenString</string>
        </dict>
    </dict>
</dict>
```

---

## Multiple Variables in One Parameter

When a parameter contains multiple variable references:

```xml
<key>Text</key>
<dict>
    <key>Value</key>
    <dict>
        <key>string</key>
        <string>Name: ￼, Age: ￼</string>
        <key>attachmentsByRange</key>
        <dict>
            <key>{6, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>UUID-FOR-NAME</string>
                <key>OutputName</key>
                <string>Name</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>{14, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>UUID-FOR-AGE</string>
                <key>OutputName</key>
                <string>Age</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

Note: Position counting includes all characters including the placeholder `￼`.
