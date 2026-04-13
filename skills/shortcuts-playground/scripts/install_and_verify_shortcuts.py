#!/usr/bin/env python3
"""Sign, import, and verify a batch of generated shortcuts.

Workflow:
1) Sign each .shortcut with timeout/retries
2) Import via Shortcuts UI automation
3) Verify presence in shortcuts list
4) Validate installed payloads from Shortcuts.sqlite
"""

from __future__ import annotations

import argparse
import json
import plistlib
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any

from validate_shortcut import load_allowed_ids, load_icon_metadata, validate


IMPORT_SCRIPT = r'''
tell application "System Events"
  tell process "Shortcuts"
    set targetWindow to missing value
    repeat with w in windows
      try
        if (count (entire contents of w)) < 80 then
          set targetWindow to w
          exit repeat
        end if
      end try
    end repeat

    if targetWindow is missing value then
      return "NO_TARGET"
    end if

    set elems to entire contents of targetWindow
    if (count elems) < 5 then
      return "NO_IMPORT_BUTTON"
    end if
    click item 5 of elems
    delay 0.5

    try
      if (count sheets of targetWindow) > 0 then
        tell sheet 1 of targetWindow
          if (count buttons) >= 3 then
            click button 3
          else if (count buttons) >= 1 then
            click button 1
          end if
        end tell
      end if
    end try
    return "IMPORTED"
  end tell
end tell
'''


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str, str, bool]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout or "", p.stderr or "", False
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", e.stderr or "", True


