# HealthKit Shortcuts Reference

Health actions are iOS/iPadOS-first. macOS Shortcuts syncs their XML but cannot fully configure the Health UI. Prefer this file and the bundled reference data over guesses.

## Evidence

Primary syntax source: bundled anonymized iOS Shortcuts XML examples captured while building this reference. User-specific shortcut names, source paths, and iCloud locations are intentionally omitted from the distributed skill.

- Find Health Samples XML example: `WFContentItemFilter` with a locked `Type is ...` predicate row, date filter row, and sample output wiring.
- Log Health Sample quantity XML example: Caffeine quantity log.
- Log Health Sample category XML example: category sample with no visible Value row in the editor.
- Log Health Sample category-value XML example: category sample with an explicit enum value picker.
- Get Details of Health Sample XML example: `WFContentItemPropertyName`, `WFInput`.
- Log Workout XML evidence: action identifier sync/export evidence only; the available export was UUID-only before a full workout configuration was captured.

Exhaustive value source: iPhoneOS 26.2 HealthKit headers plus ActionKit `WFHealthKitConstants.plist`, generated into `data/healthkit-ios26.2-reference.json`.

## Actions

### Find Health Samples

Identifier: `is.workflow.actions.filter.health.quantity`

Required parameters:

- `UUID`
- `WFContentItemFilter`: `WFContentPredicateTableTemplate` containing a non-removable `Type` predicate row. Use `Values.Enumeration` with `WFSerializationType = WFStringSubstitutableState` and the Find Health Samples picker label, for example `Caffeine`, `Steps`, `Sleep`, `Walking + Running Distance`, or `Exercise Minutes`.

Optional:

- `WFContentItemLimitEnabled`: boolean.
- `WFContentItemLimitNumber`: required when limit is enabled.

Do not use `WFHealthQuantityType`. That top-level key was previously documented here, but current iOS Shortcuts imports it as an inert plist field. Do not use a `Value` predicate row with `Values.String` either: that imports as an editable text filter (`Value is Step Count`) instead of the Health type picker (`Type is Steps`).

Observed filter shape:

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

`Operator` `4` is `is` for the `Type` row. `Operator` `1002` is the observed `Start Date is today` row; manual iOS exports include `Values.Number = "7"` and `Values.Unit = 16` on that row. Use `WFActionParameterFilterPrefix = 1` for All when combining sample-kind and date rows.

Output name observed in downstream wiring: `Health Samples`.

### Health Summary Math

When building dashboards that sum Health samples, do not infer units from HealthKit SDK names. Use the Shortcuts picker labels and the details returned by Shortcuts:

- **Exercise**: the Find Health Samples picker label is `Exercise Minutes`, not `Apple Exercise Time` or `Exercise Time`.
- **Sleep**: the Find Health Samples picker label is `Sleep`, not `Sleep Analysis`. Sleep is a category sample, and `Duration` values may display as clock-style durations such as `28:09`, `3:31`, or `1:06:52`.
- **Sleep duration math**: `Get Details of Health Sample` → `Duration` should be treated as a duration. When that value is coerced through Math, treat it as seconds. Divide by `3600` for decimal hours, or divide by `60` and label the result as minutes. Never divide sleep duration by `60` and label the result as hours.
- **Sleep date ranges**: for "last night" summaries, do not use only `Start Date is today`; sleep often starts before midnight. Prefer an explicit last-night range (for example, yesterday evening through this morning) or tell the user the range needs confirmation.
- **Walking + Running Distance**: do not assume `Value` is meters and divide by `1000`. Shortcuts returns `Value` in the action's displayed Health unit. Sum values directly, or use Convert Measurement with an explicit source unit and target unit.

### Get Details of Health Sample

Identifier: `is.workflow.actions.properties.health.quantity`

Required parameters:

- `UUID`
- `WFContentItemPropertyName`
- `WFInput`

Detail names exposed by the iOS picker:

