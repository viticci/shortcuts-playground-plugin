#!/usr/bin/env python3
"""Round-trip test for the third-party App Intents extractor.

Builds a throwaway .app on disk (Info.plist + a bundled fixture
extract.actionsdata) and asserts the extractor turns it into a correct
parameter-level schema. No network, no dependency on which apps happen to be
installed on the test machine.

Run:
  python3 tests/test_extract_appintents.py
"""

from __future__ import annotations

import plistlib
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import extract_appintents as ex  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "SampleApp.actionsdata"
BUNDLE_ID = "com.example.SampleApp"


def _build_fake_app(root: Path) -> Path:
    app = root / "SampleApp.app"
    resources = app / "Contents" / "Resources" / "Metadata.appintents"
    resources.mkdir(parents=True)
    shutil.copy(FIXTURE, resources / "extract.actionsdata")
    with (app / "Contents" / "Info.plist").open("wb") as fh:
        plistlib.dump(
            {"CFBundleIdentifier": BUNDLE_ID, "CFBundleName": "SampleApp"}, fh
        )
    return app


def test_extract_app() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        app = _build_fake_app(Path(tmp))
        catalog = ex.extract_app(app)

    action_id = f"{BUNDLE_ID}.AddItemIntent"
    assert action_id in catalog, f"missing {action_id}: {list(catalog)}"
    action = catalog[action_id]

    assert action["bundleId"] == BUNDLE_ID
    assert action["intentId"] == "AddItemIntent"
    assert action["title"] == "Add content"
    # Unsigned throwaway bundle has no Team ID; absence must be graceful, not a crash.
    assert action["teamId"] is None

    params = {p["name"]: p for p in action["parameters"]}
    assert set(params) == {"text", "imageFile", "folder"}, params
    assert params["text"]["optional"] is False, "text is a required parameter"
    assert params["text"]["type"] == "string"
    assert params["imageFile"]["optional"] is True
    assert params["imageFile"]["type"] == "file", "IntentFile must map to 'file'"
    assert params["folder"]["type"] == "entity:Folder"


def test_first_party_skipped() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        app = _build_fake_app(Path(tmp))
        # Re-stamp the bundle id as an Apple one; it must be excluded.
        with (app / "Contents" / "Info.plist").open("wb") as fh:
            plistlib.dump({"CFBundleIdentifier": "com.apple.Foo"}, fh)
        assert ex.extract_app(app) == {}, "first-party bundles must be skipped"


def _friendly_type_cases() -> None:
    assert ex._friendly_type({"primitive": {"wrapper": {"typeIdentifier": 0}}}) == "string"
    assert ex._friendly_type({"intents": {"wrapper": {"typeIdentifier": 12}}}) == "file"
    assert ex._friendly_type({"entity": {"wrapper": {"typeName": "Album"}}}) == "entity:Album"
    assert ex._friendly_type({}) == "unknown"


def main() -> int:
    test_extract_app()
    test_first_party_skipped()
    _friendly_type_cases()
    print("ok - extract_appintents round-trip, first-party skip, type mapping")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
