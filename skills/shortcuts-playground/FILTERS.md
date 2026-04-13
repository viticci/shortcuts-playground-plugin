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
| `Is Completed` | Boolean | true/false |
| `Priority` | Enumeration | `None`, `Low`, `Medium`, `High` |
| `Due Date` | Date | Use date operators |
| `Creation Date` | Date | Use date operators |
| `List` | Enumeration | List names |

---

## Common Mistakes to Avoid

1. **Using `media_type="Screenshot"`** - This is WRONG. Use `Is a Screenshot` boolean filter instead.

2. **Using Operator 4 for "is today"** - WRONG. Use Operator 1002.

3. **Using `WFInput` for DeletePhotos** - WRONG. Use `photos` (lowercase).

4. **Adding Values to "is today" filter** - WRONG. Operator 1002 doesn't need Values.

5. **Forgetting OutputUUID reference** - When passing results between actions, you must reference the source action's UUID.

6. **Using Operator 4 (is) for Find Notes Name filter** - WRONG. Operator 4 produces empty results at runtime. Always use Operator 99 (contains) for Note name matching.
