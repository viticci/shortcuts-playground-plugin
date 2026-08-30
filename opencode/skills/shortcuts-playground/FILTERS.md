# Content Item Filters Reference

Documentation for `WFContentItemFilter` used in Find/Filter actions like FindPhotos, FindFiles, FindReminders, etc.

## Filter Structure

Filters are used in actions like `is.workflow.actions.filter.photos` to specify criteria for finding content.

### Basic Filter Template

```xml
<key>WFContentItemFilter</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFActionParameterFilterPrefix</key>
        <integer>1</integer>
        <key>WFContentPredicateBoundedDate</key>
        <false/>
        <key>WFActionParameterFilterTemplates</key>
        <array>
            <!-- Filter conditions go here -->
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFContentPredicateTableTemplate</string>
</dict>
```

---

## Operator Reference

Operators define the comparison type. These were discovered from Shortcuts internal JavaScript:

| Operator | Meaning | Use Case |
|----------|---------|----------|
| 2 | `is after` | Date is after a date/token |
| 3 | `>=` | Greater than or equal |
| 4 | `is` | Exact match |
| 5 | `is not` | Not equal |
| 8 | `begins with` | String prefix |
| 9 | `ends with` | String suffix |
| 99 | `contains` | String contains |
| 100 | `has any value` | Not empty |
| 101 | `does not have any value` | Is empty |
| 999 | `does not contain` | String not contains |
| 1000 | `is in the next` | Future date range |
| 1001 | `is in the last` | Past date range |
| 1002 | `is today` | Date is today |
| 1003 | `is between` | Date range |

---

## Unit Reference

Units are used with date/time and enumeration filters:

### Date Units (for operators 1000, 1001)

| Unit | Meaning |
|------|---------|
| 4 | years |
| 8 | months |
| 8192 | weeks |
| 16384 | days |

### Boolean/Enum Unit

| Unit | Context |
|------|---------|
| 4 | Standard unit for boolean and enumeration values |

---

## Filter Templates by Type

### Boolean Filter (e.g., Is a Screenshot)

```xml
<dict>
    <key>Operator</key>
    <integer>4</integer>
    <key>Property</key>
    <string>Is a Screenshot</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict>
        <key>Bool</key>
        <true/>
        <key>Unit</key>
        <integer>4</integer>
    </dict>
</dict>
```

### "Is Today" Date Filter

The `is today` operator (1002) does NOT require Values:

```xml
<dict>
    <key>Operator</key>
    <integer>1002</integer>
    <key>Property</key>
    <string>Date Taken</string>
    <key>Removable</key>
    <true/>
</dict>
```

### Find Calendar Events: Next Event After Now

For **Find Calendar Events** date predicates, use the date-specific operator codes. Do not use numeric comparison codes such as `3` (`>=`) for `Start Date` or `End Date`; Shortcuts can import that as a red invalid condition. The common "next event after now" pattern is:

- `Start Date is today`: `Operator = 1002`, `Values = {}`.
- `Start Date is after Current Date`: `Operator = 2`, `Values.Date = CurrentDate` token.
- Sort by `Start Date`, `Oldest First`, limit to `1`.

```xml
<dict>
    <key>Operator</key>
    <integer>1002</integer>
    <key>Property</key>
    <string>Start Date</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict/>
</dict>
<dict>
    <key>Operator</key>
    <integer>2</integer>
    <key>Property</key>
    <string>Start Date</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict>
        <key>Date</key>
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
```

### Find Health Samples "Start Date Is Today" Filter

Verified from a manually created iOS Shortcuts XML example and generated shortcut failures. **Find Health Samples** uses the same `WFContentPredicateTableTemplate` wrapper, but the Health sample kind is a locked `Type` predicate row backed by an enumeration state. Do not use top-level `WFHealthQuantityType`, and do not use a `Value` predicate row with `Values.String`; current iOS Shortcuts renders that as an editable text filter instead of the Health type picker.

Use observed Find Health Samples picker labels. Examples: `Steps`, `Sleep`, `Walking + Running Distance`, `Active Calories`, and `Exercise Minutes`. Do not use SDK-derived labels such as `Sleep Analysis`, `Active Energy`, `Active Energy Burned`, or `Apple Exercise Time`.

