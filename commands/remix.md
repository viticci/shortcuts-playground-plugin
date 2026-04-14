---
description: Remix an existing Shortcuts XML plist by applying a natural-language diff. Pass `<absolute-path-to-xml> <remix idea>` — e.g. `/shortcuts-playground:remix /Users/you/Documents/Shortcuts Playground/Weather.xml add a notification before the Show Alert`. The source MUST be an unsigned `.xml` file, not a signed `.shortcut` (those are AEA1 encrypted archives).
argument-hint: <absolute path to .xml> <remix idea>
---

Delegate to the `shortcut-remixer` agent (via the Agent tool with `subagent_type: shortcut-remixer`) to apply a surgical diff to an existing Shortcuts XML plist. Pass the full instruction below to the agent so it can parse out the source path and the remix idea:

$ARGUMENTS

The agent owns the full remix workflow end-to-end. Your job as the orchestrator is minimal:

1. **Invoke the agent** with `subagent_type: shortcut-remixer`, passing `$ARGUMENTS` verbatim. The agent will extract the source path and the remix idea itself.
2. **Wait for the agent's result.** The agent is responsible for: resolving the output directory, parsing its input, validating the source (path exists, is unsigned XML, parses as a plist), reading it, baselining it against the validator, reading skill reference files, planning the diff, writing the draft, Craig-Loop validating, archiving, signing, verifying the signed file exists, and reporting.
3. **Relay the agent's report to the user** verbatim. Do not re-run any steps the agent already did.

## When the agent escalates

The remixer will escalate to you (the orchestrator) in three main cases:

- **No source path found in `$ARGUMENTS`.** The agent will ask the user to re-run the command with an explicit absolute path. Relay the agent's message verbatim and stop.
- **Source is signed (`.shortcut` / AEA1).** The agent will ask the user to export the shortcut as unsigned XML first. Relay the message verbatim.
- **Source is missing, unreadable, or not a Shortcuts plist.** The agent will report the specific reason. Relay and stop.

In all escalation cases: **do not do the agent's work for it.** Do not grep for "similar" files, do not try to `plutil`/`xxd` the signed file, do not search the user's filesystem for a matching shortcut. Just relay the escalation to the user and wait.

## Hard rules for this command

All the same rules that apply to `/shortcuts-playground:build` apply here:

- **Never grep `~/Documents` broadly, `~/Agent`, `~/.claude/skills`, `~/.claude/plugins`, `~/.claude/projects`, `~/Library`, `/Applications`, or `/System`.** Even when the agent escalates on "I don't know this schema" or "I can't find the source." Those paths may contain the user's private files, deleted plugin versions, session logs, or system binaries — none of them are authoritative reference material.
- **Never run `plutil`, `xxd`, `file`, or other binary inspectors on signed `.shortcut` files.** Signed shortcuts are Apple Encrypted Archives (AEA1); they cannot be read as plaintext plists.
- **Never mine prior archived shortcuts as a reference corpus** for the agent to crib from. The source the user gave the remixer is its ONLY reference for context; the plugin directory is the ONLY reference for patterns.
- **Never overwrite the source file.** The remixer writes to `<OUTPUT_DIR>/drafts/<new name>.xml` under a new name so the user's original stays intact.
- **Do not execute the shortcut or import it into Shortcuts.app.** The user will open the signed file themselves. Your job ends at "signed file exists, here is its path."
