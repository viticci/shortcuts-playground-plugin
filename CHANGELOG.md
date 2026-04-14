# Changelog

All notable changes to the Shortcuts Playground plugin are documented in this file. The skill-level changelog lives at `skills/shortcuts-playground/CHANGELOG.md`.

## [1.4.1] — 2026-04-14

### Added (docs-only patch, verified against a second Apple-built sample)

Federico provided `Reminders Complete.xml` covering the `Is Completed` filter in both its Find and Filter forms. Two new patterns landed in the docs as a result:

- **`skills/shortcuts-playground/FILTERS.md`** — expanded the Reminders Boolean filter section with verbatim templates for `Is Completed = Yes` and `Is Completed = No`. Documented the key distinction that **Reminders Boolean filters do NOT need `Unit: 4`** — that's a Photos-filter requirement and does not apply to Reminders. Added a new top-level section **"Find vs Filter: `WFContentItemInputParameter`"** explaining that `is.workflow.actions.filter.<type>` covers both UI variants; the presence of `WFContentItemInputParameter` (wrapping a previous action's `ActionOutput`) turns a "Find" into a chained "Filter" that operates on upstream output instead of the system database. Applies uniformly to `filter.photos`, `filter.files`, `filter.notes`, `filter.calendarevents`, etc. — not just Reminders.
- **`skills/shortcuts-playground/PARAMETER_TYPES.md`** — added a cross-reference from the Reminders schema section to the new FILTERS.md Is-Completed template and Find-vs-Filter section. Flags the "Reminders drop `Unit`, Photos require it" Boolean divergence.

No code, validator, agent, or command changes in this patch — it's pure documentation closing the gap that the v1.4.0 Rescheduler build exposed (the agent correctly refused to guess a Boolean filter schema for Is Completed because it wasn't documented).

## [1.4.0] — 2026-04-14

### Fixed — all the blockers surfaced by session 5174fcb1

Federico ran a real "Rescheduler" build and the session exposed five distinct problems:

1. **Docs gap on Reminders schema.** The `is.workflow.actions.setters.reminders` action was allowlisted but had no documented parameter schema. The first subagent escalated per the v1.2.0 rule; the main thread then spent 20+ tool calls rediscovering the schema by grepping user paths.
2. **Agent went down the `UpdateReminderAppIntent` dead end first.** The docs didn't tell it to prefer the classic WF action over the newer AppIntent.
3. **Draft/output split.** The agent wrote the draft to `~/Documents/Shortcuts Playground/drafts/` (the hardcoded fallback) instead of resolving `CLAUDE_PLUGIN_OPTION_OUTPUT_DIR` to the user-configured output directory. The signed file then landed in the correct dir (because `sign-shortcut` resolves the env var at shell level), but the draft was orphaned elsewhere.
4. **Subagent stopped after drafting.** It finished validate → fix → revalidate, but never called `sign-shortcut`. The main thread had to sign manually.
5. **Main thread did open-ended research.** When the subagent escalated, the main thread grepped `~/Documents/Shortcuts Playground`, `~/Agent`, `~/.claude/skills/shortcuts-playground` (deleted), and the plugin dir — wandering into user paths that shouldn't have been in scope.

### Added — Reminders recipes verified against an Apple-built sample

Federico provided a second sample shortcut (`Reminder Edits.xml`) that exercises `filter.reminders` with date operators plus `setters.reminders` applied to 13 different property names. That sample is now the ground truth. New content:

- **`skills/shortcuts-playground/PARAMETER_TYPES.md` → new section "Reminders — Filter & Setter Schemas (DEFINITIVE)"**
  - Full `filter.reminders` template structure (`Operator`/`Property`/`Values`, distinguished from If conditional templates).
  - Date operator codes: `1002` ("is today", empty `Values`), `1003` ("is between", `Values.Date` literal + `Values.AnotherDate` token attachment). Explicitly flags the difference from If conditional `1003` (which uses `WFNumberValue`/`WFAnotherNumber`).
  - Full `setters.reminders` template with `Mode`, `UUID`, `WFContentItemPropertyName`, chained `WFInput`, and the verified per-property value-key table: Due Date, Title, Parent Reminder, Subtasks, URL, Notes, Tags, When Messaging Person, Images, Priority, Is Completed, Is Flagged, List. Notes that `List` is the only property taking a plain string (not a token attachment).
  - Verbatim templates for single-property set, chained multi-property set, and the common "reschedule" pattern from a date-picker variable.
  - Anti-pattern list: never use `UpdateReminderAppIntent`, never chain setters without `WFInput`, never wrap `WFReminderContentItemList` in a token attachment, never conflate filter `1003` with If conditional `1003`.

