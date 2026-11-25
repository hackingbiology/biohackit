"""Fail when a production frontend dependency has a fixable high or critical vulnerability.

Runs `pnpm --dir frontend audit --prod --json` and reads the `advisories` object. There is no
ignore or waiver list: an advisory with a patched version must be fixed (upgrade or override).
A `pnpm.auditConfig` entry (ignoreCves, ignoreGhsas, ...) in frontend/package.json is a forbidden
waiver because pnpm would apply it before printing the report.
Exit codes: 0 clean, 1 fixable high/critical advisory or a waiver, 2 the audit could not run.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAILING_SEVERITIES = frozenset({"high", "critical"})
NO_PATCH = frozenset({"", "<0.0.0"})
PNPM_VULNS_FOUND = 1
TIMEOUT_SECONDS = 300
MANIFEST = ROOT / "frontend" / "package.json"


class GateError(Exception):
    """The audit could not run or its output could not be trusted."""


def find_pnpm() -> str:
    found = shutil.which("pnpm")
    if not found:
        raise GateError("pnpm not found on PATH")
    return found


def find_waivers(manifest: Path = MANIFEST) -> list[str]:
    """Return the waiver settings (`pnpm.auditConfig`) declared in the frontend manifest."""
    try:
        data = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read {manifest}: {exc}") from exc
    pnpm_config = data.get("pnpm") if isinstance(data, dict) else None
    audit_config = (
        pnpm_config.get("auditConfig") if isinstance(pnpm_config, dict) else None
    )
    if not audit_config:
        return []
    if not isinstance(audit_config, dict):
        return ["pnpm.auditConfig"]
    return [f"pnpm.auditConfig.{key}" for key in audit_config]


def advisory_line(advisory: dict) -> str:
    """Format one high/critical advisory, raising GateError when a required field is missing."""
    findings = advisory.get("findings")
    name = advisory.get("module_name")
    ident = advisory.get("github_advisory_id") or advisory.get("id")
    if not isinstance(name, str) or not ident or not isinstance(findings, list):
        raise GateError("pnpm audit advisory lacks module_name, id or findings")
    if not all(isinstance(f, dict) and "version" in f for f in findings):
        raise GateError(f"pnpm audit advisory for {name} has a finding without version")
    versions = sorted({str(f["version"]) for f in findings})
    return f"{name} {', '.join(versions)} {ident} ({advisory['severity']})"


def evaluate(report: dict) -> tuple[list[str], list[str]]:
    """Return (fixable, unfixed) high/critical advisory lines from a pnpm audit JSON report."""
    fixable: list[str] = []
    unfixed: list[str] = []
    for advisory in report["advisories"].values():
        if not isinstance(advisory, dict):
            raise GateError("pnpm audit advisory is not an object")
        if advisory.get("severity") not in FAILING_SEVERITIES:
            continue
        head = advisory_line(advisory)
        patched = str(advisory.get("patched_versions") or "").strip()
        if patched in NO_PATCH:
            unfixed.append(head)
        else:
            fixable.append(f"{head} -> {patched}")
    return fixable, unfixed


def run_audit(pnpm: str) -> dict:
    cmd = [pnpm, "--dir", str(ROOT / "frontend"), "audit", "--prod", "--json"]
    try:
        done = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"pnpm audit timed out after {TIMEOUT_SECONDS}s") from exc
    if done.returncode not in (0, PNPM_VULNS_FOUND):
        raise GateError(f"pnpm audit exited {done.returncode}: {done.stderr.strip()}")
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        raise GateError(f"pnpm audit output is not JSON: {exc}") from exc
    if not isinstance(report, dict) or not isinstance(report.get("advisories"), dict):
        raise GateError("pnpm audit JSON has no advisories object")
    return report


def main() -> int:
    try:
        waivers = find_waivers(MANIFEST)
        report = run_audit(find_pnpm())
        fixable, unfixed = evaluate(report)
    except GateError as exc:
        print(f"pnpm audit gate cannot run: {exc}")
        return 2
    if waivers:
        print("waivers are forbidden, remove: " + ", ".join(waivers))
        return 1
    for line in unfixed:
        print(f"unfixed (not failing): {line}")
    if fixable:
        print("fixable vulnerabilities:")
        for line in fixable:
            print(f"  {line}")
        return 1
    print(
        f"pnpm audit gate: {len(report['advisories'])} advisories, none fixable high/critical"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
