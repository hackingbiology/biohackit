"""Fail when an OpenSpec specification or change under openspec/ is structurally invalid.

The pinned OpenSpec CLI runs through `pnpm dlx` from the repo root, so frontend/package.json,
the lockfile and frontend/node_modules are never touched. Warnings (e.g. long requirement
text) do not fail the gate; errors do (the CLI marks such items `valid: false`).
Exit codes: 0 all valid, 1 invalid item, 2 the validator could not run (fail closed).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENSPEC = "@fission-ai/openspec@2.2.0"
TIMEOUT_SECONDS = 300
CLI_INVALID_FOUND = 1


class GateError(Exception):
    """The validator could not run or its output could not be trusted."""


def build_command(pnpm: str) -> list[str]:
    return [pnpm, "dlx", OPENSPEC, "validate", "--all", "--json", "--no-interactive"]


def run_validator(pnpm: str) -> dict:
    try:
        done = subprocess.run(
            build_command(pnpm),
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"openspec timed out after {TIMEOUT_SECONDS}s") from exc
    except OSError as exc:
        raise GateError(f"openspec could not start: {exc}") from exc
    if done.returncode not in (0, CLI_INVALID_FOUND):
        raise GateError(f"openspec exited {done.returncode}: {done.stderr.strip()}")
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        raise GateError(f"openspec output is not JSON: {exc}") from exc
    check_report(report)
    if done.returncode == CLI_INVALID_FOUND and not invalid_items(report):
        raise GateError("openspec exited 1 but its report lists no invalid item")
    return report


def check_report(report: object) -> None:
    if not isinstance(report, dict) or not isinstance(report.get("items"), list):
        raise GateError("openspec JSON has no items list")
    if not report["items"]:
        raise GateError("openspec reported no items to validate")
    if any(
        not isinstance(item, dict) or "valid" not in item for item in report["items"]
    ):
        raise GateError("openspec JSON item without a valid flag")


def invalid_items(report: dict) -> list[str]:
    """Return one line per invalid item followed by its issue messages."""
    lines: list[str] = []
    for item in report["items"]:
        if item["valid"]:
            continue
        lines.append(f"{item.get('type', '?')} {item.get('id', '?')}")
        for issue in item.get("issues", []):
            where = issue.get("path", "")
            if "line" in issue:
                where = f"{where}:{issue['line']}"
            lines.append(
                f"  {issue.get('level', '?')} {where}: {issue.get('message', '')}"
            )
    return lines


def main() -> int:
    pnpm = shutil.which("pnpm")
    try:
        if pnpm is None:
            raise GateError("pnpm not found on PATH")
        report = run_validator(pnpm)
    except GateError as exc:
        print(f"openspec validate gate cannot run: {exc}")
        return 2
    lines = invalid_items(report)
    if lines:
        print("invalid OpenSpec items:")
        for line in lines:
            print(f"  {line}")
        return 1
    print(f"openspec validate gate: {len(report['items'])} items valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
