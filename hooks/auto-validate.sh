#!/usr/bin/env bash
# Shortcuts Playground — PostToolUse auto-validator
#
# Fires after every Write/Edit tool call. Filters down to Shortcuts plist files
# (by extension + content sniff) and invokes the Craig Loop validator. Exits with
# code 2 + stderr on failure so Claude sees the validator output and can iterate.
#
# Non-shortcut files are ignored silently. Missing files are ignored (e.g. if
# another tool already moved the written file).

set -u

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
  # Fallback: resolve from this script's own location (hooks/ -> plugin root).
  PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

VALIDATOR="$PLUGIN_ROOT/skills/shortcuts-playground/scripts/validate_shortcut.py"
if [ ! -f "$VALIDATOR" ]; then
  # Plugin is mis-packaged. Stay silent so we don't spam every Write call.
  exit 0
fi

PY="${SHORTCUTS_PLAYGROUND_PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  # Python missing — stay silent; a user-facing error here would block every Write.
  exit 0
fi
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  # Interpreter too old for PEP 604 syntax the validator uses. Stay silent to
  # avoid blocking non-shortcut writes. The manual `validate-shortcut` wrapper
  # surfaces the same problem with a clear error when the user invokes it.
  exit 0
fi

# Read the hook input (JSON on stdin) and extract the file path the tool touched.
INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | "$PY" -c '
import json, sys
try:
    data = json.loads(sys.stdin.read() or "{}")
except Exception:
    sys.exit(0)
tool_input = data.get("tool_input") or {}
path = tool_input.get("file_path") or tool_input.get("path") or ""
print(path)
' 2>/dev/null || true)"

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Only act on .xml/.shortcut extensions.
case "$FILE_PATH" in
  *.xml|*.shortcut) : ;;
  *) exit 0 ;;
esac

# Content sniff: only validate plists that look like Shortcuts workflows.
if ! /usr/bin/grep -q 'WFWorkflowActions' "$FILE_PATH" 2>/dev/null; then
  exit 0
fi

# Run the validator. If it fails, echo its output to stderr and exit 2 so
# Claude Code forwards the feedback back into the model context.
if VALIDATOR_OUT="$("$PY" "$VALIDATOR" "$FILE_PATH" 2>&1)"; then
  exit 0
fi

printf 'shortcuts-playground validator failed for %s\n\n%s\n' "$FILE_PATH" "$VALIDATOR_OUT" >&2
exit 2
