# Parameter Types Reference

Complete documentation of all parameter value types used in iOS Shortcuts.

Based on analysis of 200 real-world shortcuts containing 338 unique actions and 543 parameter keys.

---

## Serialization Types

These are the `WFSerializationType` values that indicate how complex values are encoded:

| Serialization Type | Description | Use Case |
|--------------------|-------------|----------|
| `WFTextTokenString` | Text with embedded variable references | Text fields that can contain variables |
| `WFTextTokenAttachment` | Single variable reference | Input parameters referencing other actions |
| `WFDictionaryFieldValue` | Dictionary with key-value pairs | HTTP headers, JSON bodies |
| `WFContentPredicateTableTemplate` | Filter conditions | Find/Filter actions |
| `WFQuantityFieldValue` | Measurement with unit | Duration, file size, etc. |
| `WFContactFieldValue` | Contact field reference | Contact properties |
| `WFTimeOffsetValue` | Time offset/duration | Time adjustments |

---

## Basic Value Types

### String
Simple text value:
```xml
<key>WFMenuPrompt</key>
<string>Choose an option</string>
```

### Integer
Whole number:
```xml
<key>WFControlFlowMode</key>
<integer>0</integer>
```

### Number (Float)
Decimal number:
```xml
<key>WFNumberActionNumber</key>
<real>30.0</real>
```

### Boolean
True/false (CRITICAL: always use `<true/>` or `<false/>`, never strings or integers):
```xml
<key>WFShowWorkflow</key>
<true/>
```

or

```xml
<key>WFShowWorkflow</key>
<false/>
```

**Important:** Never use `<string>true</string>` or `<integer>1</integer>` for boolean values.

### Array
List of values:
```xml
<key>WFMenuItems</key>
<array>
    <string>Option 1</string>
    <string>Option 2</string>
</array>
```

### Data
Binary data (base64 in XML):
```xml
<key>WFData</key>
<data>BASE64_ENCODED_DATA</data>
```

---

## Date and Time Format Styles

### WFDateFormatStyle

Used by Format Date action to specify the date format:

| Value | Description |
|-------|-------------|
| `Custom` | Use custom format string in WFDateFormat |
| `Short` | Short format (e.g., "3/24/26") |
| `Medium` | Medium format (e.g., "Mar 24, 2026") |
| `Long` | Long format (e.g., "March 24, 2026") |
| `None` | No date component (time only) |

**CRITICAL (from analysis of 127 shortcuts + runtime testing):** When using `WFDateFormatStyle=Custom`, ALWAYS include BOTH `WFDateFormat` AND `WFDateFormatString` with the same custom pattern (e.g., `MMMM d, yyyy`). From the 127-shortcut corpus: 23 shortcuts use only `WFDateFormat`, 15 use only `WFDateFormatString`, 8 include both. The runtime primarily reads `WFDateFormat` (using `WFDateFormatString` alone causes silent failure on some OS versions), but including both ensures maximum compatibility across all Shortcuts versions.

### WFTimeFormatStyle

Used for time-only formatting:

| Value | Description |
|-------|-------------|
| `Short` | Short time format (e.g., "2:30 PM") |
| `Medium` | Medium time format (e.g., "2:30:45 PM") |
| `Long` | Long time format with timezone |
| `None` | No time component (date only) |

---

## Variable Reference Types

### WFTextTokenAttachment (Single Variable Reference)

Used when a parameter accepts a single variable/output reference:

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputName</key>
        <string>Photos</string>
        <key>OutputUUID</key>
        <string>F2BEAE11-3F38-40C3-AD1F-FD48D90F9FE2</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### WFTextTokenString (Text with Variables)

Used for text fields that can contain embedded variables:

