# Icons and Colors

Use this guide whenever you need to set `WFWorkflowIconGlyphNumber` and `WFWorkflowIconStartColor`.

## Data Sources

This skill now includes local icon/color data:

- `data/shortcuts-official-glyph-mapping.json` - official 507 glyph number -> symbol name mapping.
- `data/shortcuts-glyph-synonyms.json` - natural-language synonym map for all 507 glyphs.
- `data/shortcuts-icon-colors.json` - 15 Shortcuts icon colors (name, hex, integer values, aliases).

## Resolver Script

Use the resolver for every shortcut unless the user explicitly gives both icon and color integers:

```bash
python3 scripts/select_shortcut_icon_color.py --prompt "${USER_PROMPT}"
```

Optional overrides:

```bash
python3 scripts/select_shortcut_icon_color.py \
  --prompt "Create a shortcut for logging expenses" \
  --icon "dollar sign" \
  --color "gold"
```

Resolver output includes:

- `icon.glyph_number`
- `icon.symbol_name`
- `color.value`
- `color.name`
- `wf_workflow_icon.WFWorkflowIconGlyphNumber`
- `wf_workflow_icon.WFWorkflowIconStartColor`

Use those values directly in the root plist.

## Explicit Icon Selection

The resolver supports explicit icon requests in natural language, including:

- Glyph numbers: `icon 59819`, `glyph #61566`
- Symbol names: `use paperAirplane icon`
- Synonyms: `use robot icon`, `use terminal icon`, `use expense icon`

## Automatic Icon Selection

If no icon is specified, the resolver infers one from the full prompt using:

- Official symbol names
- Synonym matching
- Intent-focused boosts (weather, finance, translation, developer, messaging, etc.)
- Deterministic fallback to `61440` (`shortcuts`) for generic prompts

## Explicit Color Selection

Color can be selected with:

- Color names (`blue`, `purple`, `gold`, etc.)
- Synonyms (`gray`/`grey`, `turquoise`, etc.)
- Integer values (`463140863`, `-3831826433`)
- Hex values (`#24BAF7`) mapped to nearest palette color

## Automatic Color Selection

If no color is specified, color is inferred from prompt themes and falls back to Teal (`431817727`) when ambiguous.

## Supported Color Palette

| Name | Hex | Canonical value |
|---|---|---:|
| Red | `#F36F74` | `4282601983` |
| Orange | `#FF8E73` | `4251333119` |
| Yellow | `#F8AE5F` | `4271458815` |
| Gold | `#E8CA45` | `4274264319` |
| Green | `#53CD6B` | `4292093695` |
| Teal | `#57CFB4` | `431817727` |
| Cyan | `#5ACCDE` | `1440408063` |
| Blue | `#24BAF7` | `463140863` |
| Navy | `#5874CA` | `946986751` |
| Purple | `#9164C7` | `2071128575` |
| Lavender | `#C085E6` | `3679049983` |
| Pink | `#F694D8` | `3980825855` |
| Gray | `#9099A3` | `255` |
| Sage | `#9DA79D` | `3031607807` |
| Tan | `#A49995` | `2846468607` |
