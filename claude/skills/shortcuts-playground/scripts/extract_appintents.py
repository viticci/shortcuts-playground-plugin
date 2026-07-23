#!/usr/bin/env python3
"""Extract parameter-level ground truth for installed third-party App Intents.

THIRD_PARTY_ACTIONS.md enumerates which third-party actions exist, but not how
to *call* them: the exact parameter keys, their types, and whether they are
required. Without that, the builder can name a third-party action but has to
guess its parameters — and a wrong parameter key silently produces a broken
action.

This reads the ground truth straight off the Mac. Every app that ships App
Intents bundles a declared schema at:

    <App>.app/Contents/Resources/Metadata.appintents/extract.actionsdata

which is JSON. This walks installed apps, reads that schema, and pairs it with
the app's bundle id (Info.plist) and Team ID (codesign) — the two values a
shortcut's ``AppIntentDescriptor`` needs. It works even for actions the user
has never placed in a shortcut, because it reads the *app*, not a backup.

The output is a JSON catalog keyed by the fully-qualified action identifier
(``<bundleId>.<IntentName>`` — the value that goes in
``WFWorkflowActionIdentifier``) so the builder can look up an action and encode
a correct call to it.

Local and read-only: it inspects apps already installed on this Mac, makes no
network calls, and writes nothing outside the path you pass to ``--out``.

Usage:
  python3 scripts/extract_appintents.py                 # print catalog to stdout
  python3 scripts/extract_appintents.py --out cat.json   # write catalog to a file
  python3 scripts/extract_appintents.py --app /Applications/PastePal.app
  python3 scripts/extract_appintents.py --dir /Applications --dir ~/Applications

Exit code:
  0 = at least one third-party action extracted (or --allow-empty)
  1 = no third-party App Intents found
  2 = bad arguments / unreadable input
"""

from __future__ import annotations

import argparse
import json
import plistlib
import subprocess
import sys
from pathlib import Path

# App Intents shipped by the OS itself are first-party and already covered by
# the toolkit snapshot; the value of this tool is the *third-party* long tail.
FIRST_PARTY_PREFIXES = ("com.apple.",)

DEFAULT_DIRS = ("/Applications", "/Applications/Utilities")


def _find_actionsdata(app: Path) -> Path | None:
    """Return the app's extract.actionsdata, if any.

    Most apps keep it at Contents/Resources/Metadata.appintents/, but wrapped
    iOS-on-Mac apps nest a second bundle (e.g. Foo.app/Wrapper/foo.app/...), so
    fall back to a bounded search rather than hard-coding one path.
    """
    direct = app / "Contents" / "Resources" / "Metadata.appintents" / "extract.actionsdata"
    if direct.is_file():
        return direct
    matches = list(app.glob("**/Metadata.appintents/extract.actionsdata"))
    return matches[0] if matches else None


def _bundle_id(app: Path) -> str | None:
    info = app / "Contents" / "Info.plist"
    if not info.is_file():
        found = list(app.glob("**/Info.plist"))
        if not found:
            return None
        info = found[0]
    try:
        with info.open("rb") as fh:
            return plistlib.load(fh).get("CFBundleIdentifier")
    except (plistlib.InvalidFileException, OSError):
        return None


def _app_name(app: Path) -> str:
    info = app / "Contents" / "Info.plist"
    if info.is_file():
        try:
            with info.open("rb") as fh:
                data = plistlib.load(fh)
            return data.get("CFBundleDisplayName") or data.get("CFBundleName") or app.stem
        except (plistlib.InvalidFileException, OSError):
            pass
    return app.stem