```xml
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
        <string>￼</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

Key points:
- `￼` (U+FFFC) is the placeholder character
- `{0, 1}` means "at position 0, length 1"
- Multiple variables: `"Hello ￼, you have ￼ messages"` with `{6, 1}` and `{22, 1}`

**When to use WFTextTokenString vs WFTextTokenAttachment (runtime-verified):**

| Context | Use This | Why |
|---------|----------|-----|
| Display parameter with variable (Show Alert message, Notification body, Show Result text) | `WFTextTokenString` | Runtime requires `￼` + `attachmentsByRange` for UI display fields |
| Text containing mixed literals and variables | `WFTextTokenString` | Multiple insertion points need position-mapped placeholders |
| Single variable as data input (WFInput, WFDate, etc.) | `WFTextTokenAttachment` | Simpler structure for non-display data flow |
| Action input parameter IS a variable | `WFTextTokenAttachment` | Parameter is purely a variable reference |

---

## Dictionary Field Value

Used for HTTP headers, JSON bodies, and form data:

```xml
<key>WFHTTPHeaders</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFDictionaryFieldValueItems</key>
        <array>
            <dict>
                <key>WFItemType</key>
                <integer>0</integer>
                <key>WFKey</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>Content-Type</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
                <key>WFValue</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>application/json</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFDictionaryFieldValue</string>
</dict>
```

### WFItemType Values

| Value | Type |
|-------|------|
| 0 | Text/String |
| 1 | Number |
| 2 | Array |
| 3 | Dictionary |
| 4 | Boolean |

---

### Arrays in WFDictionaryFieldValue

When `WFItemType = 2` (Array), `WFValue` uses `WFArrayParameterState` with a list of items. Do not encode arrays as dictionaries with numeric keys; it can crash imports.

```xml
<dict>
    <key>WFItemType</key>
    <integer>2</integer>
    <key>WFKey</key>
    <dict>
        <key>Value</key>
        <dict>
            <key>string</key>
            <string>labels</string>
        </dict>
        <key>WFSerializationType</key>
        <string>WFTextTokenString</string>
    </dict>
    <key>WFValue</key>
    <dict>
        <key>Value</key>
        <array>
            <dict>
                <key>WFItemType</key>
                <integer>0</integer>
                <key>WFValue</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>example</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </array>
        <key>WFSerializationType</key>
        <string>WFArrayParameterState</string>
    </dict>
</dict>
```

---

## Content Filter (WFContentPredicateTableTemplate)

Used by all Find/Filter actions. See [FILTERS.md](./FILTERS.md) for complete documentation.

Actions that use content filters:
- `is.workflow.actions.filter.photos`
- `is.workflow.actions.filter.files`
- `is.workflow.actions.filter.reminders`
- `is.workflow.actions.filter.calendarevents`
- `is.workflow.actions.filter.contacts`
- `is.workflow.actions.filter.notes`
- `is.workflow.actions.filter.music`
- `is.workflow.actions.filter.articles`
- `is.workflow.actions.filter.apps`
- `is.workflow.actions.filter.health.quantity`
- `is.workflow.actions.conditional` (via `WFConditions`)

---

## Quantity Field Value

Used for measurements with units (duration, file size, etc.):

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

### Common Units

| Category | Units |
|----------|-------|
| Time | `sec`, `min`, `hr`, `days` |
| Data | `bytes`, `KB`, `MB`, `GB` |
| Length | `m`, `km`, `ft`, `mi` |

### HealthKit Quantity Fields

Verified from bundled anonymized iOS Shortcuts XML examples and ActionKit `WFHealthKitConstants.plist`.

For **Log Health Sample**, the main value uses `WFQuantitySampleQuantity`:

```xml
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>120</string>
        <key>Unit</key>
        <string>mg</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

The bundled Caffeine, Bloating, and Cervical Mucus Quality XML examples also include `WFQuantitySampleAdditionalQuantity`; it can be unit-only:

```xml
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>mg</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Category values can additionally include `WFCategorySampleEnumeration`:

```xml
<key>WFQuantitySampleType</key>
<string>Cervical Mucus Quality</string>
<key>WFCategorySampleEnumeration</key>
<string>Dry</string>
```

Health date fields such as `WFQuantitySampleDate`, `WFSampleEndDate`, and `WFWorkoutDate` accept token attachments; `{Type: CurrentDate}` is valid:

```xml
<key>WFQuantitySampleDate</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentDate</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

ActionKit Health unit strings currently covered by the regression suite:

