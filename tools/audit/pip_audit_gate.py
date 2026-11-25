"""Fail when a runtime dependency locked in backend/uv.lock has a fixable known vulnerability.

pip-audit runs in uv's isolated tool environment (`uvx`), never in backend/.venv, because the
licence gate scans every distribution of that venv. The audited input is `uv export` of the lock.
Exit codes: 0 clean, 1 fixable vulnerability, 2 the audit could not run (fail closed).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIP_AUDIT = "pip-audit==2.10.1"
LOCAL_BIN = Path.home() / ".local" / "bin"
PIP_AUDIT_VULNS_FOUND = 1


class GateError(Exception):
    """The audit could not run or its output could not be trusted."""


def find_tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    fallback = LOCAL_BIN / name
    if fallback.is_file():
        return str(fallback)
    raise GateError(f"{name} not found on PATH or in {LOCAL_BIN}")


def evaluate(report: dict) -> tuple[list[str], list[str]]:
    """Return (fixable, unfixed) vulnerability lines from a pip-audit JSON report."""
    fixable: list[str] = []
    unfixed: list[str] = []
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            head = f"{dep['name']} {dep['version']} {vuln['id']}"
            fixes = vuln.get("fix_versions") or []
            if fixes:
                fixable.append(f"{head} -> {', '.join(fixes)}")
            else:
                unfixed.append(head)
    return fixable, unfixed


def export_lock(uv: str, out: Path) -> None:
    cmd = [
        uv, "export", "--frozen", "--no-dev", "--no-emit-project",
        "--format", "requirements-txt", "--project", str(ROOT / "backend"),
        "--output-file", str(out),
    ]  # fmt: skip
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise GateError(f"uv export failed ({done.returncode}): {done.stderr.strip()}")


def run_audit(uvx: str, requirements: Path) -> dict:
    cmd = [
        uvx, PIP_AUDIT, "-r", str(requirements), "--no-deps", "--disable-pip",
        "-f", "json", "--progress-spinner", "off",
    ]  # fmt: skip
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode not in (0, PIP_AUDIT_VULNS_FOUND):
        raise GateError(f"pip-audit exited {done.returncode}: {done.stderr.strip()}")
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        raise GateError(f"pip-audit output is not JSON: {exc}") from exc
    if not isinstance(report, dict):
        raise GateError("pip-audit JSON is not an object")
    check_all_audited(report)
    return report


def check_all_audited(report: dict) -> None:
    """Fail closed when pip-audit skipped a dependency or returned no vulns verdict for it."""
    unaudited = [
        f"{dep.get('name', '?')} {dep.get('version', '?')}: "
        f"{dep.get('skip_reason', 'no vulns field in report')}"
        for dep in report.get("dependencies", [])
        if "skip_reason" in dep or "vulns" not in dep
    ]
    if unaudited:
        raise GateError("dependencies not audited: " + "; ".join(unaudited))


def main() -> int:
    try:
        uv, uvx = find_tool("uv"), find_tool("uvx")
        with tempfile.TemporaryDirectory() as tmp:
            requirements = Path(tmp) / "requirements.txt"
            export_lock(uv, requirements)
            report = run_audit(uvx, requirements)
    except GateError as exc:
        print(f"pip-audit gate cannot run: {exc}")
        return 2
    fixable, unfixed = evaluate(report)
    for line in unfixed:
        print(f"unfixed (not failing): {line}")
    if fixable:
        print("fixable vulnerabilities:")
        for line in fixable:
            print(f"  {line}")
        return 1
    print(
        f"pip-audit gate: {len(report.get('dependencies', []))} packages, no fixable vulnerability"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
