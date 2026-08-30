#!/usr/bin/env python3
"""Generate the bundled HealthKit reference used by the validator tests.

The plist syntax for Shortcuts Health actions comes from anonymized iOS
Shortcuts XML examples captured while building this reference. This script
supplements that with the installed iPhoneOS SDK so the test suite can cover
every HealthKit type/value family available on the generator machine.
"""

from __future__ import annotations

import json
import plistlib
import re
import subprocess
from datetime import date
from pathlib import Path


TYPE_PREFIXES = {
    "HKQuantityTypeIdentifier": "quantity_types",
    "HKCategoryTypeIdentifier": "category_types",
    "HKCharacteristicTypeIdentifier": "characteristic_types",
    "HKCorrelationTypeIdentifier": "correlation_types",
    "HKDocumentTypeIdentifier": "document_types",
}

LABEL_OVERRIDES = {
    "ActiveEnergyBurned": "Active Calories",
    "DietaryCaffeine": "Caffeine",
    "DistanceWalkingRunning": "Walking + Running Distance",
    "FlightsClimbed": "Flights Climbed",
    "GeneralizedBodyAche": "Body and Muscle Ache",
    "StepCount": "Step Count",
    "VO2Max": "VO2 Max",
}

OBSERVED_SHORTCUTS_LABELS = {
    "HKCategoryTypeIdentifierBloating": ["Bloating"],
    "HKCategoryTypeIdentifierCervicalMucusQuality": ["Cervical Mucus Quality"],
    "HKCategoryTypeIdentifierGeneralizedBodyAche": ["Body and Muscle Ache"],
    "HKQuantityTypeIdentifierActiveEnergyBurned": ["Active Calories"],
    "HKQuantityTypeIdentifierBodyMassIndex": ["Body Mass Index"],
    "HKQuantityTypeIdentifierDietaryCaffeine": ["Caffeine"],
    "HKQuantityTypeIdentifierDistanceWalkingRunning": ["Walking + Running Distance"],
    "HKQuantityTypeIdentifierFlightsClimbed": ["Flights Climbed"],
    "HKQuantityTypeIdentifierStepCount": ["Step Count"],
}

OBSERVED_FIND_SAMPLES_LABELS = {
    "HKCategoryTypeIdentifierSleepAnalysis": ["Sleep"],
    "HKQuantityTypeIdentifierActiveEnergyBurned": ["Active Calories"],
    "HKQuantityTypeIdentifierAppleExerciseTime": ["Exercise Minutes"],
    "HKQuantityTypeIdentifierStepCount": ["Steps"],
}

ACTIONKIT_HEALTH_CONSTANTS = Path(
    "/System/Library/PrivateFrameworks/ActionKit.framework/Versions/A/Resources/"
    "WFHealthKitConstants.plist"
)

SAMPLE_DETAIL_PROPERTIES = [
    "Type",
    "Value",
    "Unit",
    "Start Date",
    "End Date",
    "Duration",
    "Source",
    "Name",
]

BUNDLED_XML_EVIDENCE = [
    {
        "evidence_id": "find_health_samples_quantity_filter",
        "coverage": [
            "is.workflow.actions.filter.health.quantity",
            "WFContentItemFilter",
            "Type filter row",
            "WFContentItemLimitEnabled",
        ],
    },
    {
        "evidence_id": "log_health_sample_category_without_visible_value",
        "coverage": [
            "is.workflow.actions.health.quantity.log",
            "category type with no visible value row",
            "WFQuantitySampleType",
            "WFQuantitySampleQuantity",
            "WFQuantitySampleAdditionalQuantity",
        ],
        "observed_parameters": {
            "WFQuantitySampleType": "Bloating",
            "WFQuantitySampleQuantity": "WFQuantityFieldValue retained even when the editor hides Value",
            "WFQuantitySampleAdditionalQuantity": "WFQuantityFieldValue with Unit only",
        },
    },
    {
        "evidence_id": "log_health_sample_category_with_enum_value",
        "coverage": [
            "is.workflow.actions.health.quantity.log",
            "category value picker",
            "WFCategorySampleEnumeration",
            "WFQuantitySampleQuantity",
            "WFQuantitySampleAdditionalQuantity",
        ],
        "observed_parameters": {
            "WFQuantitySampleType": "Cervical Mucus Quality",
            "WFCategorySampleEnumeration": "Dry",
            "WFQuantitySampleQuantity": "WFQuantityFieldValue with Magnitude + Unit",
            "WFQuantitySampleAdditionalQuantity": "WFQuantityFieldValue with Unit only",
        },
    },
    {
        "evidence_id": "log_workout_identifier_only",
        "coverage": ["is.workflow.actions.health.workout.log"],
        "note": "Exported before workout permission/configuration was granted; UUID-only shape is not enough for generated shortcuts.",
    },
    {
        "evidence_id": "get_details_of_health_sample",
        "coverage": [
            "is.workflow.actions.properties.health.quantity",
            "WFContentItemPropertyName",
            "WFInput",
        ],
    },
]

