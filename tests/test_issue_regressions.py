#!/usr/bin/env python3
"""Focused regressions for reported GitHub issues."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORMAT_ERROR = "Error: The file couldn't be opened because it isn't in the correct format."


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def minimal_shortcut_xml(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>WFWorkflowActions</key>
                <array/>
                <key>WFWorkflowName</key>
                <string>Issue Regression</string>
            </dict>
            </plist>
            """
        ),
        encoding="utf-8",
    )


def write_shortcuts_stub(directory: Path) -> Path:
    stub = directory / "shortcuts"
    stub.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env bash
            set -eu
            if [ "${{SHORTCUTS_STUB_MODE:-success}}" = "format-error" ]; then
              printf '%s\\n' "{FORMAT_ERROR}" >&2
              exit 1
            fi
            output=""
            while [ $# -gt 0 ]; do
              case "$1" in
                --output)
                  output="$2"
                  shift 2
                  ;;
                *)
                  shift
                  ;;
              esac
            done
            if [ -z "$output" ]; then
              printf 'stub shortcuts: missing --output\\n' >&2
              exit 64
            fi
            printf 'AEA1' > "$output"
            """
        ),
        encoding="utf-8",
    )
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    return stub


class HealthKitReferenceTests(unittest.TestCase):
    def test_blood_pressure_labels_match_shortcuts_ui(self) -> None:
        expected = {
            "BloodPressureDiastolic": "Diastolic Blood Pressure",
            "BloodPressureSystolic": "Systolic Blood Pressure",
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/data/healthkit-ios26.2-reference.json",
            "codex/skills/shortcuts-playground/data/healthkit-ios26.2-reference.json",
        ):
            data = load_json(REPO_ROOT / rel_path)
            by_suffix = {
                row.get("sdk_suffix"): row.get("shortcut_label_guess")
                for row in data.get("quantity_types", [])
            }
            self.assertEqual(
                expected,
                {suffix: by_suffix.get(suffix) for suffix in expected},
                rel_path,
            )


class SigningWrapperTests(unittest.TestCase):
    def run_wrapper(
        self,
        script: Path,
        env: dict[str, str],
        args: list[str] | None = None,
        stub_mode: str = "success",
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stub_dir = tmp_path / "bin"
            stub_dir.mkdir()
            write_shortcuts_stub(stub_dir)
            input_path = tmp_path / "input.xml"
            minimal_shortcut_xml(input_path)
            proc_env = os.environ.copy()
            proc_env.update(env)
            proc_env["PATH"] = f"{stub_dir}:{proc_env['PATH']}"
            proc_env["SHORTCUTS_STUB_MODE"] = stub_mode
            return subprocess.run(
                [str(script), str(input_path), "--name", "Issue Regression", *(args or [])],
                cwd=REPO_ROOT,
                env=proc_env,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_claude_sign_shortcut_honors_env_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "env-output"
            result = self.run_wrapper(
                REPO_ROOT / "claude/bin/sign-shortcut",
                {"CLAUDE_PLUGIN_OPTION_OUTPUT_DIR": str(output_dir)},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(output_dir / "Issue Regression.shortcut", Path(payload["signed"]))

    def test_claude_sign_shortcut_output_dir_flag_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_dir = Path(tmp) / "env-output"
            flag_dir = Path(tmp) / "flag-output"
            result = self.run_wrapper(
                REPO_ROOT / "claude/bin/sign-shortcut",
                {"CLAUDE_PLUGIN_OPTION_OUTPUT_DIR": str(env_dir)},
                ["--output-dir", str(flag_dir)],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(flag_dir / "Issue Regression.shortcut", Path(payload["signed"]))
            self.assertFalse((env_dir / "Issue Regression.shortcut").exists())

    def test_codex_sign_shortcut_honors_env_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "env-output"
            result = self.run_wrapper(
                REPO_ROOT / "codex/skills/shortcuts-playground/scripts/sign_shortcut.sh",
                {"SHORTCUTS_PLAYGROUND_OUTPUT_DIR": str(output_dir)},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(output_dir / "Issue Regression.shortcut", Path(payload["signed"]))

    def test_codex_sign_shortcut_reports_codex_sandbox_hint_on_format_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_wrapper(
                REPO_ROOT / "codex/skills/shortcuts-playground/scripts/sign_shortcut.sh",
                {"SHORTCUTS_PLAYGROUND_OUTPUT_DIR": str(Path(tmp) / "out")},
                stub_mode="format-error",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(FORMAT_ERROR, result.stderr)
            self.assertIn("Codex workspace-write sandbox restrictions", result.stderr)

    def test_claude_sign_shortcut_reports_codex_sandbox_hint_on_format_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_wrapper(
                REPO_ROOT / "claude/bin/sign-shortcut",
                {"CLAUDE_PLUGIN_OPTION_OUTPUT_DIR": str(Path(tmp) / "out")},
                stub_mode="format-error",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(FORMAT_ERROR, result.stderr)
            self.assertIn("Codex workspace-write sandbox restrictions", result.stderr)


class ClaudeAgentPromptTests(unittest.TestCase):
    def test_agents_use_user_config_and_pass_explicit_signing_options(self) -> None:
        for rel_path in (
            "claude/agents/shortcut-builder.md",
            "claude/agents/shortcut-remixer.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertIn("${user_config.output_dir}", text, rel_path)
            self.assertIn("${user_config.signing_mode}", text, rel_path)
            self.assertIn('--output-dir "$OUTPUT_DIR"', text, rel_path)
            self.assertIn('--mode "$SIGNING_MODE"', text, rel_path)
            self.assertIn("Claude Code may not expose", text, rel_path)


if __name__ == "__main__":
    unittest.main()
