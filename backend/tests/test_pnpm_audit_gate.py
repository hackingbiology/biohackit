"""Offline tests of the pnpm audit gate: every subprocess call is faked."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "audit" / "pnpm_audit_gate.py"
spec = importlib.util.spec_from_file_location("pnpm_audit_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def advisory(severity: str, patched: str) -> dict:
    return {
        "id": 1,
        "github_advisory_id": "GHSA-test-test-test",
        "module_name": "demo",
        "severity": severity,
        "patched_versions": patched,
        "findings": [{"version": "1.0.0", "paths": [". > demo@1.0.0"]}],
    }


def report(severity: str, patched: str) -> dict:
    return {"advisories": {"1": advisory(severity, patched)}}


def fake_run(rc: int = 0, stdout: str = "{}"):
    def run(cmd, **_kwargs):
        return subprocess.CompletedProcess(cmd, rc, stdout, "audit boom")

    return run


@pytest.fixture
def pnpm_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")


def test_fixable_high_advisory_exits_1(monkeypatch, pnpm_present, capsys):
    # scenario: dev-process::fixable-frontend-vulnerability-rejected
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        fake_run(rc=1, stdout=json.dumps(report("high", ">=1.1.0"))),
    )
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "demo 1.0.0 GHSA-test-test-test (high) -> >=1.1.0" in out


def test_fixable_critical_is_fixable_and_moderate_is_ignored():
    # scenario: dev-process::fixable-frontend-vulnerability-rejected
    assert gate.evaluate(report("critical", ">=2.0.0"))[0]
    assert gate.evaluate(report("moderate", ">=2.0.0")) == ([], [])


def test_missing_pnpm_exits_2(monkeypatch, capsys):
    # scenario: dev-process::frontend-audit-cannot-run
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    assert gate.main() == 2
    assert "cannot run" in capsys.readouterr().out


def test_non_json_output_exits_2(monkeypatch, pnpm_present):
    # scenario: dev-process::frontend-audit-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", fake_run(rc=1, stdout="not json"))
    assert gate.main() == 2


def test_audit_error_exits_2(monkeypatch, pnpm_present):
    # scenario: dev-process::frontend-audit-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", fake_run(rc=3))
    assert gate.main() == 2


def test_json_without_advisories_exits_2(monkeypatch, pnpm_present):
    # scenario: dev-process::frontend-audit-cannot-run
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        fake_run(rc=1, stdout=json.dumps({"error": {"code": "X"}})),
    )
    assert gate.main() == 2


@pytest.mark.parametrize(
    "advisories",
    [
        {"1": {"severity": "high"}},
        {"1": "not a dict"},
        {"1": {**advisory("high", ">=1"), "findings": [{"paths": []}]}},
    ],
)
def test_malformed_advisory_exits_2(monkeypatch, pnpm_present, advisories):
    # scenario: dev-process::frontend-audit-cannot-run
    out = json.dumps({"advisories": advisories})
    monkeypatch.setattr(gate.subprocess, "run", fake_run(rc=1, stdout=out))
    assert gate.main() == 2


def test_timeout_exits_2(monkeypatch, pnpm_present):
    # scenario: dev-process::frontend-audit-cannot-run
    def run(cmd, **_kwargs):
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr(gate.subprocess, "run", run)
    assert gate.main() == 2


def test_unfixed_advisory_is_reported_not_failed(monkeypatch, pnpm_present, capsys):
    # scenario: dev-process::unfixed-frontend-advisory-reported
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        fake_run(rc=1, stdout=json.dumps(report("high", "<0.0.0"))),
    )
    assert gate.main() == 0
    assert (
        "unfixed (not failing): demo 1.0.0 GHSA-test-test-test (high)"
        in capsys.readouterr().out
    )


def manifest_with(tmp_path, pnpm_section: dict):
    path = tmp_path / "package.json"
    path.write_text(json.dumps({"pnpm": pnpm_section}))
    return path


def test_audit_config_waiver_exits_1(monkeypatch, pnpm_present, tmp_path, capsys):
    # scenario: dev-process::frontend-audit-waiver-rejected
    monkeypatch.setattr(
        gate,
        "MANIFEST",
        manifest_with(tmp_path, {"auditConfig": {"ignoreGhsas": ["GHSA-x"]}}),
    )
    monkeypatch.setattr(
        gate.subprocess, "run", fake_run(rc=0, stdout=json.dumps({"advisories": {}}))
    )
    assert gate.main() == 1
    assert "pnpm.auditConfig.ignoreGhsas" in capsys.readouterr().out


def test_manifest_without_waiver_passes_and_unreadable_exits_2(
    monkeypatch, pnpm_present, tmp_path
):
    # scenario: dev-process::frontend-audit-waiver-rejected
    assert gate.find_waivers(manifest_with(tmp_path, {"overrides": {}})) == []
    monkeypatch.setattr(gate, "MANIFEST", tmp_path / "missing.json")
    assert gate.main() == 2


def test_repository_manifest_declares_no_waiver():
    # scenario: dev-process::frontend-audit-waiver-rejected
    assert gate.find_waivers() == []