- **`skills/shortcuts-playground/FILTERS.md` — new "Is Between Date Filter" template** with the `Values.Date` + `Values.AnotherDate` structure, plus a verbatim Reminders-specific multi-row filter example.

- **`skills/shortcuts-playground/APPINTENTS.md`** — leading warning on the Reminders section explicitly directing builds away from `UpdateReminderAppIntent` and toward the documented `is.workflow.actions.setters.reminders` path.

- **`skills/shortcuts-playground/SKILL.md` new rule 56** — summarizes the Reminders-always-use-setters rule and the filter date operator codes, with a pointer to the PARAMETER_TYPES.md section.

### Changed — agent behavior hardening

**`agents/shortcut-builder.md`:**
- **New step 0: "Resolve the output directory FIRST."** The agent must run a Bash command to echo the resolved absolute path from `${CLAUDE_PLUGIN_OPTION_OUTPUT_DIR:-$HOME/Documents/Shortcuts Playground}` before doing anything else, then use that literal path for every subsequent Write/Edit/Bash call. Eliminates the draft-path split bug.
- **New step 10: "Verify + report (MANDATORY)."** The agent is not done until `ls -la "<OUTPUT_DIR>/<name>.shortcut"` succeeds with non-zero file size. "Validation passed" alone is not a valid terminal state — the agent must sign and verify before declaring the build complete.
- **Explicit allowed-search-paths rule.** The agent may Grep/Glob/Read only inside `${CLAUDE_PLUGIN_ROOT}` and the specific file being written inside `<OUTPUT_DIR>`. Every other path — `~/Documents` broadly, `~/Agent`, `~/.claude`, `~/Library`, `/Applications`, `/System` — is off limits. If the answer isn't in the plugin directory, escalate to the user per the validation gates; do not go hunting.

**`commands/build.md`:**
- **Orchestrator research scope rule.** When the subagent escalates, the main thread may read only the plugin directory and the specific draft file the agent just wrote. It may NOT grep `~/Documents` broadly, `~/Agent`, `~/.claude/skills`, `~/.claude/plugins`, `~/.claude/projects`, `~/Library`, `/Applications`, or `/System`. If the plugin directory doesn't have the answer, the main thread relays the escalation to the user verbatim instead of improvising.
- **No archive mining.** The plugin's output directory contains user-generated content, not curated examples. It may include dead ends, deprecated patterns, or quality issues. The canonical reference is the plugin directory itself. If a reference corpus is ever needed, it will be an explicit opt-in `reference/` subdirectory, not implicit archive mining.
- **No binary inspection of signed shortcuts.** Signed files are Apple Encrypted Archives (`AEA1`); they can't be read as plaintext plists via `plutil`/`xxd`/`file`. If you need to see the structure, read the unsigned XML in the drafts folder instead.

### Verified

- `shortcuts-playground-selftest` passes.
- `claude plugin validate` passes on both plugin.json and the dev marketplace.json.
- The Apple-built `Reminder Edits` sample produces **zero filter/setter schema errors** — only the expected convention-only errors (missing Comment blocks, unused input content classes).
- `sign-shortcut --output-dir` flag correctly wins over `CLAUDE_PLUGIN_OPTION_OUTPUT_DIR` env var: flag writes to the flag path, env-var path stays empty. Both produce signed files with `AEA1` magic bytes.
- `PostToolUse` auto-validate hook fires on every Write that produces a Shortcuts plist; verified via an ephemeral trace log in a fresh headless session (trace removed before commit).
- The Rescheduler prompt from session 5174fcb1 — re-run on v1.4.0 — [see test matrix below].

## [1.3.0] — 2026-04-13

### Fixed (factually wrong conditional documentation)

