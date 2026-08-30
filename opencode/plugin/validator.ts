/**
 * Shortcuts Playground — OpenCode Craig Loop validator plugin
 *
 * OpenCode hook equivalent of Claude Code's PostToolUse hook.
 *
 * Claude Code: hooks/hooks.json + hooks/auto-validate.sh (PostToolUse on Write|Edit)
 * Codex:       hooks/hooks.json + hooks/auto-validate.sh (PostToolUse on apply_patch|Write|Edit, with [features].plugin_hooks opt-in)
 * OpenCode:    this file — tool.execute.after on write/edit/apply_patch
 *
 * Mapping confirmed against https://opencode.ai/docs/plugins#events
 *   Claude PostToolUse  →  OpenCode tool.execute.after
 *   Claude PreToolUse   →  OpenCode tool.execute.before
 *
 * Behavior:
 * - Fires after every tool that may have touched a Shortcuts plist (write, edit, apply_patch, bash writes)
 * - Filters to .xml/.shortcut extensions + WFWorkflowActions content sniff
 * - Runs the shared validator (skills/shortcuts-playground/scripts/validate_shortcut.py,
 *   with fallbacks to claude/skills/... and codex/skills/...)
 * - On failure, injects validator output as additionalContext so the model can iterate (Craig Loop)
 * - Honors SHORTCUTS_PLAYGROUND_TARGET_MACOS / TARGET_PLATFORM via env passthrough (validator reads them)
 *
 * Gap vs Claude Code:
 * - OpenCode plugins cannot exit(2) to block a tool in the same way Claude's PostToolUse hook does.
 *   Instead we return additionalContext / throw with validator output so the agent sees the error.
 *   The file has still been written; the agent must fix it in the next turn.
 *   Documented in opencode/README.md under "Hook parity".
 * - OpenCode's tool.execute.after receives {tool, args, result} — file_path may be under different keys
 *   depending on tool. We handle read/write/edit/apply_patch/bash.
 */

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join, dirname, resolve, isAbsolute } from "node:path";