```xml
<key>WFContentItemFilter</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFActionParameterFilterPrefix</key>
        <integer>1</integer>
        <key>WFContentPredicateBoundedDate</key>
        <false/>
        <key>WFActionParameterFilterTemplates</key>
        <array>
            <dict>
                <key>Bounded</key>
                <true/>
                <key>Operator</key>
                <integer>4</integer>
                <key>Property</key>
                <string>Type</string>
                <key>Removable</key>
                <false/>
                <key>Values</key>
                <dict>
                    <key>Enumeration</key>
                    <dict>
                        <key>Value</key>
                        <string>Steps</string>
                        <key>WFSerializationType</key>
                        <string>WFStringSubstitutableState</string>
                    </dict>
                </dict>
            </dict>
            <dict>
                <key>Bounded</key>
                <true/>
                <key>Operator</key>
                <integer>1002</integer>
                <key>Property</key>
                <string>Start Date</string>
                <key>Removable</key>
                <false/>
                <key>Values</key>
                <dict>
                    <key>Number</key>
                    <string>7</string>
                    <key>Unit</key>
                    <integer>16</integer>
                </dict>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFContentPredicateTableTemplate</string>
</dict>
```

### "Is in the Last X" Date Filter

The `is in the last` operator (1001) requires Number and Unit:

```xml
<dict>
    <key>Operator</key>
    <integer>1001</integer>
    <key>Property</key>
    <string>Date Taken</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict>
        <key>Number</key>
        <integer>1</integer>
        <key>Unit</key>
        <integer>8192</integer>  <!-- weeks -->
    </dict>
</dict>
```

### "Is Between" Date Filter (verified against an Apple-built sample)

The `is between` operator (1003), **for date properties**, uses two value keys: `Date` for the lower bound (literal ISO date) and `AnotherDate` for the upper bound (token attachment, commonly `{Type: "CurrentDate"}` or another date variable):

```xml
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
```

⚠️ **Date filter `1003` ≠ numeric If conditional `1003`.** The If conditional version uses `WFNumberValue` + `WFAnotherNumber`. Filter-table version uses `Values.Date` + `Values.AnotherDate`. Do NOT copy one structure into the other.

### Enumeration Filter (e.g., Media Type)

**IMPORTANT**: Media Type only accepts: `Image`, `Video`, `Live Photo`
Do NOT use `Screenshot` - use the `Is a Screenshot` boolean filter instead.

```xml
<dict>
    <key>Operator</key>
    <integer>4</integer>
    <key>Property</key>
    <string>Media Type</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict>
        <key>Unit</key>
        <integer>4</integer>
        <key>Enumeration</key>
        <dict>
            <key>Value</key>
            <string>Image</string>
            <key>WFSerializationType</key>
            <string>WFStringSubstitutableState</string>
        </dict>
    </dict>
</dict>
```

### String Filter (e.g., Album name)

```xml
<dict>
    <key>Operator</key>
    <integer>4</integer>
    <key>Property</key>
    <string>Album</string>
    <key>Removable</key>
    <true/>
    <key>Values</key>
    <dict>
        <key>String</key>
        <string>Favorites</string>
        <key>Unit</key>
        <integer>4</integer>
    </dict>
</dict>
```

---

## FindPhotos Complete Example

Find screenshots taken today:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.filter.photos</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>FIND-PHOTOS-UUID</string>
        <key>WFContentItemFilter</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>WFActionParameterFilterPrefix</key>
                <integer>1</integer>
                <key>WFContentPredicateBoundedDate</key>
                <false/>
                <key>WFActionParameterFilterTemplates</key>
                <array>
                    <!-- Is a Screenshot = true -->
                    <dict>
                        <key>Operator</key>
                        <integer>4</integer>
                        <key>Property</key>
                        <string>Is a Screenshot</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict>
                            <key>Bool</key>
                            <true/>
                            <key>Unit</key>
                            <integer>4</integer>
                        </dict>
                    </dict>
                    <!-- Date Taken is today -->
                    <dict>
                        <key>Operator</key>
                        <integer>1002</integer>
                        <key>Property</key>
                        <string>Date Taken</string>
                        <key>Removable</key>
                        <true/>
                    </dict>
                </array>
            </dict>
            <key>WFSerializationType</key>
            <string>WFContentPredicateTableTemplate</string>
        </dict>
        <key>WFContentItemSortProperty</key>
        <string>Date Taken</string>
        <key>WFContentItemSortOrder</key>
        <string>Latest First</string>
    </dict>