`Type`, `Value`, `Unit`, `Start Date`, `End Date`, `Duration`, `Source`, `Name`.

Observed wiring:

```xml
<key>WFContentItemPropertyName</key>
<string>Value</string>
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputName</key>
        <string>Health Samples</string>
        <key>OutputUUID</key>
        <string>FIND-HEALTH-SAMPLES-UUID-HERE</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

`WFInput` must reference Find Health Samples or a variable sourced from Find Health Samples. Log Health Sample output is also a Health sample source.

### Log Health Sample

Identifier: `is.workflow.actions.health.quantity.log`

Required parameters:

- `UUID`
- `WFQuantitySampleType`
- A value field: usually `WFQuantitySampleQuantity`; enum category samples can also include `WFCategorySampleEnumeration`.

Quantity sample, Caffeine:

```xml
<key>WFQuantitySampleType</key>
<string>Caffeine</string>
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

Category sample with no visible value row, Bloating:

```xml
<key>WFQuantitySampleType</key>
<string>Bloating</string>
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>10</string>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Category sample with enum value, Cervical Mucus Quality:

```xml
<key>WFQuantitySampleType</key>
<string>Cervical Mucus Quality</string>
<key>WFCategorySampleEnumeration</key>
<string>Dry</string>
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>10</string>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Optional date fields:

- `WFQuantitySampleDate`
- `WFSampleEndDate`

These can use `WFTextTokenAttachment` with `{Type: CurrentDate}`.

### Log Workout

Identifier: `is.workflow.actions.health.workout.log`

The currently available XML evidence proves the identifier but not a fully configured parameter dictionary. The generator and validator support the schema below from action metadata conventions and HealthKit workout values; treat a future full iOS export as higher priority if it conflicts.

Required:

- `UUID`
- `WFWorkoutReadableActivityType`: Shortcuts UI label, for example `Running`, `Walking`, `Cycling`.

Optional:

- `WFWorkoutDate`
- `WFWorkoutDuration`: `WFQuantityFieldValue`, normally `min`.
- `WFWorkoutCaloriesQuantity`: `WFQuantityFieldValue`, normally `kcal`.
- `WFWorkoutDistanceQuantity`: `WFQuantityFieldValue`, normally `m`, `km`, `mi`, etc.

Generated shape:

```xml
<key>WFWorkoutReadableActivityType</key>
<string>Running</string>
<key>WFWorkoutDate</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentDate</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
<key>WFWorkoutDuration</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>30</string>
        <key>Unit</key>
        <string>min</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

## Values

`data/healthkit-ios26.2-reference.json` contains:

- 120 quantity types.
- 70 category types.
- 17 category value enum families, covering 61 explicit enum values.
- 84 workout activity types.
- 46 ActionKit Health unit strings.

Use `shortcut_label_guess` as a fallback, but prefer action-specific observed labels when present. For Find Health Samples, prefer `observed_find_samples_labels`; for example, `HKQuantityTypeIdentifierStepCount` is `Steps`, `HKCategoryTypeIdentifierSleepAnalysis` is `Sleep`, `HKQuantityTypeIdentifierActiveEnergyBurned` is `Active Calories`, and `HKQuantityTypeIdentifierAppleExerciseTime` is `Exercise Minutes` in the Find Health Samples picker. Other Health action contexts may use labels such as `Step Count`; for active energy burned, use `Active Calories`, not `Active Energy` or `Active Energy Burned`.

Known bundled label override:

- `HKCategoryTypeIdentifierGeneralizedBodyAche`: Shortcuts picker label is `Body and Muscle Ache`, not the SDK-derived `Generalized Body Ache`.

The validator checks Health sample types, Find Health Samples `Type` filter values, workout activity types, category enum values, and units against this bundled reference when it is available.

## Safety

Do not run Health-writing shortcuts only to test syntax. Build, inspect, validate, export, and import them; leave actual Health writes to the user unless they explicitly ask to run the shortcut.