def sign_shortcut(path: Path, retries: int, timeout_s: int) -> tuple[bool, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for n in range(1, retries + 1):
        rc, out, err, to = run(
            [
                "shortcuts",
                "sign",
                "--mode",
                "anyone",
                "--input",
                str(path),
                "--output",
                str(path),
            ],
            timeout=timeout_s,
        )
        attempts.append(
            {
                "attempt": n,
                "rc": rc,
                "timeout": to,
                "stdout_tail": out[-500:],
                "stderr_tail": err[-500:],
            }
        )
        if rc == 0:
            return True, attempts
        time.sleep(0.3)
    return False, attempts


def import_shortcut(path: Path, retries: int) -> tuple[bool, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for n in range(1, retries + 1):
        subprocess.run(["open", "-a", "Shortcuts", str(path)], capture_output=True, text=True)
        time.sleep(1.5)
        rc, out, err, to = run(["osascript", "-e", IMPORT_SCRIPT], timeout=20)
        status = (out.strip() or "").splitlines()[-1] if out.strip() else ""
        attempts.append(
            {
                "attempt": n,
                "rc": rc,
                "timeout": to,
                "status": status,
                "stdout_tail": out[-500:],
                "stderr_tail": err[-500:],
            }
        )
        if rc == 0 and status == "IMPORTED":
            time.sleep(0.5)
            return True, attempts
        time.sleep(0.5)
    return False, attempts


def list_shortcut_names() -> set[str]:
    rc, out, _, _ = run(["shortcuts", "list"], timeout=60)
    if rc != 0:
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


def installed_actions_for(shortcut_name: str) -> list[dict[str, Any]] | None:
    db = Path.home() / "Library/Shortcuts/Shortcuts.sqlite"
    con = sqlite3.connect(db)
    row = con.execute(
        "select a.ZDATA from ZSHORTCUT s join ZSHORTCUTACTIONS a on s.ZACTIONS=a.Z_PK where s.ZNAME=?",
        (shortcut_name,),
    ).fetchone()
    con.close()
    if not row:
        return None
    try:
        obj = plistlib.loads(row[0])
    except Exception:
        return None
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return obj.get("WFWorkflowActions", [])
    return None


def wrap_actions(name: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2700.0.4",
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 61440,
            "WFWorkflowIconStartColor": 431817727,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowName": name,
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install and verify batch shortcuts")
    parser.add_argument("--dir", required=True, help="Directory containing .shortcut files")
    parser.add_argument("--sign-retries", type=int, default=3)
    parser.add_argument("--import-retries", type=int, default=3)
    parser.add_argument("--sign-timeout", type=int, default=30)
    args = parser.parse_args()

    folder = Path(args.dir).expanduser().resolve()
    files = sorted(folder.glob("*.shortcut"))
    if not files:
        print(f"No .shortcut files found in {folder}")
        return 1

    run(["open", "-a", "Shortcuts"], timeout=20)
    time.sleep(2.0)

    results: list[dict[str, Any]] = []
    names = [f.stem for f in files]

    for idx, file_path in enumerate(files, start=1):
        name = file_path.stem
        row: dict[str, Any] = {
            "index": idx,
            "name": name,
            "path": str(file_path),
        }
        ok_sign, sign_attempts = sign_shortcut(file_path, args.sign_retries, args.sign_timeout)
        row["sign"] = {"ok": ok_sign, "attempts": sign_attempts}
        if not ok_sign:
            row["status"] = "failed-sign"
            results.append(row)
            continue

        ok_import, import_attempts = import_shortcut(file_path, args.import_retries)
        row["import"] = {"ok": ok_import, "attempts": import_attempts}
        if not ok_import:
            row["status"] = "failed-import"
            results.append(row)
            continue

        row["status"] = "imported"
        results.append(row)

    installed_names = list_shortcut_names()
    skill_dir = Path(__file__).resolve().parents[1]
    allowed_ids = load_allowed_ids(skill_dir)
    allowed_glyph_ids, allowed_icon_colors = load_icon_metadata(skill_dir)

    for row in results:
        name = row["name"]
        row["listed"] = name in installed_names
        actions = installed_actions_for(name)
        if actions is None:
            row["installed_validation"] = {
                "present": False,
                "valid": False,
                "errors": ["not found in Shortcuts.sqlite"],
            }
            continue
        wrapped = wrap_actions(name, actions)
        errors, _ = validate(wrapped, allowed_ids, allowed_glyph_ids, allowed_icon_colors)
        distinct = len(
            {
                a.get("WFWorkflowActionIdentifier")
                for a in actions
                if isinstance(a, dict) and a.get("WFWorkflowActionIdentifier") != "is.workflow.actions.comment"
            }
        )
        row["installed_validation"] = {
            "present": True,
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors[:20],
            "action_count": len(actions),
            "distinct_actions": distinct,
        }

    out_json = folder / "install_results.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    total = len(results)
    signed_ok = sum(1 for r in results if r.get("sign", {}).get("ok"))
    import_ok = sum(1 for r in results if r.get("import", {}).get("ok"))
    listed_ok = sum(1 for r in results if r.get("listed"))
    installed_valid = sum(
        1 for r in results if r.get("installed_validation", {}).get("valid")
    )
    failed = [r for r in results if not r.get("installed_validation", {}).get("valid")]

    summary = [
        "# Install Verification",
        "",
        f"- Batch directory: {folder}",
        f"- Total files: {total}",
        f"- Signed OK: {signed_ok}",
        f"- Imported OK: {import_ok}",
        f"- Present in shortcuts list: {listed_ok}",
        f"- Installed payloads valid (validator): {installed_valid}",
        "",
        f"- Results JSON: {out_json}",
    ]
    if failed:
        summary.append("")
        summary.append("## Failures")
        for row in failed[:20]:
            summary.append(f"- {row['name']}: {row.get('status')}")
            issues = row.get("installed_validation", {}).get("errors") or []
            for issue in issues[:3]:
                summary.append(f"  - {issue}")

    out_md = folder / "install_summary.md"
    out_md.write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"DIR={folder}")
    print(
        f"TOTAL={total} SIGNED_OK={signed_ok} IMPORT_OK={import_ok} "
        f"LISTED_OK={listed_ok} INSTALLED_VALID={installed_valid}"
    )
    print(f"RESULTS={out_json}")
    print(f"SUMMARY={out_md}")
    return 0 if installed_valid == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
