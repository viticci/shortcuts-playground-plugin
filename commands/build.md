---
description: Build a macOS/iOS Shortcut end-to-end via the shortcut-builder agent. Pass a natural-language brief — e.g. `/shortcuts-playground:build weather lookup that asks for a city and shows a notification`.
argument-hint: <natural-language brief for the shortcut>
---

Delegate to the `shortcut-builder` agent (via the Agent tool with `subagent_type: shortcut-builder`) to design, build, validate, sign, and archive a macOS/iOS Shortcut that satisfies the following brief:

$ARGUMENTS

The agent owns the full workflow end-to-end. Your job as the orchestrator is minimal:

1. **Invoke the agent** via the `Agent` tool with `subagent_type: shortcut-builder`, passing the brief as the agent's prompt.
2. **Wait for the agent's result.** The agent is responsible for: resolving the output directory, reading skill files, picking an icon, drafting, Craig-Loop validating, archiving, signing, verifying the signed file exists, and reporting absolute paths.
3. **Relay the agent's report to the user** verbatim. Don't re-run any steps the agent already completed.

## When the agent escalates

The agent will escalate to you (the orchestrator) if it cannot build — typically because of a documentation gap on an allowlisted action, a validator error it can't fix in 5 iterations, or a brief it can't parse. When that happens:

- **Do not do the agent's research for it.** Do not grep `~/Documents`, `~/Agent`, `~/.claude`, `~/Library`, `/Applications`, `/System`, or any other user or system path looking for examples or schemas. Those directories are off limits for this command.
- **The only paths you may read from are:**
  1. The plugin installation directory itself (`${CLAUDE_PLUGIN_ROOT}` — skill docs, bundled data, golden shortcuts, validator source). If the answer is here, read it and re-delegate to the agent with the answer as additional context.
  2. The file the agent just wrote to `${CLAUDE_PLUGIN_OPTION_OUTPUT_DIR:-$HOME/Documents/Shortcuts Playground}/drafts/<name>.xml`, if you need to inspect what it produced before responding.
- **Relay the escalation to the user** if the plugin directory doesn't have the answer. Present the agent's escalation reason and any options it offered, and wait for user input. Do NOT paper over the escalation by improvising.

## Hard rules for this command

- **Never grep `~/Documents` broadly, `~/Agent`, `~/.claude/skills`, `~/.claude/plugins`, `~/.claude/projects`, `~/Library`, `/Applications`, or `/System`.** Even when an agent escalates on "I don't know this schema." Those paths may contain the user's private files, deleted plugin versions, session logs, or system binaries — none of them are authoritative reference material.
- **Never run `plutil`, `xxd`, `file`, or other binary inspectors on signed `.shortcut` files.** Signed shortcuts are Apple Encrypted Archives (AEA1); they cannot be read as plaintext plists. If you need to see how a previous shortcut was structured, the unsigned XML is in the drafts folder alongside it.
- **Never mine prior archived shortcuts as a reference corpus.** The plugin's output directory contains user-generated content, not curated examples. It may include dead ends, deprecated patterns, or quality issues. The canonical reference is the plugin directory itself.
- **Do not execute the shortcut or import it into Shortcuts.app.** The user will open the signed file themselves. Your job ends at "signed file exists, here is its path."