// Resolve plugin root: the opencode/ directory containing this file's package.
// When installed as .opencode/plugins/validator.ts, dirname is that dir.
// When running from repo opencode/plugin/, we walk up to repo root.
function resolvePluginRoot(currentFileDir: string): string {
  // If this file is at <repo>/opencode/plugin/validator.ts, plugin root is <repo>/opencode
  // If installed as <project>/.opencode/plugins/validator.ts, plugin root is <project>/.opencode/plugins
  // Try to find the repo root by walking up and looking for claude/skills/shortcuts-playground
  let dir = currentFileDir;
  for (let i = 0; i < 6; i++) {
    if (existsSync(join(dir, "claude/skills/shortcuts-playground/scripts/validate_shortcut.py"))) return join(dir, "opencode");
    if (existsSync(join(dir, "skills/shortcuts-playground/scripts/validate_shortcut.py"))) return join(dir, "opencode");
    if (existsSync(join(dir, "codex/skills/shortcuts-playground/scripts/validate_shortcut.py"))) return join(dir, "opencode");
    if (existsSync(join(dir, "skills/shortcuts-playground/SKILL.md"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return currentFileDir;
}

function resolveSharedValidator(pluginRoot: string, repoRootHint?: string): string | null {
  const candidates: string[] = [];

  // Prefer shared top-level skills/ if repo has consolidated
  if (repoRootHint) {
    candidates.push(join(repoRootHint, "skills/shortcuts-playground/scripts/validate_shortcut.py"));
  }
  // Repo layout: opencode/ sibling to claude/ and codex/
  const repoRoot = resolve(join(pluginRoot, ".."));
  candidates.push(
    join(repoRoot, "skills/shortcuts-playground/scripts/validate_shortcut.py"),
    join(repoRoot, "claude/skills/shortcuts-playground/scripts/validate_shortcut.py"),
    join(repoRoot, "codex/skills/shortcuts-playground/scripts/validate_shortcut.py"),
  );
  // Also check relative to pluginRoot itself (symlinked install)
  candidates.push(
    join(pluginRoot, "skills/shortcuts-playground/scripts/validate_shortcut.py"),
    join(pluginRoot, "../claude/skills/shortcuts-playground/scripts/validate_shortcut.py"),
    join(pluginRoot, "../codex/skills/shortcuts-playground/scripts/validate_shortcut.py"),
  );

  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return null;
}

function extractFilePaths(tool: string, args: Record<string, unknown>, cwd?: string): string[] {
  const paths: string[] = [];
  const add = (p: unknown) => {
    if (typeof p !== "string" || !p) return;
    if (p === "/dev/null") return;
    let abs = p;
    if (!isAbsolute(abs) && cwd) abs = resolve(join(cwd, abs));
    if (!paths.includes(abs)) paths.push(abs);
  };

  add((args as any).file_path);
  add((args as any).path);
  add((args as any).filePath);

  // apply_patch / bash may embed paths in patch text or command string
  const command = (args as any).command;
  if (typeof command === "string") {
    // Codex-style patch headers: *** Add File: <path>, *** Update File: <path>, *** Move to: <path>
    const re = /^\*\*\* (?:Add|Update) File: (.+)$/gm;
    let m: RegExpExecArray | null;
    while ((m = re.exec(command))) add(m[1].trim());
    const re2 = /^\*\*\* Move to: (.+)$/gm;
    while ((m = re2.exec(command))) add(m[1].trim());
  }

  // OpenCode write/edit tools may include file content but path is already captured
  return paths;
}

export const ShortcutsPlaygroundValidator = async ({ project, directory }: { project: unknown; directory: string }) => {
  const pluginDir = dirname(new URL(import.meta.url).pathname);
  const pluginRoot = resolvePluginRoot(pluginDir);
  const validator = resolveSharedValidator(pluginRoot, directory);

  const py = process.env.SHORTCUTS_PLAYGROUND_PYTHON || "python3";

  // Early sanity: if python missing or too old, silently no-op (don't spam every write)
  const checkPy = spawnSync(py, ["-c", "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"]);
  const pyOk = checkPy.status === 0;

  return {
    // PostToolUse-equivalent — runs after each tool completes
    "tool.execute.after": async (input: { tool: string; args: Record<string, unknown> }, output: { result?: unknown }) => {
      if (!validator || !pyOk) return;
      if (!existsSync(validator)) return;

      // Only care about file-mutating tools
      const tool = input.tool || "";
      const isWriteTool = /^(write|edit|apply_patch|bash)$/i.test(tool) || tool.includes("write") || tool.includes("edit");
      // Also catch generic tool names that may have written a file via bash
      const args = input.args || {};

      const cwd = directory || process.cwd();
      const filePaths = extractFilePaths(tool, args as Record<string, unknown>, cwd);

      // Fallback: some tools report output path in result
      if (filePaths.length === 0 && output?.result) {
        const res = output.result as any;
        if (typeof res?.filePath === "string") extractFilePaths(tool, { file_path: res.filePath }, cwd).forEach(p => { if (!filePaths.includes(p)) filePaths.push(p); });
      }

      if (filePaths.length === 0) return;

      // Filter + validate each touched file
      const failures: string[] = [];
      for (const fp of filePaths) {
        if (!fp) continue;
        if (!existsSync(fp)) continue;
        if (!fp.endsWith(".xml") && !fp.endsWith(".shortcut")) continue;
        try {
          const content = readFileSync(fp, "utf8");
          if (!content.includes("WFWorkflowActions")) continue;
        } catch {
          continue;
        }

        const result = spawnSync(py, [validator, fp], { encoding: "utf8", timeout: 15000 });
        if (result.status === 0) continue;

        const out = (result.stdout || "") + (result.stderr || "");
        failures.push(`shortcuts-playground validator failed for ${fp}\n\n${out.trim()}`);
      }

      if (failures.length === 0) return;

      const reason = failures.join("\n\n---\n\n");

      // In OpenCode, throwing surfaces the message to the agent; returning additionalContext
      // is also supported by some plugin hosts. We throw so the agent sees it even if the
      // host doesn't propagate additionalContext for tool.execute.after.
      // The file has already been written — this is feedback, not a block (gap vs Claude).
      throw new Error(reason);
    },
  };
};

// Default export for opencode `plugin: ["./opencode/plugin/validator.ts"]` style loading
export default ShortcutsPlaygroundValidator;