BUNDLED_OBSERVED_SHAPES = [
    {
        "evidence_id": "log_health_sample_quantity",
        "note": (
            "An anonymized iOS XML example established this quantity schema; "
            "the preserved reference keeps only the parameter shape, not the "
            "user's source path."
        ),
        "observed_parameters": {
            "WFQuantitySampleType": "Caffeine",
            "WFQuantitySampleQuantity": "WFQuantityFieldValue with Magnitude + Unit",
            "WFQuantitySampleAdditionalQuantity": "WFQuantityFieldValue with Unit only",
        },
    }
]


def sdk_path() -> Path:
    raw = subprocess.check_output(["xcrun", "--sdk", "iphoneos", "--show-sdk-path"], text=True)
    return Path(raw.strip())


def actionkit_units() -> list[dict[str, object]]:
    if not ACTIONKIT_HEALTH_CONSTANTS.exists():
        return []
    try:
        with ACTIONKIT_HEALTH_CONSTANTS.open("rb") as handle:
            payload = plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException):
        return []
    units = payload.get("Units")
    if not isinstance(units, list):
        return []
    out: list[dict[str, object]] = []
    for row in units:
        if not isinstance(row, dict):
            continue
        unit_string = row.get("unitString")
        if not isinstance(unit_string, str) or unit_string == "":
            continue
        out.append(
            {
                "unit": unit_string,
                "group": row.get("group"),
                "important": bool(row.get("important", False)),
            }
        )
    return out


def split_camel(name: str) -> str:
    if name in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[name]
    working = name
    if working.startswith("Dietary") and len(working) > len("Dietary"):
        working = working[len("Dietary") :]
    working = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", working)
    working = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", working)
    working = working.replace(" VO 2 ", " VO2 ")
    working = working.replace(" S D N N", " SDNN")
    return working.strip()


def parse_types(header: Path) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {bucket: [] for bucket in TYPE_PREFIXES.values()}
    line_re = re.compile(
        r"HK_EXTERN\s+"
        r"(?P<prefix>HK(?:Quantity|Category|Characteristic|Correlation|Document)TypeIdentifier)"
        r"\s+const\s+"
        r"(?P<symbol>HK(?:Quantity|Category|Characteristic|Correlation|Document)TypeIdentifier(?P<suffix>[A-Za-z0-9]+))"
        r"\s+(?P<availability>.*?);\s*(?://\s*(?P<comment>.*))?$"
    )
    for raw_line in header.read_text(encoding="utf-8").splitlines():
        match = line_re.search(raw_line)
        if not match:
            continue
        bucket = TYPE_PREFIXES[match.group("prefix")]
        suffix = match.group("suffix")
        symbol = match.group("symbol")
        row = {
            "symbol": symbol,
            "sdk_suffix": suffix,
            "shortcut_label_guess": split_camel(suffix),
            "availability": match.group("availability").strip(),
            "unit_and_aggregation": (match.group("comment") or "").strip(),
        }
        if symbol in OBSERVED_SHORTCUTS_LABELS:
            row["observed_shortcuts_labels"] = OBSERVED_SHORTCUTS_LABELS[symbol]
        if symbol in OBSERVED_FIND_SAMPLES_LABELS:
            row["observed_find_samples_labels"] = OBSERVED_FIND_SAMPLES_LABELS[symbol]
        out[bucket].append(row)
    return out


def value_label(enum_name: str, constant: str) -> str:
    suffix = constant
    if constant.startswith(enum_name):
        suffix = constant[len(enum_name) :]
    elif constant.startswith("HKCategoryValue"):
        suffix = constant[len("HKCategoryValue") :]
    return split_camel(suffix)


def parse_category_values(header: Path) -> dict[str, list[dict[str, object]]]:
    text = header.read_text(encoding="utf-8")
    enum_re = re.compile(
        r"typedef NS_ENUM\(NSInteger,\s*(?P<enum>HKCategoryValue[A-Za-z0-9]+)\)\s*\{(?P<body>.*?)\}",
        re.S,
    )
    out: dict[str, list[dict[str, object]]] = {}
    for enum_match in enum_re.finditer(text):
        enum_name = enum_match.group("enum")
        values: list[dict[str, object]] = []
        previous_int: int | None = None
        for raw_line in enum_match.group("body").splitlines():
            line = raw_line.strip()
            if not line.startswith("HKCategoryValue"):
                continue
            const = line.split(None, 1)[0].rstrip(",")
            expr = None
            if "=" in line:
                expr = line.rsplit("=", 1)[1].split(",", 1)[0].strip()
            if expr is None:
                raw_value: int | str | None = previous_int + 1 if previous_int is not None else None
            else:
                try:
                    raw_value = int(expr, 0)
                    previous_int = raw_value
                except ValueError:
                    raw_value = expr
            if isinstance(raw_value, int):
                previous_int = raw_value
            values.append(
                {
                    "symbol": const,
                    "shortcut_label_guess": value_label(enum_name, const),
                    "value": raw_value,
                }
            )
        out[enum_name] = values
    return out


