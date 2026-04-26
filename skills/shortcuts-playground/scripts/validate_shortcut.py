#!/usr/bin/env python3
"""Validate Shortcuts XML/.shortcut outputs for common structural errors.

Usage:
  python3 scripts/validate_shortcut.py /path/to/Shortcut.xml
  python3 scripts/validate_shortcut.py /path/to/Shortcut.shortcut

Exit code:
  0 = pass
  1 = fail
"""

import argparse
import json
import os
import plistlib
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

ALLOWED_EMPTY_KEYS = {
    # User-configurable or device-specific fields that may be empty at build time
    "WFHomeAccessory",
    "WFHomeAction",
    "WFHomeScene",
    "WFHomeService",
    "WFHomeRoom",
    "WFHomeZone",
    "WFHome",
    "WFContact",
    "WFContacts",
    "WFPerson",
    "WFPeople",
    "WFRecipient",
    "WFRecipients",
}

# Keys where whitespace is meaningful and should not be treated as empty.
WHITESPACE_SIGNIFICANT_KEYS = {
    "WFTextCustomSeparator",
    "WFReplaceTextFind",
}

# Keys where an empty string can be intentional and valid.
ALLOW_EMPTY_STRING_KEYS = {
    "WFReplaceTextReplace",
}

# Matches a UUID where every hex character is the same — e.g.
# 11111111-1111-1111-1111-111111111111 or AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA.
# These are placeholder sequences that agents used to produce instead of real
# random UUIDs. They're formally valid (36 chars, right shape, uppercase) but
# break cross-shortcut uniqueness and are a tell that the generator cheated.
# The agent prompt now requires uuidgen; this regex is the backstop.
#
# Segment lengths: 8-4-4-4-12 hex characters. Backreference counts after the
# initial capture: 7 + 4 + 4 + 4 + 12 = 31 more chars matching the captured
# hex char, 32 total, plus 4 dashes = 36-char UUID.
REPEATING_UUID_RE = re.compile(
    r"\b([0-9A-F])\1{7}-\1{4}-\1{4}-\1{4}-\1{12}\b"
)

# Verified against an Apple-built sample shortcut covering all condition codes.
# All conditional codes use explicit WFInput as a Type=Variable wrapper. There
# is no "implicit input" mode; the previously documented numeric-implicit pattern
# was incorrect.

STRING_CONDITIONS = {
    "Equals",
    "Does Not Equal",
    "Contains",
    "Does Not Contain",
    "Begins With",
    "Ends With",
}

# Codes whose WFCondition value requires a non-empty WFConditionalActionString
# literal alongside the WFInput variable reference.
STRING_CONDITION_CODES = {
    4,    # is (string equals)
    5,    # is not (string inequality)
    8,    # begins with
    9,    # ends with
    99,   # contains
    999,  # does not contain
}

NUMBER_CONDITIONS = {
    "Is",
    "Is Not",
    "Is Greater Than",
    "Is Greater Than Or Equal To",
    "Is Less Than",
    "Is Less Than Or Equal To",
    "Is Between",
}

# Codes whose WFCondition value requires WFNumberValue. Code 1003 also requires
# WFAnotherNumber for the upper bound of a "between" check.
NUMBER_CONDITION_CODES = {
    0,     # is less than
    1,     # is less than or equal to
    2,     # is greater than
    3,     # is greater than or equal to
    1003,  # is between (also requires WFAnotherNumber)
}

# Codes that test for variable existence and need NEITHER WFConditionalActionString
# nor WFNumberValue. They still require WFInput.
EXISTENCE_CONDITION_CODES = {
    100,  # has any value
    101,  # does not have any value
}

# All codes the validator recognizes. Anything outside this set is rejected.
ALL_CONDITION_CODES = STRING_CONDITION_CODES | NUMBER_CONDITION_CODES | EXISTENCE_CONDITION_CODES

REQUIRED_INPUT_ACTIONS = {
    # Actions that should always have explicit input wired
    "is.workflow.actions.openurl",
    "is.workflow.actions.detect.link",
    "is.workflow.actions.choosefromlist",
    "is.workflow.actions.base64encode",
    "is.workflow.actions.text.replace",
    "is.workflow.actions.setclipboard",
    "is.workflow.actions.count",
    "is.workflow.actions.math",
    "is.workflow.actions.round",
    "is.workflow.actions.detect.dictionary",
    "is.workflow.actions.image.convert",
    "is.workflow.actions.properties.weather.conditions",
    "is.workflow.actions.gettimebetweendates",
}

EDITOR_VISIBLE_INPUT_ACTIONS = {
    # Inputs that commonly render blank unless represented as a tokenized string
    "is.workflow.actions.detect.link",
    "is.workflow.actions.text.replace",
}

TEXT_INPUT_KEY_ACTIONS = {
    # Actions whose primary input parameter key is "text", not WFInput
    "is.workflow.actions.text.changecase",
    "is.workflow.actions.text.split",
}

VCARD_MARKER = "ALLOW_VCARD"
TOKEN_FILE_MARKER = "ALLOW_TOKEN_FILE"
ALLOW_DATETIME_FORMAT_MARKER = "ALLOW_DATETIME_FORMAT"
ALLOW_MANUAL_UNIT_CONVERSION_MARKER = "ALLOW_MANUAL_UNIT_CONVERSION"
TODOIST_TASKS_PREFIX = "https://api.todoist.com/rest/v2/tasks/"
COMMENT_INTERNAL_WF_KEY_RE = re.compile(r"\bWF[A-Z][A-Za-z0-9]*\b")
COMMENT_ALLOWED_MARKERS = {
    VCARD_MARKER,
    TOKEN_FILE_MARKER,
    ALLOW_DATETIME_FORMAT_MARKER,
    ALLOW_MANUAL_UNIT_CONVERSION_MARKER,
}
COMMENT_WF_FRIENDLY_LABELS = {
    "WFInput": "Input",
    "WFDate": "Date",
    "WFImage": "Image",
    "WFURL": "URL",
    "WFDuration": "Duration",
    "WFAskActionPrompt": "Prompt",
    "WFVariableName": "Variable Name",
    "WFCondition": "Condition",
    "WFContentItemPropertyName": "Detail",
    "WFRequestVariable": "Request Body",
    "WFJSONValues": "JSON",
    "WFTextActionText": "Text",
    "WFCommentActionText": "Comment",
}

FILE_ACTION_PREFIXES = (
    "is.workflow.actions.file.",
)

FILE_ACTION_IDS = {
    "is.workflow.actions.getfile",
    "is.workflow.actions.documentpicker.open",
    "is.workflow.actions.documentpicker.save",
}

TOKEN_HINT_RE = re.compile(
    r"\b(api[\s_-]?(?:key|token)|bearer[\s_-]?token|access[\s_-]?token|secret[\s_-]?(?:key|token)|auth[\s_-]?token)\b",
    re.IGNORECASE,
)
LANG_CODE_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]+)?$")
IDENTIFIER_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
THIRD_PARTY_IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(\.[A-Za-z0-9_-]+){2,}$")
UNSAFE_ERROR_DOT_PATH_RE = re.compile(r"^error\.", re.IGNORECASE)

DATE_DELTA_UNITS = {
    "seconds",
    "minutes",
    "hours",
    "days",
    "weeks",
    "months",
    "years",
    "second",
    "minute",
    "hour",
    "day",
    "week",
    "month",
    "year",
    # Common Shortcuts aliases seen in exported payloads.
    "sec",
    "secs",
    "min",
    "mins",
    "hr",
    "hrs",
    "wk",
    "wks",
    "mo",
    "mos",
    "yr",
    "yrs",
}

CONTROL_FLOW_TOOLKIT_EXCEPTIONS = {
    "is.workflow.actions.conditional",
    "is.workflow.actions.repeat.count",
    "is.workflow.actions.repeat.each",
    "is.workflow.actions.choosefrommenu",
}

KNOWN_AGGRANDIZEMENT_TYPES = {
    "WFCoercionVariableAggrandizement",
    "WFPropertyVariableAggrandizement",
    "WFDictionaryValueVariableAggrandizement",
    "WFDateFormatVariableAggrandizement",
    "WFUnitVariableAggrandizement",
}

NOTES_CREATE_ACTIONS = {
    "com.apple.mobilenotes.SharingExtension",
    "com.apple.mobilenotes.CreateNoteLinkAction",
    "com.apple.Notes.CreateNoteFromMarkdownLinkAction",
    "com.apple.Notes.CreateNoteLinkAction",
}

NOTES_TITLE_KEYS = {
    "wfnotetitle",
    "title",
    "name",
}

NOTES_CONTENT_KEYS = {
    "wfnotecontentitem",
    "wfcreatenoteinput",
    "markdown",
    "content",
    "text",
}

REQUIRED_URL_ACTIONS = {
    "is.workflow.actions.url",
}

REQUIRED_URL_INPUT_ACTIONS = {
    "is.workflow.actions.downloadurl",
}

WEATHER_SOURCE_ACTIONS = {
    "is.workflow.actions.weather.currentconditions",
    "is.workflow.actions.weather.forecast",
}

LOCATION_SOURCE_ACTIONS = {
    "is.workflow.actions.getcurrentlocation",
    "is.workflow.actions.location",
}

WEATHER_DETAIL_PLACEHOLDER_VALUES = {
    "detail",
}

LOCATION_PARAMETER_KEYS = {
    "WFLocation",
    "WFWeatherCustomLocation",
    # Legacy export key still seen in some installed shortcuts.
    "WFWeatherLocation",
}

UNUSED_OUTPUT_ACTIONS = {
    "is.workflow.actions.gettext",
    "is.workflow.actions.number",
    "is.workflow.actions.url",
    "is.workflow.actions.getvalueforkey",
    "is.workflow.actions.format.date",
    "is.workflow.actions.ask",
    "is.workflow.actions.count",
    "is.workflow.actions.math",
}

HEALTH_FIND_SAMPLES_ACTION = "is.workflow.actions.filter.health.quantity"
HEALTH_LOG_SAMPLE_ACTION = "is.workflow.actions.health.quantity.log"
HEALTH_LOG_WORKOUT_ACTION = "is.workflow.actions.health.workout.log"
HEALTH_SAMPLE_DETAIL_ACTION = "is.workflow.actions.properties.health.quantity"

HEALTH_IOS_ONLY_ACTIONS = {
    HEALTH_FIND_SAMPLES_ACTION,
    HEALTH_LOG_SAMPLE_ACTION,
    HEALTH_LOG_WORKOUT_ACTION,
    HEALTH_SAMPLE_DETAIL_ACTION,
}

HEALTH_SAMPLE_SOURCE_ACTIONS = {
    HEALTH_FIND_SAMPLES_ACTION,
    HEALTH_LOG_SAMPLE_ACTION,
}

HEALTH_SAMPLE_DETAIL_PROPERTIES = {
    "Type",
    "Value",
    "Unit",
    "Start Date",
    "End Date",
    "Duration",
    "Source",
    "Name",
}

HEALTH_QUANTITY_FIELD_KEYS = {
    "WFQuantitySampleQuantity",
    "WFQuantitySampleAdditionalQuantity",
    "WFWorkoutDuration",
    "WFWorkoutCaloriesQuantity",
    "WFWorkoutDistanceQuantity",
}

HEALTH_REQUIRED_MAIN_QUANTITY_KEYS = {
    "WFQuantitySampleQuantity",
    "WFWorkoutDuration",
    "WFWorkoutCaloriesQuantity",
    "WFWorkoutDistanceQuantity",
}


