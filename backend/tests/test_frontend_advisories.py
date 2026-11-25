"""Offline check that the pinned `next` satisfies the advisories register."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs" / "security" / "frontend-advisories.md"
RECORDED = ROOT / "docs" / "security" / "recorded"
PACKAGE_JSON = ROOT / "frontend" / "package.json"
LOCKFILE = ROOT / "frontend" / "pnpm-lock.yaml"

Version = tuple[int, int, int]


def parse_version(text: str) -> Version:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", text)
    assert match, f"not a plain x.y.z version: {text!r}"
    return int(match[1]), int(match[2]), int(match[3])


def satisfies(version: str, patched_range: str) -> bool:
    """Support the `>=x.y.z` ranges that the audit output uses for patched versions."""
    match = re.fullmatch(r">=(\d+\.\d+\.\d+)", patched_range.strip())
    assert match, f"unsupported patched range: {patched_range!r}"
    return parse_version(version) >= parse_version(match[1])


def register_rows(text: str) -> dict[str, tuple[str, str]]:
    """GHSA id -> (severity, patched range) for every `next` row of the register."""
    rows = re.findall(
        r"^\|\s*(GHSA-[\w-]+)\s*\|\s*(\w+)\s*\|\s*next\s*\|\s*([^|]+?)\s*\|\s*$",
        text,
        re.MULTILINE,
    )
    return {ghsa: (sev, rng) for ghsa, sev, rng in rows}


def register_ranges(text: str) -> dict[str, str]:
    return {ghsa: rng for ghsa, (_, rng) in register_rows(text).items()}


def lockfile_next_versions(text: str) -> set[str]:
    return set(re.findall(r"^  next@(\d+\.\d+\.\d+):", text, re.MULTILINE))


def unpatched(version: str, ranges: dict[str, str]) -> list[str]:
    return [ghsa for ghsa, rng in ranges.items() if not satisfies(version, rng)]


def recorded_next_blocking(audit_text: str) -> dict[str, tuple[str, str]]:
    """High/critical `next` advisories in the recorded audit output."""
    advisories = json.loads(audit_text)["advisories"]
    return {
        a["github_advisory_id"]: (a["severity"], a["patched_versions"])
        for a in advisories
        if a["module_name"] == "next" and a["severity"] in ("high", "critical")
    }


def check(register_text: str, package_json_text: str, lockfile_text: str) -> list[str]:
    """List problems; empty means the pinned `next` is patched and package.json agrees."""
    ranges = register_ranges(register_text)
    if not ranges:
        return ["register lists no next advisory"]
    pin = json.loads(package_json_text)["dependencies"]["next"]
    resolved = lockfile_next_versions(lockfile_text)
    problems = []
    if resolved != {pin}:
        problems.append(
            f"package.json pins {pin} but lockfile resolves {sorted(resolved)}"
        )
    problems += [f"{pin} is vulnerable to {g}" for g in unpatched(pin, ranges)]
    return problems


def test_patched_framework_pinned() -> None:
    # scenario: dev-process::patched-framework-pinned
    problems = check(
        REGISTER.read_text(), PACKAGE_JSON.read_text(), LOCKFILE.read_text()
    )
    assert problems == []


def test_register_matches_recorded_audit() -> None:
    # scenario: dev-process::patched-framework-pinned
    recorded = recorded_next_blocking((RECORDED / "audit-before.json").read_text())
    assert register_rows(REGISTER.read_text()) == recorded
    after = json.loads((RECORDED / "audit-after.json").read_text())["advisories"]
    assert [a for a in after if a["module_name"] == "next"] == []


def test_pin_is_newest_recorded_release() -> None:
    # scenario: dev-process::patched-framework-pinned
    versions = json.loads((RECORDED / "next-versions.json").read_text())["versions"]
    pin = json.loads(PACKAGE_JSON.read_text())["dependencies"]["next"]
    assert pin == max(versions, key=parse_version)


def test_vulnerable_fixture_is_reported() -> None:
    # scenario: dev-process::patched-framework-pinned
    package_json = '{"dependencies": {"next": "15.1.0"}}'
    lockfile = "packages:\n\n  next@15.1.0:\n    resolution: {}\n"
    problems = check(REGISTER.read_text(), package_json, lockfile)
    assert "15.1.0 is vulnerable to GHSA-f82v-jwr5-mffw" in problems


def test_partially_patched_fixture_is_reported() -> None:
    # scenario: dev-process::patched-framework-pinned
    package_json = '{"dependencies": {"next": "15.5.27"}}'
    lockfile = "  next@15.5.27:\n    resolution: {}\n"
    problems = check(REGISTER.read_text(), package_json, lockfile)
    assert problems == [
        "15.5.27 is vulnerable to GHSA-2464-fhr4-w9xw",
        "15.5.27 is vulnerable to GHSA-p3m5-59mp-jv5r",
    ]


def test_pin_lockfile_mismatch_is_reported() -> None:
    # scenario: dev-process::patched-framework-pinned
    package_json = '{"dependencies": {"next": "15.5.29"}}'
    lockfile = "  next@15.5.28:\n    resolution: {}\n"
    problems = check(REGISTER.read_text(), package_json, lockfile)
    assert problems == ["package.json pins 15.5.29 but lockfile resolves ['15.5.28']"]


def test_unsupported_range_fails_loudly() -> None:
    with pytest.raises(AssertionError):
        satisfies("15.5.29", "<15.0.0")