`g`, `m`, `L`, `Pa`, `s`, `J`, `K`, `S`, `mg`, `kg`, `mm`, `km`, `mL`, `kPa`, `ms`, `kJ`, `kK`, `mS`, `kS`, `oz`, `lb`, `st`, `in`, `ft`, `mi`, `mmHg`, `cmAq`, `atm`, `fl_oz_us`, `fl_oz_imp`, `pt_us`, `pt_imp`, `min`, `hr`, `d`, `cal`, `kcal`, `degC`, `degF`, `count`, `%`, `count/min`, `mg/dl`, `J/s`, `m/s^2`, `m/s`.

---

## Named Variable Reference

For accessing named variables (not action outputs):

```xml
<key>WFVariable</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>Variable</string>
        <key>VariableName</key>
        <string>myVariable</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

---

## Special Input Types

### Magic Variable (Shortcut Input)

Reference the shortcut's input:
```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>ExtensionInput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Current Date

```xml
<key>WFDate</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentDate</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Clipboard

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>Clipboard</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Current App

Reference the currently active application:
```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentApp</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

Note: Returns app metadata. Use `WFPropertyVariableAggrandizement` to access specific properties like name or bundle ID.

---

## App Identifier

For actions that reference apps:

```xml
<key>WFAppIdentifier</key>
<string>com.apple.safari</string>
```

Or with full app info:
```xml
<key>WFApp</key>
<dict>
    <key>BundleIdentifier</key>
    <string>com.apple.mobilesafari</string>
    <key>Name</key>
    <string>Safari</string>
    <key>TeamIdentifier</key>
    <string>0000000000</string>
</dict>
```

---

## Parameter Patterns by Action Type

### Text Actions
| Parameter | Type |
|-----------|------|
| `WFTextActionText` | string or WFTextTokenString |
| `Text` | string or WFTextTokenString |

### Control Flow Actions
| Parameter | Type |
|-----------|------|
| `GroupingIdentifier` | string (UUID) |
| `WFControlFlowMode` | integer (0=start, 1=middle, 2=end) |

### Input Parameters
| Parameter | Type |
|-----------|------|
| `WFInput` | WFTextTokenAttachment |
| `WFVariable` | WFTextTokenAttachment (named variable) |

**Count action note**: For `is.workflow.actions.count`, set both `WFInput` and `Input` to the same variable so the UI shows the selected list.

### Photo Actions
| Parameter | Type | Notes |
|-----------|------|-------|
| `WFContentItemFilter` | WFContentPredicateTableTemplate | Filter conditions |
| `photos` | WFTextTokenAttachment | **DeletePhotos uses lowercase `photos`!** |
| `WFPhotoCount` | integer | Number of photos |

### HTTP Actions
| Parameter | Type |
|-----------|------|
| `WFURL` | string, WFTextTokenString, or WFTextTokenAttachment |
| `WFHTTPMethod` | string (`GET`, `POST`, `PUT`, `DELETE`) |
| `WFHTTPBodyType` | string (`JSON`, `Form`, `File`) |
| `WFHTTPHeaders` | WFDictionaryFieldValue |
| `WFJSONValues` | WFDictionaryFieldValue |
| `WFFormValues` | WFDictionaryFieldValue |

---

#### HTTP Notes

- **WFURL variables**: For `WFURL` parameters (especially `downloadurl`), prefer `WFTextTokenString` with `￼` placeholders even when the URL is entirely a variable. `WFTextTokenAttachment` is rare for `WFURL` and can crash imports.
- **JSON bodies**: When `WFHTTPBodyType = JSON`, build the payload as `WFJSONValues` (structured `WFDictionaryFieldValue`). If the body contains arrays of objects or deep nesting and renders incorrectly, use a JSON Text action, set `WFHTTPBodyType = File`, and pass it via `WFRequestVariable` with `Content-Type: application/json`.
- **File body requests**: When `WFHTTPBodyType = File`, include an empty `WFFormValues` dictionary to match system exports.
- **Form file fields**: For `WFHTTPBodyType = Form` and `WFItemType = 5`, wrap the file reference like this so the UI shows the connected file:

```xml
<dict>
    <key>WFItemType</key>
    <integer>5</integer>
    <key>WFKey</key>
    <dict>
        <key>Value</key>
        <dict>
            <key>string</key>
            <string>file</string>
        </dict>
        <key>WFSerializationType</key>
        <string>WFTextTokenString</string>
    </dict>
    <key>WFValue</key>
    <dict>
        <key>Value</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>Type</key>
                <string>Variable</string>
                <key>VariableName</key>
                <string>Repeat Item</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
        <key>WFSerializationType</key>
        <string>WFTokenAttachmentParameterState</string>
    </dict>
</dict>
```
- **Multipart file uploads**: For `WFHTTPBodyType = Form`, the file field must be a file item, not text. Use `WFItemType = 5` and `WFTokenAttachmentParameterState` for the file value. Also set `WFRequestVariable` to the file variable.

## Common Parameter Keys Across Actions

These parameters appear in many different actions:

| Parameter | Count | Type | Description |
|-----------|-------|------|-------------|
| `UUID` | all | string | Action's unique identifier |
| `WFInput` | 306 | variable_ref | Input from previous action |
| `GroupingIdentifier` | ~100 | string | Links control flow actions |
| `WFControlFlowMode` | ~100 | integer | Control flow position |
| `CustomOutputName` | ~50 | string | Custom name for output |
| `WFShowWorkflow` | ~30 | boolean | Show in workflow view |

---

## Type Coercion (Aggrandizements)

When you need to access a property or coerce a type:

```xml
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Aggrandizements</key>
        <array>
            <dict>
                <key>CoercionItemClass</key>
                <string>WFStringContentItem</string>
                <key>Type</key>
                <string>WFCoercionVariableAggrandizement</string>
            </dict>
        </array>
        <key>OutputName</key>
        <string>Model Response</string>
        <key>OutputUUID</key>
        <string>LLM-UUID</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

### Common Coercion Classes

| Class | Description |
|-------|-------------|
| `WFStringContentItem` | Coerce to text |
| `WFNumberContentItem` | Coerce to number |
| `WFBooleanContentItem` | Coerce to boolean |
| `WFDictionaryContentItem` | Coerce to dictionary |
| `WFURLContentItem` | Coerce to URL |
| `WFImageContentItem` | Coerce to image |
| `WFFileContentItem` | Coerce to file |

---

## Math and Counting Operations

### WFMathOperation Values (verified against Shortcuts app output, 2026)

| Operation | WFMathOperation value | Codepoint | Notes |
|-----------|----------------------|-----------|-------|
| **Addition** | **OMIT the key entirely** | — | No `WFMathOperation` key at all. Defaults to addition. |
| Subtraction | `-` | U+002D (ASCII) | Standard ASCII minus |
| Multiplication | `×` | **U+00D7** | Unicode MULTIPLICATION SIGN |
| Division | `÷` | **U+00F7** | Unicode DIVISION SIGN |
| Scientific (Modulus, Power, etc.) | `…` | U+2026 | Placeholder — real op in `WFScientificMathOperation` |

**⚠️ CRITICAL — DO NOT SUBSTITUTE ASCII CHARACTERS:**
- **NEVER** use `*` (asterisk, U+002A) for multiplication — use `×` (U+00D7)
- **NEVER** use `/` (forward slash, U+002F) for division — use `÷` (U+00F7)
- **NEVER** set `WFMathOperation='+'` for addition — **OMIT the key entirely**

**Why this matters**: Shortcuts silently mis-handles wrong math operators. `WFMathOperation='/'` renders in the Shortcuts UI as **addition (`+`)**, producing wrong results with no error. This caused hours of debugging on Apple Frames 4 proportional scaling. Every generated shortcut had `/` where it needed `÷`, causing the min-finding logic to compute `height + physicalHeight` instead of `height ÷ physicalHeight`, producing astronomical target widths that made `image.resize` output Zero KB files.

### WFMathOperand format (literal numbers)

When the second operand is a literal number, use a **plain string** — not a wrapped value dict:

```python
# CORRECT — how the Shortcuts app writes it
mk('is.workflow.actions.math',
   WFInput=action_ref('Number', uid_prev),
   WFMathOperand='10')            # plain string
   # (WFMathOperation omitted → addition)