def _team_id(app: Path) -> str | None:
    """Read the Team ID from the code signature (needed by AppIntentDescriptor)."""
    try:
        out = subprocess.run(
            ["codesign", "-dv", str(app)],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    for line in (out.stderr + out.stdout).splitlines():
        if line.startswith("TeamIdentifier="):
            value = line.split("=", 1)[1].strip()
            return value if value and value != "not set" else None
    return None


def _friendly_type(value_type: dict) -> str:
    """Collapse a raw valueType dict into a short human-readable type tag."""
    if not isinstance(value_type, dict) or not value_type:
        return "unknown"
    kind, body = next(iter(value_type.items()), (None, None))
    if kind is None:
        return "unknown"
    wrapper = body.get("wrapper", {}) if isinstance(body, dict) else {}
    if kind == "primitive":
        # typeIdentifier 0 is the string primitive; others are numeric/bool/etc.
        return "string" if wrapper.get("typeIdentifier") == 0 else f"primitive:{wrapper.get('typeIdentifier')}"
    if kind == "intents":
        # IntentFile — e.g. an image or document parameter.
        return "file"
    if kind == "entity":
        return f"entity:{wrapper.get('typeName', '?')}"
    if kind == "array":
        member = wrapper.get("memberValueType", {})
        return f"array:{_friendly_type(member)}"
    return str(kind)


def _title(node: dict) -> str | None:
    title = node.get("title")
    if isinstance(title, dict):
        return title.get("key")
    return title if isinstance(title, str) else None


def _parameters(action: dict) -> list[dict]:
    params = []
    for prm in action.get("parameters", []) or []:
        if not isinstance(prm, dict):
            continue
        params.append(
            {
                "name": prm.get("name"),
                "title": _title(prm),
                "optional": bool(prm.get("isOptional", False)),
                "type": _friendly_type(prm.get("valueType", {})),
            }
        )
    return params


def extract_app(app: Path) -> dict:
    """Return {action_identifier: schema} for one .app, or {} if not applicable."""
    data_path = _find_actionsdata(app)
    if data_path is None:
        return {}
    bundle_id = _bundle_id(app)
    if not bundle_id or bundle_id.startswith(FIRST_PARTY_PREFIXES):
        return {}
    try:
        actions = json.loads(data_path.read_text()).get("actions", {})
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(actions, dict) or not actions:
        return {}

    team_id = _team_id(app)
    app_name = _app_name(app)
    out: dict[str, dict] = {}
    for intent_id, action in actions.items():
        if not isinstance(action, dict):
            continue
        # WFWorkflowActionIdentifier for a third-party App Intent is
        # "<bundleId>.<IntentName>" — the identifier the builder must emit.
        full_id = f"{bundle_id}.{intent_id}"
        desc = action.get("descriptionMetadata", {}) or {}
        title_node = desc.get("descriptionText", {})
        title = title_node.get("key") if isinstance(title_node, dict) else None
        out[full_id] = {
            "bundleId": bundle_id,
            "teamId": team_id,
            "appName": app_name,
            "intentId": intent_id,
            "title": title,
            "parameters": _parameters(action),
        }
    return out


def iter_apps(dirs: list[Path], explicit: list[Path]):
    seen: set[Path] = set()
    for app in explicit:
        if app not in seen:
            seen.add(app)
            yield app
    for root in dirs:
        if not root.is_dir():
            continue
        for app in sorted(root.glob("*.app")):
            if app not in seen:
                seen.add(app)
                yield app


def build_catalog(dirs: list[Path], explicit: list[Path]) -> dict:
    actions: dict[str, dict] = {}
    for app in iter_apps(dirs, explicit):
        actions.update(extract_app(app))
    return {
        "schema_version": 1,
        "generated_by": "extract-appintents",
        "action_count": len(actions),
        "actions": dict(sorted(actions.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract parameter-level ground truth for installed third-party App Intents.",
    )
    parser.add_argument("--out", type=Path, help="Write catalog JSON here instead of stdout.")
    parser.add_argument(
        "--dir",
        action="append",
        type=lambda s: Path(s).expanduser(),
        default=[],
        help="App directory to scan (repeatable). Defaults to /Applications.",
    )
    parser.add_argument(
        "--app",
        action="append",
        type=lambda s: Path(s).expanduser(),
        default=[],
        help="Scan a single .app (repeatable). Bypasses directory scanning.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Exit 0 even when no third-party App Intents are found.",
    )
    args = parser.parse_args(argv)

    dirs = args.dir or ([] if args.app else [Path(d) for d in DEFAULT_DIRS])
    catalog = build_catalog(dirs, args.app)

    text = json.dumps(catalog, indent=2, ensure_ascii=False)
    if args.out:
        try:
            args.out.write_text(text + "\n")
        except OSError as exc:
            print(f"extract-appintents: cannot write {args.out}: {exc}", file=sys.stderr)
            return 2
    else:
        print(text)

    if catalog["action_count"] == 0 and not args.allow_empty:
        print("extract-appintents: no third-party App Intents found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