</dict>
```

---

## DeletePhotos Action

**CRITICAL**: DeletePhotos uses `photos` as the parameter key, NOT `WFInput`:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.deletephotos</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>DELETE-UUID</string>
        <key>photos</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputName</key>
                <string>Photos</string>
                <key>OutputUUID</key>
                <string>FIND-PHOTOS-UUID</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```

---

## Available Filter Properties by Content Type

### Photos (WFPhotoMediaContentItem)

| Property | Type | Values |
|----------|------|--------|
| `Album` | Enumeration | Album names |
| `Media Type` | Enumeration | `Image`, `Video`, `Live Photo` |
| `Is a Screenshot` | Boolean | true/false |
| `Is Hidden` | Boolean | true/false |
| `Is Favorite` | Boolean | true/false |
| `Date Taken` | Date | Use date operators |
| `Creation Date` | Date | Use date operators |
| `Width` | Number | Pixels |
| `Height` | Number | Pixels |
| `Orientation` | Enumeration | `Up`, `Down`, `Left`, `Right` |
| `Photo Type` | Enumeration | `HDR`, `Panorama`, etc. |
| `Frame Rate` | Number | FPS (for videos) |
| `Duration` | Number | Seconds (for videos) |
| `Camera Make` | String | Camera manufacturer |
| `Camera Model` | String | Camera model |
| `File Extension` | String | e.g., `png`, `jpg` |

### Files (WFGenericFileContentItem)

| Property | Type | Values |
|----------|------|--------|
| `Name` | String | Filename |
| `File Extension` | String | Extension without dot |
| `Creation Date` | Date | Use date operators |
| `File Size` | Number | Bytes |
| `Last Modified Date` | Date | Use date operators |

### Notes (WFNoteContentItem)

| Property | Type | Supported Operators |
|----------|------|---------------------|
| `Name` | String | **Contains (99) only** — see critical note below |
| `Body` | String | Contains (99), Does Not Contain (999) |
| `Creation Date` | Date | Use date operators |
| `Last Modified Date` | Date | Use date operators |
| `Folder` | Enumeration | Folder names |

> **CRITICAL — Name filter operator:**
> Find Notes actions only support operator `99` (contains) for `Name` matching.
> Using operator `4` (is/exact match) produces an **empty result set at runtime** — the filter silently fails.
> Always use operator `99` when searching notes by name, even when you want an exact title match.

```xml
<!-- CORRECT: Name contains -->
<key>WFFilterOperator</key>
<integer>99</integer>

<!-- WRONG: Name is — fails silently, returns nothing -->
<key>WFFilterOperator</key>
<integer>4</integer>
```

### Reminders (WFReminderContentItem)