The previous condition code documentation had multiple errors that propagated into both the validator and the agent's authoring instructions. Verified against an Apple-built sample shortcut covering every condition code and the multi-condition pattern. Specific corrections:

- **Codes 0/1/3 had wrong UI labels.** Old docs said `0 = Equals`, `1 = Does Not Equal`, `3 = Is Less Than`. Ground truth: `0 = is less than`, `1 = is less than or equal to`, `3 = is greater than or equal to`. Code `2` was already correct (`is greater than`). There is no numeric "equals" code in the modern conditional action.
- **The "implicit input for numeric conditions" rule was wrong.** Every conditional in the Apple sample — numeric, string, and existence — sets an explicit `WFInput` as a `Type=Variable` wrapper. The previous claim that codes 0–3 use implicit input and that "the validator has a gap" was the actual bug.
- **Code `1003` (`is between`) was undocumented.** Now documented: requires both `WFNumberValue` (lower bound, literal) and `WFAnotherNumber` (upper bound, token attachment that can hold a literal or a variable).
- **Multi-condition If (`Any are true` / `All are true`) was forbidden as "compound conditionals not supported".** Apple's modern Shortcuts uses them and so should generated shortcuts. Now fully documented in CONTROL_FLOW.md as the `WFConditions` + `WFContentPredicateTableTemplate` pattern with `WFActionParameterFilterPrefix` (`0` = Any, `1` = All) and `WFActionParameterFilterTemplates` array of per-row condition templates.

### Validator changes (`scripts/validate_shortcut.py`)

