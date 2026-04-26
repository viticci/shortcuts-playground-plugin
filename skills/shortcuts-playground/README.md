# Shortcuts Generator Skill

A skill for AI-assisted generation of macOS/iOS Shortcuts. It produces valid `.shortcut` plist files that can be signed and imported into Apple's Shortcuts app.

## Documentation Entry Points

- Start with [SKILL.md](SKILL.md) for workflow and high-level rules.
- Treat [BEST_PRACTICES.md](BEST_PRACTICES.md) as mandatory policy.
- Use [ACTIONS.md](ACTIONS.md), [APPINTENTS.md](APPINTENTS.md), and [THIRD_PARTY_ACTIONS.md](THIRD_PARTY_ACTIONS.md) as the identifier references.
- Use [HEALTHKIT.md](HEALTHKIT.md) for iOS/iPadOS Health actions.
- If a rule appears in multiple docs, treat [BEST_PRACTICES.md](BEST_PRACTICES.md) as policy authority.

## Installation

### 1. Create the skills directory (if it doesn't exist)

```bash
mkdir -p ~/.claude/skills
```

### 2. Clone or copy this repository

Copy or symlink the skill directory into `~/.claude/skills/shortcuts-generator/`.

### 3. Verify the installation

Your directory structure should include:

```
~/.claude/
└── skills/
    └── shortcuts-generator/
        ├── SKILL.md
        ├── README.md
        ├── ACTIONS.md
        ├── APPINTENTS.md
        ├── BEST_PRACTICES.md
        ├── CONTROL_FLOW.md
        ├── EXAMPLES.md
        ├── FILTERS.md
        ├── HEALTHKIT.md
        ├── ICONS_AND_COLORS.md
        ├── PARAMETER_TYPES.md
        ├── PLIST_FORMAT.md
        ├── THIRD_PARTY_ACTIONS.md
        ├── TOOLKIT_SNAPSHOT.md
        ├── VARIABLES.md
        ├── scripts/
        └── data/
```

### 4. Restart Claude Code

The skill will be automatically detected on the next conversation.

## Usage

Once installed, simply ask Claude Code to create a shortcut:

- "Create a shortcut that shows the current weather"
- "Build a shortcut that asks for text input and shows it"
- "Make a shortcut that opens Safari and navigates to a URL"

Claude will generate the plist XML, write it to a `.shortcut` file, and sign it so you can import it directly into the Shortcuts app.

## Icon and Color Selection

The skill now supports full shortcut icon customization from natural language:

- Explicit icon selection (`robot icon`, `paper airplane icon`, `glyph 59819`)
- Explicit color selection (`purple`, `gray`, `#24BAF7`, signed/unsigned integer values)
- Automatic icon inference when no icon is requested
- Automatic color inference when no color is requested

Resolver command:

```bash
python3 scripts/select_shortcut_icon_color.py --prompt "Build a weather shortcut"
```

## Preflight Validation

The skill uses a lightweight validation loop that runs a local validator and regenerates/fixes until the shortcut passes structural checks. The validator uses the bundled action-ID allowlist (`data/toolkit-v63-tool-ids.json`) plus the markdown references in this directory.

## Bundled action-ID snapshot

To make the skill portable for distribution, the action-ID allowlist is prepackaged as `data/toolkit-v63-tool-ids.json`. The validator reads it directly — no extra setup on the user's machine.

## What's Included

| File | Description |
|------|-------------|
| [`SKILL.md`](SKILL.md) | Skill definition with quick start guide |
| [`ACTIONS.md`](ACTIONS.md) | WF*Action identifiers and parameters |
| [`APPINTENTS.md`](APPINTENTS.md) | AppIntent actions (macOS ToolKit v63 + backups) |
| [`PARAMETER_TYPES.md`](PARAMETER_TYPES.md) | Parameter value types and serialization formats |
| [`VARIABLES.md`](VARIABLES.md) | Variable reference system |
| [`CONTROL_FLOW.md`](CONTROL_FLOW.md) | Repeat, Conditional, Menu patterns |
| [`FILTERS.md`](FILTERS.md) | Content filters for Find/Filter actions |
| [`HEALTHKIT.md`](HEALTHKIT.md) | iOS/iPadOS Health action schemas and bundled anonymized XML examples |
| [`EXAMPLES.md`](EXAMPLES.md) | Complete working examples |
| [`BEST_PRACTICES.md`](BEST_PRACTICES.md) | Mandatory build guidelines |
| [`ICONS_AND_COLORS.md`](ICONS_AND_COLORS.md) | Icon glyph and color selection workflow |
| [`THIRD_PARTY_ACTIONS.md`](THIRD_PARTY_ACTIONS.md) | Third-party actions (ToolKit + backups) |
| [`TOOLKIT_SNAPSHOT.md`](TOOLKIT_SNAPSHOT.md) | Bundled ToolKit v63 metadata package and field coverage |
| `scripts/select_shortcut_icon_color.py` | Natural-language icon/color resolver |
| `scripts/validate_shortcut.py` | Preflight validator used by the validation loop |
| `scripts/generate_healthkit_reference.py` | Generates the local HealthKit type/unit reference |
| `data/shortcuts-official-glyph-mapping.json` | Official 507 glyph mapping |
| `data/shortcuts-glyph-synonyms.json` | Synonym map for all 507 glyphs |
| `data/shortcuts-icon-colors.json` | Shortcuts 15-color palette with aliases |
| `data/toolkit-v63-tool-ids.json` | Bundled ToolKit v63 action-ID allowlist |
| `data/healthkit-ios26.2-reference.json` | HealthKit types, category values, workout types, and units |

## Requirements

- macOS with the `shortcuts` CLI tool (included with macOS)
- Claude Code CLI

## How Skills Work

Skills are collections of markdown files that provide Claude Code with specialized knowledge and capabilities. The `SKILL.md` file defines:

- **name**: Identifier for the skill
- **description**: When to use this skill (triggers automatic invocation)
- **allowed-tools**: Which tools Claude can use when the skill is active

When you ask Claude Code to do something that matches the skill's description, it automatically loads the skill's documentation to provide accurate, specialized assistance.

## License

MIT