| Property | Type | Values |
|----------|------|--------|
| `Title` | String | Reminder title |
| `Is Completed` | Boolean | `{ Bool: <true/false> }` — no `Unit` key (Reminders Boolean filters don't use it) |
| `Is Flagged` | Boolean | Same shape as Is Completed |
| `Priority` | Enumeration | `None`, `Low`, `Medium`, `High` |
| `Due Date` | Date | Use date operators (1000–1003) |
| `Creation Date` | Date | Use date operators |
| `List` | Enumeration | List names — match via operator `4` with `Values.Enumeration` |

⚠️ **Reminders Boolean filters skip `Unit: 4`.** Photos Boolean filters (e.g. `Is a Screenshot`) do require `Values = { Bool: <true/false>, Unit: 4 }`. Reminders Boolean filters use `Values = { Bool: <true/false> }` only — no `Unit` field. Verified against an Apple-built sample.

**"Is Completed = Yes" (find completed reminders):**

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.filter.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>FIND-COMPLETED-UUID</string>
        <key>WFContentItemFilter</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>WFActionParameterFilterPrefix</key>
                <integer>1</integer>
                <key>WFActionParameterFilterTemplates</key>
                <array>
                    <dict>
                        <key>Operator</key>
                        <integer>4</integer>
                        <key>Property</key>
                        <string>Is Completed</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict>
                            <key>Bool</key>
                            <true/>
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

**"Is Completed = No" (find incomplete reminders):** same action, same structure, only `Values.Bool` flips to `<false/>`.

### Find vs Filter: `WFContentItemInputParameter`

Shortcuts.app shows two variants in the UI:
- **"Find X where"** — queries the system's content database for the type (e.g., all reminders, all photos) matching the filter.
- **"Filter X where"** — applies the filter to the output of a preceding action, trimming down an already-collected list.

Both variants use the **same action identifier** (`is.workflow.actions.filter.<type>`). The difference is the presence of `WFContentItemInputParameter`:

- **Find** = no `WFContentItemInputParameter`. The filter operates on the system database.
- **Filter** = `WFContentItemInputParameter` set to a token attachment wrapping the previous action's `ActionOutput` (typically with `OutputName` matching the type — e.g., `"Reminders"`, `"Photos"`, `"Files"`).

**Chained "Filter Reminders where Is Completed = No" on the output of a preceding "Find Reminders where Is Completed = Yes":**

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.filter.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>FILTER-INCOMPLETE-UUID</string>
        <key>WFContentItemFilter</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>WFActionParameterFilterPrefix</key>
                <integer>1</integer>
                <key>WFActionParameterFilterTemplates</key>
                <array>
                    <dict>
                        <key>Operator</key>
                        <integer>4</integer>
                        <key>Property</key>
                        <string>Is Completed</string>
                        <key>Removable</key>
                        <true/>
                        <key>Values</key>
                        <dict>
                            <key>Bool</key>
                            <false/>
                        </dict>
                    </dict>
                </array>
                <key>WFContentPredicateBoundedDate</key>
                <false/>
            </dict>
            <key>WFSerializationType</key>
            <string>WFContentPredicateTableTemplate</string>
        </dict>
        <key>WFContentItemInputParameter</key>
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputName</key>
                <string>Reminders</string>
                <key>OutputUUID</key>
                <string>PREVIOUS-FILTER-REMINDERS-UUID</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```

The same `WFContentItemInputParameter` chaining pattern applies to `filter.photos`, `filter.files`, `filter.notes`, `filter.calendarevents`, and every other `filter.*` action — wire it to a previous action's output via `Type=ActionOutput` and the filter becomes a "Filter X" instead of a "Find X".

**Reminders-specific filter example (verified from an Apple-built sample). Any-are-true OR of: List is "Reminders" OR Due Date is today OR Due Date is between a literal date and Current Date:**

**Reminders-specific filter example (verified from an Apple-built sample). Any-are-true OR of: List is "Reminders" OR Due Date is today OR Due Date is between a literal date and Current Date:**

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.filter.reminders</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>FIND-REMINDERS-UUID</string>
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

For the editing side (`is.workflow.actions.setters.reminders`), see [PARAMETER_TYPES.md → Reminders — Filter & Setter Schemas](PARAMETER_TYPES.md#reminders--filter--setter-schemas-definitive) for the complete list of property names and their value keys.

---

## Common Mistakes to Avoid

1. **Using `media_type="Screenshot"`** - This is WRONG. Use `Is a Screenshot` boolean filter instead.

2. **Using Operator 4 for "is today"** - WRONG. Use Operator 1002.

3. **Using `WFInput` for DeletePhotos** - WRONG. Use `photos` (lowercase).

4. **Adding Values to "is today" filter** - WRONG. Operator 1002 doesn't need Values.

5. **Forgetting OutputUUID reference** - When passing results between actions, you must reference the source action's UUID.

6. **Using Operator 4 (is) for Find Notes Name filter** - WRONG. Operator 4 produces empty results at runtime. Always use Operator 99 (contains) for Note name matching.