mk('is.workflow.actions.math',
   WFMathOperation='-',            # ASCII minus
   WFInput=action_ref('Calculation Result', uid_prev),
   WFMathOperand='2')

mk('is.workflow.actions.math',
   WFMathOperation='×',            # U+00D7
   WFInput=action_ref('Calculation Result', uid_prev),
   WFMathOperand='3')

mk('is.workflow.actions.math',
   WFMathOperation='÷',            # U+00F7
   WFInput=action_ref('Calculation Result', uid_prev),
   WFMathOperand='2')
```

When the operand is a variable or action output, use the standard `WFTextTokenAttachment` wrapper:

```python
mk('is.workflow.actions.math',
   WFMathOperation='÷',
   WFInput=action_ref('Details of Images', uid_height),
   WFMathOperand=var_ref('Min PxPerMm'))  # variable reference
```

### WFNumberActionNumber format (for `is.workflow.actions.number`)

For literal numbers, use a **plain string**:

```python
mk('is.workflow.actions.number',
   UUID=uid, WFNumberActionNumber='1')  # plain string, NOT int
```

When the source is a variable or action output, use the standard wrapper:

```python
mk('is.workflow.actions.number',
   UUID=uid, WFNumberActionNumber=action_ref('Name', uid_getname))
```

### Scientific Math Operations

For scientific mode (Modulus, Power, Square Root, etc.), the structure is different:

```python
mk('is.workflow.actions.math',
   WFMathOperation='…',                  # U+2026 placeholder indicating scientific mode
   WFInput=action_ref('Calculation Result', uid_prev),
   WFScientificMathOperation='Modulus',   # the actual operation
   WFScientificMathOperand='1')           # the operand for scientific ops
```

Known `WFScientificMathOperation` values: `Modulus`, `Power`, `Square Root`, `Cube Root`, `Nth Root`, `Natural Logarithm`, `Common Logarithm`, `Logarithm`, `Exponent`, `Factorial`, `Sine`, `Cosine`, `Tangent`, `Arcsine`, `Arccosine`, `Arctangent`.

### Character ordinals for math operations

The correct Unicode characters for math operations (verified):
- `ord('×')` = 215 ✓ (multiplication — U+00D7)
- `ord('÷')` = 247 ✓ (division — U+00F7)
- `ord('-')` = 45 ✓ (ASCII minus — U+002D)
- `ord('…')` = 8230 ✓ (scientific placeholder — U+2026)
- `ord('/')` = 47 ✗ (ASCII slash — silently rendered as `+` by the Shortcuts app)
- `ord('*')` = 42 ✗ (ASCII asterisk — not valid)

### WFCountType Values

| Value | Description |
|-------|-------------|
| `Items` | Count array items |
| `Characters` | Count characters in text |
| `Words` | Count words in text |
| `Sentences` | Count sentences in text |
| `Lines` | Count lines in text |

### WFAdjustOperation Values (for Adjust Date)

| Value | Description |
|-------|-------------|
| `Add` | Add time duration |
| `Subtract` | Subtract time duration |

### WFInputType (for Ask for Input)

| Value | Description |
|-------|-------------|
| `Text` | Plain text input |
| `Number` | Numeric input |
| `URL` | URL input |
| `Date` | Date picker (date only) |
| `Date and Time` | Date and time picker |

### Duration Units (WFQuantityFieldValue)

Duration units used in time-related actions:

| Unit | Description |
|------|-------------|
| `sec` | Seconds |
| `min` | Minutes |
| `hr` | Hours |
| `days` | Days |
| `wk` | Weeks |
| `mon` | Months |
| `yr` | Years |

### Property Access (Dictionary Values)

```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>DictionaryKey</key>
        <string>fieldName</string>
        <key>Type</key>
        <string>WFDictionaryValueVariableAggrandizement</string>
    </dict>
