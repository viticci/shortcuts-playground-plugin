# Shortcut Plist Format

Complete documentation of the `.shortcut` file structure.

**Related docs:**
- [ACTIONS.md](./ACTIONS.md) - Action identifiers and parameters
- [FILTERS.md](./FILTERS.md) - Content filters for Find/Filter actions
- [PARAMETER_TYPES.md](./PARAMETER_TYPES.md) - All parameter value types
- [VARIABLES.md](./VARIABLES.md) - Variable references and outputs
- [CONTROL_FLOW.md](./CONTROL_FLOW.md) - Conditionals, loops, menus

## Root Structure

A `.shortcut` file is a binary plist (can be written as XML, then converted). The root is a dictionary with these keys:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- REQUIRED -->
    <key>WFWorkflowActions</key>
    <array>
        <!-- Array of action dictionaries -->
    </array>

    <!-- REQUIRED - Version info -->
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowClientRelease</key>
    <string>26A0000a</string>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>

    <!-- REQUIRED - Icon -->
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>61440</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>431817727</integer>
    </dict>

    <!-- OPTIONAL - Shortcut name (displayed in app) -->
    <key>WFWorkflowName</key>
    <string>My Shortcut</string>

    <!-- OPTIONAL - Usually empty arrays -->
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>

    <!-- OPTIONAL - Input content types accepted -->
    <key>WFWorkflowInputContentItemClasses</key>
    <array>
        <string>WFStringContentItem</string>
        <string>WFURLContentItem</string>
        <!-- ... more content types ... -->
    </array>
</dict>
</plist>
```

## Root Keys Reference

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `WFWorkflowActions` | Array | Yes | Array of action dictionaries |
| `WFWorkflowClientVersion` | String | Yes | Client version (e.g., "2700.0.4") |
| `WFWorkflowClientRelease` | String | No | Release identifier |
| `WFWorkflowMinimumClientVersion` | Integer | Yes | Minimum version number (900+) |
| `WFWorkflowMinimumClientVersionString` | String | Yes | String version of minimum |
| `WFWorkflowIcon` | Dict | Yes | Icon configuration |
| `WFWorkflowName` | String | No | Display name |
| `WFWorkflowHasOutputFallback` | Boolean | No | Has output fallback |
| `WFWorkflowImportQuestions` | Array | No | Import-time questions |
| `WFWorkflowInputContentItemClasses` | Array | No | Accepted input types |
| `WFWorkflowOutputContentItemClasses` | Array | No | Output types |
| `WFWorkflowTypes` | Array | No | Workflow types |
| `WFWorkflowHasShortcutInputVariables` | Boolean | No | True if shortcut uses input variables |
| `WFWorkflowIsDisabledOnLockScreen` | Boolean | No | Prevents execution from Lock Screen |
| `WFWorkflowQuickActionSurfaces` | Array | No | Surfaces where shortcut appears as quick action |

## Icon Configuration

```xml
<key>WFWorkflowIcon</key>
<dict>
    <key>WFWorkflowIconGlyphNumber</key>
    <integer>61440</integer>
    <key>WFWorkflowIconStartColor</key>
    <integer>431817727</integer>
</dict>
```

Use the resolver and data files documented in [ICONS_AND_COLORS.md](./ICONS_AND_COLORS.md) to pick icon values.

### Required Icon Keys

| Key | Type | Required | Notes |
|---|---|---|---|
| `WFWorkflowIconGlyphNumber` | Integer | Yes | One of the official 507 Shortcuts glyph codes |
| `WFWorkflowIconStartColor` | Integer | Yes | One of the 15 Shortcuts palette colors (canonical or alias integer) |

### Common Glyph Numbers

| Glyph | Number | Description |
|---|---:|---|
| shortcuts | `61440` | Default/fallback app icon |
| cloud | `59714` | Weather/cloud workflows |
| map | `61444` | Navigation/location workflows |
| checklist | `61587` | Tasks/todo workflows |
| dollarSign | `59395` | Finance/expense workflows |
| command | `61529` | Developer/terminal workflows |
| robot | `61566` | AI assistant workflows |
| paperAirplane | `59836` | Send/share workflows |

### Color Values (Shortcuts Palette)

Colors are 32-bit integers. Canonical values:

| Color | Value | Hex |
|---|---:|---|
| Red | `4282601983` | `#F36F74` |
| Orange | `4251333119` | `#FF8E73` |
| Yellow | `4271458815` | `#F8AE5F` |
| Gold | `4274264319` | `#E8CA45` |
| Green | `4292093695` | `#53CD6B` |
| Teal | `431817727` | `#57CFB4` |
| Cyan | `1440408063` | `#5ACCDE` |
| Blue | `463140863` | `#24BAF7` |
| Navy | `946986751` | `#5874CA` |
| Purple | `2071128575` | `#9164C7` |
| Lavender | `3679049983` | `#C085E6` |
| Pink | `3980825855` | `#F694D8` |
| Gray | `255` | `#9099A3` |
| Sage | `3031607807` | `#9DA79D` |
| Tan | `2846468607` | `#A49995` |

## Action Structure

Each action in `WFWorkflowActions` is a dictionary:

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.showresult</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <!-- Action-specific parameters -->
        <key>UUID</key>
        <string>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</string>
        <!-- ... more parameters ... -->
    </dict>
</dict>
```

### Action Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `WFWorkflowActionIdentifier` | String | Yes | Action identifier (e.g., `is.workflow.actions.showresult`) |
| `WFWorkflowActionParameters` | Dict | Yes | Action configuration |

### Common Parameter Keys

| Key | Type | Description |
|-----|------|-------------|
| `UUID` | String | Unique ID for referencing this action's output |
| `GroupingIdentifier` | String | Links control flow actions (repeat, if, menu) |
| `WFControlFlowMode` | Integer | 0=start, 1=middle, 2=end |

## Input Content Item Classes

These define what input types the shortcut accepts:

```xml
<key>WFWorkflowInputContentItemClasses</key>
<array>
    <string>WFAppStoreAppContentItem</string>
    <string>WFArticleContentItem</string>
    <string>WFContactContentItem</string>
    <string>WFDateContentItem</string>
    <string>WFEmailAddressContentItem</string>
    <string>WFGenericFileContentItem</string>
    <string>WFImageContentItem</string>
    <string>WFiTunesProductContentItem</string>
    <string>WFLocationContentItem</string>
    <string>WFDCMapsLinkContentItem</string>
    <string>WFAVAssetContentItem</string>
    <string>WFPDFContentItem</string>
    <string>WFPhoneNumberContentItem</string>
    <string>WFRichTextContentItem</string>
    <string>WFSafariWebPageContentItem</string>
    <string>WFStringContentItem</string>
    <string>WFURLContentItem</string>
</array>
```

## Binary vs XML Plist

Shortcuts are stored as binary plists but can be created as XML:

```bash
# Convert XML to binary (optional - signing handles this)
plutil -convert binary1 MyShortcut.shortcut

# Convert binary to XML (for inspection)
plutil -convert xml1 MyShortcut.shortcut
```

The `shortcuts sign` command accepts both formats.

## Complete Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.gettext</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
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
                                <string>11111111-1111-1111-1111-111111111111</string>
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
    <string>Hello World</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```