- `STRING_CONDITION_CODES` expanded from `{4, 99}` to `{4, 5, 8, 9, 99, 999}`.
- `NUMBER_CONDITION_CODES` expanded from `{2}` to `{0, 1, 2, 3, 1003}`.
- New `EXISTENCE_CONDITION_CODES = {100, 101}` — codes that take only `WFInput` and reject both `WFConditionalActionString` and `WFNumberValue`.
- New `ALL_CONDITION_CODES` aggregate; the validator now rejects unknown codes outright.
- `if not cond` truthiness check replaced with `if cond is None` (Python's `not 0` was treating valid code 0 as missing — the actual root cause behind the "validator gap" item that the old docs warned about).
- Multi-condition Ifs (`WFConditions`) are now a recognized pattern instead of an error. The validator checks: (a) `WFSerializationType` must be `WFContentPredicateTableTemplate`, (b) `WFActionParameterFilterPrefix` must be `0` (Any) or `1` (All), (c) `WFActionParameterFilterTemplates` must be a non-empty list, (d) each template has its own `WFCondition` + `WFInput` + appropriate literal field, (e) the action does NOT also set top-level `WFCondition` / `WFInput` (mutually exclusive with `WFConditions`).
- Per-code validation now enforces: code 1003 needs `WFAnotherNumber`; existence codes 100/101 must NOT set literal fields; all codes uniformly require explicit `WFInput` as a `Type=Variable` wrapper.

### Documentation changes

- **`skills/shortcuts-playground/CONTROL_FLOW.md`** — entire conditional section rewritten. New definitive code table (13 codes including 1003), uniform `WFInput` rule, `is between` template, full multi-condition If template with rules for each row inside `WFActionParameterFilterTemplates`. Anti-pattern list updated to flag mixing single-condition and multi-condition fields.
- **`skills/shortcuts-playground/BEST_PRACTICES.md`** — conditional bullet rewritten with the corrected code table and the `Type=Variable` wrapper requirement. Removed the "implicit input" advice. The "Known Validator Gaps" section had its conditional entries removed; both the code-0 truthiness bug and the implicit-input gap were fixed in this release.
- **`skills/shortcuts-playground/SKILL.md` rule #17** — replaced with the corrected uniform-input rule and pointer to CONTROL_FLOW.md.

### Verified

- The Apple sample (`Conditionals.xml`, 41 actions covering codes 0, 1, 2, 3, 4, 5, 8, 9, 99, 100, 101, 999, 1003, plus a multi-condition Any-of-three block) now validates with **zero conditional errors**. Remaining errors against the sample are convention-only (missing leading Comment blocks, unused `WFWorkflowInputContentItemClasses`) and correctly enforced for shortcuts the plugin generates.
- `shortcuts-playground-selftest` still passes all six sub-checks.
- Hello World regression still produces a signed `.shortcut`.

## [1.2.0] — 2026-04-13

### Fixed (important behavior)
- **Agent reconnaissance failure mode.** The `shortcut-builder` agent could go into unbounded exploration when an action identifier was allowlisted but lacked a documented parameter schema — it would query the user's local `~/Library/Shortcuts/Shortcuts.sqlite`, the ToolKit database, Google Drive backups, and system binaries looking for examples. Reproduced with the prompt *"Build a shortcut that gets my reminders due today and lets me select multiple ones to reschedule them"* against `is.workflow.actions.setters.reminders`. The agent now stops and escalates to the user with three clean options (best-effort guess, simpler alternative, user-provided example) and never touches local databases during authoring.

### Removed
- **All references to `Shortcuts.sqlite` / `ZSHORTCUTACTIONS` / ToolKit sqlite from user-facing skill docs.** Purged from `SKILL.md` (rule #54 rewritten), `PARAMETER_TYPES.md` (verification section replaced with character ordinal table), `BEST_PRACTICES.md` (batch install verification bullet), `TOOLKIT_SNAPSHOT.md` (rewritten), and the skill's internal `README.md` (installed-batch-verification section deleted).
- **`scripts/install_and_verify_shortcuts.py`** — deleted. The script was only referenced from the now-removed docs.
- **Optional local ToolKit sqlite expansion in `validate_shortcut.py`** — removed. The bundled `data/toolkit-v63-tool-ids.json` (1,794 identifiers) is now the only allowlist source, making the validator deterministic and sqlite-free.
- **`import sqlite3`** — no longer present anywhere in the plugin's runtime code.

### Added (agent system prompt)
- **Hard rules against reconnaissance** in `agents/shortcut-builder.md`:
  - Never inspect `~/Library/Shortcuts/Shortcuts.sqlite` for authoring discovery (post-runtime debugging use is also removed from the docs entirely).
  - Never inspect `~/Library/Shortcuts/ToolKit/*.sqlite` or any ToolKit database.
  - Never search `~/Library/CloudStorage`, `~/Library/Mobile Documents`, `/System/Applications/Shortcuts.app`, or `/Applications/Shortcuts.app` for template shortcuts.
  - Never write inline Python that imports `sqlite3` or `objc`.
  - When an allowlisted action has no documented parameter schema, **stop and ask the user** with three concrete options.
- **Bounded research budget** — the agent may use up to 8 total Read/Grep/Glob calls before authoring or escalating. Prevents the unbounded-exploration failure mode even when no single rule fires.

### Changed
- **Rule #54 in `SKILL.md`** rewritten from "Verify installed shortcut behavior against Shortcuts.sqlite" to "Never inspect the user's local system for authoring discovery" — the old rule was the specific trigger that the agent was misapplying.
- **`TOOLKIT_SNAPSHOT.md`** retitled and rewritten to remove the "to avoid extracting ToolKit sqlite" framing. The snapshot just exists; no sqlite backstory.

### Verified
- Self-test passes.
- Hello World regression produces signed `.shortcut`.
- Federico's exact failing reminders prompt now triggers the escalation path: the agent stops, presents three options, makes zero tool calls to Shortcuts.sqlite / ToolKit / Google Drive / system paths.

## [1.1.0] — 2026-04-13

### Added
- `bin/shortcuts-playground-selftest` — post-install smoke test that verifies Python 3.10+, the macOS `shortcuts` CLI, plugin root resolution, bundled data files, a validator pass on an embedded golden XML, and a full `sign-shortcut` archive + sign round trip to a temp dir. Exits with specific error messages on any failure. Supports `SHORTCUTS_PLAYGROUND_SELFTEST_SKIP_SIGN=1` for CI environments without the `shortcuts` CLI.
- `commands/build.md` — `/shortcuts-playground:build <brief>` slash command. Explicit entry point that delegates to the `shortcut-builder` agent with the brief as `$ARGUMENTS`. Complements natural-language auto-invocation.
- `.claude-plugin/marketplace.json` — single-plugin marketplace manifest so the plugin directory can be added via `claude plugin marketplace add /path/to/shortcuts-playground-plugin`.

### Changed
- **README.md** — rewrote the Requirements section to clearly state the Python 3.10+ requirement (`/usr/bin/python3` on older macOS is 3.9.6 and will fail). Added a Health Check section that walks readers through post-install verification in four commands. Added a Configuration section documenting the three ways to set `userConfig` values: interactive `/plugin` TUI, manual `settings.json` edit under `pluginConfigs`, or direct `CLAUDE_PLUGIN_OPTION_*` env var override. Added a Development section explaining the directory-vs-git marketplace cache behavior (directory installs read from source; git installs read from cache and require `claude plugin update`). Added the slash command to the Usage section.
- **Plugin version bumped from 1.0.0 → 1.1.0** (minor — additive features, no breaking changes).

### Verified
- Full test matrix on v1.1.0 (8 checks, all green):
  - T1: `claude plugin validate` on plugin.json and marketplace.json.
  - T2: `shortcuts-playground-selftest` from plugin root — all 6 sub-checks pass.
  - T3: `shortcuts-playground-selftest` from `/tmp` without `CLAUDE_PLUGIN_ROOT` — fallback path resolution works.
  - T4: negative self-test (`CLAUDE_PLUGIN_ROOT=/tmp/nonexistent`) exits 1 with 6 specific error messages.
  - T5: `/shortcuts-playground:build` slash command via headless `claude -p` produces a signed `.shortcut`.
  - T6: natural-language auto-invocation (no slash command) produces a signed `.shortcut`.
  - T7: validator hook blocks a write with an unknown action identifier in headless mode.
  - T8: re-validation of every archive XML produced in the matrix — all pass.

## [1.0.0] — 2026-04-13

### Added
- Initial plugin conversion from the standalone `generate-shortcuts-skill` Claude Code skill.
- `skills/shortcuts-playground/` — full knowledge base carried over verbatim, with `SKILL.md` adapted to invoke the new bin wrappers instead of `python3 scripts/*.py` calls. Includes `BEST_PRACTICES.md`, `ACTIONS.md`, `APPINTENTS.md`, `PARAMETER_TYPES.md`, `VARIABLES.md`, `CONTROL_FLOW.md`, `FILTERS.md`, `EXAMPLES.md`, `THIRD_PARTY_ACTIONS.md`, `TOOLKIT_SNAPSHOT.md`, `ICONS_AND_COLORS.md`, `PLIST_FORMAT.md`, the golden-shortcuts reference library, and the ToolKit v63 metadata bundle.
- `agents/shortcut-builder.md` — specialized agent that owns the full design → build → validate → sign → archive loop, keeping the main thread free of the 1.2 MB knowledge base.
- `hooks/hooks.json` + `hooks/auto-validate.sh` — `PostToolUse` hook that auto-runs the Craig Loop validator on every `Write`/`Edit` that produces a Shortcuts plist file. Exits with code 2 + stderr on failure so validator output is injected back into Claude's context for the next iteration.
- `bin/validate-shortcut` — wrapper around `validate_shortcut.py`.
- `bin/resolve-icon` — wrapper around `select_shortcut_icon_color.py`.
- `bin/sign-shortcut` — combines archive + `shortcuts sign` into one command; respects `output_dir` and `signing_mode` userConfig values.
- `userConfig.output_dir` and `userConfig.signing_mode` — prompted at install time; falls back to `~/Documents/Shortcuts Playground` and `anyone` respectively.

### Migration notes from the standalone skill
- The Craig Loop is now **automatic**. Previously the model had to remember to invoke `validate_shortcut.py` after every `Write`; now the hook runs it unconditionally.
- All paths in `SKILL.md` that referenced `python3 scripts/<name>.py` now use the bin wrappers (`validate-shortcut`, `resolve-icon`, `sign-shortcut`) or `${CLAUDE_PLUGIN_ROOT}`-prefixed paths for the dev-only regression scripts.
- The archive directory is configurable via `userConfig.output_dir` instead of the hardcoded `~/Agent/Shortcuts Playground/` path.
- The skill name namespace is now `shortcuts-playground:shortcuts-playground`; the original `shortcuts-generator` name remains available via the parallel `~/.claude/skills/generate-shortcuts-skill/` installation until it is explicitly removed.