</array>
```

### Date Format Aggrandizement

Format a date variable inline without a separate Format Date action:
```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>DateFormat</key>
        <string>Short</string>
        <key>Type</key>
        <string>WFDateFormatVariableAggrandizement</string>
    </dict>
</array>
```

### Unit Aggrandizement

Extract numeric value or unit string from a measurement variable:
```xml
<key>Aggrandizements</key>
<array>
    <dict>
        <key>PropertyName</key>
        <string>Value</string>
        <key>Type</key>
        <string>WFUnitVariableAggrandizement</string>
    </dict>
</array>
```

## Reminders — Filter & Setter Schemas (DEFINITIVE)

Verified against an Apple-built sample shortcut titled "Reminder Edits" that exercises `is.workflow.actions.filter.reminders` with date operators plus `is.workflow.actions.setters.reminders` applied to every common Reminders property. Treat this section as canonical — do NOT invent alternative parameter keys.

### Find Reminders (`is.workflow.actions.filter.reminders`)

The filter action uses a `WFContentItemFilter` dict wrapping a `WFContentPredicateTableTemplate`. Each filter **row** is a dict inside `WFActionParameterFilterTemplates`, structured differently from an If conditional's template:

| Field | Purpose |
|-------|---------|
| `Operator` (integer) | Operator code (see table below) |
| `Property` (string) | Apple-UI property name: `"List"`, `"Due Date"`, `"Is Completed"`, `"Priority"`, `"Title"`, etc. |
| `Removable` (bool) | Apple sets this `true` for user-removable rows; `<true/>` is fine |
| `Values` (dict) | Operator-specific value block (see table) |

**Filter-level fields:**
- `WFActionParameterFilterPrefix` (integer): `0` = Any are true (OR), `1` = All are true (AND). Same semantic as multi-condition If.
- `WFContentPredicateBoundedDate` (bool): `<false/>` unless the filter operates on a bounded date range.
- `WFSerializationType`: `"WFContentPredicateTableTemplate"` at the `WFContentItemFilter` level.

**Operator ↔ Values schema for Reminders (verified from the sample):**

| `Operator` | UI label | `Property` example | `Values` content |
|-----------|----------|---------------------|------------------|
| `4` | is (enumeration match) | `"List"` | `Values.Enumeration = { Value: "Reminders", WFSerializationType: "WFStringSubstitutableState" }` |
| `1002` | is today (date) | `"Due Date"` | **empty** `<dict/>` — the operator code itself means "today"; no value is required |
| `1003` | is between (date) | `"Due Date"` | `Values.Date` = ISO8601 `<date>` (lower bound, literal); `Values.AnotherDate` = token-attachment dict wrapping `{ Value: { Type: "CurrentDate" }, WFSerializationType: "WFTextTokenAttachment" }` (upper bound, literal or variable like Current Date) |

⚠️ **Filter date operator ≠ If numeric operator.** Filter row `1003` ("is between") uses `Values.Date` + `Values.AnotherDate`. The If conditional `WFCondition=1003` ("is between") uses `WFNumberValue` + `WFAnotherNumber`. Do NOT copy one structure to the other.

**Boolean filter rows for Reminders** (`Is Completed`, `Is Flagged`): use `Operator = 4` and `Values = { Bool: <true/false> }`. No `Unit` field — that's a Photos-specific requirement that does NOT apply to Reminders. See [FILTERS.md → Reminders Boolean filter](FILTERS.md#reminders-wfremindercontentitem) for verbatim templates for "Is Completed = Yes" and "Is Completed = No".

**"Find Reminders" vs "Filter Reminders"** are the same action identifier — add `WFContentItemInputParameter` wrapping a previous action's `ActionOutput` (with `OutputName = "Reminders"`) to turn a Find into a chained Filter. See [FILTERS.md → Find vs Filter](FILTERS.md#find-vs-filter-wfcontentiteminputparameter).

**Verbatim template (Find Reminders where List is Reminders, AND Due Date is between today and Current Date — Any-are-true in the sample):**

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.filter.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>FILTER-UUID</string>
        <key>WFContentItemFilter</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>WFActionParameterFilterPrefix</key>
                <integer>0</integer>
                <key>WFActionParameterFilterTemplates</key>
                <array>
                    <dict>
                        <key>Operator</key>
                        <integer>4</integer>
                        <key>Property</key>
                        <string>List</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict>
                            <key>Enumeration</key>
                            <dict>
                                <key>Value</key>
                                <string>Reminders</string>
                                <key>WFSerializationType</key>
                                <string>WFStringSubstitutableState</string>
                            </dict>
                        </dict>
                    </dict>
                    <dict>
                        <key>Operator</key>
                        <integer>1002</integer>
                        <key>Property</key>
                        <string>Due Date</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict/>
                    </dict>
                    <dict>
                        <key>Operator</key>
                        <integer>1003</integer>
                        <key>Property</key>
                        <string>Due Date</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict>
                            <key>Date</key>
                            <date>2026-04-13T09:54:12Z</date>
                            <key>AnotherDate</key>
                            <dict>
                                <key>Value</key>
                                <dict>
                                    <key>Type</key>
                                    <string>CurrentDate</string>
                                </dict>
                                <key>WFSerializationType</key>
                                <string>WFTextTokenAttachment</string>
                            </dict>
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

### Edit Reminder (`is.workflow.actions.setters.reminders`)

The setter action mutates **one property** of an existing Reminder per action. To change multiple properties on the same reminder, chain multiple setter actions — each subsequent setter's `WFInput` points at the previous setter's `ActionOutput` (`OutputName="Edited Reminder"`) so the "Edited Reminder" variable propagates down the chain.

**Required on every setter:**

| Field | Value | Notes |
|-------|-------|-------|
| `Mode` | `"Set"` | String literal. (Apple also appears to support other modes like `"Clear"` but only `"Set"` is in the reference sample — stick with `"Set"` unless the user asks otherwise.) |
| `UUID` | new uppercase UUID | Standard action UUID |
| `WFContentItemPropertyName` | string, e.g. `"Due Date"`, `"Title"` | Drives which value key the action expects — must match exactly (case + spaces). See table below. |
| `WFInput` | `WFTextTokenAttachment` wrapping the previous setter's `ActionOutput` with `OutputName="Edited Reminder"` | **Omit only on the first setter acting on a Find Reminders output** — that setter inherits the filter's output implicitly. Every subsequent setter needs an explicit chained `WFInput` or the "Edited Reminder" variable breaks. |

**Per-property value key** (add alongside `WFInput` when you want to set a non-default value):

| `WFContentItemPropertyName` | Value key | Value serialization | Notes |
|-----------------------------|-----------|---------------------|-------|
| `Due Date` | `WFReminderContentItemDueDate` | `WFTextTokenString` with a date token attachment (`{Type: "CurrentDate"}` or a literal ISO date) | Use `￼` + `attachmentsByRange` for inline date variables |
| `Title` | `WFReminderContentItemTitle` | `WFTextTokenString` | Text with optional attachments (Clipboard, Variable, etc.) |
| `Parent Reminder` | `WFReminderContentItemParentReminder` | `WFTextTokenAttachment` | Must reference another reminder (usually another "Edited Reminder" from an earlier setter chain) |
| `Subtasks` | `WFReminderContentItemSubtasks` | `WFTextTokenAttachment` | Token reference to a List variable (e.g. the output of a `list` action or a split/built list) |
| `URL` | `WFReminderContentItemURL` | `WFTextTokenString` | Plain text URL with optional attachments |
| `Notes` | `WFReminderContentItemNotes` | `WFTextTokenString` | Multiline-capable; same pattern as Title |
| `Tags` | `WFReminderContentItemTags` | `WFTextTokenString` | Apple's new Tags field; comma-separated in the text |
| `When Messaging Person` | `WFReminderContentItemWhenMessagingPerson` | `WFContactFieldValue` wrapping a `WFContactFieldValues` array of dicts with `WFContactData` (base64-encoded vCard), `WFContactMultivalue`, `WFContactProperty` | Contact-picker field. Use only when the user explicitly names a contact. |
| `Images` | `WFReminderContentItemImages` | `WFTextTokenAttachment` to an image/list variable | Attaches images to the reminder |
| `Priority` | `WFReminderContentItemPriority` | Apple UI shows a picker (None / Low / Medium / High); exact on-disk encoding varies — leave blank unless the user explicitly asks for a priority |
| `Is Completed` | `WFReminderContentItemIsCompleted` | boolean / `WFEnumerationTokenAttachment` (`"Yes"`/`"No"`) | The sample shows an unpopulated slot — when set, expect a Yes/No enumeration |
| `Is Flagged` | `WFReminderContentItemIsFlagged` | same as Is Completed | Yes/No enumeration |
| `List` | `WFReminderContentItemList` | **plain string** (list name, e.g. `"Reminders"`) — NOT a token attachment | Only property that takes a bare string value |

**Verbatim template (edit an existing reminder's Due Date to Current Date, then set Title from Clipboard, chaining both):**

```xml
<!-- First setter works on a Find Reminders output implicitly (no WFInput). -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.setters.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>SETTER1-UUID</string>
        <key>Mode</key>
        <string>Set</string>
        <key>WFContentItemPropertyName</key>
        <string>Due Date</string>
        <key>WFReminderContentItemDueDate</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{0, 1}</key>
                    <dict>
                        <key>Type</key>
                        <string>CurrentDate</string>
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