def parse_workout_activity_types(header: Path) -> list[dict[str, object]]:
    text = header.read_text(encoding="utf-8")
    match = re.search(
        r"typedef NS_ENUM\(NSUInteger,\s*HKWorkoutActivityType\)\s*\{(?P<body>.*?)\}",
        text,
        re.S,
    )
    if not match:
        return []
    values: list[dict[str, object]] = []
    previous_int: int | None = None
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line.startswith("HKWorkoutActivityType"):
            continue
        const = line.split(None, 1)[0].rstrip(",")
        suffix = const[len("HKWorkoutActivityType") :]
        expr = None
        if "=" in line:
            expr = line.rsplit("=", 1)[1].split(",", 1)[0].strip()
        if expr is None:
            raw_value: int | str | None = previous_int + 1 if previous_int is not None else None
        else:
            try:
                raw_value = int(expr, 0)
                previous_int = raw_value
            except ValueError:
                raw_value = expr
        if isinstance(raw_value, int):
            previous_int = raw_value
        values.append(
            {
                "symbol": const,
                "shortcut_label_guess": split_camel(suffix),
                "value": raw_value,
            }
        )
    return values


def quantity_unit_hints(quantity_types: list[dict[str, object]]) -> list[str]:
    out: set[str] = set()
    for row in quantity_types:
        raw = str(row.get("unit_and_aggregation") or "").split(",", 1)[0].strip()
        if raw:
            out.add(raw)
    return sorted(out)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sdk = sdk_path()
    headers = sdk / "System/Library/Frameworks/HealthKit.framework/Headers"
    types = parse_types(headers / "HKTypeIdentifiers.h")
    category_values = parse_category_values(headers / "HKCategoryValues.h")
    workouts = parse_workout_activity_types(headers / "HKWorkout.h")
    units = actionkit_units()

    payload = {
        "generated_on": date.today().isoformat(),
        "source": {
            "sdk_path": str(sdk),
            "headers": [
                "HealthKit/HKTypeIdentifiers.h",
                "HealthKit/HKCategoryValues.h",
                "HealthKit/HKWorkout.h",
            ],
            "shortcut_xml_syntax_source": (
                "Anonymized iOS Shortcuts XML examples captured while building "
                "this reference; user-specific source paths are intentionally omitted."
            ),
        },
        "bundled_xml_evidence": BUNDLED_XML_EVIDENCE,
        "bundled_observed_shapes": BUNDLED_OBSERVED_SHAPES,
        "shortcuts_actions": {
            "find_health_samples": {
                "identifier": "is.workflow.actions.filter.health.quantity",
                "sample_output_name": "Health Samples",
                "required_parameters": ["WFContentItemFilter"],
            },
            "get_health_sample_detail": {
                "identifier": "is.workflow.actions.properties.health.quantity",
                "required_parameters": ["WFInput", "WFContentItemPropertyName"],
                "properties": SAMPLE_DETAIL_PROPERTIES,
            },
            "log_health_sample": {
                "identifier": "is.workflow.actions.health.quantity.log",
                "required_parameters": ["WFQuantitySampleType"],
                "quantity_parameters": [
                    "WFQuantitySampleQuantity",
                    "WFQuantitySampleAdditionalQuantity",
                ],
                "category_parameters": [
                    "WFCategorySampleEnumeration",
                    "WFCategorySampleAdditionalEnumerationKey",
                    "WFQuantitySampleAdditionalEnumeration",
                ],
                "date_parameters": ["WFQuantitySampleDate", "WFSampleEndDate"],
            },
            "log_workout": {
                "identifier": "is.workflow.actions.health.workout.log",
                "required_parameters": ["WFWorkoutReadableActivityType"],
                "quantity_parameters": [
                    "WFWorkoutDuration",
                    "WFWorkoutCaloriesQuantity",
                    "WFWorkoutDistanceQuantity",
                ],
                "date_parameters": ["WFWorkoutDate"],
            },
        },
        **types,
        "quantity_units": units,
        "quantity_unit_hints": quantity_unit_hints(types.get("quantity_types", [])),
        "category_values": category_values,
        "workout_activity_types": workouts,
    }
    out_path = root / "data/healthkit-ios26.2-reference.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
