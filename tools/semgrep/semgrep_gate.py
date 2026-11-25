"""Fail when semgrep reports an ERROR-severity finding in our own code.

A pinned semgrep CLI runs through `uvx` (an isolated tool environment), so it is never
installed into backend/.venv (scanned by the licence gate) or frontend/node_modules.
Scans: Semgrep Registry `p/django` on backend/ and `p/typescript` on frontend/src.
WARNING and INFO findings are printed but do not fail the gate.
Exit codes: 0 no ERROR finding, 1 ERROR finding, 2 the scan could not run (fail closed).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMGREP = "semgrep==1.187.0"
TIMEOUT_SECONDS = 900
# (registry ruleset, target directory, excluded path patterns, path prefix that must be scanned)
SCANS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("p/django", "backend", (".venv", "migrations", "__pycache__"), "backend/tests/"),
    ("p/typescript", "frontend/src", ("node_modules", ".next", "build"), "frontend/src/"),
)


class GateError(Exception):
    """The scan could not run or its output could not be trusted."""


def build_command(
    uvx: str, ruleset: str, target: str, excludes: tuple[str, ...]
) -> list[str]:
    command = [uvx, SEMGREP, "scan", "--config", ruleset, "--json", "--metrics=off"]
    command += ["--disable-version-check", "--quiet"]
    for pattern in excludes:
        command += ["--exclude", pattern]
    return [*command, target]


def run_scan(
    uvx: str, ruleset: str, target: str, excludes: tuple[str, ...], required: str
) -> dict:
    try:
        done = subprocess.run(
            build_command(uvx, ruleset, target, excludes),
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise GateError(
            f"{ruleset}: semgrep timed out after {TIMEOUT_SECONDS}s"
        ) from exc
    except OSError as exc:
        raise GateError(f"{ruleset}: semgrep could not start: {exc}") from exc
    if done.returncode != 0:
        raise GateError(
            f"{ruleset}: semgrep exited {done.returncode}: {done.stderr.strip()}"
        )
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        raise GateError(f"{ruleset}: semgrep output is not JSON: {exc}") from exc
    check_report(ruleset, report, required)
    return report


def check_report(ruleset: str, report: object, required: str) -> None:
    if not isinstance(report, dict) or not isinstance(report.get("results"), list):
        raise GateError(f"{ruleset}: semgrep JSON has no results list")
    errors = report.get("errors")
    if not isinstance(errors, list):
        raise GateError(f"{ruleset}: semgrep JSON has no errors list")
    if errors:
        # Any error (parse failure, timeout, rule load) may mean unscanned code: fail closed.
        messages = "; ".join(
            str(e.get("message", e)) if isinstance(e, dict) else str(e) for e in errors
        )
        raise GateError(f"{ruleset}: semgrep scan errors: {messages}")
    paths = report.get("paths")
    scanned = paths.get("scanned") if isinstance(paths, dict) else None
    if not isinstance(scanned, list):
        raise GateError(f"{ruleset}: semgrep JSON has no paths.scanned list")
    if not any(isinstance(p, str) and p.startswith(required) for p in scanned):
        raise GateError(f"{ruleset}: no file under {required} was scanned")
    print(f"semgrep {ruleset}: {len(scanned)} files scanned")


def describe(finding: dict) -> str:
    extra = finding.get("extra", {})
    where = f"{finding.get('path', '?')}:{finding.get('start', {}).get('line', '?')}"
    message = str(extra.get("message", "")).strip().splitlines()
    return f"{where} {finding.get('check_id', '?')} {message[0] if message else ''}".rstrip()


def severity(finding: dict) -> str:
    return str(finding.get("extra", {}).get("severity", "")).upper()


def main() -> int:
    uvx = shutil.which("uvx")
    failing: list[str] = []
    try:
        if uvx is None:
            raise GateError("uvx not found on PATH")
        for ruleset, target, excludes, required in SCANS:
            report = run_scan(uvx, ruleset, target, excludes, required)
            results = report["results"]
            print(f"semgrep {ruleset} on {target}: {len(results)} results")
            for finding in results:
                level = severity(finding)
                print(f"  {level} {describe(finding)}")
                if level == "ERROR":
                    failing.append(describe(finding))
    except GateError as exc:
        print(f"semgrep gate cannot run: {exc}")
        return 2
    if failing:
        print(f"semgrep gate: {len(failing)} ERROR finding(s)")
        return 1
    print("semgrep gate: no ERROR finding")
    return 0


if __name__ == "__main__":
    sys.exit(main())
