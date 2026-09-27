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
            mode="${{SHORTCUTS_STUB_MODE:-success}}"
            count_file="$0.count"
            if [ "$mode" = "format-error-once" ] && [ ! -f "$count_file" ]; then
              printf '1' > "$count_file"
              printf '%s\\n' "{FORMAT_ERROR}" >&2
              exit 1
            fi
            if [ "$mode" = "format-error" ]; then
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
            macos_ids = module.load_packaged_toolkit_ids(skill_dir, target_macos_major=27)
            all_platform_ids = module.load_packaged_toolkit_ids(
                skill_dir,
                target_macos_major=27,
                target_platform=None,
            )

            self.assertIn("is.workflow.actions.gettext", macos_ids, rel_path)
            self.assertIn("is.workflow.actions.additemtolist", macos_ids, rel_path)
            self.assertIn("is.workflow.actions.getselectedtext", macos_ids, rel_path)
            self.assertIn("com.apple.Photos.FavoriteAssetsIntent", macos_ids, rel_path)
            self.assertNotIn("com.apple.mobileslideshow.FavoriteAssetsIntent", macos_ids, rel_path)
            self.assertNotIn("com.apple.HearingApp.AdjustVolumeIntent", macos_ids, rel_path)
            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", macos_ids, rel_path)
            self.assertNotIn("com.apple.HearingApp.SelectPresetIntent", macos_ids, rel_path)

            self.assertIn("com.apple.mobileslideshow.FavoriteAssetsIntent", all_platform_ids, rel_path)
            self.assertIn("com.apple.HearingApp.AdjustVolumeIntent", all_platform_ids, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", all_platform_ids, rel_path)
            self.assertIn("com.apple.HearingApp.SelectPresetIntent", all_platform_ids, rel_path)

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
            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", allowed_27, rel_path)
            self.assertEqual(
                "iOS 27+ (toolkit-v78-ios27)",
                future_26.get("com.apple.HearingApp.MuteVolumeIntent"),
                rel_path,
            )
            self.assertEqual(
                "iOS-only (toolkit-v78-ios27); target platform is macOS",
                module.load_future_toolkit_id_reasons(skill_dir, 27).get(
                    "com.apple.HearingApp.MuteVolumeIntent"
                ),
                rel_path,
            )

    def test_workflow_triggers_are_structurally_validated_and_target_gated(self) -> None:
        def base_plist(trigger: dict) -> dict:
            return {
                "WFWorkflowActions": [
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "UUID": "C38165B8-8776-4988-AF7B-315204D9D71A",
                            "WFCommentActionText": "OS 27 automation trigger validation fixture.",
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "UUID": "D6B4D562-79E3-4C97-872A-A944F38B4E3F",
                            "WFCommentActionText": (
                                "Shortcuts generated by Shortcuts Playground. "
                                "May contain mistakes. Always check the shortcut's actions first."
                            ),
                        },
                    },
                ],
                "WFWorkflowIcon": {
                    "WFWorkflowIconGlyphNumber": 61440,
                    "WFWorkflowIconStartColor": 431817727,
                },
                "WFWorkflowInputContentItemClasses": [],
                "WFWorkflowOutputContentItemClasses": [],
                "WFWorkflowTypes": [],
                "WFWorkflowTriggers": [trigger],
            }

        valid_trigger = {
            "WFTriggerIdentifier": "WFLowPowerModeTrigger",
            "WFTriggerSerializedParameters": {"WFLowPowerModeType": "both"},
            "WFTriggerUUID": "5BE2B672-086C-4DB2-91E5-64021E6AA5F2",
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "workflow_trigger_catalog": module.load_workflow_trigger_catalog(
                    skill_dir,
                    target_macos_major=27,
                ),
                "target_macos_major": 27,
            }

            valid_errors, _ = module.validate(base_plist(valid_trigger), **common_kwargs)
            self.assertFalse(
                [error for error in valid_errors if "WFWorkflowTriggers" in error],
                f"{rel_path}: {valid_errors}",
            )

            macos26_errors, _ = module.validate(
                base_plist(valid_trigger),
                allowed_ids=module.load_allowed_ids(skill_dir, target_macos_major=26),
                workflow_trigger_catalog=module.load_workflow_trigger_catalog(
                    skill_dir,
                    target_macos_major=26,
                ),
                target_macos_major=26,
            )
            self.assertTrue(
                any("WFWorkflowTriggers requires macOS/iOS 27+" in error for error in macos26_errors),
                f"{rel_path}: {macos26_errors}",
            )

            missing_uuid = dict(valid_trigger)
            missing_uuid.pop("WFTriggerUUID")
            missing_uuid_errors, _ = module.validate(base_plist(missing_uuid), **common_kwargs)
            self.assertTrue(
                any("missing required key(s): WFTriggerUUID" in error for error in missing_uuid_errors),
                f"{rel_path}: {missing_uuid_errors}",
            )

            placeholder_trigger = {
                "WFTriggerIdentifier": "WFWifiTrigger",
                "WFTriggerSerializedParameters": {
                    "WFNetworks": {"$placeholder": "user-selected Wi-Fi network name"}
                },
                "WFTriggerUUID": "86292079-FE94-4A96-B6FD-53B35F66378B",
            }
            placeholder_errors, _ = module.validate(
                base_plist(placeholder_trigger),
                **common_kwargs,
            )
            self.assertTrue(
                any("catalog placeholder values" in error for error in placeholder_errors),
                f"{rel_path}: {placeholder_errors}",
            )

            bad_key_trigger = {
                "WFTriggerIdentifier": "WFLowPowerModeTrigger",
                "WFTriggerSerializedParameters": {"WrongKey": "both"},
                "WFTriggerUUID": "E71E827E-6C5C-4509-824A-EB9018BA4F9B",
            }
            bad_key_errors, _ = module.validate(base_plist(bad_key_trigger), **common_kwargs)
            self.assertTrue(
                any("unknown key(s) for WFLowPowerModeTrigger" in error for error in bad_key_errors),
                f"{rel_path}: {bad_key_errors}",
            )

            for picker_identifier in (
                "WFDiskMountTrigger",
                "WFFileTrigger",
                "WFFolderTrigger",
            ):
                picker_trigger = {
                    "WFTriggerIdentifier": picker_identifier,
                    "WFTriggerSerializedParameters": {},
                    "WFTriggerUUID": "4F9319DF-F6D4-41A2-A549-8DDB157404D7",
                }
                picker_errors, _ = module.validate(
                    base_plist(picker_trigger),
                    **common_kwargs,
                )
                self.assertTrue(
                    any("lossy empty trigger dictionary" in error for error in picker_errors),
                    f"{rel_path}: {picker_identifier}: {picker_errors}",
                )

    def test_ios27_toolkit_ids_require_ios_or_all_target_platform(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            macos_ids = module.load_allowed_ids(skill_dir, target_macos_major=27)
            ios_ids = module.load_allowed_ids(
                skill_dir,
                target_macos_major=27,
                target_platform="ios",
            )
            all_ids = module.load_allowed_ids(
                skill_dir,
                target_macos_major=27,
                target_platform=None,
            )

            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", macos_ids, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", ios_ids, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", all_ids, rel_path)
            self.assertIn("com.apple.Safari.CreateNewTabGroup", macos_ids, rel_path)
            self.assertNotIn("com.apple.Safari.CreateNewTabGroup", ios_ids, rel_path)
            self.assertNotIn("com.apple.mobilesafari.CreateNewTabGroup", macos_ids, rel_path)
            self.assertIn("com.apple.mobilesafari.CreateNewTabGroup", ios_ids, rel_path)
            self.assertIn("com.apple.mobilesafari.CreateNewTabGroup", all_ids, rel_path)
            self.assertIn("com.apple.Photos.FavoriteAssetsIntent", macos_ids, rel_path)
            self.assertNotIn("com.apple.Photos.FavoriteAssetsIntent", ios_ids, rel_path)
            self.assertNotIn("com.apple.mobileslideshow.FavoriteAssetsIntent", macos_ids, rel_path)
            self.assertIn("com.apple.mobileslideshow.FavoriteAssetsIntent", ios_ids, rel_path)
            self.assertIn("com.apple.mobileslideshow.FavoriteAssetsIntent", all_ids, rel_path)

    def test_toolkit_parameter_schemas_are_target_gated(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            macos_schemas = module.load_toolkit_parameter_schemas(
                skill_dir,
                target_macos_major=27,
            )
            ios_schemas = module.load_toolkit_parameter_schemas(
                skill_dir,
                target_macos_major=27,
                target_platform="ios",
            )
            macos_26_schemas = module.load_toolkit_parameter_schemas(
                skill_dir,
                target_macos_major=26,
            )

            self.assertIn("com.apple.MobileSMS.SendMessageIntent", macos_schemas, rel_path)
            self.assertIn("content", macos_schemas["com.apple.MobileSMS.SendMessageIntent"], rel_path)
            self.assertNotIn("com.apple.HearingApp.MuteVolumeIntent", macos_schemas, rel_path)
            self.assertIn("com.apple.HearingApp.MuteVolumeIntent", ios_schemas, rel_path)
            self.assertIn("com.apple.Safari.CreateNewTabGroup", macos_schemas, rel_path)
            self.assertNotIn("com.apple.Safari.CreateNewTabGroup", ios_schemas, rel_path)
            self.assertNotIn("com.apple.mobilesafari.CreateNewTabGroup", macos_schemas, rel_path)
            self.assertIn("com.apple.mobilesafari.CreateNewTabGroup", ios_schemas, rel_path)
            self.assertIn("com.apple.Photos.FavoriteAssetsIntent", macos_schemas, rel_path)
            self.assertNotIn("com.apple.Photos.FavoriteAssetsIntent", ios_schemas, rel_path)
            self.assertNotIn("com.apple.mobileslideshow.FavoriteAssetsIntent", macos_schemas, rel_path)
            self.assertIn("com.apple.mobileslideshow.FavoriteAssetsIntent", ios_schemas, rel_path)
            self.assertIn("com.apple.mail.MailMessage", macos_schemas, rel_path)
            self.assertIn("com.apple.mail.MailMessageEntity", macos_schemas, rel_path)
            self.assertEqual(
                {"ShowWhenRun"},
                macos_schemas["com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent"],
                rel_path,
            )
            self.assertEqual(
                {"ShowWhenRun", "device", "appearanceToggle"},
                ios_schemas["com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent"],
                rel_path,
            )
            self.assertIn("OpenWhenRun", macos_schemas["com.apple.Preview.FlipIntent"], rel_path)
            self.assertNotIn("OpenWhenRun", ios_schemas["com.apple.Preview.FlipIntent"], rel_path)
            self.assertEqual(
                {"WFShazamMediaActionShowWhenRun", "WFShazamMediaActionErrorIfNotRecognized"},
                macos_schemas["com.apple.musicrecognition.RecognizeMusicIntent"],
                rel_path,
            )
            self.assertEqual(
                {"addToLibrary", "errorIfNotRecognized"},
                ios_schemas["com.apple.musicrecognition.RecognizeMusicIntent"],
                rel_path,
            )
            self.assertEqual({}, macos_26_schemas, rel_path)

    def test_toolkit_parameter_enum_cases_are_target_gated(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            macos_enum_cases = module.load_toolkit_parameter_enum_cases(
                skill_dir,
                target_macos_major=27,
            )
            ios_enum_cases = module.load_toolkit_parameter_enum_cases(
                skill_dir,
                target_macos_major=27,
                target_platform="ios",
            )
            macos_26_enum_cases = module.load_toolkit_parameter_enum_cases(
                skill_dir,
                target_macos_major=26,
            )

            self.assertEqual({}, macos_26_enum_cases, rel_path)
            self.assertEqual(
                {"person", "organization"},
                macos_enum_cases["com.apple.AddressBook.CreateContactIntent"]["contactType"],
                rel_path,
            )
            self.assertEqual(
                {
                    "WTUIRequestedToolRewriting",
                    "WTUIRequestedToolRewriteFriendly",
                    "WTUIRequestedToolRewriteProfessional",
                    "WTUIRequestedToolRewriteConcise",
                    "WTUIRequestedToolRewriteOpenEnded",
                    "WTUIRequestedToolSummary",
                    "WTUIRequestedToolTransformKeyPoints",
                    "WTUIRequestedToolTransformList",
                    "WTUIRequestedToolTransformTable",
                    "WTUIRequestedToolCompose",
                    "WTUIRequestedToolProofreading",
                },
                macos_enum_cases["com.apple.AppKit.WritingToolsRewriteIntent"]["type"],
                rel_path,
            )
            self.assertEqual(
                {"favorite", "unfavorite"},
                macos_enum_cases["com.apple.Photos.FavoriteAssetsIntent"]["action"],
                rel_path,
            )
            self.assertEqual(
                {"hide", "unhide"},
                macos_enum_cases["com.apple.Photos.HideAssetsIntent"]["action"],
                rel_path,
            )
            self.assertEqual(
                {"MD5", "SHA1", "SHA256", "SHA512"},
                macos_enum_cases["is.workflow.actions.hash"]["WFHashType"],
                rel_path,
            )
            self.assertEqual(
                {"GET", "POST", "PUT", "PATCH", "DELETE"},
                macos_enum_cases["is.workflow.actions.downloadurl"]["WFHTTPMethod"],
                rel_path,
            )
            self.assertEqual(
                {"mark", "toggle"},
                macos_enum_cases["com.apple.MobileSMS.MarkConversationAsUnreadIntent"]["operation"],
                rel_path,
            )
            self.assertEqual(
                {"standard", "groceries"},
                macos_enum_cases["com.apple.reminders.TTRCreateListAppIntent"]["type"],
                rel_path,
            )
            self.assertEqual(
                {"both", "personal", "shared"},
                macos_enum_cases["com.apple.Photos.FilterLibraryIntent"]["viewMode"],
                rel_path,
            )
            self.assertEqual(
                {
                    "sunday",
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                },
                macos_enum_cases[
                    "com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent"
                ]["repeats"],
                rel_path,
            )
            self.assertEqual(
                {
                    "BalancedNoise",
                    "BrightNoise",
                    "DarkNoise",
                    "Ocean",
                    "Rain",
                    "Stream",
                    "Babble",
                    "Steam",
                    "Airplane",
                    "Boat",
                    "Bus",
                    "Train",
                    "RainOnRoof",
                    "QuietNight",
                    "Fire",
                    "Night",
                },
                macos_enum_cases[
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent"
                ]["backgroundSound"],
                rel_path,
            )
            self.assertEqual(
                {"endInterval", "duration"},
                macos_enum_cases[
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent"
                ]["interval"],
                rel_path,
            )
            self.assertEqual(
                {"turn", "toggle"},
                macos_enum_cases[
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent"
                ]["operation"],
                rel_path,
            )
            self.assertNotIn(
                "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                macos_enum_cases,
                rel_path,
            )
            self.assertEqual(
                {"light", "dark"},
                ios_enum_cases["com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent"][
                    "appearanceToggle"
                ],
                rel_path,
            )
            self.assertEqual(
                {"set", "toggle"},
                macos_enum_cases["com.apple.NanoSettings.NPRFSetAlwaysOnIntent"]["operation"],
                rel_path,
            )
    def test_toolkit_enum_and_boolean_validation_covers_classic_wf_actions(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.hash",
                    "WFWorkflowActionParameters": {
                        "WFHashType": "SHA999",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.alert",
                    "WFWorkflowActionParameters": {
                        "WFAlertActionTitle": "Heads up",
                        "WFAlertActionMessage": "Testing",
                        "WFAlertActionCancelButtonShown": "true",
                    },
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.hash",
                    "WFWorkflowActionParameters": {
                        "WFHashType": "SHA256",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.alert",
                    "WFWorkflowActionParameters": {
                        "WFAlertActionTitle": "Heads up",
                        "WFAlertActionMessage": "Testing",
                        "WFAlertActionCancelButtonShown": True,
                    },
                },
            ],
        }
        dynamic_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.hash",
                    "WFWorkflowActionParameters": {
                        "WFHashType": {
                            "Value": {
                                "Type": "Variable",
                                "VariableName": "Hash Type",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.alert",
                    "WFWorkflowActionParameters": {
                        "WFAlertActionTitle": "Heads up",
                        "WFAlertActionMessage": "Testing",
                        "WFAlertActionCancelButtonShown": {
                            "Value": {"Type": "Ask"},
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                },
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_enum_cases": module.load_toolkit_parameter_enum_cases(
                    skill_dir,
                    target_macos_major=27,
                ),
                "toolkit_parameter_boolean_keys": module.load_toolkit_parameter_boolean_keys(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [
                    error
                    for error in invalid_errors
                    if "Invalid ToolKit enum value" in error
                    and "is.workflow.actions.hash.WFHashType" in error
                    and "SHA999" in error
                ],
                f"{rel_path}: {invalid_errors}",
            )
            self.assertTrue(
                [
                    error
                    for error in invalid_errors
                    if "Invalid ToolKit boolean value" in error
                    and "is.workflow.actions.alert.WFAlertActionCancelButtonShown" in error
                ],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "Invalid ToolKit enum value" in error
                    or "Invalid ToolKit boolean value" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

            dynamic_errors, _ = module.validate(dynamic_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in dynamic_errors
                    if "Invalid ToolKit enum value" in error
                    or "Invalid ToolKit boolean value" in error
                ],
                f"{rel_path}: {dynamic_errors}",
            )

    def test_math_operation_uses_shortcuts_operator_encoding(self) -> None:
        number_uuid = "7F3A4E91-C2D8-4B56-BE5A-0242AC120002"
        math_uuid = "93AE54B1-53C0-4EAF-8B4F-53FA44B27A9E"

        def math_plist(operation: str | None) -> dict:
            math_params = {
                "UUID": math_uuid,
                "WFInput": {
                    "WFSerializationType": "WFTextTokenAttachment",
                    "Value": {
                        "Type": "ActionOutput",
                        "OutputUUID": number_uuid,
                        "OutputName": "Number",
                    },
                },
                "WFMathOperand": "2",
            }
            if operation is not None:
                math_params["WFMathOperation"] = operation
            return {
                "WFWorkflowActions": [
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.number",
                        "WFWorkflowActionParameters": {
                            "UUID": number_uuid,
                            "WFNumberActionNumber": "10",
                        },
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.math",
                        "WFWorkflowActionParameters": math_params,
                    },
                ]
            }

        invalid_cases = {
            "+": "omit WFMathOperation for addition",
            "*": "use '×' (U+00D7) for multiplication",
            "/": "use '÷' (U+00F7) for division",
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            allowed_ids = module.load_allowed_ids(skill_dir, target_macos_major=27)

            for operation, expected in invalid_cases.items():
                errors = module.validate(math_plist(operation), allowed_ids=allowed_ids)[0]
                self.assertTrue(
                    [error for error in errors if expected in error],
                    f"{rel_path}: {operation}: {errors}",
                )

            for operation in (None, "-", "×", "÷"):
                errors = module.validate(math_plist(operation), allowed_ids=allowed_ids)[0]
                self.assertFalse(
                    [error for error in errors if "Math action uses" in error],
                    f"{rel_path}: {operation}: {errors}",
                )

    def test_appintent_parameter_schema_rejects_unknown_com_apple_keys(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.MobileSMS.SendMessageIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.MobileSMS.SendMessageIntent"
                        },
                        "content": "Hello",
                        "contents": "Typo should be content",
                    },
                }
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.MobileSMS.SendMessageIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.MobileSMS.SendMessageIntent"
                        },
                        "content": "Hello",
                    },
                }
            ],
        }
        legacy_wf_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
                    "WFWorkflowActionParameters": {
                        "WFURL": "https://example.com",
                        "Advanced": False,
                        "ShowHeaders": False,
                    },
                }
            ],
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
                "toolkit_parameter_enum_cases": module.load_toolkit_parameter_enum_cases(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [
                    error
                    for error in invalid_errors
                    if "Unknown AppIntent parameter key(s)" in error and "contents" in error
                ],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [error for error in valid_errors if "Unknown AppIntent parameter key(s)" in error],
                f"{rel_path}: {valid_errors}",
            )

            legacy_errors, _ = module.validate(legacy_wf_plist, **common_kwargs)
            self.assertFalse(
                [error for error in legacy_errors if "Unknown AppIntent parameter key(s)" in error],
                f"{rel_path}: {legacy_errors}",
            )

    def test_appintent_parameter_enum_cases_reject_invalid_literal_values(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.AddressBook.CreateContactIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.AddressBook.CreateContactIntent"
                        },
                        "contactType": "company",
                    },
                }
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.AddressBook.CreateContactIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.AddressBook.CreateContactIntent"
                        },
                        "contactType": "organization",
                    },
                }
            ],
        }
        dynamic_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.AddressBook.CreateContactIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.AddressBook.CreateContactIntent"
                        },
                        "contactType": {
                            "Value": {
                                "Type": "Variable",
                                "VariableName": "Contact Type",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                }
            ],
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
                "toolkit_parameter_enum_cases": module.load_toolkit_parameter_enum_cases(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [
                    error
                    for error in invalid_errors
                    if "Invalid AppIntent enum value" in error
                    and "contactType" in error
                    and "company" in error
                ],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [error for error in valid_errors if "Invalid AppIntent enum value" in error],
                f"{rel_path}: {valid_errors}",
            )

            dynamic_errors, _ = module.validate(dynamic_plist, **common_kwargs)
            self.assertFalse(
                [error for error in dynamic_errors if "Invalid AppIntent enum value" in error],
                f"{rel_path}: {dynamic_errors}",
            )

    def test_appintent_actions_require_descriptor(self) -> None:
        missing_descriptor = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.MobileSMS.SendMessageIntent",
                    "WFWorkflowActionParameters": {
                        "content": "Hello",
                    },
                }
            ],
        }
        missing_identifier = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.MobileSMS.SendMessageIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {},
                        "content": "Hello",
                    },
                }
            ],
        }
        valid_descriptor = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.MobileSMS.SendMessageIntent",
                    "WFWorkflowActionParameters": {
                        "AppIntentDescriptor": {
                            "AppIntentIdentifier": "com.apple.MobileSMS.SendMessageIntent"
                        },
                        "content": "Hello",
                    },
                }
            ],
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            missing_descriptor_errors, _ = module.validate(missing_descriptor, **common_kwargs)
            self.assertTrue(
                [
                    error
                    for error in missing_descriptor_errors
                    if "AppIntent action missing AppIntentDescriptor" in error
                ],
                f"{rel_path}: {missing_descriptor_errors}",
            )

            missing_identifier_errors, _ = module.validate(missing_identifier, **common_kwargs)
            self.assertTrue(
                [
                    error
                    for error in missing_identifier_errors
                    if "AppIntentDescriptor missing AppIntentIdentifier" in error
                ],
                f"{rel_path}: {missing_identifier_errors}",
            )

            valid_descriptor_errors, _ = module.validate(valid_descriptor, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_descriptor_errors
                    if "AppIntentDescriptor" in error
                ],
                f"{rel_path}: {valid_descriptor_errors}",
            )

    def test_os27_stored_content_actions_require_key_and_store_input(self) -> None:
        source_uuid = "12345678-1234-4234-9234-123456789ABC"
        key_uuid = "22345678-1234-4234-9234-123456789ABC"
        source_attachment = {
            "Value": {
                "OutputName": "Text",
                "OutputUUID": source_uuid,
                "Type": "ActionOutput",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        }
        source_wrapped_attachment = {
            "Type": "Variable",
            "Variable": source_attachment,
        }
        source_token_string = {
            "Value": {
                "attachmentsByRange": {
                    "{0, 1}": {
                        "OutputName": "Text",
                        "OutputUUID": source_uuid,
                        "Type": "ActionOutput",
                    }
                },
                "string": "\ufffc",
            },
            "WFSerializationType": "WFTextTokenString",
        }
        source_token_string_with_literal = {
            "Value": {
                "attachmentsByRange": {
                    "{7, 1}": {
                        "OutputName": "Text",
                        "OutputUUID": source_uuid,
                        "Type": "ActionOutput",
                    }
                },
                "string": "Value: \ufffc",
            },
            "WFSerializationType": "WFTextTokenString",
        }
        tokenized_key = {
            "Value": {
                "attachmentsByRange": {
                    "{0, 1}": {
                        "OutputName": "Text",
                        "OutputUUID": key_uuid,
                        "Type": "ActionOutput",
                    }
                },
                "string": "\ufffc",
            },
            "WFSerializationType": "WFTextTokenString",
        }
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.setstoredcontent",
                    "WFWorkflowActionParameters": {
                        "WFStoredContentGlobalValue": "true",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getstoredcontent",
                    "WFWorkflowActionParameters": {
                        "WFStoredContentKey": "",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.deletestoredcontent",
                    "WFWorkflowActionParameters": {},
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                    "WFWorkflowActionParameters": {
                        "UUID": source_uuid,
                        "WFTextActionText": "Stored value",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                    "WFWorkflowActionParameters": {
                        "UUID": key_uuid,
                        "WFTextActionText": "shortcut-key",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.setstoredcontent",
                    "WFWorkflowActionParameters": {
                        "WFInput": source_token_string,
                        "WFStoredContentGlobalValue": False,
                        "WFStoredContentKey": tokenized_key,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getstoredcontent",
                    "WFWorkflowActionParameters": {
                        "WFStoredContentGlobalValue": False,
                        "WFStoredContentKey": "shortcut-key",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.deletestoredcontent",
                    "WFWorkflowActionParameters": {
                        "WFStoredContentGlobalValue": False,
                        "WFStoredContentKey": "shortcut-key",
                    },
                },
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [error for error in invalid_errors if "Missing WFInput" in error],
                f"{rel_path}: {invalid_errors}",
            )
            self.assertEqual(
                3,
                sum("Stored Content action missing WFStoredContentKey" in error for error in invalid_errors),
                f"{rel_path}: {invalid_errors}",
            )
            self.assertTrue(
                [error for error in invalid_errors if "WFStoredContentGlobalValue must be boolean" in error],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "Stored Content action" in error
                    or "WFStoredContentGlobalValue" in error
                    or (
                        "Missing WFInput" in error
                        and "is.workflow.actions.setstoredcontent" in error
                    )
                ],
                f"{rel_path}: {valid_errors}",
            )

            for name, bad_input in (
                ("bare attachment", source_attachment),
                ("wrapped attachment", source_wrapped_attachment),
                ("literal token string", source_token_string_with_literal),
            ):
                bad_attachment = {
                    "WFWorkflowActions": [
                        valid_plist["WFWorkflowActions"][0],
                        {
                            "WFWorkflowActionIdentifier": "is.workflow.actions.setstoredcontent",
                            "WFWorkflowActionParameters": {
                                "WFInput": bad_input,
                                "WFStoredContentGlobalValue": False,
                                "WFStoredContentKey": "shortcut-key",
                            },
                        },
                    ],
                }
                bad_attachment_errors, _ = module.validate(bad_attachment, **common_kwargs)
                self.assertTrue(
                    [
                        error
                        for error in bad_attachment_errors
                        if "exactly one object placeholder" in error
                        and "bare or wrapped token attachments import as an empty Content parameter" in error
                    ],
                    f"{rel_path} {name}: {bad_attachment_errors}",
                )

    def test_os27_get_on_screen_context_parameters_are_validated(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getonscreencontext",
                    "WFWorkflowActionParameters": {
                        "WFOnScreenContextScope": "Everything",
                        "WFOnScreenContextLimitEnabled": "true",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getonscreencontext",
                    "WFWorkflowActionParameters": {
                        "WFOnScreenContextScope": "Focused App Only",
                        "WFOnScreenContextLimitEnabled": True,
                        "WFOnScreenContextLimit": 0,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getonscreencontext",
                    "WFWorkflowActionParameters": {
                        "WFOnScreenContextScope": "All Visible",
                        "WFOnScreenContextLimitEnabled": True,
                    },
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getonscreencontext",
                    "WFWorkflowActionParameters": {
                        "WFOnScreenContextResultType": "Text",
                        "WFOnScreenContextScope": "All Visible",
                        "WFOnScreenContextLimitEnabled": True,
                        "WFOnScreenContextLimit": 3,
                    },
                }
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [error for error in invalid_errors if "unknown WFOnScreenContextScope" in error],
                f"{rel_path}: {invalid_errors}",
            )
            self.assertTrue(
                [error for error in invalid_errors if "WFOnScreenContextLimitEnabled must be boolean" in error],
                f"{rel_path}: {invalid_errors}",
            )
            self.assertTrue(
                [error for error in invalid_errors if "limit is enabled but missing WFOnScreenContextLimit" in error],
                f"{rel_path}: {invalid_errors}",
            )
            self.assertTrue(
                [error for error in invalid_errors if "WFOnScreenContextLimit must be greater than 0" in error],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "WFOnScreenContext" in error
                    or "Get What's On Screen limit" in error
                    or "Get What's On Screen has unknown" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

    def test_os27_vpn_parameters_are_validated(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.filter.vpns",
                    "WFWorkflowActionParameters": {
                        "WFContentItemSortProperty": "Status",
                        "WFContentItemInputParameter": "Selected Items",
                        "WFCompoundType": "Either",
                        "WFContentItemLimitEnabled": "true",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.filter.vpns",
                    "WFWorkflowActionParameters": {
                        "WFContentItemSortProperty": "Name",
                        "WFCompoundType": "All",
                        "WFContentItemLimitEnabled": True,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.filter.vpns",
                    "WFWorkflowActionParameters": {
                        "WFContentItemSortProperty": "Server Address",
                        "WFContentItemLimitEnabled": True,
                        "WFContentItemLimitNumber": 0,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.vpn.set",
                    "WFWorkflowActionParameters": {},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.vpn.set",
                    "WFWorkflowActionParameters": {
                        "WFVPNOperation": "Enable",
                        "WFVPN": "Work VPN",
                        "WFOnDemandValue": "true",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.vpn.set",
                    "WFWorkflowActionParameters": {
                        "WFVPNOperation": "Set On Demand",
                        "WFVPN": "Work VPN",
                    },
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.filter.vpns",
                    "WFWorkflowActionParameters": {
                        "WFContentItemSortProperty": "Server Address",
                        "WFContentItemSortOrder": "A to Z",
                        "WFContentItemLimitEnabled": True,
                        "WFContentItemLimitNumber": 3,
                        "WFCompoundType": "All",
                        "WFContentItemInputParameter": "Library",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.vpn.set",
                    "WFWorkflowActionParameters": {
                        "WFVPNOperation": "Set On Demand",
                        "WFVPN": "Work VPN",
                        "WFOnDemandValue": False,
                    },
                },
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            for expected in (
                "unknown WFContentItemSortProperty",
                "unknown WFContentItemInputParameter",
                "unknown WFCompoundType",
                "WFContentItemLimitEnabled must be boolean",
                "limit is enabled but missing WFContentItemLimitNumber",
                "WFContentItemLimitNumber must be greater than 0",
                "Set VPN missing WFVPNOperation",
                "Set VPN missing WFVPN",
                "unknown WFVPNOperation",
                "WFOnDemandValue must be boolean",
                "Set On Demand missing WFOnDemandValue",
            ):
                self.assertTrue(
                    [error for error in invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {invalid_errors}",
                )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "Find VPNs" in error
                    or "Set VPN" in error
                    or "WFOnDemandValue" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

    def test_os27_list_action_parameters_are_validated(self) -> None:
        list_uuid = "11111111-2222-4333-9444-555555555555"

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

        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.list",
                    "WFWorkflowActionParameters": {"UUID": list_uuid},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Orange",
                        "WFListVariable": action_output(list_uuid),
                        "WFInsertPosition": "Middle",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Orange",
                        "WFListVariable": action_output(list_uuid),
                        "WFInsertPosition": "Index",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Orange",
                        "WFListVariable": action_output(list_uuid),
                        "WFInsertPosition": "Index",
                        "WFItemIndex": "zero",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Orange",
                        "WFListVariable": action_output(list_uuid),
                        "WFInsertPosition": "End",
                        "WFItemIndex": 2,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
                    "WFWorkflowActionParameters": {
                        "WFInput": action_output(list_uuid),
                        "WFChooseFromListActionSelectMultiple": "true",
                        "WFChooseFromListActionSelectAll": "false",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
                    "WFWorkflowActionParameters": {
                        "WFInput": action_output(list_uuid),
                        "WFChooseFromListActionSelectMultiple": False,
                        "WFChooseFromListActionSelectAll": True,
                    },
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.list",
                    "WFWorkflowActionParameters": {"UUID": list_uuid},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Pear",
                        "WFListVariable": action_output(list_uuid),
                        "WFInsertPosition": "End",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.additemtolist",
                    "WFWorkflowActionParameters": {
                        "WFListItem": "Orange",
                        "WFListVariable": variable_attachment("Fruit List"),
                        "WFInsertPosition": "Index",
                        "WFItemIndex": 1,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
                    "WFWorkflowActionParameters": {
                        "WFInput": action_output(list_uuid),
                        "WFChooseFromListActionPrompt": "Pick a fruit",
                        "WFChooseFromListActionSelectMultiple": True,
                        "WFChooseFromListActionSelectAll": False,
                    },
                },
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            for expected in (
                "Add Item to List missing WFListItem",
                "Add Item to List missing WFListVariable",
                "Add Item to List has unknown WFInsertPosition",
                "Add Item to List position Index missing WFItemIndex",
                "Add Item to List WFItemIndex must be an integer",
                "Add Item to List WFItemIndex is only valid when WFInsertPosition is Index",
                "WFChooseFromListActionSelectMultiple must be boolean",
                "WFChooseFromListActionSelectAll must be boolean",
                "WFChooseFromListActionSelectAll requires WFChooseFromListActionSelectMultiple",
            ):
                self.assertTrue(
                    [error for error in invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {invalid_errors}",
                )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "Add Item to List" in error
                    or "WFChooseFromListActionSelect" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

    def test_auto_target_macos_falls_back_to_26_when_host_unknown(self) -> None:
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, _ = self.load_validator_module(rel_path)
            original = module.detect_host_macos_major
            try:
                module.detect_host_macos_major = lambda: None
                self.assertEqual(26, module.resolve_target_macos_major("auto"), rel_path)
                self.assertEqual(26, module.resolve_target_macos_major(None), rel_path)
                self.assertIsNone(module.resolve_target_macos_major("latest"), rel_path)
            finally:
                module.detect_host_macos_major = original

    def test_os27_parameter_keys_are_target_gated(self) -> None:
        expected = {
            "com.apple.Safari.CreateNewTabGroup": {"contents"},
            "com.apple.mobilesafari.CreateNewTabGroup": {"contents"},
            "com.apple.mobilenotes.SharingExtension": {"interpretAsMarkdown"},
            "is.workflow.actions.appendnote": {
                "ignoreWhitespace",
                "interpretAsMarkdown",
                "section",
            },
            "is.workflow.actions.askllm": {"FollowUp", "WFAllowWebSearch"},
            "is.workflow.actions.extracttextfromimage": {"imageFile"},
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

    def test_extract_from_image_accepts_os27_image_file_key(self) -> None:
        image_uuid = "12345678-1234-4234-9234-123456789ABC"
        image_attachment = {
            "Value": {
                "OutputName": "File",
                "OutputUUID": image_uuid,
                "Type": "ActionOutput",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        }
        plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getfile",
                    "WFWorkflowActionParameters": {
                        "UUID": image_uuid,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.extracttextfromimage",
                    "WFWorkflowActionParameters": {
                        "imageFile": image_attachment,
                    },
                },
            ],
            "WFWorkflowIcon": {
                "WFWorkflowIconGlyphNumber": 61440,
                "WFWorkflowIconStartColor": 431817727,
            },
            "WFWorkflowName": "Extract from Image Regression",
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            errors_27, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=27),
                unavailable_ids=module.load_future_toolkit_id_reasons(skill_dir, 27),
                unavailable_parameter_keys=module.load_future_parameter_key_reasons(27),
            )
            self.assertFalse(
                [error for error in errors_27 if "Extract Text from Image" in error],
                f"{rel_path}: {errors_27}",
            )

            errors_26, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=26),
                unavailable_ids=module.load_future_toolkit_id_reasons(skill_dir, 26),
                unavailable_parameter_keys=module.load_future_parameter_key_reasons(26),
            )
            self.assertTrue(
                [
                    error
                    for error in errors_26
                    if "Parameter 'imageFile' on is.workflow.actions.extracttextfromimage requires macOS 27+"
                    in error
                ],
                f"{rel_path}: {errors_26}",
            )

    def test_os27_updated_parameter_values_are_validated(self) -> None:
        image_uuid = "12345678-1234-4234-9234-123456789ABC"
        image_attachment = {
            "Value": {
                "OutputName": "File",
                "OutputUUID": image_uuid,
                "Type": "ActionOutput",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        }
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.appendnote",
                    "WFWorkflowActionParameters": {
                        "operation": "replace",
                        "ignoreWhitespace": "true",
                        "interpretAsMarkdown": "false",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.mobilenotes.SharingExtension",
                    "WFWorkflowActionParameters": {"interpretAsMarkdown": "true"},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.askllm",
                    "WFWorkflowActionParameters": {
                        "FollowUp": "no",
                        "WFAllowWebSearch": "yes",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.addnewreminder",
                    "WFWorkflowActionParameters": {"WFUrgent": "true"},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.searchlocalbusinesses",
                    "WFWorkflowActionParameters": {"WFSearchSortOrder": "Nearest"},
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetBatteryChargeLimitAction",
                    "WFWorkflowActionParameters": {"setUntilTomorrow": "yes"},
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetMultitaskingModeAction",
                    "WFWorkflowActionParameters": {
                        "mode": "splitView",
                        "automaticallyShowAndHideDock": "false",
                        "showRecentApps": "true",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetMultitaskingModeAction",
                    "WFWorkflowActionParameters": {
                        "mode": {
                            "identifier": "splitView",
                            "value": "splitView",
                            "title": {"key": "Split View"},
                            "subtitle": {"key": "Split View"},
                        },
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getdistance",
                    "WFWorkflowActionParameters": {
                        "WFGetDirectionsActionMode": "Flying",
                        "WFAvoidTolls": "true",
                        "WFDistanceUnit": "Meters",
                        "Accuracy": "NearestFiveMeters",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettraveltime",
                    "WFWorkflowActionParameters": {
                        "WFGetDirectionsActionMode": "Direct",
                        "WFAvoidHighways": "false",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.scanbarcode",
                    "WFWorkflowActionParameters": {"imageFile": ""},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.scanbarcode",
                    "WFWorkflowActionParameters": {"imageFile": "literal path"},
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.Safari.CreateNewTabGroup",
                    "WFWorkflowActionParameters": {"contents": ""},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.hide.app",
                    "WFWorkflowActionParameters": {
                        "WFHideAppMode": "Window",
                        "WFAppsExcept": "",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.quit.app",
                    "WFWorkflowActionParameters": {
                        "WFQuitAppMode": "App",
                        "WFAskToSaveChanges": "yes",
                    },
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getfile",
                    "WFWorkflowActionParameters": {"UUID": image_uuid},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.appendnote",
                    "WFWorkflowActionParameters": {
                        "operation": "prepend",
                        "section": "Inbox",
                        "ignoreWhitespace": True,
                        "interpretAsMarkdown": False,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.mobilenotes.SharingExtension",
                    "WFWorkflowActionParameters": {
                        "contents": "# Heading",
                        "interpretAsMarkdown": True,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.askllm",
                    "WFWorkflowActionParameters": {
                        "FollowUp": False,
                        "WFAllowWebSearch": True,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.addnewreminder",
                    "WFWorkflowActionParameters": {
                        "WFCalendarItemTitle": "Follow up",
                        "WFUrgent": True,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.searchlocalbusinesses",
                    "WFWorkflowActionParameters": {"WFSearchSortOrder": "Distance"},
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetBatteryChargeLimitAction",
                    "WFWorkflowActionParameters": {
                        "limit": 80,
                        "setUntilTomorrow": False,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetMultitaskingModeAction",
                    "WFWorkflowActionParameters": {
                        "mode": "stageManager",
                        "automaticallyShowAndHideDock": True,
                        "showRecentApps": False,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.ShortcutsActions.SetMultitaskingModeAction",
                    "WFWorkflowActionParameters": {
                        "mode": {
                            "identifier": "windowedApps",
                            "value": "windowedApps",
                            "title": {"key": "Windowed Apps"},
                            "subtitle": {"key": "Windowed Apps"},
                            "symbol": {"systemName": "macwindow.on.rectangle"},
                        },
                        "automaticallyShowAndHideDock": False,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getdistance",
                    "WFWorkflowActionParameters": {
                        "WFGetDirectionsActionMode": "Direct",
                        "WFAvoidTolls": True,
                        "WFAvoidHighways": False,
                        "WFDistanceUnit": "Miles",
                        "Accuracy": "NearestTenMeters",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettraveltime",
                    "WFWorkflowActionParameters": {
                        "WFGetDirectionsActionMode": "Transit",
                        "WFAvoidTolls": False,
                        "WFAvoidHighways": True,
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.scanbarcode",
                    "WFWorkflowActionParameters": {"imageFile": image_attachment},
                },
                {
                    "WFWorkflowActionIdentifier": "com.apple.Safari.CreateNewTabGroup",
                    "WFWorkflowActionParameters": {"contents": "https://example.com"},
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.hide.app",
                    "WFWorkflowActionParameters": {
                        "WFHideAppMode": "All Apps",
                        "WFAppsExcept": "Finder",
                    },
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.quit.app",
                    "WFWorkflowActionParameters": {
                        "WFQuitAppMode": "App",
                        "WFApp": "Safari",
                        "WFAskToSaveChanges": False,
                    },
                },
            ],
            "WFWorkflowIcon": {
                "WFWorkflowIconGlyphNumber": 61440,
                "WFWorkflowIconStartColor": 431817727,
            },
            "WFWorkflowName": "OS 27 Updated Parameter Regression",
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(skill_dir, target_macos_major=27),
                "unavailable_ids": module.load_future_toolkit_id_reasons(skill_dir, 27),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            for expected in (
                "Append to Note has unknown operation",
                "ignoreWhitespace must be boolean",
                "interpretAsMarkdown must be boolean",
                "FollowUp must be boolean",
                "WFAllowWebSearch must be boolean",
                "WFUrgent must be boolean",
                "Find Places has unknown WFSearchSortOrder",
                "setUntilTomorrow must be boolean",
                "Set Multitasking Mode has unknown mode",
                "automaticallyShowAndHideDock must be boolean",
                "showRecentApps must be boolean",
                "is.workflow.actions.getdistance has unknown WFGetDirectionsActionMode",
                "Get Distance has unknown WFDistanceUnit",
                "Get Distance has unknown Accuracy",
                "is.workflow.actions.gettraveltime has unknown WFGetDirectionsActionMode",
                "WFAvoidTolls must be boolean",
                "WFAvoidHighways must be boolean",
                "Scan QR or Barcode missing imageFile",
                "Scan QR or Barcode imageFile is not a token attachment",
                "Create Tab Group has empty contents",
                "is.workflow.actions.hide.app has unknown WFHideAppMode",
                "is.workflow.actions.hide.app has empty WFAppsExcept",
                "is.workflow.actions.quit.app mode App missing WFApp",
                "WFAskToSaveChanges must be boolean",
            ):
                self.assertTrue(
                    [error for error in invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {invalid_errors}",
                )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "must be boolean" in error
                    or "unknown WFSearchSortOrder" in error
                    or "Set Multitasking Mode has unknown mode" in error
                    or "unknown WFGetDirectionsActionMode" in error
                    or "unknown WFDistanceUnit" in error
                    or "unknown Accuracy" in error
                    or "Scan QR or Barcode" in error
                    or "Create Tab Group has empty contents" in error
                    or "unknown WFHideAppMode" in error
                    or "unknown WFQuitAppMode" in error
                    or "mode App missing WFApp" in error
                    or "empty WFAppsExcept" in error
                    or "WFAskToSaveChanges" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

    def test_ios_create_tab_group_uses_mobilesafari_identifier(self) -> None:
        invalid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.mobilesafari.CreateNewTabGroup",
                    "WFWorkflowActionParameters": {"contents": ""},
                },
            ],
        }
        valid_plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.mobilesafari.CreateNewTabGroup",
                    "WFWorkflowActionParameters": {"contents": "https://example.com"},
                },
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            common_kwargs = {
                "allowed_ids": module.load_allowed_ids(
                    skill_dir,
                    target_macos_major=27,
                    target_platform="ios",
                ),
                "unavailable_ids": module.load_future_toolkit_id_reasons(
                    skill_dir,
                    27,
                    target_platform="ios",
                ),
                "unavailable_parameter_keys": module.load_future_parameter_key_reasons(27),
                "toolkit_parameter_schemas": module.load_toolkit_parameter_schemas(
                    skill_dir,
                    target_macos_major=27,
                    target_platform="ios",
                ),
            }

            invalid_errors, _ = module.validate(invalid_plist, **common_kwargs)
            self.assertTrue(
                [error for error in invalid_errors if "Create Tab Group has empty contents" in error],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors, _ = module.validate(valid_plist, **common_kwargs)
            self.assertFalse(
                [error for error in valid_errors if "Create Tab Group has empty contents" in error],
                f"{rel_path}: {valid_errors}",
            )

    def test_notes_markdown_contents_is_a_valid_content_key(self) -> None:
        plist = {
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "com.apple.Notes.CreateNoteFromMarkdownLinkAction",
                    "WFWorkflowActionParameters": {
                        "title": "Markdown Note",
                        "markdownContents": "# Heading\n\nBody",
                    },
                }
            ],
            "WFWorkflowIcon": {
                "WFWorkflowIconGlyphNumber": 61440,
                "WFWorkflowIconStartColor": 431817727,
            },
            "WFWorkflowName": "Notes Markdown Regression",
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            self.assertIn("markdowncontents", module.NOTES_CONTENT_KEYS, rel_path)
            skill_dir = module_path.parents[1]
            errors, _ = module.validate(
                plist,
                module.load_allowed_ids(skill_dir, target_macos_major=27),
            )
            self.assertFalse(
                [error for error in errors if "Notes create action missing content" in error],
                f"{rel_path}: {errors}",
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
                        "WFInput": conditional_input,
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


    def test_find_calendar_events_calendar_filter_row_is_validated(self) -> None:
        date_uuid = "7E8F9012-A3B4-4C5D-8E6F-708192A3B4C5"
        variable_calendar = {
            "Value": {
                "Value": {"Type": "Variable", "VariableName": "Example Calendar"},
                "WFSerializationType": "WFTextTokenAttachment",
            },
            "WFSerializationType": "WFStringSubstitutableState",
        }

        def literal_calendar(name: str) -> dict:
            return {"Value": name, "WFSerializationType": "WFStringSubstitutableState"}

        def calendar_row(values: dict, operator: int = 4) -> dict:
            return {
                "Operator": operator,
                "Property": "Calendar",
                "Removable": True,
                "Values": values,
            }

        def plist_for(calendar_template: dict) -> dict:
            return {
                "WFWorkflowActions": [
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
                        "WFWorkflowActionParameters": {
                            "WFCommentActionText": "Regression for the Find Calendar Events Calendar row."
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
                        "WFWorkflowActionIdentifier": "is.workflow.actions.date",
                        "WFWorkflowActionParameters": {"UUID": date_uuid},
                    },
                    {
                        "WFWorkflowActionIdentifier": "is.workflow.actions.filter.calendarevents",
                        "WFWorkflowActionParameters": {
                            "UUID": "8F901234-B4C5-4D6E-9F70-8192A3B4C5D6",
                            "WFContentItemFilter": {
                                "Value": {
                                    "WFActionParameterFilterPrefix": 1,
                                    "WFActionParameterFilterTemplates": [
                                        {
                                            "Bounded": True,
                                            "Operator": 1003,
                                            "Property": "Start Date",
                                            "Removable": True,
                                            "Values": {
                                                "AnotherDate": {
                                                    "Value": {"Type": "CurrentDate"},
                                                    "WFSerializationType": "WFTextTokenAttachment",
                                                },
                                                "Date": {
                                                    "Value": {
                                                        "OutputName": "Date",
                                                        "OutputUUID": date_uuid,
                                                        "Type": "ActionOutput",
                                                    },
                                                    "WFSerializationType": "WFTextTokenAttachment",
                                                },
                                            },
                                        },
                                        calendar_template,
                                    ],
                                    "WFContentPredicateBoundedDate": False,
                                },
                                "WFSerializationType": "WFContentPredicateTableTemplate",
                            },
                            "WFContentItemSortOrder": "Oldest First",
                            "WFContentItemSortProperty": "Start Date",
                        },
                    },
                ],
                "WFWorkflowIcon": {
                    "WFWorkflowIconGlyphNumber": 61440,
                    "WFWorkflowIconStartColor": 431817727,
                },
                "WFWorkflowName": "Calendar Filter Regression",
            }

        valid_rows = {
            "variable is": calendar_row({"Enumeration": variable_calendar}),
            "literal is": calendar_row({"Enumeration": literal_calendar("Home")}),
            "literal is not": calendar_row({"Enumeration": literal_calendar("Work")}, operator=5),
        }
        broken_rows = {
            "operator must be 4 (is) or 5 (is not)": calendar_row(
                {"Enumeration": literal_calendar("Home")}, operator=99
            ),
            "missing Values.Enumeration": calendar_row({}),
            "must use WFStringSubstitutableState": calendar_row(
                {"Enumeration": {"Value": "Example Calendar", "WFSerializationType": "WFTextTokenString"}}
            ),
            "Enumeration value is empty": calendar_row(
                {"Enumeration": {"Value": "", "WFSerializationType": "WFStringSubstitutableState"}}
            ),
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            allowed = module.load_allowed_ids(skill_dir, target_macos_major=27)

            for label, template in valid_rows.items():
                valid_errors, _ = module.validate(plist_for(template), allowed)
                self.assertFalse(
                    [err for err in valid_errors if "Find Calendar Events" in err],
                    f"{rel_path} {label}: {valid_errors}",
                )

            for expected, template in broken_rows.items():
                errors, _ = module.validate(plist_for(template), allowed)
                self.assertTrue(
                    [err for err in errors if "Calendar filter" in err and expected in err],
                    f"{rel_path} {expected}: {errors}",
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
    ENUM_CATALOG_PATHS = (
        "claude/skills/shortcuts-playground/data/toolkit-v78-first-party-enum-cases.json",
        "codex/skills/shortcuts-playground/data/toolkit-v78-first-party-enum-cases.json",
    )
    TRIGGER_CATALOG_PATHS = (
        "claude/skills/shortcuts-playground/data/toolkit-v78-trigger-parameter-keys.json",
        "codex/skills/shortcuts-playground/data/toolkit-v78-trigger-parameter-keys.json",
    )
    WORKFLOW_TRIGGER_SAMPLE_CATALOG_PATHS = (
        "claude/skills/shortcuts-playground/data/macos27-workflow-trigger-samples.json",
        "codex/skills/shortcuts-playground/data/macos27-workflow-trigger-samples.json",
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
            self.assertIn("localized parameter names", catalog["scope"], rel_path)
            self.assertIn("sort orders", catalog["scope"], rel_path)
            self.assertIn("typePythonNames", catalog["scope"], rel_path)
            self.assertIn("per-parameter platform provenance", catalog["scope"], rel_path)
            self.assertEqual(2585, len(catalog["tools"]), rel_path)

            send_message = catalog["tools"]["com.apple.MobileSMS.SendMessageIntent"]
            self.assertEqual("messages_send_message", send_message["pythonName"], rel_path)
            self.assertEqual("Send Message", send_message["displayName"], rel_path)
            self.assertIn("macOS 27", send_message["platforms"], rel_path)
            self.assertIn("iOS 27 Simulator", send_message["platforms"], rel_path)
            self.assertEqual(8, send_message["parameterCount"], rel_path)
            self.assertEqual(send_message["parameterCount"], len(send_message["parameters"]), rel_path)
            parameters = {parameter["key"]: parameter for parameter in send_message["parameters"]}
            parameter_keys = set(parameters)
            self.assertIn("content", parameter_keys, rel_path)
            self.assertIn("scheduledDate", parameter_keys, rel_path)
            self.assertEqual("Content", parameters["content"]["name"], rel_path)
            self.assertEqual(2, parameters["content"]["sortOrder"], rel_path)
            self.assertEqual(4, parameters["content"]["flags"], rel_path)
            self.assertEqual("Date", parameters["scheduledDate"]["name"], rel_path)
            destination = parameters["destination"]
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

            create_contact = catalog["tools"]["com.apple.AddressBook.CreateContactIntent"]
            open_when_run = next(
                parameter
                for parameter in create_contact["parameters"]
                if parameter["key"] == "OpenWhenRun"
            )
            self.assertEqual("Open When Run", open_when_run["name"], rel_path)
            self.assertEqual("On", open_when_run["trueString"], rel_path)
            self.assertEqual("Off", open_when_run["falseString"], rel_path)

            launch_app = catalog["tools"]["com.apple.TVRemoteUIService.LaunchApplicationIntent"]
            launch_parameters = {
                parameter["key"]: parameter
                for parameter in launch_app["parameters"]
            }
            self.assertEqual(["iOS 27 Simulator"], launch_parameters["device"]["platforms"], rel_path)
            self.assertEqual(
                ["iOS 27 Simulator"],
                launch_parameters["application"]["platforms"],
                rel_path,
            )
            show_when_run = next(
                parameter
                for parameter in launch_app["parameters"]
                if parameter["key"] == "ShowWhenRun"
            )
            self.assertEqual(
                ["iOS 27 Simulator", "macOS 27"],
                show_when_run["platforms"],
                rel_path,
            )
            self.assertEqual(
                {"iOS 27 Simulator": 2, "macOS 27": 0},
                show_when_run["sortOrders"],
                rel_path,
            )

    def test_toolkit_parameter_catalog_rows_match_platform_snapshots(self) -> None:
        for prefix in ("claude", "codex"):
            data_dir = REPO_ROOT / prefix / "skills/shortcuts-playground/data"
            macos_ids = set(load_json(data_dir / "toolkit-v78-tool-ids.json")["ids"])
            ios_ids = set(load_json(data_dir / "toolkit-v78-ios27-tool-ids.json")["ids"])
            tools = load_json(data_dir / "toolkit-v78-first-party-parameter-keys.json")[
                "tools"
            ]

            mismatches: list[tuple[str, str]] = []
            for identifier, entry in tools.items():
                platforms = entry.get("platforms") or []
                if any(platform.startswith("macOS") for platform in platforms) and identifier not in macos_ids:
                    mismatches.append(("macOS", identifier))
                if any(platform.startswith("iOS") for platform in platforms) and identifier not in ios_ids:
                    mismatches.append(("iOS", identifier))

            self.assertEqual([], mismatches, prefix)

    def test_toolkit_v78_enum_case_catalog_is_packaged(self) -> None:
        expected = {
            "additemtolist_wfinsert_position": {"Beginning", "End", "Index"},
            "searchlocalbusinesses_wfsearch_sort_order": {"Relevance", "Distance"},
            "com_apple_shortcuts_actions_multitasking_mode": {
                "fullScreenApps",
                "windowedApps",
                "stageManager",
            },
            "vpn_set_wfvpnoperation": {
                "Connect",
                "Disconnect",
                "Toggle",
                "Set On Demand",
                "Toggle On Demand",
            },
            "com_apple_shortcuts_wfairplane_mode_trigger_wfairplane_mode_type": {
                "on",
                "off",
                "both",
            },
            "com_apple_shortcuts_wfexternal_display_trigger_wfconnection_type": {
                "connect",
                "disconnect",
                "both",
            },
            "com_apple_shortcuts_wfstage_manager_trigger_wfstage_manager_type": {
                "on",
                "off",
                "both",
            },
            "com_apple_mobile_sms_tapback": {
                "2000",
                "2001",
                "2002",
                "2003",
                "2004",
                "2005",
            },
        }
        for rel_path in self.ENUM_CATALOG_PATHS:
            catalog = load_json(REPO_ROOT / rel_path)

            self.assertEqual("toolkit-v78-first-party-enum-cases", catalog["version"], rel_path)
            self.assertIn("automation-trigger parameter typePythonName", catalog["scope"], rel_path)
            self.assertIn("Descriptions are intentionally omitted", catalog["scope"], rel_path)
            self.assertIn("Dynamic user-local picker cases", catalog["scope"], rel_path)
            self.assertEqual(3259, catalog["referencedTypePythonNameCount"], rel_path)
            self.assertEqual(2180, catalog["enumTypeCount"], rel_path)
            self.assertEqual(8139, catalog["caseCount"], rel_path)
            for redacted_type in (
                "setters_reminders_wfreminder_content_item_list",
                "setters_contacts_wfcontact_content_item_group",
            ):
                self.assertNotIn(redacted_type, catalog["types"], f"{rel_path}: {redacted_type}")
            catalog_text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for local_name in ("Editorial", "Socials", "WWDC 26", "Weekly 517"):
                self.assertNotIn(local_name, catalog_text, f"{rel_path}: {local_name}")

            for type_name, case_ids in expected.items():
                entry = catalog["types"][type_name]
                self.assertEqual(
                    case_ids,
                    {case["id"] for case in entry["cases"]},
                    f"{rel_path}: {type_name}",
                )
                self.assertIn("macOS 27", entry["platforms"], f"{rel_path}: {type_name}")
                self.assertIn(
                    "iOS 27 Simulator",
                    entry["platforms"],
                    f"{rel_path}: {type_name}",
                )

    def test_toolkit_enum_catalog_references_are_consistent(self) -> None:
        for prefix in ("claude", "codex"):
            data_dir = REPO_ROOT / prefix / "skills/shortcuts-playground/data"
            tools = load_json(data_dir / "toolkit-v78-first-party-parameter-keys.json")[
                "tools"
            ]
            triggers = load_json(data_dir / "toolkit-v78-trigger-parameter-keys.json")[
                "triggers"
            ]
            enum_types = load_json(data_dir / "toolkit-v78-first-party-enum-cases.json")[
                "types"
            ]

            referenced_types: set[str] = set()
            for collection in (tools, triggers):
                for entry in collection.values():
                    for parameter in entry.get("parameters") or []:
                        type_name = parameter.get("typePythonName")
                        if isinstance(type_name, str):
                            referenced_types.add(type_name)
                        for alternate_type in parameter.get("typePythonNames") or []:
                            if isinstance(alternate_type, str):
                                referenced_types.add(alternate_type)

            self.assertFalse(
                [
                    type_name
                    for type_name, entry in enum_types.items()
                    if not entry.get("cases")
                ],
                prefix,
            )
            self.assertEqual(set(enum_types), set(enum_types) & referenced_types, prefix)

    def test_toolkit_v78_trigger_catalog_is_packaged(self) -> None:
        for rel_path in self.TRIGGER_CATALOG_PATHS:
            catalog = load_json(REPO_ROOT / rel_path)

            self.assertEqual("toolkit-v78-trigger-parameter-keys", catalog["version"], rel_path)
            self.assertIn("not an import-ready automation plist schema", catalog["scope"], rel_path)
            self.assertEqual(42, len(catalog["triggers"]), rel_path)

            time_of_day = catalog["triggers"][
                "com.apple.shortcuts.WFTimeOfDayTrigger.at_time_on_recurring_day"
            ]
            self.assertEqual("Time of Day", time_of_day["displayName"], rel_path)
            self.assertEqual(
                "when_time_of_day_at_time_on_recurring_day",
                time_of_day["pythonName"],
                rel_path,
            )
            self.assertEqual(["iOS 27 Simulator", "macOS 27"], time_of_day["platforms"], rel_path)
            self.assertEqual(
                {"WFTime", "WFRecurrence"},
                {parameter["key"] for parameter in time_of_day["parameters"]},
                rel_path,
            )

            app_opened = catalog["triggers"]["com.apple.shortcuts.WFAppInFocusTrigger.opened"]
            self.assertEqual("when_app_opened", app_opened["pythonName"], rel_path)
            self.assertEqual(
                {"WFSelectedApps", "WFAppState"},
                {parameter["key"] for parameter in app_opened["parameters"]},
                rel_path,
            )

    def test_macos27_workflow_trigger_sample_catalog_is_packaged(self) -> None:
        for rel_path in self.WORKFLOW_TRIGGER_SAMPLE_CATALOG_PATHS:
            catalog = load_json(REPO_ROOT / rel_path)

            self.assertEqual("macos27-workflow-trigger-samples", catalog["version"], rel_path)
            self.assertEqual("WFWorkflowTriggers", catalog["rootKey"], rel_path)
            self.assertIn("Do not read from or write to the live Shortcuts database", catalog["policy"], rel_path)
            self.assertEqual(42, catalog["observedToolkitTriggerCount"], rel_path)
            self.assertEqual(0, catalog["unobservedToolkitTriggerCount"], rel_path)
            self.assertEqual(42, len(catalog["triggers"]), rel_path)

            low_power = catalog["triggers"][
                "com.apple.shortcuts.WFLowPowerModeTrigger.changes"
            ]
            self.assertTrue(low_power["observed"], rel_path)
            self.assertEqual(
                "copyable-with-fresh-uuid",
                low_power["templateStatus"],
                rel_path,
            )
            self.assertEqual(
                "WFLowPowerModeTrigger",
                low_power["workflowTrigger"]["WFTriggerIdentifier"],
                rel_path,
            )
            self.assertEqual(
                {"WFLowPowerModeType": "both"},
                low_power["workflowTrigger"]["WFTriggerSerializedParameters"],
                rel_path,
            )

            wifi_disconnect = catalog["triggers"][
                "com.apple.shortcuts.WFWifiTrigger.disconnect_from_selected"
            ]
            self.assertEqual(
                "disconnected",
                wifi_disconnect["workflowTrigger"]["WFTriggerSerializedParameters"]["WFConnectionType"],
                rel_path,
            )

            display = catalog["triggers"]["com.apple.shortcuts.WFExternalDisplayTrigger."]
            self.assertTrue(display["observed"], rel_path)
            self.assertEqual("copyable-with-fresh-uuid", display["templateStatus"], rel_path)
            self.assertEqual(
                {"WFConnectionType": "both"},
                display["workflowTrigger"]["WFTriggerSerializedParameters"],
                rel_path,
            )
            self.assertEqual(
                {"connect", "disconnect", "both"},
                set(display["serializedParameterShape"]["WFConnectionType"]["allowedValues"]),
                rel_path,
            )

            stage_manager = catalog["triggers"]["com.apple.shortcuts.WFStageManagerTrigger.on"]
            self.assertTrue(stage_manager["observed"], rel_path)
            self.assertEqual("copyable-with-fresh-uuid", stage_manager["templateStatus"], rel_path)
            self.assertEqual(
                {"WFStageManagerType": "both"},
                stage_manager["workflowTrigger"]["WFTriggerSerializedParameters"],
                rel_path,
            )
            self.assertEqual(
                {"on", "off", "both"},
                set(stage_manager["serializedParameterShape"]["WFStageManagerType"]["allowedValues"]),
                rel_path,
            )

            mac_trigger_expectations = {
                "com.apple.shortcuts.WFDiskMountTrigger.external_drive": "WFDiskMountTrigger",
                "com.apple.shortcuts.WFFileTrigger.file_modified": "WFFileTrigger",
                "com.apple.shortcuts.WFFolderTrigger.folder_changed": "WFFolderTrigger",
            }
            for trigger_id, workflow_identifier in mac_trigger_expectations.items():
                trigger = catalog["triggers"][trigger_id]
                self.assertTrue(trigger["observed"], rel_path)
                self.assertEqual("requires-user-values", trigger["templateStatus"], rel_path)
                self.assertTrue(
                    any("outside the portable WFWorkflowTriggers dictionary" in note for note in trigger["notes"]),
                    f"{rel_path}: {trigger_id}: {trigger['notes']}",
                )
                self.assertEqual(
                    workflow_identifier,
                    trigger["workflowTrigger"]["WFTriggerIdentifier"],
                    rel_path,
                )
                self.assertEqual(
                    {},
                    trigger["workflowTrigger"]["WFTriggerSerializedParameters"],
                    rel_path,
                )

            catalog_text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for private_token in (
                "BEGIN:VCARD",
                "WFContactData",
                "WFContactFieldValues",
                "WFContactMultivalue",
                "WFContactProperty",
                "accountIdentifier",
                "cachedDescription",
                "Gmail",
            ):
                self.assertNotIn(private_token, catalog_text, f"{rel_path}: {private_token}")

            email = catalog["triggers"]["com.apple.shortcuts.WFEmailTrigger.subject_contains"]
            self.assertEqual(
                {"type": "redacted-local-email-predicate-table"},
                email["serializedParameterShape"]["WFEmailConditions"],
                rel_path,
            )
            message = catalog["triggers"]["com.apple.shortcuts.WFMessageTrigger.senders_are"]
            self.assertEqual(
                {"type": "redacted-local-message-predicate-table"},
                message["serializedParameterShape"]["WFMessageConditions"],
                rel_path,
            )

    def test_toolkit_trigger_ids_remain_metadata_only(self) -> None:
        for prefix in ("claude", "codex"):
            data_dir = REPO_ROOT / prefix / "skills/shortcuts-playground/data"
            macos_ids = set(load_json(data_dir / "toolkit-v78-tool-ids.json")["ids"])
            ios_ids = set(load_json(data_dir / "toolkit-v78-ios27-tool-ids.json")["ids"])
            trigger_ids = set(
                load_json(data_dir / "toolkit-v78-trigger-parameter-keys.json")[
                    "triggers"
                ]
            )

            self.assertFalse(trigger_ids & (macos_ids | ios_ids), prefix)

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
            content = next(
                parameter
                for parameter in entry["toolkitParameterSummary"]["parameters"]
                if parameter["key"] == "content"
            )
            self.assertEqual("Content", content["name"], rel_path)
            self.assertEqual(2, content["sortOrder"], rel_path)

    def test_lookup_action_grounding_falls_back_to_classic_toolkit_enum_summary(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "is.workflow.actions.hash",
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
            self.assertEqual("is.workflow.actions.hash", entry["identifier"], rel_path)
            self.assertEqual("toolkit-parameter-summary", entry["status"], rel_path)
            hash_type = next(
                parameter
                for parameter in entry["toolkitParameterSummary"]["parameters"]
                if parameter["key"] == "WFHashType"
            )
            self.assertEqual(
                {"MD5", "SHA1", "SHA256", "SHA512"},
                {case["id"] for case in hash_type["enumCases"]},
                rel_path,
            )

    def test_lookup_action_grounding_filters_toolkit_parameters_by_target_platform(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            macos_result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                    "--target-macos",
                    "27",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            macos_payload = json.loads(macos_result.stdout)
            macos_parameters = {
                parameter["key"]
                for parameter in macos_payload["results"][0]["toolkitParameterSummary"][
                    "parameters"
                ]
            }
            self.assertEqual({"ShowWhenRun"}, macos_parameters, rel_path)

            ios_result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                    "--target-macos",
                    "27",
                    "--target-platform",
                    "ios",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            ios_payload = json.loads(ios_result.stdout)
            ios_parameters = {
                parameter["key"]
                for parameter in ios_payload["results"][0]["toolkitParameterSummary"][
                    "parameters"
                ]
            }
            self.assertEqual({"ShowWhenRun", "device", "appearanceToggle"}, ios_parameters, rel_path)

            macos_music = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.musicrecognition.RecognizeMusicIntent",
                    "--target-macos",
                    "27",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            music_payload = json.loads(macos_music.stdout)
            music_parameters = {
                parameter["key"]
                for parameter in music_payload["results"][0]["toolkitParameterSummary"][
                    "parameters"
                ]
            }
            self.assertEqual(
                {"WFShazamMediaActionShowWhenRun", "WFShazamMediaActionErrorIfNotRecognized"},
                music_parameters,
                rel_path,
            )

    def test_lookup_action_grounding_exposes_toolkit_enum_cases(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "is.workflow.actions.additemtolist",
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
            self.assertEqual(
                "toolkit-v78-first-party-enum-cases",
                payload["enumCatalog"]["version"],
                rel_path,
            )
            position = next(
                parameter
                for parameter in entry["toolkitParameterSummary"]["parameters"]
                if parameter["key"] == "WFInsertPosition"
            )
            self.assertEqual(
                {"Beginning", "End", "Index"},
                {case["id"] for case in position["enumCases"]},
                rel_path,
            )
            self.assertEqual(
                "additemtolist_wfinsert_position",
                position["enumTypes"][0]["typePythonName"],
                rel_path,
            )

    def test_lookup_action_grounding_exposes_trigger_enum_cases(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--python-name",
                    "when_airplane_mode_changes",
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
            state = next(
                parameter
                for parameter in entry["toolkitTriggerSummary"]["parameters"]
                if parameter["key"] == "WFAirplaneModeType"
            )
            self.assertEqual({"on", "off", "both"}, {case["id"] for case in state["enumCases"]}, rel_path)
            self.assertEqual(
                "com_apple_shortcuts_wfairplane_mode_trigger_wfairplane_mode_type",
                state["enumTypes"][0]["typePythonName"],
                rel_path,
            )
            self.assertEqual(
                "macos27-workflow-trigger-samples",
                payload["workflowTriggerCatalog"]["version"],
                rel_path,
            )
            sample = entry["workflowTriggerSample"]
            self.assertTrue(sample["observed"], rel_path)
            self.assertEqual(
                "WFAirplaneModeTrigger",
                sample["workflowTrigger"]["WFTriggerIdentifier"],
                rel_path,
            )
            self.assertEqual(
                {"WFAirplaneModeType": "both"},
                sample["workflowTrigger"]["WFTriggerSerializedParameters"],
                rel_path,
            )

    def test_lookup_action_grounding_marks_mac_workflow_triggers_observed(self) -> None:
        expectations = {
            "com.apple.shortcuts.WFDiskMountTrigger.external_drive": "WFDiskMountTrigger",
            "com.apple.shortcuts.WFFileTrigger.file_modified": "WFFileTrigger",
            "com.apple.shortcuts.WFFolderTrigger.folder_changed": "WFFolderTrigger",
        }
        for rel_path in self.LOOKUP_SCRIPTS:
            for trigger_id, workflow_identifier in expectations.items():
                result = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / rel_path),
                        "--identifier",
                        trigger_id,
                        "--target-macos",
                        "27",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                payload = json.loads(result.stdout)
                sample = payload["results"][0]["workflowTriggerSample"]
                self.assertTrue(sample["observed"], rel_path)
                self.assertEqual("requires-user-values", sample["templateStatus"], rel_path)
                self.assertEqual(
                    workflow_identifier,
                    sample["workflowTrigger"]["WFTriggerIdentifier"],
                    rel_path,
                )
                self.assertEqual(
                    {},
                    sample["workflowTrigger"]["WFTriggerSerializedParameters"],
                    rel_path,
                )

    def test_lookup_action_grounding_marks_ios_only_parameter_catalog_entries(self) -> None:
        expected_note = (
            "Only observed in iOS 27 Simulator ToolKit; no macOS ToolKit row observed."
        )
        expected_target_note = (
            "Only observed for iOS 27 Simulator; target platform is macOS."
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
            self.assertEqual(
                expected_target_note,
                payload["targetPlatformAvailabilityNote"],
                rel_path,
            )
            self.assertEqual("macOS", payload["targetPlatform"], rel_path)
            self.assertEqual(expected_note, entry["platformAvailabilityNote"], rel_path)
            self.assertEqual(expected_target_note, entry["targetPlatformAvailabilityNote"], rel_path)
            self.assertEqual(["iOS 27 Simulator"], entry["toolkitPlatforms"], rel_path)
            self.assertEqual("toolkit-parameter-summary", entry["status"], rel_path)

            ios_result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "com.apple.HearingApp.MuteVolumeIntent",
                    "--target-macos",
                    "27",
                    "--target-platform",
                    "ios",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            ios_payload = json.loads(ios_result.stdout)
            ios_entry = ios_payload["results"][0]
            self.assertEqual("iOS/iPadOS", ios_payload["targetPlatform"], rel_path)
            self.assertIsNone(ios_payload["targetPlatformAvailabilityNote"], rel_path)
            self.assertIsNone(ios_entry["targetPlatformAvailabilityNote"], rel_path)

    def test_lookup_action_grounding_marks_deprecated_toolkit_rows(self) -> None:
        expected_note = (
            "Deprecated in ToolKit v78; use is.workflow.actions.getonscreencontext "
            "for new Get What's On Screen shortcuts."
        )
        for rel_path in self.LOOKUP_SCRIPTS:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / rel_path),
                    "--identifier",
                    "getonscreencontent",
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
            self.assertEqual(expected_note, payload["deprecationNote"], rel_path)
            self.assertEqual(expected_note, entry["deprecationNote"], rel_path)
            self.assertEqual("is.workflow.actions.getonscreencontent", entry["identifier"], rel_path)

    def test_lookup_action_grounding_auto_target_falls_back_to_26_when_host_unknown(self) -> None:
        for rel_path in self.LOOKUP_SCRIPTS:
            import importlib.util

            script_path = REPO_ROOT / rel_path
            spec = importlib.util.spec_from_file_location(
                f"lookup_action_grounding_{rel_path.split('/')[0]}",
                script_path,
            )
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            lookup_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lookup_module)
            original = lookup_module.host_macos_major
            try:
                lookup_module.host_macos_major = lambda: None
                self.assertEqual(26, lookup_module.resolve_target_macos("auto"), rel_path)
                self.assertEqual(26, lookup_module.resolve_target_macos(None), rel_path)
                self.assertIsNone(lookup_module.resolve_target_macos("latest"), rel_path)
                self.assertEqual("macos", lookup_module.resolve_target_platform(None), rel_path)
                self.assertEqual("ios", lookup_module.resolve_target_platform("ipad"), rel_path)
                self.assertIsNone(lookup_module.resolve_target_platform("all"), rel_path)
            finally:
                lookup_module.host_macos_major = original

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

    def test_lookup_action_grounding_resolves_trigger_metadata(self) -> None:
        expected_note = "Trigger metadata is from OS 27 ToolKit; target macOS is 26."
        for rel_path in self.LOOKUP_SCRIPTS:
            for lookup_args in (
                ["--python-name", "when_app_opened"],
                ["--identifier", "com.apple.shortcuts.WFAppInFocusTrigger.opened"],
            ):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / rel_path),
                        *lookup_args,
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

                self.assertEqual(expected_note, payload["triggerMetadataAvailabilityNote"], rel_path)
                self.assertEqual(expected_note, entry["triggerMetadataAvailabilityNote"], rel_path)
                self.assertEqual("toolkit-trigger-summary", entry["status"], rel_path)
                self.assertEqual("com.apple.shortcuts.WFAppInFocusTrigger.opened", entry["identifier"], rel_path)
                self.assertEqual("when_app_opened", entry["pythonName"], rel_path)
                self.assertEqual(27, entry["triggerMetadataMinimumMacOSMajor"], rel_path)
                self.assertEqual(
                    {"WFSelectedApps", "WFAppState"},
                    {
                        parameter["key"]
                        for parameter in entry["toolkitTriggerSummary"]["parameters"]
                    },
                    rel_path,
                )


class OS27AutomatorsReferenceTests(unittest.TestCase):
    def load_validator_module(self, rel_path: str):
        import importlib.util

        module_path = REPO_ROOT / rel_path
        spec = importlib.util.spec_from_file_location(
            f"validate_shortcut_os27_{rel_path.split('/')[0]}", module_path
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module_path

    def test_os27_target_gating_is_documented_in_skill_and_snapshot_docs(self) -> None:
        required_terms = (
            "target-gated ToolKit snapshots",
            "OS 27-only parameters",
            "WFAllowWebSearch",
            "FollowUp",
            "interpretAsMarkdown",
            "WFAvoidTolls",
            "Safari Tab Group `contents`",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/SKILL.md",
            "codex/skills/shortcuts-playground/SKILL.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")

        snapshot_terms = (
            "OS 27-only parameter keys are rejected on macOS 26 targets",
            "OS 27-era parameter keys are also target-gated",
            "v78-only identifier or parameter key",
            "toolkit-v78-first-party-parameter-keys.json",
            "toolkit-v78-first-party-enum-cases.json",
            "toolkit-v78-trigger-parameter-keys.json",
            "Automation trigger metadata",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/TOOLKIT_SNAPSHOT.md",
            "codex/skills/shortcuts-playground/TOOLKIT_SNAPSHOT.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in snapshot_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")

        trigger_terms = (
            "Automation Triggers",
            "WFWorkflowTriggers",
            "when_app_opened",
            "macos27-workflow-trigger-samples.json",
            "Display / external display",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/AUTOMATION_TRIGGERS.md",
            "codex/skills/shortcuts-playground/AUTOMATION_TRIGGERS.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in trigger_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")

    def test_os27_action_parameter_updates_are_documented(self) -> None:
        required_action_terms = (
            "WFAllowWebSearch",
            "FollowUp",
            "WFUrgent",
            "Append to Note",
            "Section",
            "Ignore Whitespace",
            "Interpret as Markdown",
            "operation",
            "append",
            "prepend",
            "WFInsertPosition",
            "Beginning",
            "End",
            "Index",
            "1-based integer",
            "WFChooseFromListActionSelectMultiple",
            "WFChooseFromListActionSelectAll",
            "WFSearchSortOrder",
            "Relevance",
            "Open Directions",
            "multi-stop trips are only supported by Apple Maps",
            "WFAvoidTolls",
            "WFAvoidHighways",
            "Avoid Tolls",
            "Avoid Highways",
            "WFAppsExcept",
            "interpretAsMarkdown",
            "com.apple.mobilenotes.SharingExtension",
            "com.apple.Safari.CreateNewTabGroup",
            "com.apple.mobilesafari.CreateNewTabGroup",
            "Scan QR or Barcode",
            "Get Distance",
            "Get Travel Time",
            "WFGetDirectionsActionMode",
            "WFDistanceUnit",
            "Miles",
            "Kilometers",
            "Accuracy",
            "NearestTenMeters",
            "ThreeKilometers",
            "Hide App",
            "Quit App",
            "WFHideAppMode",
            "WFQuitAppMode",
            "WFAskToSaveChanges",
            "Create Tab Group",
            "Extract from Image (`imageFile` in ToolKit v78)",
            "Search Photos",
            "com.apple.Photos.PhotosSearchAssistantIntent",
            "OS 26.4 Choose from List Compatibility",
            "dictionaries and named text",
            "Contact email and phone-number list values remain macOS-only",
            "OS 18 to 26.1 Automators Follow-up",
            "WFWindowingFormat",
            "Window Location & Size",
            "Full Screen",
            "Left Third",
            "Right Third",
            "Search in Files",
            "unresolved",
            "is.workflow.actions.filter.files",
            "is.workflow.actions.getonscreencontext",
            "is.workflow.actions.getonscreencontent",
            "#### Get What's On Screen",
            "WFOnScreenContextScope",
            "All Visible",
            "Focused App Only",
            "WFOnScreenContextLimitEnabled",
            "WFOnScreenContextLimit",
            "is.workflow.actions.extracttextfromimage",
            "#### Stored Content",
            "Store Content",
            "Get Stored Content",
            "Delete Stored Content",
            "WFStoredContentKey",
            "WFStoredContentGlobalValue",
            "is.workflow.actions.setstoredcontent",
            "WFTextTokenString",
            "plutil -convert binary1",
            "#### VPN Actions",
            "is.workflow.actions.filter.vpns",
            "is.workflow.actions.vpn.get",
            "is.workflow.actions.vpn.set",
            "WFVPNOperation",
            "WFOnDemandValue",
            "WFVPN",
            "Server Address",
            "#### iOS Workout Controls",
            "is.workflow.actions.workout.start",
            "is.workflow.actions.workout.end",
            "workoutName",
            "WorkoutGoal",
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
            "com.apple.ShortcutsActions.SetBatteryChargeLimitAction",
            "com.apple.ShortcutsActions.GetMultitaskingModeAction",
            "com.apple.ShortcutsActions.SetMultitaskingModeAction",
            "setUntilTomorrow",
            "fullScreenApps",
            "stageManager",
            "windowedApps",
            "Set Appearance on Apple TV",
            "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
            "appearanceToggle",
            "light",
            "dark",
            "com.apple.sociallayerd.CollaborationIntent",
            "com.apple.mobilenotes.SharingExtension",
            "com.apple.Safari.CreateNewTabGroup",
            "com.apple.mobilesafari.CreateNewTabGroup",
            "com.apple.MobileSMS.ChangeFilterModeIntent",
            "com.apple.MobileSMS.SearchMessagesIntent",
            "Unknown Senders",
            "All Transactions",
            "Recently Deleted",
            "Send Later",
            "mark",
            "toggle",
            "Unread",
            "isRead",
            "WFContentItemInputParameter = Library",
            "com.apple.Photos.OpenAssetIntent",
            "com.apple.mobileslideshow.OpenAssetIntent",
            "com.apple.mobileslideshow.FavoriteAssetsIntent",
            "com.apple.mobileslideshow.HideAssetsIntent",
            "com.apple.mobileslideshow.DeleteAlbumsIntent",
            "albumType",
            "creationDate",
            "favorite",
            "unfavorite",
            "hide",
            "unhide",
            "com.apple.mail.MailMessage",
            "com.apple.mail.MailMessageEntity",
            "dateReceived",
            "subject",
            "body",
            "Edit List",
            "badge",
            "parent",
            "Auto-Categorize",
            "deleteSublists",
            "is.workflow.actions.vpn.get",
            "AppIntent entity/query",
            "com.apple.reminders.CreateSectionAppIntent",
            "com.apple.systempreferences.OpenVPNDeepLink",
            "com.apple.systempreferences.CurrentlyConnectedVPN",
            "com.apple.systempreferences.CurrentlyConnectedVPN-UpdatableEntity",
            "com.apple.systempreferences.VPNConfigurationEntity-UpdatableEntity",
            "com.apple.HearingApp.AdjustVolumeIntent",
            "com.apple.HearingApp.MuteVolumeIntent",
            "com.apple.HearingApp.SelectPresetIntent",
            "HearingEarSelection",
            "VolumeDirection",
            "Apple Intelligence / AppKit Runtime Actions",
            "com.apple.AppKit.FetchIntelligenceCommands",
            "com.apple.AppKit.InsertIntelligenceText",
            "com.apple.AppKit.PresentWritingToolsResult",
            "com.apple.AppKit.RequestEditingContext",
            "com.apple.AppKit.RunIntelligenceCommand",
            "com.apple.AppKit.RunIntelligenceCommandForKey",
            "com.apple.AppKit.WritingToolsCanPerformIntent",
            "com.apple.AppKit.WritingToolsOpenEndedIntent",
            "com.apple.AppKit.WritingToolsPartnerIntent",
            "com.apple.AppKit.WritingToolsSummarizeIntent",
            "com.apple.AppKit.WritingToolsTransformKeyPointsIntent",
            "com.apple.AppKit.WritingToolsTransformListIntent",
            "com.apple.AppKit.WritingToolsTransformTableIntent",
            "processInstanceIdentifier",
            "targetWindowIdentifier",
            "targetFrame",
            "AccessibilityUtilities.framework",
            "ToggleHearingAidMute",
            "AXToggleHearingAidMuteIntent",
            "ToggleVehicleMotionCues",
            "AXToggleVehicleMotionCuesIntent",
            "Set Switch Control Switch Set",
            "SetSwitchControlProfile",
            "AXSetSwitchControlProfileIntent",
            "profile",
            "SwitchControlProfile",
            "WFWorkflowActionIdentifier",
            "com.apple.systempreferences.OpenAccessibilitySwitchControlStaticDeepLinks",
            "switchControlSwitches",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent",
            "com.apple.systempreferences.AxFeatureSwitchcontrolEntity-UpdatableEntity",
            "Toggle Vehicle Motion Cues",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent",
            "com.apple.systempreferences.AxMotionCuesEnabledEntity-UpdatableEntity",
            "Linked OS 18 to 26.1 ToolKit Deltas",
            "com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent",
            "OpenWhenRun",
            "com.apple.reminders.TTRCreateListAppIntent",
            "standard",
            "groceries",
            "com.apple.Photos.OpenPersonIntent",
            "com.apple.mobileslideshow.OpenPersonIntent",
            "com.apple.Photos.FilterLibraryIntent",
            "com.apple.mobileslideshow.FilterLibraryIntent",
            "viewMode",
            "both",
            "personal",
            "shared",
            "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent",
            "BalancedNoise",
            "Night",
            "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsVolumeIntent",
            "volumeValue",
            "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent",
            "endInterval",
            "duration",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent",
        )
        for rel_path in (
            "claude/skills/shortcuts-playground/APPINTENTS.md",
            "codex/skills/shortcuts-playground/APPINTENTS.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for term in required_appintent_terms:
                self.assertIn(term, text, f"{rel_path}: {term}")

    def test_automators_os26_to_27_action_rows_map_to_catalog_ids(self) -> None:
        expected_rows = {
            "Store Content": {"is.workflow.actions.setstoredcontent"},
            "Get Stored Content": {"is.workflow.actions.getstoredcontent"},
            "Delete Stored Content": {"is.workflow.actions.deletestoredcontent"},
            "Add Item to List": {"is.workflow.actions.additemtolist"},
            "Get Selected Text": {"is.workflow.actions.getselectedtext"},
            "Get Current VPN": {
                "is.workflow.actions.vpn.get",
                "com.apple.systempreferences.CurrentlyConnectedVPN",
            },
            "Find VPNs": {"is.workflow.actions.filter.vpns"},
            "Share and Collaborate": {"com.apple.sociallayerd.CollaborationIntent"},
            "Toggle Hearing Aid Mute": {"com.apple.HearingApp.MuteVolumeIntent"},
            "Toggle Vehicle Motion Cues": {
                "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent"
            },
            "Open Inbox": {"com.apple.MobileSMS.ChangeFilterModeIntent"},
            "Delete Conversations": {"com.apple.MobileSMS.DeleteConversationIntent"},
            "Delete Messages": {"com.apple.MobileSMS.DeleteMessageIntent"},
            "Mark as Read": {"com.apple.MobileSMS.MarkConversationAsUnreadIntent"},
            "Search in Messages": {"com.apple.MobileSMS.SearchMessagesIntent"},
            "Send Tapback": {"com.apple.MobileSMS.SendMessageReactionIntent"},
            "Find Album": {
                "com.apple.Photos.AlbumEntity",
                "com.apple.mobileslideshow.AlbumEntity",
            },
            "Auto Enhance Photo": {
                "com.apple.Photos.EnhanceIntent",
                "com.apple.mobileslideshow.EnhanceIntent",
            },
            "Favorite Photos": {
                "com.apple.Photos.FavoriteAssetsIntent",
                "com.apple.mobileslideshow.FavoriteAssetsIntent",
            },
            "Open Photo": {
                "com.apple.Photos.OpenAssetIntent",
                "com.apple.mobileslideshow.OpenAssetIntent",
            },
            "Hide Photos": {
                "com.apple.Photos.HideAssetsIntent",
                "com.apple.mobileslideshow.HideAssetsIntent",
            },
            "Delete Albums": {
                "com.apple.Photos.DeleteAlbumsIntent",
                "com.apple.mobileslideshow.DeleteAlbumsIntent",
            },
            "Find Message": {
                "com.apple.MobileSMS.MessageEntity",
                "com.apple.mail.MailMessage",
                "com.apple.mail.MailMessageEntity",
            },
            "Create Group": {"com.apple.reminders.CreateGroupAppIntent"},
            "Create Section": {"com.apple.reminders.CreateSectionAppIntent"},
            "Edit List": {"com.apple.reminders.ListEntity-UpdatableEntity"},
            "Delete Lists": {"com.apple.reminders.DeleteListsAppIntent"},
            "Delete Groups": {"com.apple.reminders.DeleteRemindersListGroupsAppIntent"},
            "Delete Sections": {"com.apple.reminders.DeleteSectionsAppIntent"},
            "Get What's On Screen": {"is.workflow.actions.getonscreencontext"},
        }
        private_switch_set_names = {
            "AXSetSwitchControlProfileIntent",
            "SetSwitchControlProfile",
            "Set Switch Control Switch Set",
        }

        for prefix in ("claude", "codex"):
            data_dir = REPO_ROOT / prefix / "skills/shortcuts-playground/data"
            tools = load_json(data_dir / "toolkit-v78-first-party-parameter-keys.json")[
                "tools"
            ]
            display_names = {
                tool.get("displayName")
                for tool in tools.values()
                if isinstance(tool, dict)
            }

            for display_name, identifiers in expected_rows.items():
                for identifier in identifiers:
                    self.assertIn(identifier, tools, f"{prefix}: {display_name}")

            self.assertIn("is.workflow.actions.getonscreencontent", tools, prefix)
            self.assertNotIn("Set Switch Control Switch Set", display_names, prefix)
            self.assertFalse(private_switch_set_names & set(tools), prefix)

            action_docs = (
                REPO_ROOT / prefix / "skills/shortcuts-playground/ACTIONS.md"
            ).read_text(encoding="utf-8")
            self.assertIn("Otherwise If", action_docs, prefix)
            self.assertIn("is.workflow.actions.conditional", action_docs, prefix)

    def test_os27_private_accessibility_intents_remain_sample_gated(self) -> None:
        private_intent_names = {
            "AXSetSwitchControlProfileIntent",
            "AXToggleHearingAidMuteIntent",
            "AXToggleVehicleMotionCuesIntent",
            "SetSwitchControlProfile",
            "ToggleHearingAidMute",
            "ToggleVehicleMotionCues",
        }
        confirmed_macos_ids = {
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent",
            "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent",
        }
        confirmed_ios_ids = {
            "com.apple.HearingApp.AdjustVolumeIntent",
            "com.apple.HearingApp.MuteVolumeIntent",
            "com.apple.HearingApp.SelectPresetIntent",
        }

        for prefix in ("claude", "codex"):
            data_dir = REPO_ROOT / prefix / "skills/shortcuts-playground/data"
            macos_ids = set(load_json(data_dir / "toolkit-v78-tool-ids.json")["ids"])
            ios_ids = set(load_json(data_dir / "toolkit-v78-ios27-tool-ids.json")["ids"])
            parameter_catalog = load_json(data_dir / "toolkit-v78-first-party-parameter-keys.json")
            display_names = {
                tool.get("displayName")
                for tool in parameter_catalog.get("tools", {}).values()
            }

            self.assertTrue(confirmed_macos_ids.issubset(macos_ids), prefix)
            self.assertTrue(confirmed_ios_ids.issubset(ios_ids), prefix)
            self.assertFalse(private_intent_names & macos_ids, prefix)
            self.assertFalse(private_intent_names & ios_ids, prefix)
            self.assertIn("Set Motion Cues", display_names, prefix)
            self.assertIn("Mute Hearing Device Volume", display_names, prefix)
            self.assertNotIn("Toggle Vehicle Motion Cues", display_names, prefix)
            self.assertNotIn("Toggle Hearing Aid Mute", display_names, prefix)
            self.assertNotIn("Set Switch Control Switch Set", display_names, prefix)

    def test_os27_accessibility_and_hearing_appintent_values_are_validated(self) -> None:
        def appintent(identifier: str, params: dict) -> dict:
            return {
                "WFWorkflowActionIdentifier": identifier,
                "WFWorkflowActionParameters": {
                    "AppIntentDescriptor": {"AppIntentIdentifier": identifier},
                    **params,
                },
            }

        macos_invalid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent",
                    {"operation": "enable", "state": "true", "ShowWhenRun": "false"},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent",
                    {"operation": "enable", "state": "true"},
                ),
                appintent(
                    "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                    {"appearanceToggle": "auto", "ShowWhenRun": "true"},
                ),
            ],
        }
        macos_valid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent",
                    {"operation": "toggle", "state": True, "ShowWhenRun": False},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent",
                    {"operation": "turn", "state": False},
                ),
                appintent(
                    "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                    {"ShowWhenRun": True},
                ),
            ],
        }
        ios_invalid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.HearingApp.AdjustVolumeIntent",
                    {"direction": "raise", "ear": "middle"},
                ),
                appintent(
                    "com.apple.HearingApp.SelectPresetIntent",
                    {"presetName": "Outdoor", "ear": "center"},
                ),
                appintent(
                    "com.apple.HearingApp.MuteVolumeIntent",
                    {"ear": "both"},
                ),
            ],
        }
        ios_valid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.HearingApp.AdjustVolumeIntent",
                    {"direction": "down", "ear": "right"},
                ),
                appintent(
                    "com.apple.HearingApp.SelectPresetIntent",
                    {"presetName": "Outdoor", "ear": "left"},
                ),
                appintent("com.apple.HearingApp.MuteVolumeIntent", {}),
                appintent(
                    "com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                    {"device": "Living Room", "appearanceToggle": "dark", "ShowWhenRun": True},
                ),
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            def validate_for(platform: str, plist: dict) -> list[str]:
                return module.validate(
                    plist,
                    allowed_ids=module.load_allowed_ids(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    unavailable_ids=module.load_future_toolkit_id_reasons(
                        skill_dir,
                        27,
                        target_platform=platform,
                    ),
                    unavailable_parameter_keys=module.load_future_parameter_key_reasons(27),
                    toolkit_parameter_schemas=module.load_toolkit_parameter_schemas(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    toolkit_parameter_enum_cases=module.load_toolkit_parameter_enum_cases(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    toolkit_parameter_boolean_keys=module.load_toolkit_parameter_boolean_keys(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                )[0]

            macos_boolean_keys = module.load_toolkit_parameter_boolean_keys(
                skill_dir,
                target_macos_major=27,
                target_platform="macos",
            )
            self.assertIn(
                "state",
                macos_boolean_keys["com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent"],
                rel_path,
            )
            self.assertIn(
                "ShowWhenRun",
                macos_boolean_keys["com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent"],
                rel_path,
            )
            self.assertIn(
                "ShowWhenRun",
                macos_boolean_keys["com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent"],
                rel_path,
            )

            macos_invalid_errors = validate_for("macos", macos_invalid)
            for expected in (
                "Invalid AppIntent enum value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent.operation",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent.state",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleMotionCuesIntent.ShowWhenRun",
                "Invalid AppIntent enum value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent.operation",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleSwitchControlIntent.state",
                "Unknown AppIntent parameter key(s) for com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent",
                "Invalid AppIntent boolean value for com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent.ShowWhenRun",
            ):
                self.assertTrue(
                    [error for error in macos_invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {macos_invalid_errors}",
                )

            macos_valid_errors = validate_for("macos", macos_valid)
            self.assertFalse(
                [
                    error
                    for error in macos_valid_errors
                    if "Invalid AppIntent enum value" in error
                    or "Invalid AppIntent boolean value" in error
                    or "Unknown AppIntent parameter" in error
                ],
                f"{rel_path}: {macos_valid_errors}",
            )

            ios_invalid_errors = validate_for("ios", ios_invalid)
            for expected in (
                "Invalid AppIntent enum value for com.apple.HearingApp.AdjustVolumeIntent.direction",
                "Invalid AppIntent enum value for com.apple.HearingApp.AdjustVolumeIntent.ear",
                "Invalid AppIntent enum value for com.apple.HearingApp.SelectPresetIntent.ear",
                "Unknown AppIntent parameter key(s) for com.apple.HearingApp.MuteVolumeIntent",
            ):
                self.assertTrue(
                    [error for error in ios_invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {ios_invalid_errors}",
                )

            ios_valid_errors = validate_for("ios", ios_valid)
            self.assertFalse(
                [
                    error
                    for error in ios_valid_errors
                    if "Invalid AppIntent enum value" in error
                    or "Unknown AppIntent parameter" in error
                    or "requires iOS-only" in error
                ],
                f"{rel_path}: {ios_valid_errors}",
            )

    def test_automators_followup_appintent_values_are_validated(self) -> None:
        def appintent(identifier: str, params: dict) -> dict:
            return {
                "WFWorkflowActionIdentifier": identifier,
                "WFWorkflowActionParameters": {
                    "AppIntentDescriptor": {"AppIntentIdentifier": identifier},
                    **params,
                },
            }

        macos_invalid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent",
                    {"repeats": "weekday", "allowsSnooze": "yes", "OpenWhenRun": "no"},
                ),
                appintent(
                    "com.apple.reminders.TTRCreateListAppIntent",
                    {"type": "smart", "OpenWhenRun": "true"},
                ),
                appintent("com.apple.Photos.FilterLibraryIntent", {"viewMode": "combined"}),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent",
                    {"backgroundSound": "Forest", "ShowWhenRun": "true"},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent",
                    {"interval": "later", "always": "false", "ShowWhenRun": "true"},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent",
                    {"operation": "enable", "state": "true", "ShowWhenRun": "false"},
                ),
            ],
        }
        macos_valid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent",
                    {
                        "name": "Review Automators",
                        "repeats": "monday",
                        "allowsSnooze": True,
                        "OpenWhenRun": False,
                    },
                ),
                appintent(
                    "com.apple.reminders.TTRCreateListAppIntent",
                    {"name": "Groceries", "type": "groceries", "OpenWhenRun": True},
                ),
                appintent("com.apple.Photos.FilterLibraryIntent", {"viewMode": "shared"}),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent",
                    {"backgroundSound": "Rain", "ShowWhenRun": False},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent",
                    {"interval": "duration", "always": True, "ShowWhenRun": False},
                ),
                appintent(
                    "com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent",
                    {"operation": "turn", "state": True, "ShowWhenRun": False},
                ),
            ],
        }
        ios_invalid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.mobileslideshow.FilterLibraryIntent",
                    {"viewMode": "combined"},
                ),
            ],
        }
        ios_valid = {
            "WFWorkflowActions": [
                appintent(
                    "com.apple.mobileslideshow.FilterLibraryIntent",
                    {"viewMode": "personal"},
                ),
            ],
        }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]

            def validate_for(platform: str, plist: dict) -> list[str]:
                return module.validate(
                    plist,
                    allowed_ids=module.load_allowed_ids(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    unavailable_ids=module.load_future_toolkit_id_reasons(
                        skill_dir,
                        27,
                        target_platform=platform,
                    ),
                    unavailable_parameter_keys=module.load_future_parameter_key_reasons(27),
                    toolkit_parameter_schemas=module.load_toolkit_parameter_schemas(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    toolkit_parameter_enum_cases=module.load_toolkit_parameter_enum_cases(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                    toolkit_parameter_boolean_keys=module.load_toolkit_parameter_boolean_keys(
                        skill_dir,
                        target_macos_major=27,
                        target_platform=platform,
                    ),
                )[0]

            macos_invalid_errors = validate_for("macos", macos_invalid)
            for expected in (
                "Invalid AppIntent enum value for com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent.repeats",
                "Invalid AppIntent boolean value for com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent.allowsSnooze",
                "Invalid AppIntent boolean value for com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent.OpenWhenRun",
                "Invalid AppIntent enum value for com.apple.reminders.TTRCreateListAppIntent.type",
                "Invalid AppIntent boolean value for com.apple.reminders.TTRCreateListAppIntent.OpenWhenRun",
                "Invalid AppIntent enum value for com.apple.Photos.FilterLibraryIntent.viewMode",
                "Invalid AppIntent enum value for com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent.backgroundSound",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundIntent.ShowWhenRun",
                "Invalid AppIntent enum value for com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent.interval",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent.always",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UASetBackgroundSoundsTimerIntent.ShowWhenRun",
                "Invalid AppIntent enum value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent.operation",
                "Invalid AppIntent boolean value for com.apple.UniversalAccess.UASettingsShortcuts.UAToggleBackgroundSoundsIntent.state",
            ):
                self.assertTrue(
                    [error for error in macos_invalid_errors if expected in error],
                    f"{rel_path}: missing {expected}: {macos_invalid_errors}",
                )

            macos_valid_errors = validate_for("macos", macos_valid)
            self.assertFalse(
                [
                    error
                    for error in macos_valid_errors
                    if "Invalid AppIntent enum value" in error
                    or "Invalid AppIntent boolean value" in error
                    or "Unknown AppIntent parameter" in error
                ],
                f"{rel_path}: {macos_valid_errors}",
            )

            ios_invalid_errors = validate_for("ios", ios_invalid)
            self.assertTrue(
                [
                    error
                    for error in ios_invalid_errors
                    if "Invalid AppIntent enum value for com.apple.mobileslideshow.FilterLibraryIntent.viewMode"
                    in error
                ],
                f"{rel_path}: {ios_invalid_errors}",
            )

            ios_valid_errors = validate_for("ios", ios_valid)
            self.assertFalse(
                [
                    error
                    for error in ios_valid_errors
                    if "Invalid AppIntent enum value" in error
                    or "Unknown AppIntent parameter" in error
                    or "requires iOS-only" in error
                ],
                f"{rel_path}: {ios_valid_errors}",
            )

    def test_open_app_windowing_format_values_are_validated(self) -> None:
        def open_app(windowing_format: str) -> dict:
            return {
                "WFWorkflowActionIdentifier": "is.workflow.actions.openapp",
                "WFWorkflowActionParameters": {
                    "WFSelectedApp": {
                        "BundleIdentifier": "com.apple.MobileSMS",
                        "Name": "Messages",
                    },
                    "WFWindowingFormat": windowing_format,
                },
            }

        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/validate_shortcut.py",
            "codex/skills/shortcuts-playground/scripts/validate_shortcut.py",
        ):
            module, module_path = self.load_validator_module(rel_path)
            skill_dir = module_path.parents[1]
            allowed_ids = module.load_allowed_ids(
                skill_dir,
                target_macos_major=27,
                target_platform="ios",
            )

            invalid_errors = module.validate(
                {"WFWorkflowActions": [open_app("Stage Left")]},
                allowed_ids=allowed_ids,
                unavailable_ids={},
                unavailable_parameter_keys={},
                toolkit_parameter_schemas={},
                toolkit_parameter_enum_cases={},
                toolkit_parameter_boolean_keys={},
            )[0]
            self.assertTrue(
                [
                    error
                    for error in invalid_errors
                    if "Open App has unknown WFWindowingFormat" in error
                ],
                f"{rel_path}: {invalid_errors}",
            )

            valid_errors = module.validate(
                {"WFWorkflowActions": [open_app("Left Third")]},
                allowed_ids=allowed_ids,
                unavailable_ids={},
                unavailable_parameter_keys={},
                toolkit_parameter_schemas={},
                toolkit_parameter_enum_cases={},
                toolkit_parameter_boolean_keys={},
            )[0]
            self.assertFalse(
                [
                    error
                    for error in valid_errors
                    if "Open App has unknown WFWindowingFormat" in error
                ],
                f"{rel_path}: {valid_errors}",
            )

    def test_random_mixed_suite_can_include_os27_action_module(self) -> None:
        required_ids = {
            "is.workflow.actions.additemtolist",
            "is.workflow.actions.setstoredcontent",
            "is.workflow.actions.getstoredcontent",
            "is.workflow.actions.deletestoredcontent",
            "is.workflow.actions.getselectedtext",
            "is.workflow.actions.getonscreencontext",
            "is.workflow.actions.vpn.get",
        }
        for rel_path in (
            "claude/skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py",
            "codex/skills/shortcuts-playground/scripts/test_random_mixed_shortcuts.py",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / rel_path),
                        "--count",
                        "1",
                        "--min-actions",
                        "10",
                        "--target-macos",
                        "27",
                        "--include-os27-actions",
                        "--output-dir",
                        tmp,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                out_line = next(
                    line for line in result.stdout.splitlines() if line.startswith("OUT_DIR=")
                )
                manifest = load_json(Path(out_line.removeprefix("OUT_DIR=")) / "manifest.json")
                self.assertEqual(1, len(manifest), rel_path)
                self.assertTrue(required_ids.issubset(set(manifest[0]["action_ids"])), rel_path)
                self.assertIn("os27.actions", manifest[0]["extras_used"], rel_path)

    def test_claude_selftest_checks_parameter_catalog(self) -> None:
        text = (REPO_ROOT / "claude/bin/shortcuts-playground-selftest").read_text(encoding="utf-8")
        self.assertIn("toolkit-v78-first-party-parameter-keys.json", text)
        self.assertIn("toolkit-v78-first-party-enum-cases.json", text)
        self.assertIn("toolkit-v78-trigger-parameter-keys.json", text)
        self.assertIn("macos27-workflow-trigger-samples.json", text)

    def test_claude_agents_use_packaged_grounding_for_appintent_gaps(self) -> None:
        for rel_path in (
            "claude/agents/shortcut-builder.md",
            "claude/agents/shortcut-remixer.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertIn("lookup_action_grounding.py", text, rel_path)
            self.assertIn("bundled JSON only", text, rel_path)
            self.assertIn("toolkit-parameter-summary", text, rel_path)


class PackageConsistencyTests(unittest.TestCase):
    def test_shared_codex_and_claude_skill_files_do_not_drift(self) -> None:
        codex_root = REPO_ROOT / "codex/skills/shortcuts-playground"
        claude_root = REPO_ROOT / "claude/skills/shortcuts-playground"
        expected_drift = {
            "BEST_PRACTICES.md",
            "README.md",
            "SKILL.md",
            "scripts/sign_shortcut.sh",
        }

        codex_files = {
            path.relative_to(codex_root).as_posix(): path
            for path in codex_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        claude_files = {
            path.relative_to(claude_root).as_posix(): path
            for path in claude_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }

        unexpected: list[str] = []
        for rel_path in sorted(set(codex_files) - set(claude_files)):
            if rel_path not in expected_drift:
                unexpected.append(f"codex-only: {rel_path}")
        for rel_path in sorted(set(claude_files) - set(codex_files)):
            if rel_path not in expected_drift:
                unexpected.append(f"claude-only: {rel_path}")
        for rel_path in sorted(set(codex_files) & set(claude_files)):
            if rel_path in expected_drift:
                continue
            if codex_files[rel_path].read_bytes() != claude_files[rel_path].read_bytes():
                unexpected.append(f"content drift: {rel_path}")

        self.assertEqual([], unexpected)

    def test_readmes_surface_os27_catalogs_without_stale_counts(self) -> None:
        for rel_path in (
            "README.md",
            "codex/README.md",
            "codex/skills/shortcuts-playground/README.md",
            "claude/README.md",
            "claude/INSTALL.md",
            "claude/skills/shortcuts-playground/README.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertNotIn("57 best-practice", text, rel_path)
            self.assertNotIn("13 reference markdown files", text, rel_path)

        root_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("exported `WFWorkflowTriggers` catalogs", root_text)

        codex_text = (REPO_ROOT / "codex/README.md").read_text(encoding="utf-8")
        self.assertIn("toolkit-v78-first-party-parameter-keys.json", codex_text)
        self.assertIn("toolkit-v78-first-party-enum-cases.json", codex_text)
        self.assertIn("toolkit-v78-trigger-parameter-keys.json", codex_text)
        self.assertIn("macos27-workflow-trigger-samples.json", codex_text)

        install_text = (REPO_ROOT / "claude/INSTALL.md").read_text(encoding="utf-8")
        self.assertIn("v1.1.0", install_text)
        self.assertNotIn("You're installing **v1.0**", install_text)

        for rel_path in (
            "codex/skills/shortcuts-playground/README.md",
            "claude/skills/shortcuts-playground/README.md",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertIn("AUTOMATION_TRIGGERS.md", text, rel_path)
            self.assertIn("toolkit-v78-first-party-parameter-keys.json", text, rel_path)
            self.assertIn("toolkit-v78-first-party-enum-cases.json", text, rel_path)
            self.assertIn("toolkit-v78-trigger-parameter-keys.json", text, rel_path)
            self.assertIn("macos27-workflow-trigger-samples.json", text, rel_path)


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

    def test_codex_sign_shortcut_retries_format_error_after_binary_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "out"
            result = self.run_wrapper(
                REPO_ROOT / "codex/skills/shortcuts-playground/scripts/sign_shortcut.sh",
                {"SHORTCUTS_PLAYGROUND_OUTPUT_DIR": str(output_dir)},
                stub_mode="format-error-once",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("binary plist conversion", result.stderr)
            payload = json.loads(result.stdout)
            signed_path = Path(payload["signed"])
            self.assertEqual(output_dir / "Issue Regression.shortcut", signed_path)
            self.assertTrue(signed_path.exists())

    def test_claude_sign_shortcut_reports_unrestricted_shell_hint_on_format_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_wrapper(
                REPO_ROOT / "claude/bin/sign-shortcut",
                {"CLAUDE_PLUGIN_OPTION_OUTPUT_DIR": str(Path(tmp) / "out")},
                stub_mode="format-error",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(FORMAT_ERROR, result.stderr)
            self.assertIn("retry from an unrestricted shell", result.stderr)

    def test_claude_sign_shortcut_retries_format_error_after_binary_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "out"
            result = self.run_wrapper(
                REPO_ROOT / "claude/bin/sign-shortcut",
                {"CLAUDE_PLUGIN_OPTION_OUTPUT_DIR": str(output_dir)},
                stub_mode="format-error-once",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("binary plist conversion", result.stderr)
            payload = json.loads(result.stdout)
            signed_path = Path(payload["signed"])
            self.assertEqual(output_dir / "Issue Regression.shortcut", signed_path)
            self.assertTrue(signed_path.exists())


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
