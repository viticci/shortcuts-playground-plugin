---
description: Build a macOS/iOS Shortcut end-to-end via the shortcut-builder agent. Pass a natural-language brief — e.g. /build-shortcut weather lookup that asks for a city and shows a notification.
agent: shortcut-builder
---

Delegate to the `shortcut-builder` subagent to design, build, validate, sign, and archive a macOS/iOS Shortcut that satisfies the following brief:

$ARGUMENTS

The agent owns the full workflow end-to-end. Your job as the orchestrator is minimal:

1. **Invoke the agent** via the Task tool with `subagent_type: shortcut-builder`, passing the brief as the agent's prompt.
2. **Wait for the agent's result.** The agent is responsible for: resolving the output directory, reading skill files from the shared catalog (`claude/skills/shortcuts-playground/` or `skills/shortcuts-playground/`), picking an icon, drafting, Craig-Loop validating (via the `tool.execute.after` plugin hook in `opencode/plugin/validator.ts`), archiving, signing, verifying the signed file exists, and reporting absolute paths.
3. **Reject incomplete reports.** If the agent returns only "validation passed", a draft XML path, or anything without a verified signed `.shortcut` path plus archive XML path, treat that as an incomplete build and re-delegate with: "Pipeline first: skip optional polish, run the shared sign script on the current valid draft, verify the signed file exists, and report the signed and archive paths."
4. **Relay the agent's report to the user** verbatim. Don't re-run any steps the agent already completed.

## When the agent escalates

The agent will escalate to you (the orchestrator) if it cannot build — typically because of a documentation gap on an allowlisted action, a validator error it can't fix in 5 iterations, or a brief it can't parse. When that happens:

- **Do not do the agent's research for it.** Do not grep `~/Documents`, `~/.config`, `~/.claude`, `~/Library`, `/Applications`, `/System`, or any other user or system path looking for examples or schemas. Those directories are off limits for this command.
- **The only paths you may read from are:**
  1. The shared plugin catalog (`skills/shortcuts-playground/` or `claude/skills/shortcuts-playground/` or `codex/skills/shortcuts-playground/` — skill docs, bundled data, golden shortcuts, validator source). If the answer is here, read it and re-delegate to the agent with the answer as additional context.
  2. The file the agent just wrote under the `OUTPUT_DIR` it printed in step 0, if you need to inspect what it produced before responding.
- **Relay the escalation to the user** if the shared directory doesn't have the answer. Present the agent's escalation reason and any options it offered, and wait for user input. Do NOT paper over the escalation by improvising.

## Hard rules for this command

- **Never grep `~/Documents` broadly, `~/.config`, `~/.claude/skills`, `~/.claude/plugins`, `~/Library`, `/Applications`, or `/System`.** Even when an agent escalates on "I don't know this schema." Those paths may contain the user's private files, deleted plugin versions, session logs, or system binaries — none of them are authoritative reference material.
- **Never run `plutil`, `xxd`, `file`, or other binary inspectors on signed `.shortcut` files.** Signed shortcuts are Apple Encrypted Archives (AEA1); they cannot be read as plaintext plists. If you need to see how a previous shortcut was structured, the unsigned XML is in the drafts folder alongside it.
- **Never mine prior archived shortcuts as a reference corpus.** The output directory contains user-generated content, not curated examples. It may include dead ends, deprecated patterns, or quality issues. The canonical reference is the shared plugin directory itself.
- **Do not execute the shortcut or import it into Shortcuts.app.** The user will open the signed file themselves. Your job ends at "signed file exists, here is its path."