<!-- Second setter chains via WFInput = previous setter's ActionOutput (OutputName "Edited Reminder"). -->
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.setters.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>SETTER2-UUID</string>
        <key>Mode</key>
        <string>Set</string>
        <key>WFContentItemPropertyName</key>
        <string>Title</string>
        <key>WFInput</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputName</key>
                <string>Edited Reminder</string>
                <key>OutputUUID</key>
                <string>SETTER1-UUID</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
        <key>WFReminderContentItemTitle</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{0, 1}</key>
                    <dict>
                        <key>Type</key>
                        <string>Clipboard</string>
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

### Reschedule pattern (common, copy-paste safe)

The most common Reminders task is "reschedule a reminder to a new date." It's a single setter on `Due Date`, where the value comes from an `Ask for Input` (Date and Time) action earlier in the shortcut:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.setters.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>RESCHEDULE-SETTER-UUID</string>
        <key>Mode</key>
        <string>Set</string>
        <key>WFContentItemPropertyName</key>
        <string>Due Date</string>
        <key>WFInput</key>
        <dict>
            <!-- Reminder to reschedule: chain from the filter or a Repeat Item -->
            <key>Value</key>
            <dict>
                <key>Type</key>
                <string>Variable</string>
                <key>VariableName</key>
                <string>Repeat Item</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
        <key>WFReminderContentItemDueDate</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>attachmentsByRange</key>
                <dict>
                    <key>{0, 1}</key>
                    <dict>
                        <key>OutputName</key>
                        <string>Provided Input</string>
                        <key>OutputUUID</key>
                        <string>ASK-FOR-INPUT-UUID</string>
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

### What you never do with Reminders

- **Never use `com.apple.reminders.UpdateReminderAppIntent`** for editing reminder properties. The identifier is allowlisted but its parameter schema is not published by Apple and changes between OS releases. The WF-classic path (`is.workflow.actions.setters.reminders`) is documented above, verified, and stable — always prefer it for editing existing reminders.
- **Never chain setters without `WFInput`.** The first setter acting directly on a Find Reminders output can omit `WFInput` (implicit from the preceding filter). Every subsequent setter needs an explicit `WFInput` token attachment pointing at the previous setter's `ActionOutput` (`OutputName="Edited Reminder"`) or the chain breaks and every downstream setter edits the wrong reminder.
- **Never put `WFReminderContentItemList` inside a token attachment dict.** It's the one property that takes a plain string — `<string>Reminders</string>`, not a wrapper.
- **Never use filter operator `1003` with `WFNumberValue`/`WFAnotherNumber`.** Date filters use `Values.Date` + `Values.AnotherDate`. That's different from If conditional `1003`.
