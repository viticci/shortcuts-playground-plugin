#!/usr/bin/env python3
"""Look up reviewed Apple-derived Shortcuts grounding metadata.

This helper reads the packaged static macOS 27 Shortpy catalog plus compact
ToolKit v78 first-party parameter-key, enum-case, trigger, and exported
workflow-trigger snapshots. It never reads the user's live Shortcuts databases
and never calls private Apple frameworks.
Use it as an authoring aid when a macOS 27 action or Apple Shortpy function
name needs additional grounding beyond the markdown references.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


TARGET_MACOS_ENV_VARS = (
    "SHORTCUTS_PLAYGROUND_TARGET_MACOS",
    "CLAUDE_PLUGIN_OPTION_TARGET_MACOS",
)
TARGET_PLATFORM_ENV_VARS = (
    "SHORTCUTS_PLAYGROUND_TARGET_PLATFORM",
    "CLAUDE_PLUGIN_OPTION_TARGET_PLATFORM",
)
TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR = {
    "toolkit-v78": 27,
    "toolkit-v78-ios27": 27,
}
PARAMETER_CATALOG_MIN_MACOS_MAJOR = 27
TRIGGER_CATALOG_MIN_MACOS_MAJOR = 27
WORKFLOW_TRIGGER_CATALOG_MIN_MACOS_MAJOR = 27
DEPRECATED_IDENTIFIER_NOTES = {
    "is.workflow.actions.getonscreencontent": (
        "Deprecated in ToolKit v78; use is.workflow.actions.getonscreencontext "
        "for new Get What's On Screen shortcuts."
    ),
}


def toolkit_snapshot_min_macos_major(version: str | None) -> int | None:
    if not isinstance(version, str) or not version:
        return None
    if version in TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR:
        return TOOLKIT_SNAPSHOT_MIN_MACOS_MAJOR[version]
    import re

    match = re.search(r"v(\d+)", version)
    if match and int(match.group(1)) >= 78:
        return 27
    return None


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/macos27-shortpy-grounding.json"


def parameter_catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/toolkit-v78-first-party-parameter-keys.json"


def enum_catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/toolkit-v78-first-party-enum-cases.json"


def trigger_catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/toolkit-v78-trigger-parameter-keys.json"


def workflow_trigger_catalog_path(base: Path | None = None) -> Path:
    return (base or skill_dir()) / "data/macos27-workflow-trigger-samples.json"


def load_catalog(base: Path | None = None) -> dict[str, Any]:
    path = catalog_path(base)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_parameter_catalog(base: Path | None = None) -> dict[str, Any]:
    path = parameter_catalog_path(base)
    if not path.exists():
        return {"tools": {}}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_enum_catalog(base: Path | None = None) -> dict[str, Any]:
    path = enum_catalog_path(base)
    if not path.exists():
        return {"types": {}}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_trigger_catalog(base: Path | None = None) -> dict[str, Any]:
    path = trigger_catalog_path(base)
    if not path.exists():
        return {"triggers": {}}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_workflow_trigger_catalog(base: Path | None = None) -> dict[str, Any]:
    path = workflow_trigger_catalog_path(base)
    if not path.exists():
        return {"triggers": {}}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_identifier_min_macos(base: Path | None = None) -> dict[str, int | None]:
    """Return the earliest packaged snapshot availability for each identifier."""

    data_dir = (base or skill_dir()) / "data"
    availability: dict[str, int | None] = {}
    for path in sorted(data_dir.glob("toolkit-v*-tool-ids.json")):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        version = payload.get("version") or path.stem.replace("-tool-ids", "")
        min_macos = toolkit_snapshot_min_macos_major(version)
        ids = set(payload.get("ids") or [])
        ids.update(payload.get("control_flow_exceptions_missing_from_tools_table") or [])
        for identifier in ids:
            if identifier not in availability:
                availability[identifier] = min_macos
            elif availability[identifier] is not None and (
                min_macos is None or min_macos < availability[identifier]
            ):
                availability[identifier] = min_macos
    return availability


def host_macos_major() -> int | None:
    if platform.system() != "Darwin":
        return None
    try:
        result = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    major = result.stdout.strip().split(".", 1)[0]
    return int(major) if major.isdigit() else None


def resolve_target_macos(value: str | None) -> int | None:
    raw = value
    if raw is None:
        for env_name in TARGET_MACOS_ENV_VARS:
            raw = os.environ.get(env_name)
            if raw:
                break
    if raw is None or raw == "" or raw.lower() == "auto":
        detected = host_macos_major()
        return detected if detected is not None else 26
    if raw.lower() in {"latest", "all"}:
        return None
    if raw.isdigit():
        return int(raw)
    raise ValueError(f"Invalid macOS target: {raw!r}")


def resolve_target_platform(value: str | None) -> str | None:
    raw = value
    if raw is None:
        for env_name in TARGET_PLATFORM_ENV_VARS:
            raw = os.environ.get(env_name)
            if raw:
                break
    if raw is None:
        raw = "macos"
    normalized = raw.strip().lower().replace("_", "-")
    if normalized in {"", "auto", "host", "mac", "macos", "mac-os"}:
        return "macos"
    if normalized in {"ios", "ipados", "iphone", "ipad"}:
        return "ios"
    if normalized in {"latest", "all", "any"}:
        return None
    raise ValueError(f"Invalid target platform: {raw!r}")


def normalized_identifier(value: str) -> str:
    if value.startswith("is.workflow.actions."):
        return value
    return f"is.workflow.actions.{value}"


def find_by_identifier(catalog: dict[str, Any], value: str) -> tuple[str, dict[str, Any]] | None:
    tools = catalog.get("tools") or {}
    structural = catalog.get("structuralActions") or {}
    candidates = {**tools, **structural}
    for key in (value, normalized_identifier(value)):
        if key in candidates:
            return key, candidates[key]
    suffix = value.removeprefix("is.workflow.actions.")
    matches = [
        (identifier, entry)
        for identifier, entry in candidates.items()
        if identifier.endswith(f".{suffix}") or identifier.rsplit(".", 1)[-1] == suffix
    ]
    return matches[0] if len(matches) == 1 else None


def find_by_python_name(catalog: dict[str, Any], value: str) -> tuple[str, dict[str, Any]] | None:
    lookup = catalog.get("pythonLookup") or {}
    if value in lookup:
        entry = lookup[value]
        identifier = entry.get("wfIdentifier")
        if identifier:
            found = find_by_identifier(catalog, identifier)
            return found or (identifier, entry)
    for identifier, entry in (catalog.get("tools") or {}).items():
        if entry.get("pythonName") == value:
            return identifier, entry
    return None


def parameter_entry_to_grounding(identifier: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "toolkit-parameter-summary",
        "name": entry.get("displayName") or identifier,
        "pythonName": entry.get("pythonName"),
        "summary": (
            "ToolKit v78 parameter-key summary. This proves the action exists "
            "and names its parameters, but it is not a full authored shortcut sample."
        ),
        "toolkitPlatforms": entry.get("platforms") or [],
        "toolkitToolType": entry.get("toolType"),
        "toolkitParameterSummary": {
            "parameterCount": entry.get("parameterCount"),
            "parameters": entry.get("parameters") or [],
        },
        "parameters": [],
        "sourceFunctions": {},
        "sampleShortcuts": [],
    }


def trigger_entry_to_grounding(identifier: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "toolkit-trigger-summary",
        "minimumMacOSMajor": TRIGGER_CATALOG_MIN_MACOS_MAJOR,
        "name": entry.get("displayName") or identifier,
        "pythonName": entry.get("pythonName"),
        "summary": (
            "ToolKit v78 automation-trigger metadata. This proves the trigger "
            "exists and names its parameters. When present, workflowTriggerSample "
            "shows the exported WFWorkflowTriggers plist shape for OS 27 shortcut XML."
        ),
        "toolkitPlatforms": entry.get("platforms") or [],
        "toolkitTriggerSummary": {
            "parameterCount": entry.get("parameterCount"),
            "parameters": entry.get("parameters") or [],
            "outputTypeIdentifiers": entry.get("outputTypeIdentifiers") or [],
        },
        "parameters": [],
        "sourceFunctions": {},
        "sampleShortcuts": [],
    }


def augment_with_parameter_summary(
    identifier: str,
    entry: dict[str, Any],
    parameter_catalog: dict[str, Any],
) -> dict[str, Any]:
    toolkit_entry = (parameter_catalog.get("tools") or {}).get(identifier)
    if not isinstance(toolkit_entry, dict):
        return entry
    out = dict(entry)
    out["toolkitPlatforms"] = toolkit_entry.get("platforms") or []
    out["toolkitToolType"] = toolkit_entry.get("toolType")
    out["toolkitParameterSummary"] = {
        "parameterCount": toolkit_entry.get("parameterCount"),
        "parameters": toolkit_entry.get("parameters") or [],
    }
    return out


def toolkit_parameter_type_names(parameter: dict[str, Any]) -> list[str]:
    type_names = parameter.get("typePythonNames")
    if isinstance(type_names, list):
        return [str(name) for name in type_names if name]
    single = parameter.get("typePythonName")
    return [str(single)] if single else []


def toolkit_parameter_matches_target(
    parameter: dict[str, Any],
    target_platform: str | None,
) -> bool:
    platforms = parameter.get("platforms")
    if not isinstance(platforms, list) or not platforms:
        return True
    return platform_matches_target(
        [str(platform) for platform in platforms if platform],
        target_platform,
    )


def toolkit_parameter_type_names_for_target(
    parameter: dict[str, Any],
    target_platform: str | None,
) -> list[str]:
    if target_platform is not None:
        by_platform = parameter.get("typePythonNamesByPlatform")
        if isinstance(by_platform, dict):
            names: list[str] = []
            for platform, type_names in by_platform.items():
                if not isinstance(platform, str) or not platform_matches_target(
                    [platform],
                    target_platform,
                ):
                    continue
                if isinstance(type_names, list):
                    names.extend(str(name) for name in type_names if name)
            if names:
                return sorted(set(names))
    return toolkit_parameter_type_names(parameter)


def filter_toolkit_parameter_for_target(
    parameter: dict[str, Any],
    target_platform: str | None,
) -> dict[str, Any] | None:
    if not toolkit_parameter_matches_target(parameter, target_platform):
        return None
    out = dict(parameter)
    if target_platform is not None:
        type_names = toolkit_parameter_type_names_for_target(parameter, target_platform)
        if len(type_names) == 1:
            out["typePythonName"] = type_names[0]
            out.pop("typePythonNames", None)
        elif type_names:
            out.pop("typePythonName", None)
            out["typePythonNames"] = type_names
    return out


def filter_toolkit_parameter_summary_for_target(
    summary: dict[str, Any],
    target_platform: str | None,
) -> dict[str, Any]:
    parameters = summary.get("parameters")
    if not isinstance(parameters, list):
        return summary
    filtered: list[dict[str, Any]] = []
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        filtered_parameter = filter_toolkit_parameter_for_target(
            parameter,
            target_platform,
        )
        if filtered_parameter is not None:
            filtered.append(filtered_parameter)
    out = dict(summary)
    out["parameters"] = filtered
    out["parameterCount"] = len(filtered)
    return out


def filter_entry_for_target_platform(
    entry: dict[str, Any],
    target_platform: str | None,
) -> dict[str, Any]:
    summary = entry.get("toolkitParameterSummary")
    if not isinstance(summary, dict):
        return entry
    out = dict(entry)
    out["toolkitParameterSummary"] = filter_toolkit_parameter_summary_for_target(
        summary,
        target_platform,
    )
    return out


def enum_type_summary(
    type_python_name: str,
    enum_catalog: dict[str, Any],
) -> dict[str, Any] | None:
    enum_entry = (enum_catalog.get("types") or {}).get(type_python_name)
    if not isinstance(enum_entry, dict):
        return None
    cases = enum_entry.get("cases") or []
    if not cases:
        return None
    return {
        "typePythonName": type_python_name,
        "displayNames": enum_entry.get("displayNames") or [],
        "platforms": enum_entry.get("platforms") or [],
        "caseCount": enum_entry.get("caseCount") or len(cases),
        "cases": cases,
    }


def augment_parameter_with_enum_cases(
    parameter: dict[str, Any],
    enum_catalog: dict[str, Any],
) -> dict[str, Any]:
    enum_types = [
        enum_type
        for type_name in toolkit_parameter_type_names(parameter)
        if (enum_type := enum_type_summary(type_name, enum_catalog)) is not None
    ]
    if not enum_types:
        return parameter
    out = dict(parameter)
    out["enumTypes"] = enum_types
    if len(enum_types) == 1:
        out["enumCases"] = enum_types[0]["cases"]
        out["enumCaseCount"] = enum_types[0]["caseCount"]
        out["enumDisplayNames"] = enum_types[0]["displayNames"]
    return out


def augment_summary_parameters_with_enum_cases(
    summary: dict[str, Any],
    enum_catalog: dict[str, Any],
) -> dict[str, Any]:
    parameters = summary.get("parameters")
    if not isinstance(parameters, list):
        return summary
    out = dict(summary)
    out["parameters"] = [
        augment_parameter_with_enum_cases(parameter, enum_catalog)
        if isinstance(parameter, dict)
        else parameter
        for parameter in parameters
    ]
    return out


def augment_with_enum_cases(
    entry: dict[str, Any],
    enum_catalog: dict[str, Any],
) -> dict[str, Any]:
    out = dict(entry)
    parameter_summary = out.get("toolkitParameterSummary")
    if isinstance(parameter_summary, dict):
        out["toolkitParameterSummary"] = augment_summary_parameters_with_enum_cases(
            parameter_summary,
            enum_catalog,
        )
    trigger_summary = out.get("toolkitTriggerSummary")
    if isinstance(trigger_summary, dict):
        out["toolkitTriggerSummary"] = augment_summary_parameters_with_enum_cases(
            trigger_summary,
            enum_catalog,
        )
    return out


def augment_with_workflow_trigger_sample(
    identifier: str,
    entry: dict[str, Any],
    workflow_trigger_catalog: dict[str, Any],
) -> dict[str, Any]:
    sample = (workflow_trigger_catalog.get("triggers") or {}).get(identifier)
    if not isinstance(sample, dict):
        return entry
    out = dict(entry)
    out["workflowTriggerSample"] = sample
    return out


def find_parameter_by_identifier(
    parameter_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    tools = parameter_catalog.get("tools") or {}
    for key in (value, normalized_identifier(value)):
        entry = tools.get(key)
        if isinstance(entry, dict):
            return key, parameter_entry_to_grounding(key, entry)
    suffix = value.removeprefix("is.workflow.actions.")
    matches = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in tools.items()
        if identifier.endswith(f".{suffix}") or identifier.rsplit(".", 1)[-1] == suffix
    ]
    return matches[0] if len(matches) == 1 else None


def find_parameter_by_python_name(
    parameter_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    tools = parameter_catalog.get("tools") or {}
    matches = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in tools.items()
        if entry.get("pythonName") == value
    ]
    return matches[0] if len(matches) == 1 else None


def find_trigger_by_identifier(
    trigger_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    triggers = trigger_catalog.get("triggers") or {}
    entry = triggers.get(value)
    if isinstance(entry, dict):
        return value, trigger_entry_to_grounding(value, entry)
    suffix = value.removeprefix("com.apple.shortcuts.")
    matches = [
        (identifier, trigger_entry_to_grounding(identifier, entry))
        for identifier, entry in triggers.items()
        if identifier.endswith(suffix) or identifier.rsplit(".", 1)[-1] == suffix
    ]
    return matches[0] if len(matches) == 1 else None


def find_trigger_by_python_name(
    trigger_catalog: dict[str, Any],
    value: str,
) -> tuple[str, dict[str, Any]] | None:
    triggers = trigger_catalog.get("triggers") or {}
    matches = [
        (identifier, trigger_entry_to_grounding(identifier, entry))
        for identifier, entry in triggers.items()
        if entry.get("pythonName") == value
    ]
    return matches[0] if len(matches) == 1 else None


def entry_search_text(identifier: str, entry: dict[str, Any]) -> str:
    parts: list[str] = [
        identifier,
        entry.get("status") or "",
        entry.get("name") or "",
        entry.get("pythonName") or "",
        entry.get("summary") or "",
        " ".join(entry.get("keywords") or []),
        " ".join(entry.get("sourceFunctions") or {}),
    ]
    for parameter in entry.get("parameters") or []:
        parts.extend(
            [
                parameter.get("wfKey") or "",
                parameter.get("pythonKeyword") or "",
                parameter.get("label") or "",
                parameter.get("description") or "",
            ]
        )
    toolkit_summary = entry.get("toolkitParameterSummary") or {}
    if isinstance(toolkit_summary, dict):
        for parameter in toolkit_summary.get("parameters") or []:
            if isinstance(parameter, dict):
                parts.extend(
                    [
                        parameter.get("key") or "",
                        parameter.get("name") or "",
                        parameter.get("typePythonName") or "",
                        " ".join(toolkit_parameter_type_names(parameter)),
                    ]
                )
    trigger_summary = entry.get("toolkitTriggerSummary") or {}
    if isinstance(trigger_summary, dict):
        parts.append(" ".join(trigger_summary.get("outputTypeIdentifiers") or []))
        for parameter in trigger_summary.get("parameters") or []:
            if isinstance(parameter, dict):
                parts.extend(
                    [
                        parameter.get("key") or "",
                        parameter.get("name") or "",
                        parameter.get("typePythonName") or "",
                        " ".join(toolkit_parameter_type_names(parameter)),
                    ]
                )
    workflow_trigger = entry.get("workflowTriggerSample") or {}
    if isinstance(workflow_trigger, dict):
        parts.append("workflow triggers exported automation header")
        parts.extend(workflow_trigger.get("notes") or [])
        payload = workflow_trigger.get("workflowTrigger") or {}
        if isinstance(payload, dict):
            parts.append(str(payload.get("WFTriggerIdentifier") or ""))
            serialized = payload.get("WFTriggerSerializedParameters") or {}
            if isinstance(serialized, dict):
                parts.extend(str(key) for key in serialized)
    return "\n".join(parts).lower()


def search_entries(catalog: dict[str, Any], query: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    terms = [term.lower() for term in query.split() if term]
    tools = catalog.get("tools") or {}
    structural = catalog.get("structuralActions") or {}
    entries = sorted({**tools, **structural}.items())
    if not terms:
        return entries[:limit]
    matches = [
        (identifier, entry)
        for identifier, entry in entries
        if all(term in entry_search_text(identifier, entry) for term in terms)
    ]
    return matches[:limit]


def search_parameter_entries(
    parameter_catalog: dict[str, Any],
    query: str,
    limit: int,
) -> list[tuple[str, dict[str, Any]]]:
    terms = [term.lower() for term in query.split() if term]
    entries = sorted((parameter_catalog.get("tools") or {}).items())
    converted = [
        (identifier, parameter_entry_to_grounding(identifier, entry))
        for identifier, entry in entries
    ]
    if not terms:
        return converted[:limit]
    return [
        (identifier, entry)
        for identifier, entry in converted
        if all(term in entry_search_text(identifier, entry) for term in terms)
    ][:limit]


def search_trigger_entries(
    trigger_catalog: dict[str, Any],
    query: str,
    limit: int,
) -> list[tuple[str, dict[str, Any]]]:
    terms = [term.lower() for term in query.split() if term]
    entries = sorted((trigger_catalog.get("triggers") or {}).items())
    converted = [
        (identifier, trigger_entry_to_grounding(identifier, entry))
        for identifier, entry in entries
    ]
    if not terms:
        return converted[:limit]
    return [
        (identifier, entry)
        for identifier, entry in converted
        if all(term in entry_search_text(identifier, entry) for term in terms)
    ][:limit]


def target_note(minimum: int | None, target_macos: int | None) -> str | None:
    if target_macos is not None and minimum is not None and target_macos < minimum:
        return f"Requires macOS {minimum}+; target macOS is {target_macos}."
    return None


def deprecation_note(identifier: str) -> str | None:
    return DEPRECATED_IDENTIFIER_NOTES.get(identifier)


def platform_availability_note(entry: dict[str, Any]) -> str | None:
    platforms = entry.get("toolkitPlatforms") or []
    if not isinstance(platforms, list) or not platforms:
        return None
    platform_text = [str(platform) for platform in platforms]
    has_macos = any("macos" in platform.lower() for platform in platform_text)
    has_ios = any("ios" in platform.lower() for platform in platform_text)
    if has_ios and not has_macos:
        return "Only observed in iOS 27 Simulator ToolKit; no macOS ToolKit row observed."
    if has_macos and not has_ios:
        return "Only observed in macOS 27 ToolKit; no iOS 27 Simulator ToolKit row observed."
    return None


def target_platform_label(target_platform: str | None) -> str:
    if target_platform == "ios":
        return "iOS/iPadOS"
    if target_platform == "macos":
        return "macOS"
    return "all platforms"


def platform_matches_target(platforms: list[str], target_platform: str | None) -> bool:
    if target_platform is None:
        return True
    for platform in platforms:
        normalized = platform.lower()
        if target_platform == "ios" and "ios" in normalized:
            return True
        if target_platform == "macos" and "macos" in normalized:
            return True
    return False


def target_platform_note(entry: dict[str, Any], target_platform: str | None) -> str | None:
    platforms = entry.get("toolkitPlatforms") or []
    if not isinstance(platforms, list) or not platforms:
        return None
    platform_text = [str(platform) for platform in platforms]
    if platform_matches_target(platform_text, target_platform):
        return None
    observed = ", ".join(platform_text)
    return (
        f"Only observed for {observed}; target platform is "
        f"{target_platform_label(target_platform)}."
    )


def has_toolkit_parameter_summary(entry: dict[str, Any]) -> bool:
    summary = entry.get("toolkitParameterSummary")
    if not isinstance(summary, dict):
        return False
    return "parameterCount" in summary or bool(summary.get("parameters"))


def parameter_metadata_note(
    entry: dict[str, Any],
    target_macos: int | None,
    action_minimum_macos: int | None,
) -> str | None:
    if target_macos is None or target_macos >= PARAMETER_CATALOG_MIN_MACOS_MAJOR:
        return None
    if not has_toolkit_parameter_summary(entry):
        return None
    if action_minimum_macos is not None and action_minimum_macos > target_macos:
        return None
    return (
        f"Parameter metadata is from OS {PARAMETER_CATALOG_MIN_MACOS_MAJOR} ToolKit; "
        f"target macOS is {target_macos}."
    )


def trigger_metadata_note(entry: dict[str, Any], target_macos: int | None) -> str | None:
    if target_macos is None or target_macos >= TRIGGER_CATALOG_MIN_MACOS_MAJOR:
        return None
    if not isinstance(entry.get("toolkitTriggerSummary"), dict):
        return None
    return (
        f"Trigger metadata is from OS {TRIGGER_CATALOG_MIN_MACOS_MAJOR} ToolKit; "
        f"target macOS is {target_macos}."
    )


def entry_min_macos(identifier: str, availability: dict[str, int | None]) -> int | None:
    return availability.get(identifier)


def compact_entry(
    identifier: str,
    entry: dict[str, Any],
    availability: dict[str, int | None],
    target_macos: int | None,
    target_platform: str | None,
) -> dict[str, Any]:
    minimum = entry_min_macos(identifier, availability)
    return {
        "identifier": identifier,
        "status": entry.get("status"),
        "minimumMacOSMajor": minimum,
        "availabilityNote": target_note(minimum, target_macos),
        "deprecationNote": deprecation_note(identifier),
        "parameterMetadataMinimumMacOSMajor": (
            PARAMETER_CATALOG_MIN_MACOS_MAJOR if has_toolkit_parameter_summary(entry) else None
        ),
        "parameterMetadataAvailabilityNote": parameter_metadata_note(
            entry,
            target_macos,
            minimum,
        ),
        "triggerMetadataMinimumMacOSMajor": (
            TRIGGER_CATALOG_MIN_MACOS_MAJOR
            if isinstance(entry.get("toolkitTriggerSummary"), dict)
            else None
        ),
        "triggerMetadataAvailabilityNote": trigger_metadata_note(entry, target_macos),
        "platformAvailabilityNote": platform_availability_note(entry),
        "targetPlatformAvailabilityNote": target_platform_note(entry, target_platform),
        "name": entry.get("name"),
        "pythonName": entry.get("pythonName"),
        "toolRendererEmbedded": entry.get("toolRendererEmbedded"),
        "toolRendererScriptingUtility": entry.get("toolRendererScriptingUtility"),
        "summary": entry.get("summary"),
        "parameters": entry.get("parameters") or [],
        "toolkitPlatforms": entry.get("toolkitPlatforms") or [],
        "toolkitToolType": entry.get("toolkitToolType"),
        "toolkitParameterSummary": entry.get("toolkitParameterSummary") or {},
        "toolkitTriggerSummary": entry.get("toolkitTriggerSummary") or {},
        "workflowTriggerSample": entry.get("workflowTriggerSample") or {},
        "sourceFunctions": entry.get("sourceFunctions") or {},
        "sampleShortcuts": entry.get("sampleShortcuts") or [],
    }


def print_markdown_entry(
    identifier: str,
    entry: dict[str, Any],
    availability: dict[str, int | None],
    target_macos: int | None,
    target_platform: str | None,
) -> None:
    print(f"## {entry.get('name') or identifier}")
    print()
    print(f"- Identifier: `{identifier}`")
    if entry.get("pythonName"):
        print(f"- Apple Shortpy name: `{entry['pythonName']}`")
    print(f"- Status: `{entry.get('status')}`")
    minimum = entry_min_macos(identifier, availability)
    if minimum is not None:
        print(f"- Minimum target: macOS {minimum}+")
    note = target_note(minimum, target_macos)
    if note:
        print(f"- Availability: {note}")
    deprecated = deprecation_note(identifier)
    if deprecated:
        print(f"- Deprecation: {deprecated}")
    parameter_note = parameter_metadata_note(entry, target_macos, minimum)
    if parameter_note:
        print(f"- Parameter metadata availability: {parameter_note}")
    trigger_note = trigger_metadata_note(entry, target_macos)
    if trigger_note:
        print(f"- Trigger metadata availability: {trigger_note}")
    platform_note = platform_availability_note(entry)
    if platform_note:
        print(f"- Platform availability: {platform_note}")
    target_platform_message = target_platform_note(entry, target_platform)
    if target_platform_message:
        print(f"- Target platform availability: {target_platform_message}")
    if entry.get("toolRendererEmbedded"):
        flag = "ToolRenderer embedded"
        if entry.get("toolRendererScriptingUtility"):
            flag += ", scripting utility"
        print(f"- Apple surface: {flag}")
    if entry.get("summary"):
        print(f"- Summary: {entry['summary']}")
    samples = entry.get("sampleShortcuts") or []
    if samples:
        print(f"- Observed samples: {', '.join(samples)}")
    parameters = entry.get("parameters") or []
    if parameters:
        print()
        print("| WF key | Apple keyword | Required | Label |")
        print("|--------|---------------|----------|-------|")
        for parameter in parameters:
            print(
                "| `{}` | `{}` | {} | {} |".format(
                    parameter.get("wfKey") or "",
                    parameter.get("pythonKeyword") or "",
                    "yes" if parameter.get("required") else "no",
                    parameter.get("label") or "",
                )
            )
    toolkit_summary = entry.get("toolkitParameterSummary") or {}
    toolkit_parameters = toolkit_summary.get("parameters") if isinstance(toolkit_summary, dict) else None
    if toolkit_parameters:
        print()
        print("| ToolKit key | Name | Type | Cases |")
        print("|-------------|------|------|-------|")
        for parameter in toolkit_parameters:
            print(
                "| `{}` | {} | `{}` | {} |".format(
                    parameter.get("key") or "",
                    markdown_cell(parameter.get("name") or ""),
                    "`, `".join(toolkit_parameter_type_names(parameter)),
                    toolkit_parameter_enum_case_preview(parameter),
                )
            )
    trigger_summary = entry.get("toolkitTriggerSummary") or {}
    trigger_parameters = trigger_summary.get("parameters") if isinstance(trigger_summary, dict) else None
    if trigger_parameters:
        print()
        print("| Trigger key | Name | Type | Cases |")
        print("|-------------|------|------|-------|")
        for parameter in trigger_parameters:
            print(
                "| `{}` | {} | `{}` | {} |".format(
                    parameter.get("key") or "",
                    markdown_cell(parameter.get("name") or ""),
                    "`, `".join(toolkit_parameter_type_names(parameter)),
                    toolkit_parameter_enum_case_preview(parameter),
                )
            )
    output_types = (
        trigger_summary.get("outputTypeIdentifiers")
        if isinstance(trigger_summary, dict)
        else None
    )
    if output_types:
        print()
        print("- Trigger output types: " + ", ".join(f"`{item}`" for item in output_types))
    workflow_trigger = entry.get("workflowTriggerSample") or {}
    if isinstance(workflow_trigger, dict) and workflow_trigger:
        print()
        observed = workflow_trigger.get("observed")
        if observed is True:
            print("- Workflow trigger sample: observed exported `WFWorkflowTriggers` payload")
        elif observed is False:
            print("- Workflow trigger sample: no exported `WFWorkflowTriggers` sample yet")
        template_status = workflow_trigger.get("templateStatus")
        if template_status:
            print(f"- Template status: `{template_status}`")
        payload = workflow_trigger.get("workflowTrigger") or {}
        if isinstance(payload, dict):
            wf_identifier = payload.get("WFTriggerIdentifier")
            if wf_identifier:
                print(f"- `WFTriggerIdentifier`: `{wf_identifier}`")
            serialized = payload.get("WFTriggerSerializedParameters")
            if isinstance(serialized, dict):
                keys = ", ".join(f"`{key}`" for key in sorted(serialized))
                print(f"- Serialized parameter keys: {keys if keys else 'none'}")
        notes = workflow_trigger.get("notes") or []
        if notes:
            print("- Sample notes: " + " ".join(str(note) for note in notes))


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def toolkit_parameter_enum_case_preview(parameter: dict[str, Any], limit: int = 12) -> str:
    enum_types = parameter.get("enumTypes")
    if not isinstance(enum_types, list) or not enum_types:
        return ""
    rendered_types: list[str] = []
    include_type_name = len(enum_types) > 1
    for enum_type in enum_types:
        if not isinstance(enum_type, dict):
            continue
        cases = enum_type.get("cases") or []
        rendered_cases: list[str] = []
        for case in cases[:limit]:
            if not isinstance(case, dict):
                continue
            case_id = markdown_cell(case.get("id") or "")
            title = markdown_cell(case.get("title") or "")
            rendered_cases.append(
                f"`{case_id}`" if not title or title == case_id else f"`{case_id}` ({title})"
            )
        if len(cases) > limit:
            rendered_cases.append(f"... +{len(cases) - limit} more")
        if not rendered_cases:
            continue
        rendered = ", ".join(rendered_cases)
        if include_type_name:
            type_name = markdown_cell(enum_type.get("typePythonName") or "")
            rendered = f"`{type_name}`: {rendered}"
        rendered_types.append(rendered)
    return "<br>".join(rendered_types)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--identifier",
        help=(
            "WF action/AppIntent identifier, automation trigger identifier, "
            "or short WF action suffix, e.g. additemtolist"
        ),
    )
    group.add_argument("--python-name", help="Apple Shortpy function name, e.g. com_apple_shortcuts_add_item_to_list")
    group.add_argument("--query", help="Search names, summaries, keywords, parameters, and Python names")
    parser.add_argument("--target-macos", default=None, help="Target macOS major version, auto, latest, or all")
    parser.add_argument(
        "--target-platform",
        default=None,
        help="Target platform: macos (default), ios/ipados, or all",
    )
    parser.add_argument("--limit", type=int, default=10, help="Maximum search/list results")
    parser.add_argument("--list", action="store_true", help="List catalog entries")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    try:
        target_macos = resolve_target_macos(args.target_macos)
        target_platform = resolve_target_platform(args.target_platform)
    except ValueError as exc:
        print(str(exc))
        return 2
    catalog = load_catalog()
    parameter_catalog = load_parameter_catalog()
    enum_catalog = load_enum_catalog()
    trigger_catalog = load_trigger_catalog()
    workflow_trigger_catalog = load_workflow_trigger_catalog()
    availability = load_identifier_min_macos()

    results: list[tuple[str, dict[str, Any]]]
    if args.identifier:
        found = find_by_identifier(catalog, args.identifier)
        if found:
            found = (
                found[0],
                augment_with_parameter_summary(found[0], found[1], parameter_catalog),
            )
        else:
            found = find_parameter_by_identifier(parameter_catalog, args.identifier)
        if not found:
            found = find_trigger_by_identifier(trigger_catalog, args.identifier)
        results = [found] if found else []
    elif args.python_name:
        found = find_by_python_name(catalog, args.python_name)
        if found:
            found = (
                found[0],
                augment_with_parameter_summary(found[0], found[1], parameter_catalog),
            )
        else:
            found = find_parameter_by_python_name(parameter_catalog, args.python_name)
        if not found:
            found = find_trigger_by_python_name(trigger_catalog, args.python_name)
        results = [found] if found else []
    elif args.query:
        results = [
            (identifier, augment_with_parameter_summary(identifier, entry, parameter_catalog))
            for identifier, entry in search_entries(catalog, args.query, args.limit)
        ]
        seen = {identifier for identifier, _ in results}
        if len(results) < args.limit:
            for identifier, entry in search_parameter_entries(
                parameter_catalog,
                args.query,
                args.limit - len(results),
            ):
                if identifier not in seen:
                    results.append((identifier, entry))
                    seen.add(identifier)
        if len(results) < args.limit:
            for identifier, entry in search_trigger_entries(
                trigger_catalog,
                args.query,
                args.limit - len(results),
            ):
                if identifier not in seen:
                    results.append((identifier, entry))
                    seen.add(identifier)
    else:
        results = (
            [
                (identifier, augment_with_parameter_summary(identifier, entry, parameter_catalog))
                for identifier, entry in search_entries(catalog, "", args.limit)
            ]
            if args.list
            else []
        )
    results = [
        (identifier, filter_entry_for_target_platform(entry, target_platform))
        for identifier, entry in results
    ]
    results = [
        (identifier, augment_with_enum_cases(entry, enum_catalog))
        for identifier, entry in results
    ]
    results = [
        (
            identifier,
            augment_with_workflow_trigger_sample(
                identifier,
                entry,
                workflow_trigger_catalog,
            ),
        )
        for identifier, entry in results
    ]

    if args.json:
        result_notes = [
            target_note(entry_min_macos(identifier, availability), target_macos)
            for identifier, _ in results
        ]
        unique_notes = sorted({note for note in result_notes if note})
        deprecation_notes = [
            deprecation_note(identifier)
            for identifier, _ in results
        ]
        unique_deprecation_notes = sorted({note for note in deprecation_notes if note})
        platform_notes = [
            platform_availability_note(entry)
            for _, entry in results
        ]
        unique_platform_notes = sorted({note for note in platform_notes if note})
        target_platform_notes = [
            target_platform_note(entry, target_platform)
            for _, entry in results
        ]
        unique_target_platform_notes = sorted({note for note in target_platform_notes if note})
        parameter_notes = [
            parameter_metadata_note(entry, target_macos, entry_min_macos(identifier, availability))
            for identifier, entry in results
        ]
        unique_parameter_notes = sorted({note for note in parameter_notes if note})
        trigger_notes = [
            trigger_metadata_note(entry, target_macos)
            for _, entry in results
        ]
        unique_trigger_notes = sorted({note for note in trigger_notes if note})
        payload = {
            "catalog": {
                "schemaVersion": catalog.get("schemaVersion"),
                "minimumMacOSMajor": catalog.get("minimumMacOSMajor"),
                "summary": catalog.get("summary"),
                "runtimePolicy": catalog.get("runtimePolicy"),
            },
            "enumCatalog": {
                "version": enum_catalog.get("version"),
                "enumTypeCount": enum_catalog.get("enumTypeCount"),
                "caseCount": enum_catalog.get("caseCount"),
            },
            "workflowTriggerCatalog": {
                "version": workflow_trigger_catalog.get("version"),
                "rootKey": workflow_trigger_catalog.get("rootKey"),
                "observedToolkitTriggerCount": workflow_trigger_catalog.get(
                    "observedToolkitTriggerCount"
                ),
                "unobservedToolkitTriggerCount": workflow_trigger_catalog.get(
                    "unobservedToolkitTriggerCount"
                ),
                "minimumMacOSMajor": WORKFLOW_TRIGGER_CATALOG_MIN_MACOS_MAJOR,
            },
            "targetMacOSMajor": target_macos,
            "targetPlatform": target_platform_label(target_platform),
            "availabilityNote": unique_notes[0] if len(unique_notes) == 1 else None,
            "deprecationNote": (
                unique_deprecation_notes[0]
                if len(unique_deprecation_notes) == 1
                else None
            ),
            "parameterMetadataAvailabilityNote": (
                unique_parameter_notes[0] if len(unique_parameter_notes) == 1 else None
            ),
            "triggerMetadataAvailabilityNote": (
                unique_trigger_notes[0] if len(unique_trigger_notes) == 1 else None
            ),
            "platformAvailabilityNote": (
                unique_platform_notes[0] if len(unique_platform_notes) == 1 else None
            ),
            "targetPlatformAvailabilityNote": (
                unique_target_platform_notes[0]
                if len(unique_target_platform_notes) == 1
                else None
            ),
            "results": [
                compact_entry(identifier, entry, availability, target_macos, target_platform)
                for identifier, entry in results
            ],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if results else 1

    if not results:
        print("No Apple-derived grounding entry found.")
        return 1
    for index, (identifier, entry) in enumerate(results):
        if index:
            print()
        print_markdown_entry(identifier, entry, availability, target_macos, target_platform)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
