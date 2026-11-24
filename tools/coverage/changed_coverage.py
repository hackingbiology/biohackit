"""Fail when a changed backend source file has less than 90% line coverage.

Changed files come from `git diff` against BASE (added, modified, renamed; deletions are skipped).
Tests, migrations, manage.py and conftest.py are excluded. Coverage runs only when files remain.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
THRESHOLD = 90.0


def _is_checked(path: str) -> bool:
    p = PurePosixPath(path)
    if p.suffix != ".py" or p.parts[:1] != ("backend",):
        return False
    if p.name in {"manage.py", "conftest.py"}:
        return False
    return not {"tests", "migrations"} & set(p.parts)


def changed_files(base: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AMR", f"{base}...HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.splitlines() if _is_checked(line)]


def evaluate(
    report: dict[str, Any], files: list[str], threshold: float = THRESHOLD
) -> list[tuple[str, float]]:
    """Return (repo path, percent) for each file below the threshold; a missing file counts as 0.0."""
    covered = report.get("files", {})
    failing: list[tuple[str, float]] = []
    for path in files:
        key = str(PurePosixPath(path).relative_to("backend"))
        entry = covered.get(key)
        percent = float(entry["summary"]["percent_covered"]) if entry else 0.0
        if percent < threshold:
            failing.append((path, percent))
    return failing


def _run(args: list[str]) -> int:
    return subprocess.run(args, cwd=BACKEND, check=False).returncode


def main(argv: list[str]) -> int:
    base = argv[1] if len(argv) > 1 else "origin/main"
    files = changed_files(base)
    if not files:
        print("changed-file coverage: no changed backend source files to check")
        return 0
    if (
        _run(
            [
                ".venv/bin/coverage",
                "run",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
            ]
        )
        != 0
    ):
        print("changed-file coverage: backend test run failed")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "coverage.json"
        if _run([".venv/bin/coverage", "json", "-o", str(out)]) != 0:
            print("changed-file coverage: coverage json failed")
            return 1
        report = json.loads(out.read_text())
    failing = dict(evaluate(report, files))
    for path in files:
        if path in failing:
            print(f"FAIL {path}: {failing[path]:.1f}% < {THRESHOLD:.0f}%")
        else:
            print(f"ok   {path}")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
