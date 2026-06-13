#!/usr/bin/env python3
"""Focused regressions for reported GitHub issues."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
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


class ToolkitSnapshotTests(unittest.TestCase):
    def load_validator_module(self, rel_path: str):
        import importlib.util

        module_path = REPO_ROOT / rel_path
        spec = importlib.util.spec_from_file_location(
            f"validate_shortcut_{rel_path.split('/')[0]}", module_path
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module_path

    def test_validator_loads_multiple_packaged_toolkit_snapshots(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)

            skill_dir = module_path.parents[1]
            allowed_ids = module.load_packaged_toolkit_ids(skill_dir, target_macos_major=27)

            self.assertIn("is.workflow.actions.gettext", allowed_ids, rel_path)
            self.assertIn("is.workflow.actions.additemtolist", allowed_ids, rel_path)
            self.assertIn("is.workflow.actions.getselectedtext", allowed_ids, rel_path)
            self.assertIn("com.apple.HearingApp.AdjustVolumeIntent", allowed_ids, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", allowed_ids, rel_path)
            self.assertIn("com.apple.HearingApp.SelectPresetIntent", allowed_ids, rel_path)

    def test_macos27_toolkit_ids_are_target_gated(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            allowed_26 = module.load_allowed_ids(skill_dir, target_macos_major=26)
            allowed_27 = module.load_allowed_ids(skill_dir, target_macos_major=27)
            future_26 = module.load_future_toolkit_id_reasons(skill_dir, 26)

            self.assertIn("is.workflow.actions.gettext", allowed_26, rel_path)
            self.assertNotIn("is.workflow.actions.additemtolist", allowed_26, rel_path)
            self.assertIn("is.workflow.actions.additemtolist", allowed_27, rel_path)
            self.assertEqual(
                "macOS 27+ (toolkit-v78)",
                future_26.get("is.workflow.actions.additemtolist"),
                rel_path,
            )
            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", allowed_26, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", allowed_27, rel_path)
            self.assertEqual(
                "iOS 27+ (toolkit-v78-ios27)",
                future_26.get("com.apple.HearingApp.MuteVolumeIntent"),
                rel_path,
            )

    def test_os27_parameter_keys_are_target_gated(self) -> None:
        expected = {
            "com.apple.Safari.CreateNewTabGroup": {"contents"},
            "com.apple.mobilenotes.SharingExtension": {"interpretAsMarkdown"},
            "is.workflow.actions.appendnote": {
                "ignoreWhitespace",
                "interpretAsMarkdown",
                "section",
            },
            "is.workflow.actions.askllm": {"WFAllowWebSearch"},
            "is.workflow.actions.getdistance": {"WFAvoidHighways", "WFAvoidTolls"},
            "is.workflow.actions.gettraveltime": {"WFAvoidHighways", "WFAvoidTolls"},
            "is.workflow.actions.hide.app": {"WFAppsExcept"},
            "is.workflow.actions.quit.app": {"WFAppsExcept"},
            "is.workflow.actions.scanbarcode": {"imageFile"},
        }

        plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": identifier,
                    "WFWorkflowActionParameters": {key: True for key in sorted(keys)},
                }
                for identifier, keys in sorted(expected.items())
            ],
            "WFWorkflowName": "OS 27 Parameter Gate Regression",
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            future_params_26 = module.load_future_parameter_key_reasons(26)
            future_params_27 = module.load_future_parameter_key_reasons(27)

            self.assertEqual(
                expected,
                {identifier: set(keys) for identifier, keys in module.OS27_PARAMETER_KEYS_BY_ACTION.items()},
                rel_path,
            )
            self.assertEqual({}, future_params_27, rel_path)
            for identifier, keys in expected.items():
                self.assertEqual(set(keys), set(future_params_26[identifier]), rel_path)

            errors_26, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=26),
                unavailable_ids=module.load_future_toolkit_id_reasons(skill_dir, 26),
                unavailable_parameter_keys=future_params_26,
            )
            for identifier, keys in expected.items():
                for key in keys:
                    self.assertTrue(
                        [
                            error
                            for error in errors_26
                            if f"Parameter '{key}' on {identifier} requires macOS 27+" in error
                        ],
                        f"{rel_path}: missing gate for {identifier} {key}: {errors_26}",
                    )

            errors_27, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=27),
                unavailable_ids=module.load_future_toolkit_id_reasons(skill_dir, 27),
                unavailable_parameter_keys=future_params_27,
            )
            self.assertFalse(
                [error for error in errors_27 if "toolkit-v78 parameter" in error],
                f"{rel_path}: {errors_27}",
            )

    def test_ios27_toolkit_snapshot_is_packaged(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/data/toolkit-v78-ios27-tool-ids.json",
            "codex/skills/shortcuts-playground/data/toolkit-v78-ios27-tool-ids.json",
        ):
            payload = load_json(REPO_ROOT / rel_path)
            self.assertEqual("toolkit-v78-ios27", payload["version"], rel_path)
            self.assertEqual("iOS Simulator", payload["platform"], rel_path)
            self.assertEqual("iOS 27.0 Simulator", payload["source_runtime"], rel_path)
            self.assertEqual(1206, len(payload["ids"]), rel_path)
            self.assertIn("com.apple.HearingApp.AdjustVolumeIntent", payload["ids"], rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", payload["ids"], rel_path)
            self.assertIn("com.apple.HearingApp.SelectPresetIntent", payload["ids"], rel_path)
            self.assertIn("com.apple.SharingUIService.ShareIntent", payload["ids"], rel_path)
            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", load_json(REPO_ROOT / rel_path.replace("-ios27", ""))["ids"], rel_path)

    def test_macos27_otherwise_if_shape_validates(self) -> None:
        source_uuid = "12345678-1234-4234-9234-123456789ABC"
        group_uuid = "87654321-4321-4321-9321-CBA987654321"
        conditional_input = {
            "Type": "Variable",
            "Variable": {
                "Value": {
                    "OutputName": "Text",
                    "OutputUUID": source_uuid,
                    "Type": "ActionOutput",
                },
                "WFSerializationType": "WFTextTokenAttachment",
            },
        }
        plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                    "WFWorkflowActionParameters": {
                        "WFCommentActionText": "Regression shortcut for macOS 27 Otherwise If."
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                    "WFWorkflowActionParameters": {
                        "WFCommentActionText": (
                            "Shortcuts generated by Shortcuts Playground. "
                            "May contain mistakes. Always check the shortcut's actions first."
                        )
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                    "WFWorkflowActionParameters": {
                        "WFTextActionText": "Four",
                        "UUID": source_uuid,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                    "WFWorkflowActionParameters": {
                        "WFCommentActionText": "- Test generated text\n- Branch with Otherwise If"
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                    "WFWorkflowActionParameters": {
                        "GroupingIdentifier": group_uuid,
                        "WFControlFlowMode": 0,
                        "WFCondition": 99,
                        "WFInput": conditional_input,
                        "WFConditionalActionString": "Five",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.nothing",
                    "WFWorkflowActionParameters": {
                        "UUID": "D3D04895-B3B0-44DD-B05E-65EC64C94C04"
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                    "WFWorkflowActionParameters": {
                        "GroupingIdentifier": group_uuid,
                        "WFControlFlowMode": 1,
                        "WFCondition": 99,
                        "WFInput": conditional_input,
                        "WFConditionalActionString": "Four",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.nothing",
                    "WFWorkflowActionParameters": {
                        "UUID": "9B24500B-F86C-4BBF-9228-0C09E43C6090"
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                    "WFWorkflowActionParameters": {
                        "GroupingIdentifier": group_uuid,
                        "WFControlFlowMode": 1,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.nothing",
                    "WFWorkflowActionParameters": {
                        "UUID": "A26AFC56-284D-43E8-A5F8-4BF07F18B077"
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                    "WFWorkflowActionParameters": {
                        "GroupingIdentifier": group_uuid,
                        "WFControlFlowMode": 2,
                    },
                },
            ],
            "WFWorkflowIcon": {
                "WFWorkflowIconGlyphNumber": 61440,
                "WFWorkflowIconStartColor": 431817727,
            },
            "WFWorkflowName": "Otherwise If Regression",
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            errors, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=27),
            )

            self.assertNotIn(
                "Conditional missing WFInput/WFCondition at index 6",
                "\n".join(errors),
                rel_path,
            )
            self.assertFalse(
                [err for err in errors if "Otherwise If" in err or "unknown WFCondition" in err],
                f"{rel_path}: {errors}",
            )

    def test_reassigned_list_variable_contains_is_rejected(self) -> None:
        list_uuid = "11111111-2222-4333-9444-555555555555"
        add_uuid = "22222222-3333-4444-9555-666666666666"
        group_uuid = "33333333-4444-4555-9666-777777777777"

        def action_output(output_uuid: str, output_name: str = "List") -> dict:
            return {
                "Value": {
                    "OutputName": output_name,
                    "OutputUUID": output_uuid,
                    "Type": "ActionOutput",
                },
                "WFSerializationType": "WFTextTokenAttachment",
            }

        def variable_attachment(name: str) -> dict:
            return {
                "Value": {"VariableName": name, "Type": "Variable"},
                "WFSerializationType": "WFTextTokenAttachment",
            }

        def conditional_input(name: str) -> dict:
            return {"Type": "Variable", "Variable": variable_attachment(name)}

        def plist_for(first_name: str, final_name: str, condition_name: str) -> dict:
            return {
                "WFWorkflowActions": [
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "WFCommentActionText": "Regression for reassigned list contains."
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "WFCommentActionText": (
                                "Shortcuts generated by Shortcuts Playground. "
                                "May contain mistakes. Always check the shortcut's actions first."
                            )
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.list",
                        "WFWorkflowActionParameters": {"UUID": list_uuid},
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
                        "WFWorkflowActionParameters": {
                            "WFInput": action_output(list_uuid),
                            "WFVariableName": first_name,
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                        "WFWorkflowActionParameters": {
                            "WFListItem": "Orange",
                            "WFListVariable": variable_attachment(first_name),
                            "UUID": add_uuid,
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
                        "WFWorkflowActionParameters": {
                            "WFInput": action_output(add_uuid),
                            "WFVariableName": final_name,
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "WFCommentActionText": "- Check final list for Orange"
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                        "WFWorkflowActionParameters": {
                            "GroupingIdentifier": group_uuid,
                            "WFControlFlowMode": 0,
                            "WFCondition": 99,
                            "WFInput": conditional_input(condition_name),
                            "WFConditionalActionString": "Orange",
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.nothing",
                        "WFWorkflowActionParameters": {
                            "UUID": "44444444-5555-4666-9777-888888888888"
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                        "WFWorkflowActionParameters": {
                            "GroupingIdentifier": group_uuid,
                            "WFControlFlowMode": 2,
                        },
                    },
                ],
                "WFWorkflowIcon": {
                    "WFWorkflowIconGlyphNumber": 61440,
                    "WFWorkflowIconStartColor": 431817727,
                },
                "WFWorkflowName": "Reassigned List Contains Regression",
            }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            allowed = module.load_allowed_ids(skill_dir, target_macos_major=27)

            broken_errors, _ = module.validate(
                plist_for("Fruit List", "Fruit List", "Fruit List"),
                allowed,
            )
            self.assertTrue(
                [err for err in broken_errors if "blank comparison value" in err],
                f"{rel_path}: {broken_errors}",
            )

            fixed_errors, _ = module.validate(
                plist_for("Working Fruit List", "Fruit List", "Fruit List"),
                allowed,
            )
            self.assertFalse(
                [err for err in fixed_errors if "blank comparison value" in err],
                f"{rel_path}: {fixed_errors}",
            )


class AppleGroundingCatalogTests(unittest.TestCase):
    CATALOG_PATHS = (
        "claude/skills/shortcuts-playground/data/macos27-shortpy-grounding.json",
        "codex/skills/shortcuts-playground/data/macos27-shortpy-grounding.json",
    )
    PARAMETER_CATALOG_PATHS = (
        "claude/skills/shortcuts-playground/data/toolkit-v78-first-party-parameter-keys.json",
        "codex/skills/shortcuts-playground/data/toolkit-v78-first-party-parameter-keys.json",
    )
    LOOKUP_SCRIPTS = (
        "claude/skills/shortcuts-playground/scripts/lookup_action_grounding.py",
        "codex/skills/shortcuts-playground/scripts/lookup_action_grounding.py",
    )

    def test_static_apple_grounding_catalog_is_packaged_and_portable(self) -> None:
        for rel_path in self.CATALOG_PATHS:
            catalog = load_json(REPO_ROOT / rel_path)

            self.assertEqual(1, catalog["schemaVersion"], rel_path)
            self.assertEqual(27, catalog["minimumMacOSMajor"], rel_path)
            self.assertIn("Static metadata only", catalog["runtimePolicy"], rel_path)
            self.assertEqual(29, catalog["summary"]["toolCount"], rel_path)
            self.assertEqual(29, catalog["summary"]["pythonLookupFunctionCount"], rel_path)
            self.assertEqual(11, catalog["summary"]["toolRendererScriptingUtilityIdentifierCount"], rel_path)
            self.assertEqual(4, catalog["summary"]["shortcutsLanguageSyntaxSignals"], rel_path)

            add_item = catalog["tools"]["is.workflow.actions.additemtolist"]
            self.assertEqual("catalog_ready_observed_keywords", add_item["status"], rel_path)
            self.assertEqual("com_apple_shortcuts_add_item_to_list", add_item["pythonName"], rel_path)
            keywords = {
                parameter["wfKey"]: parameter["pythonKeyword"]
                for parameter in add_item["parameters"]
            }
            self.assertEqual("item", keywords["WFListItem"], rel_path)
            self.assertEqual("list", keywords["WFListVariable"], rel_path)
            self.assertEqual("position", keywords["WFInsertPosition"], rel_path)
            self.assertEqual("index", keywords["WFItemIndex"], rel_path)

            syntax = catalog["shortcutsLanguageSyntaxSurface"]
            self.assertTrue(syntax["supportsElifSyntax"], rel_path)
            self.assertTrue(syntax["supportsListLiterals"], rel_path)
            self.assertEqual("is.workflow.actions.appendvariable", syntax["appendActionIdentifier"], rel_path)

    def test_toolkit_v78_parameter_key_catalog_is_packaged(self) -> None:
        for rel_path in self.PARAMETER_CATALOG_PATHS:
            catalog = load_json(REPO_ROOT / rel_path)

            self.assertEqual("toolkit-v78-first-party-parameter-keys", catalog["version"], rel_path)
            self.assertIn("Descriptions are intentionally omitted", catalog["scope"], rel_path)
            self.assertIn("typePythonNames", catalog["scope"], rel_path)
            self.assertEqual(2585, len(catalog["tools"]), rel_path)

            send_message = catalog["tools"]["com.apple.MobileSMS.SendMessageIntent"]
            self.assertEqual("messages_send_message", send_message["pythonName"], rel_path)
            self.assertEqual("Send Message", send_message["displayName"], rel_path)
            self.assertIn("macOS 27", send_message["platforms"], rel_path)
            self.assertIn("iOS 27 Simulator", send_message["platforms"], rel_path)
            self.assertEqual(8, send_message["parameterCount"], rel_path)
            self.assertEqual(send_message["parameterCount"], len(send_message["parameters"]), rel_path)
            parameter_keys = {parameter["key"] for parameter in send_message["parameters"]}
            self.assertIn("content", parameter_keys, rel_path)
            self.assertIn("scheduledDate", parameter_keys, rel_path)
            destination = next(
                parameter
                for parameter in send_message["parameters"]
                if parameter["key"] == "destination"
            )
            self.assertEqual(
                {
                    "com_apple_mobile_sms_conversation_entity",
                    "com_apple_mobile_sms_message_person",
                },
                set(destination["typePythonNames"]),
                rel_path,
            )
            self.assertTrue(
                all("description" not in parameter for parameter in send_message["parameters"]),
                rel_path,
            )

    def test_lookup_action_grounding_resolves_identifier_and_target_warning(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "additemtolist",
                    "--target-macos",
                    "26",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual("Requires macOS 27+; target macOS is 26.", payload["availabilityNote"], rel_path)
            self.assertEqual("is.workflow.actions.additemtolist", payload["results"][0]["identifier"], rel_path)
            self.assertEqual(27, payload["results"][0]["minimumMacOSMajor"], rel_path)
            self.assertEqual(
                "Requires macOS 27+; target macOS is 26.",
                payload["results"][0]["availabilityNote"],
                rel_path,
            )
            self.assertEqual(
                "WFListItem",
                next(
                    parameter["wfKey"]
                    for parameter in payload["results"][0]["parameters"]
                    if parameter["pythonKeyword"] == "item"
                ),
                rel_path,
            )

    def test_lookup_action_grounding_resolves_python_name(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--python-name",
                    "com_apple_shortcuts_add_item_to_list",
                    "--target-macos",
                    "27",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIsNone(payload["availabilityNote"], rel_path)
            self.assertEqual("is.workflow.actions.additemtolist", payload["results"][0]["identifier"], rel_path)

    def test_lookup_action_grounding_uses_toolkit_snapshots_for_availability(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "runshellscript",
                    "--target-macos",
                    "26",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIsNone(payload["availabilityNote"], rel_path)
            self.assertEqual("is.workflow.actions.runshellscript", payload["results"][0]["identifier"], rel_path)
            self.assertIsNone(payload["results"][0]["minimumMacOSMajor"], rel_path)
            self.assertIsNone(payload["results"][0]["availabilityNote"], rel_path)

    def test_lookup_action_grounding_falls_back_to_parameter_catalog(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.MobileSMS.SendMessageIntent",
                    "--target-macos",
                    "27",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            entry = payload["results"][0]
            self.assertEqual("com.apple.MobileSMS.SendMessageIntent", entry["identifier"], rel_path)
            self.assertEqual("toolkit-parameter-summary", entry["status"], rel_path)
            self.assertEqual("appIntent", entry["toolkitToolType"], rel_path)
            self.assertIn("macOS 27", entry["toolkitPlatforms"], rel_path)
            self.assertIn("iOS 27 Simulator", entry["toolkitPlatforms"], rel_path)
            parameter_keys = {
                parameter["key"]
                for parameter in entry["toolkitParameterSummary"]["parameters"]
            }
            self.assertIn("destination", parameter_keys, rel_path)
            self.assertIn("content", parameter_keys, rel_path)
            self.assertIn("scheduledDate", parameter_keys, rel_path)

    def test_lookup_action_grounding_marks_ios_only_parameter_catalog_entries(self) -> None:
        expected_note = (
            "Only observed in iOS 27 Simulator ToolKit; no macOS ToolKit row observed."
        )
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.HearingApp.MuteVolumeIntent",
                    "--target-macos",
                    "27",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            entry = payload["results"][0]
            self.assertIsNone(payload["availabilityNote"], rel_path)
            self.assertEqual(expected_note, payload["platformAvailabilityNote"], rel_path)
            self.assertEqual(expected_note, entry["platformAvailabilityNote"], rel_path)
            self.assertEqual(["iOS 27 Simulator"], entry["toolkitPlatforms"], rel_path)
            self.assertEqual("toolkit-parameter-summary", entry["status"], rel_path)

    def test_lookup_action_grounding_marks_macos_only_and_v78_parameter_metadata(self) -> None:
        platform_note = (
            "Only observed in macOS 27 ToolKit; no iOS 27 Simulator ToolKit row observed."
        )
        parameter_note = "Parameter metadata is from OS 27 ToolKit; target macOS is 26."
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.Safari.CreateNewTabGroup",
                    "--target-macos",
                    "26",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            entry = payload["results"][0]
            self.assertIsNone(payload["availabilityNote"], rel_path)
            self.assertEqual(parameter_note, payload["parameterMetadataAvailabilityNote"], rel_path)
            self.assertEqual(platform_note, payload["platformAvailabilityNote"], rel_path)
            self.assertIsNone(entry["minimumMacOSMajor"], rel_path)
            self.assertEqual(27, entry["parameterMetadataMinimumMacOSMajor"], rel_path)
            self.assertEqual(parameter_note, entry["parameterMetadataAvailabilityNote"], rel_path)
            self.assertEqual(platform_note, entry["platformAvailabilityNote"], rel_path)
            self.assertEqual(["macOS 27"], entry["toolkitPlatforms"], rel_path)
            contents = next(
                parameter
                for parameter in entry["toolkitParameterSummary"]["parameters"]
                if parameter["key"] == "contents"
            )
            self.assertEqual(
                {"URL", "com_apple_safari_tab_entity"},
                set(contents["typePythonNames"]),
                rel_path,
            )


class OS27AutomatorsReferenceTests(unittest.TestCase):
    def test_os27_action_parameter_updates_are_documented(self) -> None:
        required_action_terms = (
            "WFAllowWebSearch",
            "WFAvoidTolls",
            "WFAvoidHighways",
            "WFAppsExcept",
            "interpretAsMarkdown",
            "com.apple.mobilenotes.SharingExtension",
            "com.apple.Safari.CreateNewTabGroup",
            "Create Tab Group",
            "is.workflow.actions.getonscreencontext",
            "is.workflow.actions.getonscreencontent",
            "is.workflow.actions.extracttextfromimage",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/ACTIONS.md",
            "codex/skills/shortcuts-playground/ACTIONS.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in required_action_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")

    def test_os27_appintent_updates_are_documented(self) -> None:
        required_appintent_terms = (
            "com.apple.sociallayerd.CollaborationIntent",
            "com.apple.mobilenotes.SharingExtension",
            "com.apple.Safari.CreateNewTabGroup",
            "com.apple.MobileSMS.ChangeFilterModeIntent",
            "com.apple.MobileSMS.SearchMessagesIntent",
            "com.apple.Photos.OpenAssetIntent",
            "com.apple.reminders.CreateSectionAppIntent",
            "com.apple.HearingApp.AdjustVolumeIntent",
            "com.apple.HearingApp.MuteVolumeIntent",
            "com.apple.HearingApp.SelectPresetIntent",
            "HearingEarSelection",
            "VolumeDirection",
            "Set Switch Control Switch Set",
            "com.apple.systempreferences.OpenAccessibilitySwitchControlStaticDeepLinks",
            "switchControlSwitches",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent",
            "com.apple.systempreferences.AxFeatureSwitchcontrolEntity-UpdatableEntity",
            "Toggle Vehicle Motion Cues",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent",
            "com.apple.systempreferences.AxMotionCuesEnabledEntity-UpdatableEntity",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/APPINTENTS.md",
            "codex/skills/shortcuts-playground/APPINTENTS.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in required_appintent_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")


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
