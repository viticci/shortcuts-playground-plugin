#!/usr/bin/env bash
# Shortcuts Playground for Codex: archive + sign a Shortcuts plist.
#
# Usage:
#   sign_shortcut.sh <input.xml> [--name "Final Name"] [--mode anyone|people-who-know-me] [--output-dir DIR]
#
# Defaults:
#   --mode        : $SHORTCUTS_PLAYGROUND_SIGNING_MODE, else "anyone"
#   --output-dir  : $SHORTCUTS_PLAYGROUND_OUTPUT_DIR, else "$HOME/Documents/Shortcuts Playground"
#   --name        : basename of the input file without extension

set -euo pipefail

INPUT=""
NAME=""
MODE="${SHORTCUTS_PLAYGROUND_SIGNING_MODE:-anyone}"
OUTPUT_DIR="${SHORTCUTS_PLAYGROUND_OUTPUT_DIR:-$HOME/Documents/Shortcuts Playground}"

usage() {
  cat <<'USAGE' >&2
Usage: sign_shortcut.sh <input.xml> [--name NAME] [--mode anyone|people-who-know-me] [--output-dir DIR]
USAGE
  exit 64
}

while [ $# -gt 0 ]; do
  case "$1" in
    --name)
      [ $# -ge 2 ] || usage
      NAME="$2"
      shift 2
      ;;
    --mode)
      [ $# -ge 2 ] || usage
      MODE="$2"
      shift 2
      ;;
    --output-dir)
      [ $# -ge 2 ] || usage
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [ -z "$INPUT" ]; then
        INPUT="$1"
        shift
      else
        printf 'Unexpected argument: %s\n' "$1" >&2
        usage
      fi
      ;;
  esac
done

[ -n "$INPUT" ] || usage

if [ ! -f "$INPUT" ]; then
  printf 'Input file not found: %s\n' "$INPUT" >&2
  exit 2
fi

if [ "$MODE" != "anyone" ] && [ "$MODE" != "people-who-know-me" ]; then
  printf 'Invalid --mode: %s (expected "anyone" or "people-who-know-me")\n' "$MODE" >&2
  exit 64
fi

if ! command -v shortcuts >/dev/null 2>&1; then
  printf 'Apple shortcuts CLI not found on PATH; signing requires macOS Shortcuts.\n' >&2
  exit 127
fi

if [ -z "$NAME" ]; then
  BASENAME="$(basename "$INPUT")"
  NAME="${BASENAME%.*}"
fi

case "$NAME" in
  */*|*\\*|.|..)
    printf 'Invalid --name: shortcut names cannot contain path separators or dot path segments.\n' >&2
    exit 64
    ;;
esac

DATE_STAMP="$(date +%F)"
TIME_STAMP="$(date +%H%M%S)"
ARCHIVE_DIR="$OUTPUT_DIR/$DATE_STAMP"
ARCHIVE_FILE="$ARCHIVE_DIR/${NAME}-${TIME_STAMP}.xml"
SIGNED_PATH="$OUTPUT_DIR/${NAME}.shortcut"

mkdir -p "$ARCHIVE_DIR" "$OUTPUT_DIR"
cp "$INPUT" "$ARCHIVE_FILE"
cp "$INPUT" "$SIGNED_PATH"

set +e
SIGN_OUTPUT="$(shortcuts sign --mode "$MODE" --input "$SIGNED_PATH" --output "$SIGNED_PATH" 2>&1)"
SIGN_STATUS=$?
set -e
if [ "$SIGN_STATUS" -ne 0 ]; then
  if [ -n "$SIGN_OUTPUT" ]; then
    printf '%s\n' "$SIGN_OUTPUT" >&2
  fi
  case "$SIGN_OUTPUT" in
    *"isn't in the correct format"*|*"isn’t in the correct format"*)
      printf '\nshortcuts-playground: Apple shortcuts sign reported a format error. If validate_shortcut.py and plutil -lint both pass, this can be caused by Codex workspace-write sandbox restrictions rather than malformed XML. Retry signing outside the restricted sandbox or with Codex filesystem sandboxing set to full access.\n' >&2
      ;;
  esac
  exit "$SIGN_STATUS"
fi

printf '{"archive":"%s","signed":"%s","mode":"%s"}\n' "$ARCHIVE_FILE" "$SIGNED_PATH" "$MODE"