def _load_healthkit_reference_sets() -> dict[str, set[str]]:
    out = {
        "quantity_types": set(),
        "sample_types": set(),
        "category_values": set(),
        "workouts": set(),
        "units": set(),
    }
    ref_path = Path(__file__).resolve().parents[1] / "data/healthkit-ios26.2-reference.json"
    if not ref_path.exists():
        return out
    try:
        payload = json.loads(ref_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return out

    def labels_from_rows(rows) -> set[str]:
        labels: set[str] = set()
        if not isinstance(rows, list):
            return labels
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in ("shortcut_label_guess", "sdk_suffix"):
                value = row.get(key)
                if isinstance(value, str) and value:
                    labels.add(value)
            observed = row.get("observed_shortcuts_labels")
            if isinstance(observed, list):
                labels.update(item for item in observed if isinstance(item, str) and item)
        return labels

    quantity_labels = labels_from_rows(payload.get("quantity_types"))
    category_labels = labels_from_rows(payload.get("category_types"))
    out["quantity_types"].update(quantity_labels)
    out["sample_types"].update(quantity_labels | category_labels)
    out["workouts"].update(labels_from_rows(payload.get("workout_activity_types")))

    category_values = payload.get("category_values")
    if isinstance(category_values, dict):
        for rows in category_values.values():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for key in ("shortcut_label_guess", "symbol"):
                    value = row.get(key)
                    if isinstance(value, str) and value:
                        out["category_values"].add(value)

    for row in payload.get("quantity_units", []):
        if isinstance(row, dict):
            unit = row.get("unit")
            if isinstance(unit, str) and unit:
                out["units"].add(unit)
    for unit in payload.get("quantity_unit_hints", []):
        if isinstance(unit, str) and unit:
            out["units"].add(unit)

    return out


HEALTH_REFERENCE_SETS = _load_healthkit_reference_sets()

BUILTIN_VARIABLES = {
    "Repeat Item",
    "Repeat Item 2",
    "Repeat Item 3",
    "Repeat Item 4",
    "Repeat Results",
    "Repeat Results 2",
    "Repeat Results 3",
    "Repeat Index",
    "Repeat Index 2",
    "Repeat Index 3",
    "Shortcut Input",
    "Clipboard",
    "Current Date",
    "Current Location",
}

ACTION_ALIAS_HINTS: dict[str, str] = {
    "is.workflow.actions.text": "is.workflow.actions.gettext",
    "is.workflow.actions.translate": "is.workflow.actions.text.translate",
    "is.workflow.actions.getshortcutinput": "is.workflow.actions.input",
    "is.workflow.actions.sendmail": "is.workflow.actions.sendemail",
    "is.workflow.actions.runscript": "is.workflow.actions.runshellscript (or runapplescript / runjavascriptforautomation)",
    "is.workflow.actions.properties.podcastepisode": "is.workflow.actions.properties.podcast or is.workflow.actions.properties.podcastshow",
}

UNIT_KEYWORD_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bmiles?\b", re.I),
    re.compile(r"\bkilometers?\b", re.I),
    re.compile(r"\bkilometres?\b", re.I),
    re.compile(r"\bkm\b", re.I),
    re.compile(r"\bmeters?\b", re.I),
    re.compile(r"\bmetres?\b", re.I),
    re.compile(r"\bcm\b", re.I),
    re.compile(r"\bmm\b", re.I),
    re.compile(r"\bfeet\b", re.I),
    re.compile(r"\bfoot\b", re.I),
    re.compile(r"\bft\b", re.I),
    re.compile(r"\byards?\b", re.I),
    re.compile(r"\binches?\b", re.I),
    re.compile(r"\bpounds?\b", re.I),
    re.compile(r"\blbs?\b", re.I),
    re.compile(r"\blb\b", re.I),
    re.compile(r"\bkilograms?\b", re.I),
    re.compile(r"\bkg\b", re.I),
    re.compile(r"\boz\b", re.I),
    re.compile(r"\bounces?\b", re.I),
    re.compile(r"\bgallons?\b", re.I),
    re.compile(r"\bliters?\b", re.I),
    re.compile(r"\blitres?\b", re.I),
    re.compile(r"\bmilliliters?\b", re.I),
    re.compile(r"\bmillilitres?\b", re.I),
    re.compile(r"\bml\b", re.I),
    re.compile(r"°f", re.I),
    re.compile(r"°c", re.I),
    re.compile(r"\bfahrenheit\b", re.I),
    re.compile(r"\bcelsius\b", re.I),
]

UNIT_KEYWORD_IGNORED_KEYS = {
    "WFDateFormat",
    "WFDateFormatString",
    "WFTimeFormatStyle",
    "WFRelativeDateFormatStyle",
    "WFMatchTextPattern",
    # Key used inside WFDateFormatVariableAggrandizement payloads — matches
    # the literal plist key, not the WF-prefixed parameter. Date format strings
    # like "yyyy-MM-dd" contain "MM" which otherwise trips \bmm\b.
    "DateFormat",
    # Unit values inside WFQuantityFieldValue are structured metadata, not
    # evidence of a manual unit conversion.
    "Unit",
}


def _coerce_control_flow_mode(params: dict) -> int | None:
    """Extract WFControlFlowMode as int, coercing string digits."""
    mode = params.get("WFControlFlowMode")
    if isinstance(mode, str) and mode.isdigit():
        return int(mode)
    return mode


def _collect_variable_append_counts(actions: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for act in actions:
        if act.get("WFWorkflowActionIdentifier") != "is.workflow.actions.appendvariable":
            continue
        params = act.get("WFWorkflowActionParameters") or {}
        name = params.get("WFVariableName")
        if isinstance(name, str) and name.strip():
            counts[name] = counts.get(name, 0) + 1
    return counts


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_actions_md(text: str) -> set[str]:
    """Parse ACTIONS.md and return the set of valid action identifiers.

    Only rows inside tables whose first column header is "Identifier" are
    treated as action rows. Parameter/property tables (first column
    "Parameter", "Property", "Class Name", etc.) are skipped so their
    backticked cells do not pollute the allowlist — a prior version wrongly
    injected entries like `is.workflow.actions.UUID` / `is.workflow.actions.Album`.
    """

    actions: set[str] = set()
    in_identifier_table = False

    def add_action_id(token: str):
        if not IDENTIFIER_TOKEN_RE.match(token):
            return
        if token.startswith("is.workflow.actions."):
            actions.add(token)
            return
        if token.startswith(("WF", "com.apple.", "io.")):
            return
        actions.add(f"is.workflow.actions.{token}")

    header_re = re.compile(r"^\|\s*([^|`]+?)\s*\|")
    separator_re = re.compile(r"^\|\s*[-:]+")
    row_re = re.compile(r"\|\s*`([^`]+)`\s*\|")

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_identifier_table = False
            continue
        if separator_re.match(line):
            continue
        if stripped.startswith("|"):
            # Heuristic: if the first column is plain text (no backticks) it's
            # a header row. Switch mode based on whether header == "Identifier".
            header_m = header_re.match(line)
            backtick_m = row_re.match(line)
            if header_m and not backtick_m:
                col = header_m.group(1).strip().lower()
                in_identifier_table = col == "identifier"
                continue
            if in_identifier_table and backtick_m:
                add_action_id(backtick_m.group(1).strip())
    return actions


def parse_appintents_md(text: str) -> set[str]:
    intents: set[str] = set()

    def add_intent_id(token: str):
        if "." not in token:
            return
        if not IDENTIFIER_TOKEN_RE.match(token):
            return
        if token.startswith(("com.apple.", "is.workflow.actions.")):
            intents.add(token)

    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|", line)
        if m:
            add_intent_id(m.group(1).strip())
    return intents


def parse_third_party_md(text: str) -> set[str]:
    ids: set[str] = set()
    for match in re.finditer(r"`([^`]+)`", text):
        ident = match.group(1).strip()
        if "." in ident and IDENTIFIER_TOKEN_RE.match(ident):
            ids.add(ident)
    return ids


def load_packaged_toolkit_ids(skill_dir: Path) -> set[str]:
    data_dir = skill_dir / "data"
    candidates = [
        data_dir / "toolkit-v63-tool-ids.json",
    ]
    allowed: set[str] = set()
    for path in candidates:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        ids = payload.get("ids") if isinstance(payload, dict) else None
        if isinstance(ids, list):
            for item in ids:
                if isinstance(item, str) and item:
                    allowed.add(item)
        exceptions = (
            payload.get("control_flow_exceptions_missing_from_tools_table")
            if isinstance(payload, dict)
            else None
        )
        if isinstance(exceptions, list):
            for item in exceptions:
                if isinstance(item, str) and item:
                    allowed.add(item)
    allowed |= CONTROL_FLOW_TOOLKIT_EXCEPTIONS
    allowed |= HEALTH_IOS_ONLY_ACTIONS
    return allowed


def load_allowed_ids(skill_dir: Path) -> set[str]:
    allowed = set()
    allowed |= load_packaged_toolkit_ids(skill_dir)

    # Keep markdown references as additive fallback, especially for backup-only third-party IDs.
    actions_md = skill_dir / "ACTIONS.md"
    appintents_md = skill_dir / "APPINTENTS.md"
    third_party_md = skill_dir / "THIRD_PARTY_ACTIONS.md"

    if actions_md.exists():
        allowed |= parse_actions_md(read_text(actions_md))
    if appintents_md.exists():
        allowed |= parse_appintents_md(read_text(appintents_md))
    if third_party_md.exists():
        allowed |= parse_third_party_md(read_text(third_party_md))

    allowed |= CONTROL_FLOW_TOOLKIT_EXCEPTIONS
    allowed |= HEALTH_IOS_ONLY_ACTIONS
    return allowed


def load_icon_metadata(skill_dir: Path) -> tuple[set[int], set[int]]:
    glyph_ids: set[int] = set()
    color_values: set[int] = set()

    glyph_path = skill_dir / "data/shortcuts-official-glyph-mapping.json"
    color_path = skill_dir / "data/shortcuts-icon-colors.json"

    try:
        if glyph_path.exists():
            with glyph_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, dict):
                for key in payload.keys():
                    try:
                        glyph_ids.add(int(key))
                    except (TypeError, ValueError):
                        continue
    except json.JSONDecodeError:
        pass

    try:
        if color_path.exists():
            with color_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, list):
                for row in payload:
                    if not isinstance(row, dict):
                        continue
                    value = row.get("value")
                    if isinstance(value, (int, float)):
                        color_values.add(int(value))
                    for alias in row.get("aliases", []):
                        if isinstance(alias, (int, float)):
                            color_values.add(int(alias))
    except json.JSONDecodeError:
        pass

    return glyph_ids, color_values


def load_plist(path: Path):
    with path.open("rb") as f:
        return plistlib.load(f)


def iter_empty_strings(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = path + (k,)
            if isinstance(v, str):
                # Some text fields legitimately preserve whitespace and should only
                # fail when truly empty.
                if k in WHITESPACE_SIGNIFICANT_KEYS:
                    if v == "":
                        yield new_path
                elif k in ALLOW_EMPTY_STRING_KEYS:
                    continue
                elif v.strip() == "" and k not in ALLOWED_EMPTY_KEYS:
                    yield new_path
            else:
                yield from iter_empty_strings(v, new_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_empty_strings(v, path + (f"[{i}]",))


def iter_strings(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = path + (k,)
            if isinstance(v, str):
                yield new_path, v
            else:
                yield from iter_strings(v, new_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_strings(v, path + (f"[{i}]",))


def iter_text_token_strings(obj):
    if isinstance(obj, dict):
        if obj.get("WFSerializationType") == "WFTextTokenString":
            yield obj
        for v in obj.values():
            yield from iter_text_token_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_text_token_strings(v)


def _utf16_units(s: str) -> list[int]:
    data = s.encode("utf-16-le")
    return [data[i] + (data[i + 1] << 8) for i in range(0, len(data), 2)]


def iter_action_output_refs(obj):
    if isinstance(obj, dict):
        if obj.get("Type") == "ActionOutput":
            uuid = obj.get("OutputUUID")
            if uuid:
                yield uuid
        for v in obj.values():
            yield from iter_action_output_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_action_output_refs(v)


def iter_action_output_refs_with_name(obj):
    if isinstance(obj, dict):
        if obj.get("Type") == "ActionOutput":
            uuid = obj.get("OutputUUID")
            name = obj.get("OutputName")
            if uuid or name:
                yield uuid, name
        for v in obj.values():
            yield from iter_action_output_refs_with_name(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_action_output_refs_with_name(v)


def iter_variable_names(obj):
    if isinstance(obj, dict):
        if obj.get("Type") == "Variable":
            name = obj.get("VariableName")
            if isinstance(name, str):
                yield name
        for v in obj.values():
            yield from iter_variable_names(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_variable_names(v)


def _comment_has_bullets(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("-", "•", "–")):
            return True
    return False


def _friendly_comment_field_name(token: str) -> str:
    friendly = COMMENT_WF_FRIENDLY_LABELS.get(token)
    if friendly:
        return friendly
    if token.startswith("WF") and len(token) > 2:
        return token[2:]
    return token


def _comment_internal_wf_terms(text: str) -> list[str]:
    found: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Skip quoted user prompt lines in the required prompt Comment block.
        if line.startswith(">"):
            continue
        upper = line.upper()
        if any(marker in upper for marker in COMMENT_ALLOWED_MARKERS):
            continue
        for token in COMMENT_INTERNAL_WF_KEY_RE.findall(line):
            found.add(token)
    return sorted(found)


def _text_has_unit_keywords(text: str) -> bool:
    for pat in UNIT_KEYWORD_PATTERNS:
        if pat.search(text):
            return True
    return False


def iter_extension_input_refs(obj):
    if isinstance(obj, dict):
        if obj.get("Type") == "ExtensionInput":
            yield True
        for v in obj.values():
            yield from iter_extension_input_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_extension_input_refs(v)


def _snippet(params: dict) -> str:
    simple = {}
    for k, v in params.items():
        if isinstance(v, (str, int, float, bool)) and v != "":
            simple[k] = v
    if not simple:
        simple = {"keys": sorted(params.keys())}
    s = repr(simple)
    if len(s) > 240:
        s = s[:237] + "..."
    return s


def _input_is_attached(value) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("Type") == "Variable" and isinstance(value.get("Variable"), dict):
        return _input_is_attached(value.get("Variable"))
    if value.get("WFSerializationType") in {"WFTextTokenAttachment", "WFTextTokenString"}:
        return True
    return False


def _conditional_input_is_wrapped(value) -> bool:
    return isinstance(value, dict) and value.get("Type") == "Variable" and isinstance(value.get("Variable"), dict)


def _wrapped_variable_contains_action_output(value) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("Type") != "Variable":
        return False
    inner = value.get("Variable")
    if not isinstance(inner, dict):
        return False
    ser = inner.get("WFSerializationType")
    val = inner.get("Value")
    if ser == "WFTextTokenAttachment":
        return isinstance(val, dict) and val.get("Type") == "ActionOutput"
    if ser == "WFTextTokenString" and isinstance(val, dict):
        attachments = val.get("attachmentsByRange")
        if isinstance(attachments, dict):
            for att in attachments.values():
                if isinstance(att, dict) and att.get("Type") == "ActionOutput":
                    return True
    return False


def _input_is_token_string(value) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("WFSerializationType") != "WFTextTokenString":
        return False
    inner = value.get("Value")
    if not isinstance(inner, dict):
        return False
    attachments = inner.get("attachmentsByRange")
    return isinstance(attachments, dict) and bool(attachments)


def _input_is_editor_visible(value) -> bool:
    return _conditional_input_is_wrapped(value) or _input_is_token_string(value)


def _token_param_is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (int, float, bool)):
        return False
    if not isinstance(value, dict):
        return False
    ser = value.get("WFSerializationType")
    if ser == "WFTextTokenString":
        inner = value.get("Value")
        if not isinstance(inner, dict):
            return True
        string = inner.get("string")
        attachments = inner.get("attachmentsByRange")
        if isinstance(attachments, dict) and attachments:
            return False
        return not isinstance(string, str) or string.strip() == ""
    if ser == "WFTextTokenAttachment":
        inner = value.get("Value")
        if not isinstance(inner, dict):
            return True
        token_type = inner.get("Type")
        if isinstance(token_type, str) and token_type.strip():
            return False
        return True
    return False


def _validate_health_quantity_field(
    value,
    *,
    key: str,
    idx: int,
    errors: list[str],
    require_magnitude: bool = True,
) -> None:
    if not isinstance(value, dict):
        errors.append(f"Health quantity field {key} must be a dict at index {idx}")
        return
    if value.get("WFSerializationType") != "WFQuantityFieldValue":
        errors.append(
            f"Health quantity field {key} must use WFQuantityFieldValue serialization at index {idx}"
        )
        return
    inner = value.get("Value")
    if not isinstance(inner, dict):
        errors.append(f"Health quantity field {key} missing Value dict at index {idx}")
        return

    magnitude = inner.get("Magnitude")
    unit = inner.get("Unit")
    if require_magnitude and _token_param_is_empty(magnitude):
        errors.append(f"Health quantity field {key} missing Magnitude at index {idx}")
    if not isinstance(unit, str) or unit.strip() == "":
        errors.append(f"Health quantity field {key} missing Unit at index {idx}")
    elif HEALTH_REFERENCE_SETS["units"] and unit not in HEALTH_REFERENCE_SETS["units"]:
        errors.append(f"Health quantity field {key} uses unknown Unit '{unit}' at index {idx}")


def _validate_health_date_like(value, *, key: str, idx: int, errors: list[str]) -> None:
    if _token_param_is_empty(value):
        errors.append(f"Health date field {key} is empty at index {idx}")


def _validate_health_filter_template(
    filter_value,
    *,
    action_label: str,
    idx: int,
    errors: list[str],
) -> None:
    if not isinstance(filter_value, dict):
        errors.append(f"{action_label} missing WFContentItemFilter at index {idx}")
        return
    if filter_value.get("WFSerializationType") != "WFContentPredicateTableTemplate":
        errors.append(
            f"{action_label} WFContentItemFilter must use WFContentPredicateTableTemplate at index {idx}"
        )
        return
    inner = filter_value.get("Value")
    if not isinstance(inner, dict):
        errors.append(f"{action_label} WFContentItemFilter missing Value dict at index {idx}")
        return
    prefix = inner.get("WFActionParameterFilterPrefix")
    if prefix not in (0, 1):
        errors.append(
            f"{action_label} WFContentItemFilter prefix must be 0 (Any) or 1 (All) at index {idx}"
        )
    templates = inner.get("WFActionParameterFilterTemplates")
    if not isinstance(templates, list) or not templates:
        errors.append(f"{action_label} WFContentItemFilter has no templates at index {idx}")
        return
    for tidx, template in enumerate(templates):
        if not isinstance(template, dict):
            errors.append(f"{action_label} filter template {tidx} is not a dict at index {idx}")
            continue
        if _token_param_is_empty(template.get("Property")):
            errors.append(f"{action_label} filter template {tidx} missing Property at index {idx}")
        if "Operator" not in template:
            errors.append(f"{action_label} filter template {tidx} missing Operator at index {idx}")
        if "Values" in template and not isinstance(template.get("Values"), dict):
            errors.append(f"{action_label} filter template {tidx} Values must be a dict at index {idx}")


def _lang_value_is_code(value) -> bool:
    if isinstance(value, str):
        return bool(LANG_CODE_RE.match(value)) and " " not in value
    if isinstance(value, dict) and value.get("WFSerializationType") == "WFTextTokenString":
        inner = value.get("Value")
        if isinstance(inner, dict):
            s = inner.get("string")
            if isinstance(s, str) and "￼" not in s:
                return bool(LANG_CODE_RE.match(s)) and " " not in s
    return False


def _extract_input_variable_name(value) -> Optional[str]:
    if not isinstance(value, dict):
        return None
    if value.get("Type") == "Variable" and isinstance(value.get("Variable"), dict):
        value = value.get("Variable")
    if not isinstance(value, dict):
        return None
    # WFTextTokenAttachment with direct variable
    val = value.get("Value")
    if isinstance(val, dict) and val.get("Type") == "Variable":
        name = val.get("VariableName")
        if isinstance(name, str) and name.strip():
            return name
    # WFTextTokenString with variable attachment
    if value.get("WFSerializationType") == "WFTextTokenString":
        val = value.get("Value")
        if isinstance(val, dict):
            attachments = val.get("attachmentsByRange")
            if isinstance(attachments, dict):
                for att in attachments.values():
                    if isinstance(att, dict) and att.get("Type") == "Variable":
                        name = att.get("VariableName")
                        if isinstance(name, str) and name.strip():
                            return name
    return None


def _input_action_output_uuids(value) -> list[str]:
    if not isinstance(value, dict):
        return []
    if value.get("Type") == "Variable" and isinstance(value.get("Variable"), dict):
        value = value.get("Variable")
    ser = value.get("WFSerializationType")
    if ser == "WFTextTokenAttachment":
        val = value.get("Value")
        if isinstance(val, dict) and val.get("Type") == "ActionOutput":
            uuid = val.get("OutputUUID")
            return [uuid] if uuid else []
    if ser == "WFTextTokenString":
        val = value.get("Value") if isinstance(value.get("Value"), dict) else {}
        attachments = val.get("attachmentsByRange")
        if isinstance(attachments, dict):
            out = []
            for att in attachments.values():
                if isinstance(att, dict) and att.get("Type") == "ActionOutput":
                    uuid = att.get("OutputUUID")
                    if uuid:
                        out.append(uuid)
            return out
    return []


def _input_has_reference(value) -> bool:
    if _extract_input_variable_name(value) or _input_action_output_uuids(value):
        return True
    if not isinstance(value, dict):
        return False
    if value.get("Type") == "Variable" and isinstance(value.get("Variable"), dict):
        value = value.get("Variable")
    if not isinstance(value, dict):
        return False
    if value.get("WFSerializationType") == "WFTextTokenAttachment":
        val = value.get("Value")
        return isinstance(val, dict) and val.get("Type") == "ExtensionInput"
    if value.get("WFSerializationType") == "WFTextTokenString":
        val = value.get("Value")
        if isinstance(val, dict):
            attachments = val.get("attachmentsByRange")
            if isinstance(attachments, dict):
                for att in attachments.values():
                    if isinstance(att, dict) and att.get("Type") == "ExtensionInput":
                        return True
    return False


def _math_operand_has_reference(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str) and value.strip() != "":
        return True
    if isinstance(value, dict):
        if value.get("WFSerializationType") in {"WFTextTokenAttachment", "WFTextTokenString"}:
            val = value.get("Value")
            if isinstance(val, dict):
                if val.get("Type") == "Variable" and val.get("VariableName"):
                    return True
                if val.get("Type") == "ActionOutput" and val.get("OutputUUID"):
                    return True
                if isinstance(val.get("string"), str) and val.get("string").strip() != "":
                    return True
    return False


def iter_aggrandizements(obj):
    """Yield all Aggrandizement dicts found recursively in a parameter tree."""
    if isinstance(obj, dict):
        aggs = obj.get("Aggrandizements")
        if isinstance(aggs, list):
            for item in aggs:
                if isinstance(item, dict):
                    yield item
        for v in obj.values():
            yield from iter_aggrandizements(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_aggrandizements(v)


def validate(
    plist,
    allowed_ids: set[str],
    allowed_glyph_ids: Optional[set[int]] = None,
    allowed_icon_colors: Optional[set[int]] = None,
) -> Tuple[list[str], Optional[Tuple[int, str, str]]]:
    errors: list[str] = []
    first_error: Optional[Tuple[int, str, str]] = None
    actions = plist.get("WFWorkflowActions", [])
    comments: list[str] = []
    uuid_to_ident: dict[str, str] = {}
    uuid_to_params: dict[str, dict] = {}
    append_counts = _collect_variable_append_counts(actions)
    used_output_uuids: set[str] = set()
    repeat_stack: list[dict] = []
    repeat_end_uuids: dict[str, str] = {}
    defined_vars: set[str] = set()
    uuid_to_var_name: dict[str, str] = {}
    var_format_dates: dict[str, dict] = {}
    cents_vars: set[str] = set()
    divide_by_100_vars: set[str] = set()
    divide_by_100_uuids: set[str] = set()
    cents_context_steps = 0
    unit_text_found = False
    has_measurement_convert = False
    weather_source_vars: set[str] = set()
    location_source_vars: set[str] = set()
    health_sample_source_vars: set[str] = set()

    for idx, act in enumerate(actions):
        ident = act.get("WFWorkflowActionIdentifier")
        if ident == "is.workflow.actions.comment":
            params = act.get("WFWorkflowActionParameters") or {}
            text = params.get("WFCommentActionText")
            if isinstance(text, str):
                comments.append(text)
                wf_terms = _comment_internal_wf_terms(text)
                if wf_terms:
                    hints = ", ".join(
                        f"{token}->{_friendly_comment_field_name(token)}" for token in wf_terms
                    )
                    errors.append(
                        f"Comment uses internal WF parameter names at index {idx}: {hints}. "
                        "Use Shortcuts UI wording (for example: Input, Date, Provided Input, Repeat Item)."
                    )
                if not unit_text_found and _text_has_unit_keywords(text):
                    unit_text_found = True
        if ident == "is.workflow.actions.measurement.convert":
            has_measurement_convert = True
        params = act.get("WFWorkflowActionParameters") or {}
        used_output_uuids.update(iter_action_output_refs(params))
        if not unit_text_found:
            for path, s in iter_strings(params):
                if path and path[-1] in UNIT_KEYWORD_IGNORED_KEYS:
                    continue
                if isinstance(s, str) and s and _text_has_unit_keywords(s):
                    unit_text_found = True
                    break
        uuid = params.get("UUID")
        if uuid and ident:
            uuid_to_ident[uuid] = ident
            uuid_to_params[uuid] = params

    allow_vcard = any(VCARD_MARKER in text.upper() for text in comments)
    allow_token_file = any(TOKEN_FILE_MARKER in text.upper() for text in comments)
    allow_datetime_format = any(ALLOW_DATETIME_FORMAT_MARKER in text.upper() for text in comments)
    allow_manual_unit_conversion = any(
        ALLOW_MANUAL_UNIT_CONVERSION_MARKER in text.upper() for text in comments
    )

    # --- GroupingIdentifier consistency check ---
    grouping_start: dict[str, tuple[int, str]] = {}  # grouping_id -> (idx, ident)
    grouping_seen_end: set[str] = set()

    for idx, act in enumerate(actions):
        ident = act.get("WFWorkflowActionIdentifier")
        if ident not in CONTROL_FLOW_TOOLKIT_EXCEPTIONS:
            continue
        params = act.get("WFWorkflowActionParameters") or {}
        mode = _coerce_control_flow_mode(params)
        if mode is None:
            mode = 0
        grouping = params.get("GroupingIdentifier")
        if not grouping:
            continue
        if mode == 0:
            if grouping in grouping_start:
                errors.append(
                    f"Duplicate GroupingIdentifier '{grouping[:12]}...' for start action at index {idx}; "
                    f"first seen at index {grouping_start[grouping][0]}"
                )
            else:
                grouping_start[grouping] = (idx, ident or "")
        elif mode in (1, 2):
            if grouping not in grouping_start:
                errors.append(
                    f"Control-flow middle/end at index {idx} has GroupingIdentifier with no matching start (mode 0)"
                )
            else:
                start_ident = grouping_start[grouping][1]
                if ident != start_ident:
                    errors.append(
                        f"GroupingIdentifier mismatch at index {idx}: action '{ident}' "
                        f"does not match start action '{start_ident}'"
                    )
            if mode == 2:
                grouping_seen_end.add(grouping)

    for grouping, (start_idx, start_ident) in grouping_start.items():
        if grouping not in grouping_seen_end:
            errors.append(
                f"Control-flow start '{start_ident}' at index {start_idx} has no matching end (mode 2)"
            )

    # --- Menu case count and title matching check ---
    menu_items_by_grouping: dict[str, list[str]] = {}
    menu_cases_by_grouping: dict[str, list[tuple[int, str]]] = {}

    for idx, act in enumerate(actions):
        if act.get("WFWorkflowActionIdentifier") != "is.workflow.actions.choosefrommenu":
            continue
        params = act.get("WFWorkflowActionParameters") or {}
        mode = _coerce_control_flow_mode(params)
        if mode is None:
            mode = 0
        grouping = params.get("GroupingIdentifier")
        if not grouping:
            continue
        if mode == 0:
            items = params.get("WFMenuItems")
            if isinstance(items, list):
                # Menu items can be plain strings or rich dicts with WFValue
                extracted = []
                for i in items:
                    if isinstance(i, str):
                        extracted.append(i)
                    elif isinstance(i, dict):
                        extracted.append(str(i))  # count it even if rich format
                menu_items_by_grouping[grouping] = extracted
        elif mode == 1:
            title = params.get("WFMenuItemTitle", "")
            menu_cases_by_grouping.setdefault(grouping, []).append((idx, title))

    for grouping, items in menu_items_by_grouping.items():
        cases = menu_cases_by_grouping.get(grouping, [])
        if len(cases) != len(items):
            errors.append(
                f"Choose from Menu: {len(items)} item(s) in WFMenuItems but {len(cases)} case action(s) found"
            )
        else:
            # Only validate title matching when items are plain strings
            raw_items = menu_items_by_grouping.get(grouping, [])
            original_list = None
            for idx2, act2 in enumerate(actions):
                if act2.get("WFWorkflowActionIdentifier") == "is.workflow.actions.choosefrommenu":
                    p2 = act2.get("WFWorkflowActionParameters") or {}
                    if p2.get("GroupingIdentifier") == grouping:
                        m2 = p2.get("WFControlFlowMode")
                        if isinstance(m2, str) and m2.isdigit():
                            m2 = int(m2)
                        if m2 is None or m2 == 0:
                            original_list = p2.get("WFMenuItems", [])
                            break
            all_strings = original_list and all(isinstance(i, str) for i in original_list)
            if all_strings:
                for order_idx, ((case_act_idx, case_title), expected) in enumerate(zip(cases, items)):
                    if case_title != expected:
                        errors.append(
                            f"Choose from Menu case {order_idx} at index {case_act_idx}: "
                            f"WFMenuItemTitle '{case_title}' does not match WFMenuItems[{order_idx}] '{expected}'"
                        )

    input_classes = plist.get("WFWorkflowInputContentItemClasses") or []
    uses_input = False
    for act in actions:
        ident = act.get("WFWorkflowActionIdentifier")
        params = act.get("WFWorkflowActionParameters") or {}
        if ident == "is.workflow.actions.input":
            uses_input = True
            break
        for name in iter_variable_names(params):
            if name == "Shortcut Input":
                uses_input = True
                break
        if uses_input:
            break
        for _, out_name in iter_action_output_refs_with_name(params):
            if out_name == "Shortcut Input":
                uses_input = True
                break
        if uses_input:
            break
        if any(iter_extension_input_refs(params)):
            uses_input = True
            break
    if not input_classes and uses_input:
        errors.append(
            "Shortcut uses Shortcut Input but WFWorkflowInputContentItemClasses is empty (causes Stop and Respond)."
        )
    if input_classes and not uses_input:
        errors.append(
            "WFWorkflowInputContentItemClasses is set but Shortcut Input is unused; remove input types or use Shortcut Input."
        )

    icon_dict = plist.get("WFWorkflowIcon")
    if not isinstance(icon_dict, dict):
        errors.append("Missing WFWorkflowIcon root dictionary")
    else:
        glyph_number = icon_dict.get("WFWorkflowIconGlyphNumber")
        start_color = icon_dict.get("WFWorkflowIconStartColor")

        if glyph_number is None:
            errors.append("WFWorkflowIcon missing WFWorkflowIconGlyphNumber")
        else:
            try:
                glyph_int = int(glyph_number)
            except (TypeError, ValueError):
                errors.append("WFWorkflowIconGlyphNumber must be an integer")
            else:
                if allowed_glyph_ids and glyph_int not in allowed_glyph_ids:
                    errors.append(
                        f"WFWorkflowIconGlyphNumber {glyph_int} is not in the official 507 glyph mapping"
                    )

        if start_color is None:
            errors.append("WFWorkflowIcon missing WFWorkflowIconStartColor")
        else:
            try:
                color_int = int(start_color)
            except (TypeError, ValueError):
                errors.append("WFWorkflowIconStartColor must be an integer")
            else:
                if allowed_icon_colors and color_int not in allowed_icon_colors:
                    errors.append(
                        f"WFWorkflowIconStartColor {color_int} is not in the known Shortcuts color palette"
                    )

    if actions:
        if len(actions) < 2:
            errors.append("Missing required two leading Comment actions")
        else:
            first = actions[0]
            second = actions[1]
            if first.get("WFWorkflowActionIdentifier") != "is.workflow.actions.comment":
                errors.append("First action must be a Comment describing the shortcut")
            else:
                first_text = (first.get("WFWorkflowActionParameters") or {}).get("WFCommentActionText")
                if not first_text:
                    errors.append("First Comment is empty")
            if second.get("WFWorkflowActionIdentifier") != "is.workflow.actions.comment":
                errors.append("Second action must be the prompt Comment block")
            else:
                second_text = (second.get("WFWorkflowActionParameters") or {}).get("WFCommentActionText", "")
                if "Shortcuts generated by Shortcuts Playground." not in second_text:
                    errors.append("Second Comment missing required Shortcuts Playground prompt text")

    # Comment density requirements
    comment_count = len(comments)
    min_comments = 2
    if len(actions) >= 24:
        min_comments = 5
    elif len(actions) >= 16:
        min_comments = 4
    elif len(actions) >= 8:
        min_comments = 3
    if comment_count < min_comments:
        errors.append(
            f"Insufficient Comment blocks: {comment_count} found, require {min_comments} for {len(actions)} actions"
        )

    if unit_text_found and not has_measurement_convert and not allow_manual_unit_conversion:
        errors.append(
            "Unit conversion detected but no measurement.convert action; use measurement.create + measurement.convert or add ALLOW_MANUAL_UNIT_CONVERSION comment."
        )

    if errors and actions and first_error is None:
        first_action = actions[0]
        first_params = first_action.get("WFWorkflowActionParameters") or {}
        first_error = (0, first_action.get("WFWorkflowActionIdentifier") or "UNKNOWN", _snippet(first_params))

    for idx, act in enumerate(actions):
        ident = act.get("WFWorkflowActionIdentifier")
        params = act.get("WFWorkflowActionParameters") or {}
        uuid = params.get("UUID")

        # WFControlFlowMode must be <integer>, not <string>
        if ident in CONTROL_FLOW_TOOLKIT_EXCEPTIONS:
            raw_mode = params.get("WFControlFlowMode")
            if isinstance(raw_mode, str):
                errors.append(
                    f"WFControlFlowMode must be <integer> not <string> at index {idx}: "
                    f"{ident} (found: {raw_mode!r})"
                )

        # Aggrandizement type validation
        for agg in iter_aggrandizements(params):
            agg_type = agg.get("Type")
            if agg_type is None:
                errors.append(f"Aggrandizement missing Type field at index {idx}: {ident}")
            elif agg_type not in KNOWN_AGGRANDIZEMENT_TYPES:
                errors.append(
                    f"Unknown aggrandizement Type '{agg_type}' at index {idx}: {ident}"
                )

        # Enforce descriptive Comment immediately before control-flow starts
        if ident in {
            "is.workflow.actions.repeat.each",
            "is.workflow.actions.repeat.count",
            "is.workflow.actions.conditional",
            "is.workflow.actions.choosefrommenu",
        }:
            mode = _coerce_control_flow_mode(params)
            if mode == 0:
                if idx == 0 or actions[idx - 1].get("WFWorkflowActionIdentifier") != "is.workflow.actions.comment":
                    errors.append(
                        f"Missing descriptive Comment immediately before control-flow start at index {idx}"
                    )
                else:
                    prev_params = actions[idx - 1].get("WFWorkflowActionParameters") or {}
                    prev_text = prev_params.get("WFCommentActionText", "")
                    if not _comment_has_bullets(prev_text):
                        errors.append(
                            f"Control-flow Comment must include a bulleted wiring list at index {idx - 1}"
                        )

        if ident == "is.workflow.actions.comment":
            text = params.get("WFCommentActionText")
            if isinstance(text, str) and "cents" in text.lower():
                cents_context_steps = 10

        # Track repeat nesting (repeat.each and repeat.count)
        if ident in {"is.workflow.actions.repeat.each", "is.workflow.actions.repeat.count"}:
            mode = _coerce_control_flow_mode(params)
            if mode is None:
                mode = 0
            grouping = params.get("GroupingIdentifier")
            if mode == 0:
                repeat_stack.append({"group": grouping, "uuid": uuid, "kind": ident})
            elif mode == 2 and repeat_stack:
                if grouping:
                    repeat_end_uuids[grouping] = uuid
                repeat_stack.pop()

        # Validate repeat variables inside nested loops
        if repeat_stack:
            innermost = repeat_stack[-1]
            innermost_uuid = innermost.get("uuid")
            loop_label = "Repeat with Each" if innermost.get("kind") == "is.workflow.actions.repeat.each" else "Repeat (count)"
            repeat_uuids = {item.get("uuid") for item in repeat_stack if item.get("uuid")}
            active_groups = {item.get("group") for item in repeat_stack if item.get("group")}
            active_end_uuids = {repeat_end_uuids.get(g) for g in active_groups if repeat_end_uuids.get(g)}
            for out_uuid, out_name in iter_action_output_refs_with_name(params):
                if out_name and out_name.startswith("Repeat Results"):
                    errors.append(
                        f"Repeat Results referenced inside {loop_label} at index {idx}"
                    )
                if out_uuid in repeat_uuids:
                    if out_name == "Repeat Results":
                        errors.append(
                            f"Repeat Results referenced inside {loop_label} at index {idx}"
                        )
                    elif out_name in {"Repeat Item", "Repeat Index"} and out_uuid != innermost_uuid:
                        errors.append(
                            f"Nested repeat uses outer {out_name} at index {idx}; use innermost Repeat Item/Index"
                        )
                    # Even for innermost, prefer Variable references (not ActionOutput) to avoid UI showing Repeat Results
                    if out_name in {"Repeat Item", "Repeat Index"}:
                        errors.append(
                            f"Repeat Item/Index should be referenced as a Variable (not ActionOutput) inside {loop_label} at index {idx}"
                        )
                if out_uuid in active_end_uuids:
                    if out_name in {"Repeat Item", "Repeat Index"}:
                        errors.append(
                            f"{out_name} should be referenced as a Variable (not ActionOutput) inside {loop_label} at index {idx}"
                        )
                    else:
                        errors.append(
                            f"Repeat Results (end output) used inside {loop_label} at index {idx}"
                        )
            for name in iter_variable_names(params):
                if name.startswith("Repeat Results"):
                    errors.append(
                        f"Repeat Results variable used inside {loop_label} at index {idx}"
                    )

        # Track variable definitions
        if ident == "is.workflow.actions.setvariable":
            name = params.get("WFVariableName")
            if isinstance(name, str) and name.strip():
                defined_vars.add(name)
                if "cents" in name.lower():
                    cents_vars.add(name)
                wfinput = params.get("WFInput")
                out_uuids = _input_action_output_uuids(wfinput)
                source_var_name = _extract_input_variable_name(wfinput)
                weather_source = bool(source_var_name and source_var_name in weather_source_vars)
                location_source = bool(source_var_name and source_var_name in location_source_vars)
                health_sample_source = bool(
                    source_var_name and source_var_name in health_sample_source_vars
                )
                for source_uuid in out_uuids:
                    source_ident = uuid_to_ident.get(source_uuid)
                    if source_ident == "is.workflow.actions.format.date":
                        var_format_dates[name] = uuid_to_params.get(source_uuid, {})
                    if source_ident in WEATHER_SOURCE_ACTIONS:
                        weather_source = True
                    if source_ident in LOCATION_SOURCE_ACTIONS:
                        location_source = True
                    if source_ident in HEALTH_SAMPLE_SOURCE_ACTIONS:
                        health_sample_source = True
                if weather_source:
                    weather_source_vars.add(name)
                if location_source:
                    location_source_vars.add(name)
                if health_sample_source:
                    health_sample_source_vars.add(name)

        if ident == "is.workflow.actions.getvariable":
            wfvar = params.get("WFVariable")
            if isinstance(wfvar, dict):
                val = wfvar.get("Value")
                if isinstance(val, dict):
                    name = val.get("VariableName")
                    if isinstance(name, str) and name.strip() and uuid:
                        uuid_to_var_name[uuid] = name

        # Unknown actions
        if ident:
            if ident.startswith("is.workflow.actions."):
                if ident not in allowed_ids:
                    hint = ACTION_ALIAS_HINTS.get(ident)
                    if hint:
                        errors.append(
                            f"Unknown action identifier at index {idx}: {ident} (use {hint})"
                        )
                    else:
                        errors.append(f"Unknown action identifier at index {idx}: {ident}")
            elif ident.startswith("com.apple."):
                if ident not in allowed_ids:
                    errors.append(f"Unknown AppIntent identifier at index {idx}: {ident}")
            else:
                # Accept unknown vendor-prefixed third-party identifiers so shared
                # skills remain usable without local ToolKit extraction.
                if ident not in allowed_ids and not THIRD_PARTY_IDENTIFIER_RE.match(ident):
                    errors.append(f"Unknown third-party identifier at index {idx}: {ident}")

        if ident in NOTES_CREATE_ACTIONS:
            title_val = None
            content_val = None
            for key, value in (params or {}).items():
                if key.lower() in NOTES_TITLE_KEYS and title_val is None:
                    title_val = value
                if key.lower() in NOTES_CONTENT_KEYS and content_val is None:
                    content_val = value
            if title_val is None:
                errors.append(f"Notes create action missing title/name parameter at index {idx}")
            elif _token_param_is_empty(title_val):
                errors.append(f"Notes create action title/name is empty at index {idx}")
            if content_val is None:
                errors.append(f"Notes create action missing content/markdown parameter at index {idx}")
            elif _token_param_is_empty(content_val):
                errors.append(f"Notes create action content/markdown is empty at index {idx}")

        # Empty strings in parameters
        for path in iter_empty_strings(params):
            errors.append(f"Empty parameter at index {idx}: {ident} -> {'/'.join(path)}")

        # Validate WFTextTokenString placeholders (Shortcuts uses UTF-16 indices)
        for token in iter_text_token_strings(params):
            value = token.get("Value") if isinstance(token, dict) else None
            if not isinstance(value, dict):
                errors.append(f"WFTextTokenString missing Value dict at index {idx}")
                continue
            string = value.get("string")
            attachments = value.get("attachmentsByRange")
            if not isinstance(string, str):
                errors.append(f"WFTextTokenString missing string at index {idx}")
                continue
            if attachments is None:
                if "￼" in string:
                    errors.append(f"WFTextTokenString missing attachmentsByRange at index {idx}")
                continue
            if not isinstance(attachments, dict):
                errors.append(f"WFTextTokenString attachmentsByRange not a dict at index {idx}")
                continue
            units = _utf16_units(string)
            total_len = 0
            for key in attachments.keys():
                m = re.match(r"^\{(\d+),\s*(\d+)\}$", str(key))
                if not m:
                    errors.append(f"Invalid attachmentsByRange key at index {idx}: {key}")
                    continue
                start = int(m.group(1))
                length = int(m.group(2))
                total_len += length
                if start < 0 or start + length > len(units):
                    errors.append(f"attachmentsByRange out of bounds at index {idx}: {key}")
                    continue
                if any(units[start + j] != 0xFFFC for j in range(length)):
                    errors.append(f"attachmentsByRange does not match placeholder at index {idx}: {key}")
            if string.count("￼") != total_len:
                errors.append(f"Placeholder count mismatch at index {idx}")

        # vCard/VCF usage should be explicit
        if ident != "is.workflow.actions.comment" and not allow_vcard:
            for _, value in iter_strings(params):
                upper = value.upper()
                if "BEGIN:VCARD" in upper or "VCARD" in upper:
                    errors.append(f"vCard/VCF content detected at index {idx}: {ident}")
                    break

        # Token file usage should be explicit
        if not allow_token_file and ident:
            if ident in FILE_ACTION_IDS or any(ident.startswith(p) for p in FILE_ACTION_PREFIXES):
                for path, value in iter_strings(params):
                    if "WFSerializationType" in path:
                        continue
                    if value in {
                        "WFTextTokenString",
                        "WFTextTokenAttachment",
                        "WFTokenAttachmentParameterState",
                    }:
                        continue
                    if TOKEN_HINT_RE.search(value or ""):
                        errors.append(f"API token loaded from file at index {idx}: {ident}")
                        break

        # TODOIST update URL should include task ID placeholder
        if ident != "is.workflow.actions.comment":
            for _, value in iter_strings(params):
                if TODOIST_TASKS_PREFIX in value:
                    suffix = value.split(TODOIST_TASKS_PREFIX, 1)[1]
                    if "￼" not in suffix:
                        errors.append(f"Todoist task update URL missing task ID placeholder at index {idx}")
                    break

        # Conditional must be fully specified for mode 0 (start). Verified against
        # an Apple-built sample covering codes 0, 1, 2, 3, 4, 5, 8, 9, 99, 100, 101,
        # 999, 1003, plus the multi-condition (Any/All are true) WFConditions pattern.
        if ident == "is.workflow.actions.conditional":
            mode = _coerce_control_flow_mode(params)
            if mode is None:
                mode = 0
            if mode != 0:
                continue

            cond = params.get("WFCondition")
            inp = params.get("WFInput")
            wfconds = params.get("WFConditions")

            # Multi-condition pattern: WFConditions holds an array of templates,
            # each template is its own (WFCondition + WFInput + literal). When
            # this is set, the action does NOT have top-level WFCondition/WFInput.
            if wfconds is not None:
                if not isinstance(wfconds, dict):
                    errors.append(f"Conditional WFConditions must be a dict at index {idx}")
                else:
                    serialization = wfconds.get("WFSerializationType")
                    if serialization != "WFContentPredicateTableTemplate":
                        errors.append(
                            f"Conditional WFConditions WFSerializationType must be "
                            f"WFContentPredicateTableTemplate at index {idx}"
                        )
                    value = wfconds.get("Value")
                    templates = None
                    prefix = None
                    if isinstance(value, dict):
                        templates = value.get("WFActionParameterFilterTemplates")
                        prefix = value.get("WFActionParameterFilterPrefix")
                    if not templates:
                        errors.append(
                            f"Conditional WFConditions has empty filter templates at index {idx}"
                        )
                    elif not isinstance(templates, list):
                        errors.append(
                            f"Conditional WFConditions templates must be a list at index {idx}"
                        )
                    else:
                        if prefix not in (0, 1):
                            errors.append(
                                f"Conditional WFConditions WFActionParameterFilterPrefix must be "
                                f"0 (Any are true) or 1 (All are true) at index {idx}"
                            )
                        for tidx, template in enumerate(templates):
                            if not isinstance(template, dict):
                                errors.append(
                                    f"Conditional template {tidx} is not a dict at index {idx}"
                                )
                                continue
                            tcond = template.get("WFCondition")
                            tinp = template.get("WFInput")
                            if tcond is None or tinp is None:
                                errors.append(
                                    f"Conditional template {tidx} missing WFCondition or WFInput at index {idx}"
                                )
                                continue
                            if not isinstance(tcond, int):
                                errors.append(
                                    f"Conditional template {tidx} WFCondition must be integer at index {idx}"
                                )
                                continue
                            if tcond not in ALL_CONDITION_CODES:
                                errors.append(
                                    f"Conditional template {tidx} uses unknown WFCondition {tcond} at index {idx}"
                                )
                                continue
                            if not _input_is_attached(tinp) or not _conditional_input_is_wrapped(tinp):
                                errors.append(
                                    f"Conditional template {tidx} WFInput must be a Type=Variable "
                                    f"wrapper at index {idx}"
                                )
                            if tcond in STRING_CONDITION_CODES and not template.get("WFConditionalActionString"):
                                errors.append(
                                    f"Conditional template {tidx} (string code {tcond}) missing "
                                    f"WFConditionalActionString at index {idx}"
                                )
                            if tcond in NUMBER_CONDITION_CODES and template.get("WFNumberValue") is None:
                                errors.append(
                                    f"Conditional template {tidx} (numeric code {tcond}) missing "
                                    f"WFNumberValue at index {idx}"
                                )
                            if tcond == 1003 and template.get("WFAnotherNumber") is None:
                                errors.append(
                                    f"Conditional template {tidx} (between, code 1003) missing "
                                    f"WFAnotherNumber upper bound at index {idx}"
                                )
                # Multi-condition is mutually exclusive with top-level WFCondition/WFInput.
                if cond is not None or inp is not None:
                    errors.append(
                        f"Conditional has both WFConditions multi-condition block and "
                        f"top-level WFCondition/WFInput at index {idx}; remove the top-level fields"
                    )
                continue

            # Single-condition pattern: top-level WFCondition + WFInput + literal field.
            # Use `is None` (not truthiness) — code 0 (less than) is a valid integer.
            if cond is None or inp is None:
                errors.append(f"Conditional missing WFInput/WFCondition at index {idx}")
                continue
            if not isinstance(cond, int):
                errors.append(
                    f"Conditional WFCondition should use integer code for runtime stability at index {idx}"
                )
                continue
            if cond not in ALL_CONDITION_CODES:
                errors.append(
                    f"Conditional uses unknown WFCondition code {cond} at index {idx}; see CONTROL_FLOW.md"
                )
                continue
            if not _input_is_attached(inp):
                errors.append(f"Conditional WFInput is not a token attachment at index {idx}")
                continue
            is_wrapped = _conditional_input_is_wrapped(inp)
            if not is_wrapped:
                errors.append(
                    f"Conditional WFInput must use Type=Variable wrapper for editor visibility at index {idx}"
                )
            # Per-code field requirements.
            if cond in STRING_CONDITION_CODES:
                if not params.get("WFConditionalActionString"):
                    errors.append(
                        f"Conditional (string code {cond}) missing WFConditionalActionString at index {idx}"
                    )
                else:
                    for out_uuid in _input_action_output_uuids(inp):
                        ident_inp = uuid_to_ident.get(out_uuid)
                        if ident_inp == "is.workflow.actions.getvalueforkey":
                            errors.append(
                                f"Conditional compares Dictionary Value directly at index {idx}; wrap in Text first"
                            )
            elif cond in NUMBER_CONDITION_CODES:
                if params.get("WFNumberValue") is None:
                    errors.append(
                        f"Conditional (numeric code {cond}) missing WFNumberValue at index {idx}"
                    )
                if cond == 1003 and params.get("WFAnotherNumber") is None:
                    errors.append(
                        f"Conditional (between, code 1003) missing WFAnotherNumber upper bound at index {idx}"
                    )
            elif cond in EXISTENCE_CONDITION_CODES:
                # Existence checks (100/101) take no literal — only WFInput.
                if params.get("WFConditionalActionString") is not None:
                    errors.append(
                        f"Conditional (existence code {cond}) must not set WFConditionalActionString at index {idx}"
                    )
                if params.get("WFNumberValue") is not None:
                    errors.append(
                        f"Conditional (existence code {cond}) must not set WFNumberValue at index {idx}"
                    )

        # Choose from Menu start requires items
        if ident == "is.workflow.actions.choosefrommenu":
            mode = _coerce_control_flow_mode(params)
            if mode is None:
                mode = 0
            if mode == 0:
                items = params.get("WFMenuItems")
                if not items:
                    errors.append(f"Choose from Menu has no items at index {idx}")
                prompt = params.get("WFMenuPrompt")
                if isinstance(prompt, str) and prompt == "":
                    errors.append(f"Choose from Menu has empty prompt at index {idx}")

        # Ask for Input must have a prompt
        if ident == "is.workflow.actions.ask":
            if "WFAskActionPrompt" not in params or not params.get("WFAskActionPrompt"):
                errors.append(f"Ask for Input missing prompt at index {idx}")
            if params.get("WFAskActionDefaultAnswer") == "":
                errors.append(f"Ask for Input has empty default answer at index {idx}")

        if ident == "is.workflow.actions.input":
            errors.append(
                f"Shortcut Input action is not runtime-safe on iOS at index {idx}; use ExtensionInput attachment instead"
            )

        # Text action should not be blank
        if ident == "is.workflow.actions.gettext":
            if "WFTextActionText" not in params:
                errors.append(f"Text action missing text at index {idx}")
            else:
                text = params.get("WFTextActionText")
                if text == "":
                    errors.append(f"Text action has empty text at index {idx}")

        if ident == "is.workflow.actions.number":
            number = params.get("WFNumberActionNumber")
            if number is None or number == "" or number == {}:
                errors.append(f"Number action missing WFNumberActionNumber at index {idx}")

        # URL action should have URL
        if ident in REQUIRED_URL_ACTIONS:
            if not params.get("WFURLActionURL"):
                errors.append(f"URL action missing WFURLActionURL at index {idx}")

        # Require explicit input for selected actions
        if ident in REQUIRED_INPUT_ACTIONS:
            wfinput = params.get("WFInput")
            if not wfinput:
                errors.append(f"Missing WFInput at index {idx}: {ident}")
            elif not _input_is_attached(wfinput):
                errors.append(f"WFInput is not a token attachment at index {idx}: {ident}")
            elif not _input_has_reference(wfinput):
                errors.append(f"WFInput has no variable/output reference at index {idx}: {ident}")
            else:
                for out_uuid in _input_action_output_uuids(wfinput):
                    if out_uuid not in uuid_to_ident:
                        errors.append(f"WFInput references unknown OutputUUID at index {idx}: {ident}")
            if ident in EDITOR_VISIBLE_INPUT_ACTIONS and not _input_is_editor_visible(wfinput):
                errors.append(
                    f"WFInput should use WFTextTokenString (placeholder) or wrapped Variable for editor visibility at index {idx}: {ident}"
                )

        if ident == "is.workflow.actions.location" and "WFLocation" not in params:
            errors.append(f"Location action missing WFLocation at index {idx}")

        for location_key in LOCATION_PARAMETER_KEYS:
            if location_key not in params:
                continue
            location_value = params.get(location_key)
            if _token_param_is_empty(location_value):
                errors.append(
                    f"Location parameter {location_key} is empty at index {idx}: {ident}"
                )
                continue
            if not _input_is_attached(location_value):
                errors.append(
                    f"Location parameter {location_key} is not a token attachment at index {idx}: {ident}"
                )
                continue
            if (
                isinstance(location_value, dict)
                and location_value.get("WFSerializationType") != "WFTextTokenAttachment"
            ):
                errors.append(
                    f"Location parameter {location_key} should use WFTextTokenAttachment (token strings can import as empty) at index {idx}: {ident}"
                )
                continue
            if not _input_has_reference(location_value):
                errors.append(
                    f"Location parameter {location_key} has no variable/output reference at index {idx}: {ident}"
                )
                continue
            input_var_name = _extract_input_variable_name(location_value)
            if input_var_name:
                if input_var_name not in location_source_vars:
                    errors.append(
                        f"Location parameter {location_key} variable '{input_var_name}' does not resolve to a location source variable at index {idx}: {ident}"
                    )
                continue
            for out_uuid in _input_action_output_uuids(location_value):
                source_ident = uuid_to_ident.get(out_uuid)
                if source_ident is None:
                    errors.append(
                        f"Location parameter {location_key} references unknown OutputUUID at index {idx}: {ident}"
                    )
                elif source_ident not in LOCATION_SOURCE_ACTIONS:
                    errors.append(
                        f"Location parameter {location_key} should reference output from Get Current Location/Location action at index {idx}: {ident}"
                    )

        wfinput = params.get("WFInput")
        if (
            wfinput
            and ident != "is.workflow.actions.conditional"
            and _wrapped_variable_contains_action_output(wfinput)
        ):
            errors.append(
                f"WFInput wraps ActionOutput in Type=Variable wrapper at index {idx}: {ident}"
            )

        # Data-producing actions should have their outputs referenced later
        if ident in UNUSED_OUTPUT_ACTIONS and uuid and uuid not in used_output_uuids:
            if idx != len(actions) - 1:
                errors.append(
                    f"Output from {ident} at index {idx} is unused; likely missing variable wiring"
                )

        # Download URL should have WFURL or WFInput
        if ident in REQUIRED_URL_INPUT_ACTIONS:
            if not params.get("WFURL") and not params.get("WFInput"):
                errors.append(f"Get Contents of URL missing WFURL/WFInput at index {idx}")

        if ident == "is.workflow.actions.count":
            if "Input" not in params:
                errors.append(f"Count action should include Input mirror of WFInput at index {idx}")
            elif params.get("WFInput") and params.get("Input") != params.get("WFInput"):
                errors.append(f"Count action Input must match WFInput reference at index {idx}")

        # Action-specific required fields
        if ident == "is.workflow.actions.getvalueforkey":
            wfinput = params.get("WFInput")
            if not wfinput:
                errors.append(f"Get Dictionary Value missing input at index {idx}")
            elif not _input_is_attached(wfinput):
                errors.append(f"Get Dictionary Value WFInput is not a token attachment at index {idx}")
            elif not _input_has_reference(wfinput):
                errors.append(f"Get Dictionary Value WFInput has no variable/output reference at index {idx}")
            else:
                for out_uuid in _input_action_output_uuids(wfinput):
                    if out_uuid not in uuid_to_ident:
                        errors.append(f"Get Dictionary Value references unknown OutputUUID at index {idx}")

            value_type = params.get("WFGetDictionaryValueType")
            if value_type in (None, "", "Value"):
                key_param = params.get("WFDictionaryKey")
                if _token_param_is_empty(key_param):
                    errors.append(f"Get Dictionary Value missing key at index {idx}")
                elif isinstance(key_param, str):
                    if UNSAFE_ERROR_DOT_PATH_RE.match(key_param.strip()):
                        errors.append(
                            f"Get Dictionary Value uses unsafe direct key path '{key_param}' at index {idx}; extract 'error' first, then read nested keys inside a guarded If block"
                        )

        if ident == "is.workflow.actions.image.convert":
            if _token_param_is_empty(params.get("WFImageFormat")):
                errors.append(f"Convert Image missing WFImageFormat at index {idx}")

        if ident == "is.workflow.actions.properties.weather.conditions":
            prop_name = params.get("WFContentItemPropertyName")
            if _token_param_is_empty(prop_name):
                errors.append(
                    f"Get Detail of Weather Conditions missing WFContentItemPropertyName at index {idx}"
                )
            elif (
                isinstance(prop_name, str)
                and prop_name.strip().lower() in WEATHER_DETAIL_PLACEHOLDER_VALUES
            ):
                errors.append(
                    f"Get Detail of Weather Conditions uses placeholder detail name at index {idx}: {prop_name!r}"
                )
            weather_input = params.get("WFInput")
            if _token_param_is_empty(weather_input):
                errors.append(f"Get Detail of Weather Conditions missing WFInput at index {idx}")
            elif not _input_is_attached(weather_input):
                errors.append(
                    f"Get Detail of Weather Conditions WFInput is not a token attachment at index {idx}"
                )
            elif not _input_has_reference(weather_input):
                errors.append(
                    f"Get Detail of Weather Conditions WFInput has no variable/output reference at index {idx}"
                )
            else:
                input_var_name = _extract_input_variable_name(weather_input)
                if input_var_name:
                    errors.append(
                        f"Get Detail of Weather Conditions WFInput should reference weather action output directly (variable '{input_var_name}' can import as generic Detail) at index {idx}"
                    )

                out_uuids = _input_action_output_uuids(weather_input)
                if not out_uuids:
                    errors.append(
                        f"Get Detail of Weather Conditions WFInput should reference output from Get Weather/Forecast directly at index {idx}"
                    )
                else:
                    has_weather_source = False
                    for out_uuid in out_uuids:
                        source_ident = uuid_to_ident.get(out_uuid)
                        if source_ident is None:
                            errors.append(
                                f"Get Detail of Weather Conditions references unknown OutputUUID at index {idx}"
                            )
                        elif source_ident in WEATHER_SOURCE_ACTIONS:
                            has_weather_source = True
                    if not has_weather_source:
                        errors.append(
                            f"Get Detail of Weather Conditions WFInput should reference output from Get Weather/Forecast at index {idx}"
                        )

        if ident == "is.workflow.actions.gettimebetweendates":
            date_keys = ("WFDate", "WFTimeUntilCustomDate", "WFTimeUntilFromDate")
            non_empty_date_refs: list[tuple[str, object]] = []
            for key in date_keys:
                if key not in params:
                    continue
                value = params.get(key)
                if _token_param_is_empty(value):
                    errors.append(
                        f"Get Time Between Dates has empty {key} at index {idx}; omit unused date keys"
                    )
                else:
                    non_empty_date_refs.append((key, value))

            if not non_empty_date_refs:
                errors.append(
                    f"Get Time Between Dates missing WFDate/WFTimeUntilCustomDate/WFTimeUntilFromDate at index {idx}"
                )
            elif len(non_empty_date_refs) > 1:
                used = ", ".join(key for key, _ in non_empty_date_refs)
                errors.append(
                    f"Get Time Between Dates should set exactly one non-empty date operand (found: {used}) at index {idx}"
                )

            for key, reference in non_empty_date_refs:
                if not _input_is_attached(reference):
                    errors.append(
                        f"Get Time Between Dates {key} is not a token attachment at index {idx}"
                    )
                    continue
                if not _input_has_reference(reference):
                    errors.append(
                        f"Get Time Between Dates {key} has no variable/output reference at index {idx}"
                    )
                    continue
                for out_uuid in _input_action_output_uuids(reference):
                    if out_uuid not in uuid_to_ident:
                        errors.append(
                            f"Get Time Between Dates {key} references unknown OutputUUID at index {idx}"
                        )

            unit = params.get("WFTimeUntilUnit")
            if not _token_param_is_empty(unit) and isinstance(unit, str) and unit.strip().lower() not in DATE_DELTA_UNITS:
                errors.append(f"Get Time Between Dates has unsupported WFTimeUntilUnit '{unit}' at index {idx}")

        if ident == "is.workflow.actions.extracttextfromimage":
            image_keys = ("WFImage", "WFInput")
            non_empty_image_inputs: list[tuple[str, object]] = []
            for key in image_keys:
                if key not in params:
                    continue
                value = params.get(key)
                if _token_param_is_empty(value):
                    errors.append(
                        f"Extract Text from Image has empty {key} at index {idx}; omit unused image-input keys"
                    )
                else:
                    non_empty_image_inputs.append((key, value))

            if not non_empty_image_inputs:
                errors.append(
                    f"Extract Text from Image missing WFImage/WFInput at index {idx}"
                )
            elif len(non_empty_image_inputs) > 1:
                used = ", ".join(key for key, _ in non_empty_image_inputs)
                errors.append(
                    f"Extract Text from Image should set exactly one non-empty image input key (found: {used}) at index {idx}"
                )

            for key, value in non_empty_image_inputs:
                if not _input_is_attached(value):
                    errors.append(
                        f"Extract Text from Image {key} is not a token attachment at index {idx}"
                    )
                    continue
                if not _input_has_reference(value):
                    errors.append(
                        f"Extract Text from Image {key} has no variable/output reference at index {idx}"
                    )
                    continue
                for out_uuid in _input_action_output_uuids(value):
                    if out_uuid not in uuid_to_ident:
                        errors.append(
                            f"Extract Text from Image {key} references unknown OutputUUID at index {idx}"
                        )

        if ident == "is.workflow.actions.setvalueforkey":
            if not params.get("WFDictionary"):
                errors.append(f"Set Dictionary Value missing WFDictionary at index {idx}")

        if ident == "is.workflow.actions.text.match":
            if "WFInput" in params:
                errors.append(
                    f"Match Text should use 'text' parameter (not WFInput) at index {idx}"
                )
            text_param = params.get("text")
            if text_param is None:
                errors.append(f"Match Text missing 'text' parameter at index {idx}")
            elif _token_param_is_empty(text_param):
                errors.append(f"Match Text has empty 'text' parameter at index {idx}")

        if ident in TEXT_INPUT_KEY_ACTIONS:
            action_name = "Change Case" if ident == "is.workflow.actions.text.changecase" else "Split Text"
            text_param = params.get("text")
            if text_param is None:
                if "WFInput" in params:
                    errors.append(
                        f"{action_name} should use 'text' parameter (not WFInput) at index {idx}"
                    )
                else:
                    errors.append(f"{action_name} missing 'text' parameter at index {idx}")
            else:
                if _token_param_is_empty(text_param):
                    errors.append(f"{action_name} has empty 'text' parameter at index {idx}")
                elif isinstance(text_param, dict) and not _input_is_attached(text_param):
                    errors.append(f"{action_name} 'text' parameter is not a token attachment at index {idx}")
            if "WFInput" in params:
                errors.append(
                    f"{action_name} should not include WFInput; wire input via 'text' parameter at index {idx}"
                )
            if ident == "is.workflow.actions.text.split":
                sep = params.get("WFTextSeparator")
                if sep == "Custom":
                    custom_sep = params.get("WFTextCustomSeparator")
                    # A single space is a valid custom separator; only reject missing/empty-string.
                    if custom_sep is None:
                        errors.append(f"Split Text missing WFTextCustomSeparator for Custom separator at index {idx}")
                    elif isinstance(custom_sep, str) and custom_sep == "":
                        errors.append(f"Split Text missing WFTextCustomSeparator for Custom separator at index {idx}")
                    elif isinstance(custom_sep, dict) and _token_param_is_empty(custom_sep):
                        errors.append(f"Split Text missing WFTextCustomSeparator for Custom separator at index {idx}")

        if ident == "is.workflow.actions.text.replace":
            if "text" in params and "WFInput" not in params:
                errors.append(
                    f"Replace Text should use WFInput (not 'text') at index {idx}"
                )

        if ident == "is.workflow.actions.filter.notes":
            filt = params.get("WFContentItemFilter")
            if not isinstance(filt, dict):
                errors.append(f"Find Notes missing WFContentItemFilter at index {idx}")
            else:
                if filt.get("WFSerializationType") != "WFContentPredicateTableTemplate":
                    errors.append(
                        f"Find Notes WFContentItemFilter must use WFContentPredicateTableTemplate at index {idx}"
                    )
                fval = filt.get("Value")
                if not isinstance(fval, dict):
                    errors.append(f"Find Notes WFContentItemFilter missing Value dict at index {idx}")
                else:
                    templates = fval.get("WFActionParameterFilterTemplates")
                    if not isinstance(templates, list) or not templates:
                        errors.append(f"Find Notes filter has no templates at index {idx}")
                    else:
                        for tidx, template in enumerate(templates):
                            if not isinstance(template, dict):
                                errors.append(
                                    f"Find Notes filter template {tidx} is not a dict at index {idx}"
                                )
                                continue
                            prop = template.get("Property")
                            values = template.get("Values")
                            if not isinstance(values, dict):
                                errors.append(
                                    f"Find Notes filter template '{prop}' missing Values dict at index {idx}"
                                )
                                continue
                            if prop == "Name":
                                string_state = values.get("String")
                                if _token_param_is_empty(string_state):
                                    errors.append(
                                        f"Find Notes Name filter has empty String value at index {idx}"
                                    )
                                elif isinstance(string_state, dict) and string_state.get(
                                    "WFSerializationType"
                                ) != "WFTextTokenString":
                                    errors.append(
                                        f"Find Notes Name filter should use WFTextTokenString for String value at index {idx}"
                                    )
                            if prop == "Folder":
                                enum_state = values.get("Enumeration")
                                if not isinstance(enum_state, dict):
                                    errors.append(
                                        f"Find Notes Folder filter missing Enumeration value at index {idx}"
                                    )
                                else:
                                    if (
                                        enum_state.get("WFSerializationType")
                                        != "WFLinkDynamicOptionSubstitutableState"
                                    ):
                                        errors.append(
                                            f"Find Notes Folder filter should use WFLinkDynamicOptionSubstitutableState at index {idx}"
                                        )
                                    enum_value = enum_state.get("Value")
                                    if _token_param_is_empty(enum_value):
                                        errors.append(
                                            f"Find Notes Folder filter Enumeration value is empty at index {idx}"
                                        )

        if ident == HEALTH_FIND_SAMPLES_ACTION:
            health_type = params.get("WFHealthQuantityType")
            if _token_param_is_empty(health_type):
                errors.append(f"Find Health Samples missing WFHealthQuantityType at index {idx}")
            elif (
                isinstance(health_type, str)
                and HEALTH_REFERENCE_SETS["quantity_types"]
                and health_type not in HEALTH_REFERENCE_SETS["quantity_types"]
            ):
                errors.append(
                    f"Find Health Samples uses unknown WFHealthQuantityType '{health_type}' at index {idx}"
                )
            _validate_health_filter_template(
                params.get("WFContentItemFilter"),
                action_label="Find Health Samples",
                idx=idx,
                errors=errors,
            )
            if "WFContentItemLimitEnabled" in params and not isinstance(
                params.get("WFContentItemLimitEnabled"), bool
            ):
                errors.append(
                    f"Find Health Samples WFContentItemLimitEnabled must be boolean at index {idx}"
                )
            if params.get("WFContentItemLimitEnabled") is True:
                limit_number = params.get("WFContentItemLimitNumber")
                if limit_number is None or limit_number == "":
                    errors.append(
                        f"Find Health Samples limit is enabled but WFContentItemLimitNumber is missing at index {idx}"
                    )

        if ident == HEALTH_SAMPLE_DETAIL_ACTION:
            prop_name = params.get("WFContentItemPropertyName")
            if _token_param_is_empty(prop_name):
                errors.append(
                    f"Get Details of Health Sample missing WFContentItemPropertyName at index {idx}"
                )
            elif isinstance(prop_name, str) and prop_name not in HEALTH_SAMPLE_DETAIL_PROPERTIES:
                errors.append(
                    f"Get Details of Health Sample uses unknown detail '{prop_name}' at index {idx}"
                )

            health_input = params.get("WFInput")
            if _token_param_is_empty(health_input):
                errors.append(f"Get Details of Health Sample missing WFInput at index {idx}")
            elif not _input_is_attached(health_input):
                errors.append(
                    f"Get Details of Health Sample WFInput is not a token attachment at index {idx}"
                )
            elif not _input_has_reference(health_input):
                errors.append(
                    f"Get Details of Health Sample WFInput has no variable/output reference at index {idx}"
                )
            else:
                input_var_name = _extract_input_variable_name(health_input)
                if input_var_name:
                    if input_var_name not in health_sample_source_vars:
                        errors.append(
                            f"Get Details of Health Sample variable '{input_var_name}' does not resolve to Health Samples at index {idx}"
                        )
                for out_uuid in _input_action_output_uuids(health_input):
                    source_ident = uuid_to_ident.get(out_uuid)
                    if source_ident is None:
                        errors.append(
                            f"Get Details of Health Sample references unknown OutputUUID at index {idx}"
                        )
                    elif source_ident not in HEALTH_SAMPLE_SOURCE_ACTIONS:
                        errors.append(
                            f"Get Details of Health Sample should reference Find Health Samples/Log Health Sample output at index {idx}"
                        )

        if ident == HEALTH_LOG_SAMPLE_ACTION:
            sample_type = params.get("WFQuantitySampleType")
            if _token_param_is_empty(sample_type):
                errors.append(f"Log Health Sample missing WFQuantitySampleType at index {idx}")
            elif (
                isinstance(sample_type, str)
                and HEALTH_REFERENCE_SETS["sample_types"]
                and sample_type not in HEALTH_REFERENCE_SETS["sample_types"]
            ):
                errors.append(
                    f"Log Health Sample uses unknown WFQuantitySampleType '{sample_type}' at index {idx}"
                )

            has_quantity = "WFQuantitySampleQuantity" in params
            has_category = (
                "WFCategorySampleEnumeration" in params
                or "WFCategorySampleAdditionalEnumerationKey" in params
            )
            if not has_quantity and not has_category:
                errors.append(
                    f"Log Health Sample missing sample value: use WFQuantitySampleQuantity or WFCategorySampleEnumeration at index {idx}"
                )

            for key in HEALTH_QUANTITY_FIELD_KEYS:
                if key not in params:
                    continue
                require_magnitude = key in HEALTH_REQUIRED_MAIN_QUANTITY_KEYS
                if key == "WFQuantitySampleAdditionalQuantity":
                    # The bundled Caffeine XML example includes only Unit for
                    # the secondary quantity field, so Magnitude stays optional.
                    require_magnitude = False
                _validate_health_quantity_field(
                    params.get(key),
                    key=key,
                    idx=idx,
                    errors=errors,
                    require_magnitude=require_magnitude,
                )

            for key in (
                "WFCategorySampleEnumeration",
                "WFCategorySampleAdditionalEnumerationKey",
                "WFQuantitySampleAdditionalEnumeration",
            ):
                if key in params and _token_param_is_empty(params.get(key)):
                    errors.append(f"Log Health Sample {key} is empty at index {idx}")
                elif (
                    key in params
                    and isinstance(params.get(key), str)
                    and HEALTH_REFERENCE_SETS["category_values"]
                    and params.get(key) not in HEALTH_REFERENCE_SETS["category_values"]
                ):
                    errors.append(
                        f"Log Health Sample {key} uses unknown category value '{params.get(key)}' at index {idx}"
                    )

            for key in ("WFQuantitySampleDate", "WFSampleEndDate"):
                if key in params:
                    _validate_health_date_like(params.get(key), key=key, idx=idx, errors=errors)

        if ident == HEALTH_LOG_WORKOUT_ACTION:
            workout_type = params.get("WFWorkoutReadableActivityType")
            if _token_param_is_empty(workout_type):
                errors.append(f"Log Workout missing WFWorkoutReadableActivityType at index {idx}")
            elif (
                isinstance(workout_type, str)
                and HEALTH_REFERENCE_SETS["workouts"]
                and workout_type not in HEALTH_REFERENCE_SETS["workouts"]
            ):
                errors.append(
                    f"Log Workout uses unknown WFWorkoutReadableActivityType '{workout_type}' at index {idx}"
                )
            for key in ("WFWorkoutDate",):
                if key in params:
                    _validate_health_date_like(params.get(key), key=key, idx=idx, errors=errors)
            for key in ("WFWorkoutDuration", "WFWorkoutCaloriesQuantity", "WFWorkoutDistanceQuantity"):
                if key in params:
                    _validate_health_quantity_field(
                        params.get(key),
                        key=key,
                        idx=idx,
                        errors=errors,
                        require_magnitude=True,
                    )

        if ident == "is.workflow.actions.text.translate":
            if "WFInputText" not in params:
                if "WFInput" in params:
                    errors.append(
                        f"Translate Text should use WFInputText (not WFInput) at index {idx}"
                    )
                else:
                    errors.append(f"Translate Text missing WFInputText at index {idx}")
            lang = params.get("WFSelectedLanguage")
            if lang is None or lang == "":
                errors.append(f"Translate Text missing WFSelectedLanguage at index {idx}")
            elif _lang_value_is_code(lang):
                errors.append(
                    f"Translate Text WFSelectedLanguage should use display name (not code) at index {idx}"
                )

        if ident == "is.workflow.actions.ask":
            if "WFAskActionDefaultAnswer" in params:
                default = params.get("WFAskActionDefaultAnswer")
                if default is None or (isinstance(default, str) and default.strip() == ""):
                    errors.append(f"Ask for Input has empty default answer at index {idx}; omit WFAskActionDefaultAnswer")

        if ident == "is.workflow.actions.setvariable":
            wfinput = params.get("WFInput")
            if not wfinput:
                errors.append(f"Set Variable missing WFInput at index {idx}")
            elif not _input_is_attached(wfinput):
                errors.append(f"Set Variable WFInput is not a token attachment at index {idx}")

        if ident == "is.workflow.actions.sendmessage":
            # Mixed content should be sent via an appended variable list
            content = params.get("WFSendMessageContent")
            attachments = params.get("WFSendMessageAttachments")
            if not content and not attachments and not params.get("WFInput"):
                errors.append(f"Send Message missing content/attachments at index {idx}")
            if content and attachments:
                errors.append(
                    f"Send Message mixes content + attachments; use Append Variable list and pass single variable at index {idx}"
                )
            if isinstance(content, dict):
                name = _extract_input_variable_name(content)
                if name and append_counts.get(name, 0) < 2:
                    errors.append(
                        f"Send Message content variable '{name}' should be built with Append Variable (2+ items) at index {idx}"
                    )
                # Disallow ActionOutput attachments for Send Message content
                out_uuids = _input_action_output_uuids(content)
                if out_uuids:
                    errors.append(
                        f"Send Message content should reference a named variable (not ActionOutput) at index {idx}"
                    )
                # Require WFTextTokenString for variable content to avoid blank UI
                if content.get("WFSerializationType") == "WFTextTokenAttachment":
                    errors.append(
                        f"Send Message content should use WFTextTokenString with variable placeholder at index {idx}"
                    )

        if ident == "is.workflow.actions.sendemail":
            for key in (params or {}).keys():
                if key.startswith("WFSendMailAction"):
                    errors.append(
                        f"Send Email uses legacy SendMail parameter keys; use WFSendEmailAction* at index {idx}"
                    )

        if ident == "is.workflow.actions.file.rename":
            wf_file = params.get("WFFile")
            if _token_param_is_empty(wf_file):
                errors.append(f"Set Name missing WFFile at index {idx}")
            elif not _input_is_attached(wf_file):
                errors.append(f"Set Name WFFile is not a token attachment at index {idx}")
            elif not _input_has_reference(wf_file):
                errors.append(f"Set Name WFFile has no variable/output reference at index {idx}")
            else:
                for out_uuid in _input_action_output_uuids(wf_file):
                    if out_uuid not in uuid_to_ident:
                        errors.append(f"Set Name WFFile references unknown OutputUUID at index {idx}")

            if _token_param_is_empty(params.get("WFNewFilename")):
                errors.append(f"Set Name missing WFNewFilename at index {idx}")

        if ident == "is.workflow.actions.format.date":
            if not params.get("WFDate"):
                errors.append(f"Format Date missing WFDate at index {idx}")
            else:
                wfdate = params.get("WFDate")
                if not _input_is_editor_visible(wfdate):
                    errors.append(f"Format Date WFDate should use WFTextTokenString with placeholder at index {idx}")
            if params.get("WFDateFormat") == "Custom" and not params.get("WFDateFormatString"):
                errors.append(f"Format Date custom format is empty at index {idx}")
            if params.get("WFDateFormat") == "Custom" and params.get("WFDateFormatString"):
                if params.get("WFDateFormatStyle") != "Custom":
                    errors.append(f"Format Date custom style must be set to Custom at index {idx}")
            custom_name = params.get("CustomOutputName")
            enforce_custom_style = custom_name in {"Start Date", "End Date"}
            if params.get("WFDateFormat") == "Custom":
                fmt = params.get("WFDateFormatString", "")
                if enforce_custom_style:
                    if fmt and not allow_datetime_format and re.search(r"[HhmsZ]|'T'", fmt):
                        errors.append(
                            f"Custom date format includes time; use date-only or add ALLOW_DATETIME_FORMAT at index {idx}"
                        )
                    if "00:00:00" in fmt or "23:59:59" in fmt:
                        errors.append(
                            f"Custom date format hardcodes start/end of day; use date-only yyyy-MM-dd at index {idx}"
                        )

        # Heuristic: Start/End Date variables should use Custom format (API-friendly)
        if ident == "is.workflow.actions.setvariable":
            name = params.get("WFVariableName")
            if isinstance(name, str) and name.strip() and name in {"Start Date", "End Date"}:
                fmt_params = var_format_dates.get(name)
                if fmt_params is not None:
                    fmt_key = fmt_params.get("WFDateFormat")
                    fmt_str = fmt_params.get("WFDateFormatString", "")
                    # Accept Custom or a direct date-only format (e.g., yyyy-MM-dd)
                    effective = fmt_str if fmt_key == "Custom" else (fmt_key or fmt_str)
                    if not allow_datetime_format and isinstance(effective, str) and re.search(r"[HhmsZ]|'T'", effective):
                        errors.append(f"{name} should use date-only format (yyyy-MM-dd)")

        if ident == "is.workflow.actions.math":
            if not params.get("WFMathOperand"):
                errors.append(f"Math action missing WFMathOperand at index {idx}")
            elif not _math_operand_has_reference(params.get("WFMathOperand")):
                errors.append(f"Math operand is empty or unreferenced at index {idx}")
            # If the math input is a variable, ensure it exists
            wfinput = params.get("WFInput")
            var_name = _extract_input_variable_name(wfinput)
            if var_name and var_name not in defined_vars and var_name not in BUILTIN_VARIABLES:
                errors.append(f"Math input references undefined variable '{var_name}' at index {idx}")
            op = params.get("WFMathOperation")
            operand = params.get("WFMathOperand")
            is_100 = False
            if isinstance(operand, int) and operand == 100:
                is_100 = True
            elif isinstance(operand, dict):
                val = operand.get("Value")
                if isinstance(val, dict):
                    if isinstance(val.get("string"), str) and val.get("string").strip() == "100":
                        is_100 = True
            if op == "/" and is_100:
                divide_by_100_uuids.add(uuid)
                input_name = var_name
                if input_name is None and isinstance(wfinput, dict):
                    val = wfinput.get("Value")
                    if isinstance(val, dict) and val.get("Type") == "ActionOutput":
                        out_uuid = val.get("OutputUUID")
                        if out_uuid in uuid_to_var_name:
                            input_name = uuid_to_var_name[out_uuid]
                        else:
                            output_name = val.get("OutputName")
                            if isinstance(output_name, str):
                                input_name = output_name
                if input_name:
                    divide_by_100_vars.add(input_name)
            # If operating on cents with literal 100, must use divide
            input_name = var_name
            if input_name is None and isinstance(wfinput, dict):
                val = wfinput.get("Value")
                if isinstance(val, dict) and val.get("Type") == "ActionOutput":
                    out_uuid = val.get("OutputUUID")
                    if out_uuid in uuid_to_var_name:
                        input_name = uuid_to_var_name[out_uuid]
                    else:
                        output_name = val.get("OutputName")
                        if isinstance(output_name, str):
                            input_name = output_name
            if is_100 and input_name and "cents" in input_name.lower() and op not in {"/", "÷"}:
                errors.append(f"Math uses {op} with 100 on cents; must divide by 100 at index {idx}")
            if is_100 and cents_context_steps > 0 and op not in {"/", "÷"}:
                errors.append(f"Math uses {op} with 100 in cents context; must divide by 100 at index {idx}")

        if ident == "is.workflow.actions.round":
            wfinput = params.get("WFInput")
            if not wfinput:
                errors.append(f"Round Number missing WFInput at index {idx}")
            else:
                used_divide = False
                for out_uuid in _input_action_output_uuids(wfinput):
                    if out_uuid in divide_by_100_uuids:
                        used_divide = True
                        break
                if not used_divide:
                    var_name = _extract_input_variable_name(wfinput)
                    if var_name and "cents" in var_name.lower():
                        errors.append(f"Round used on cents without divide-by-100 at index {idx}")

        if ident == "is.workflow.actions.adjustdate":
            date_keys = ("WFDate", "WFInput")
            non_empty_date_refs: list[tuple[str, object]] = []
            for key in date_keys:
                if key not in params:
                    continue
                value = params.get(key)
                if _token_param_is_empty(value):
                    errors.append(f"Adjust Date has empty {key} at index {idx}")
                else:
                    non_empty_date_refs.append((key, value))

            if not non_empty_date_refs:
                errors.append(f"Adjust Date missing WFDate/WFInput at index {idx}")
            else:
                for key, reference in non_empty_date_refs:
                    if not _input_is_attached(reference):
                        errors.append(f"Adjust Date {key} is not a token attachment at index {idx}")
                        continue
                    if not _input_has_reference(reference):
                        errors.append(f"Adjust Date {key} has no variable/output reference at index {idx}")
                        continue
                    for out_uuid in _input_action_output_uuids(reference):
                        if out_uuid not in uuid_to_ident:
                            errors.append(f"Adjust Date {key} references unknown OutputUUID at index {idx}")

            has_offset_picker = "WFAdjustOffsetPicker" in params
            has_legacy_op = "WFAdjustOperation" in params
            has_legacy_duration = "WFDuration" in params
            if not has_legacy_duration:
                if has_offset_picker:
                    errors.append(
                        f"Adjust Date offset-picker-only payload is unreliable on iOS import; include WFDuration at index {idx}"
                    )
                else:
                    errors.append(f"Adjust Date missing WFDuration at index {idx}")
            if has_offset_picker:
                offset = params.get("WFAdjustOffsetPicker")
                if not isinstance(offset, dict) or offset.get("WFSerializationType") != "WFTimeOffsetValue":
                    errors.append(
                        f"Adjust Date WFAdjustOffsetPicker must be WFTimeOffsetValue at index {idx}"
                    )
            if has_legacy_op:
                op = params.get("WFAdjustOperation")
                if _token_param_is_empty(op):
                    errors.append(f"Adjust Date has empty WFAdjustOperation at index {idx}")
                elif isinstance(op, str) and op not in {"Add", "Subtract"}:
                    errors.append(f"Adjust Date WFAdjustOperation should be Add or Subtract at index {idx}")
            if has_legacy_duration:
                duration = params.get("WFDuration")
                if duration is None:
                    errors.append(f"Adjust Date missing WFDuration at index {idx}")
                elif not isinstance(duration, dict):
                    errors.append(f"Adjust Date WFDuration must be a dict at index {idx}")
                else:
                    if duration.get("WFSerializationType") != "WFQuantityFieldValue":
                        errors.append(
                            f"Adjust Date WFDuration must use WFQuantityFieldValue serialization at index {idx}"
                        )
                    dur_val = duration.get("Value")
                    if not isinstance(dur_val, dict):
                        errors.append(f"Adjust Date WFDuration missing Value dict at index {idx}")
                    else:
                        magnitude = dur_val.get("Magnitude")
                        unit = dur_val.get("Unit")
                        if magnitude is None or (isinstance(magnitude, str) and magnitude.strip() == ""):
                            errors.append(f"Adjust Date WFDuration missing Magnitude at index {idx}")
                        if not isinstance(unit, str) or unit.strip() == "":
                            errors.append(f"Adjust Date WFDuration missing Unit at index {idx}")
                        elif unit.strip().lower() not in DATE_DELTA_UNITS:
                            errors.append(f"Adjust Date WFDuration has unsupported Unit '{unit}' at index {idx}")

        if errors and first_error is None:
            first_error = (idx, ident or "UNKNOWN", _snippet(params))

        if cents_context_steps > 0:
            cents_context_steps -= 1

    # If cents variables exist but no divide-by-100 conversion is present, flag it
    for name in sorted(cents_vars):
        if name not in divide_by_100_vars:
            errors.append(f"Cents variable '{name}' is never divided by 100 (missing cents→dollars conversion)")
            if first_error is None:
                first_error = (0, "VALIDATION", "Missing cents→dollars conversion")

    return errors, first_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Shortcuts output for empty params and unknown actions")
    parser.add_argument("shortcut", help="Path to .xml or .shortcut file")
    args = parser.parse_args()

    shortcut_path = Path(args.shortcut).expanduser().resolve()
    if not shortcut_path.exists():
        print(f"File not found: {shortcut_path}", file=sys.stderr)
        return 1

    skill_dir = Path(__file__).resolve().parents[1]
    allowed_ids = load_allowed_ids(skill_dir)
    allowed_glyph_ids, allowed_icon_colors = load_icon_metadata(skill_dir)

    try:
        plist = load_plist(shortcut_path)
    except Exception as e:
        print(f"Failed to read plist: {e}", file=sys.stderr)
        return 1

    errors, first_error = validate(plist, allowed_ids, allowed_glyph_ids, allowed_icon_colors)

    # Repeating-hex UUID check (agent placeholder detection). Runs on the raw
    # file text so we catch UUIDs in WFWorkflowActionParameters.UUID,
    # OutputUUID references, GroupingIdentifier, and anywhere else a repeating
    # placeholder could hide. Deduplicated so we surface each offending UUID
    # once with a single remediation hint.
    try:
        raw_text = shortcut_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raw_text = ""
    repeating_uuids = sorted({
        match.group(0) for match in REPEATING_UUID_RE.finditer(raw_text)
    })
    if repeating_uuids:
        examples = ", ".join(repeating_uuids[:3])
        more = f" (+{len(repeating_uuids) - 3} more)" if len(repeating_uuids) > 3 else ""
        errors.append(
            f"Found {len(repeating_uuids)} repeating-hex placeholder UUID(s): {examples}{more}. "
            f"Every action UUID must be generated via `uuidgen | tr '[:lower:]' '[:upper:]'`, "
            f"not hand-picked sequences. Re-mint ALL offending UUIDs and update every "
            f"OutputUUID / GroupingIdentifier reference to match."
        )

    if errors:
        print("Validation failed:\n")
        if first_error:
            idx, ident, snippet = first_error
            print(f"First failing action: index {idx} ({ident})")
            print(f"Snippet: {snippet}\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
