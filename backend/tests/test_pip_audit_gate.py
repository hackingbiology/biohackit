"""Offline tests of the pip-audit gate: every subprocess call is faked."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "audit" / "pip_audit_gate.py"
spec = importlib.util.spec_from_file_location("pip_audit_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def report(fix_versions: list[str]) -> dict:
    vuln = {
        "id": "PYSEC-0000-1",
        "fix_versions": fix_versions,
        "aliases": [],
        "description": "x",
    }
    return {
        "dependencies": [
            {"name": "demo", "version": "1.0", "vulns": [vuln]},
            {"name": "clean", "version": "2.0", "vulns": []},
        ],
        "fixes": [],
    }


def fake_run(export_rc: int = 0, audit_rc: int = 0, stdout: str = "{}"):
    def run(cmd, **_kwargs):
        if "export" in cmd:
            return subprocess.CompletedProcess(cmd, export_rc, "", "export boom")
        return subprocess.CompletedProcess(cmd, audit_rc, stdout, "audit boom")

    return run


@pytest.fixture
def tools_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")


def test_evaluate_splits_fixable_and_unfixed():
    # scenario: dev-process::fixable-backend-vulnerability-rejected
    fixable, unfixed = gate.evaluate(report(["1.1", "2.0"]))
    assert fixable == ["demo 1.0 PYSEC-0000-1 -> 1.1, 2.0"]
    assert unfixed == []


def test_fixable_vulnerability_exits_1(monkeypatch, tools_present, capsys):
    # scenario: dev-process::fixable-backend-vulnerability-rejected
    monkeypatch.setattr(
        gate.subprocess, "run", fake_run(audit_rc=1, stdout=json.dumps(report(["1.1"])))
    )
    assert gate.main() == 1
    assert "demo 1.0 PYSEC-0000-1 -> 1.1" in capsys.readouterr().out


def test_unfixed_vulnerability_is_reported_not_failing(
    monkeypatch, tools_present, capsys
):
    # scenario: dev-process::unfixed-backend-advisory-reported
    monkeypatch.setattr(
        gate.subprocess, "run", fake_run(audit_rc=1, stdout=json.dumps(report([])))
    )
    assert gate.main() == 0
    assert "unfixed (not failing): demo 1.0 PYSEC-0000-1" in capsys.readouterr().out


def test_clean_report_exits_0(monkeypatch, tools_present, capsys):
    # scenario: dev-process::unfixed-backend-advisory-reported
    clean = {
        "dependencies": [{"name": "clean", "version": "2.0", "vulns": []}],
        "fixes": [],
    }
    monkeypatch.setattr(gate.subprocess, "run", fake_run(stdout=json.dumps(clean)))
    assert gate.main() == 0
    assert "1 packages, no fixable vulnerability" in capsys.readouterr().out


def test_missing_uv_exits_2(monkeypatch, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    monkeypatch.setattr(gate, "LOCAL_BIN", Path("/nonexistent-bin"))
    assert gate.main() == 2
    assert "pip-audit gate cannot run: uv not found" in capsys.readouterr().out


def test_missing_uvx_exits_2(monkeypatch, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(
        gate.shutil, "which", lambda name: "/bin/uv" if name == "uv" else None
    )
    monkeypatch.setattr(gate, "LOCAL_BIN", Path("/nonexistent-bin"))
    assert gate.main() == 2
    assert "uvx not found" in capsys.readouterr().out


def test_export_failure_exits_2(monkeypatch, tools_present, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", fake_run(export_rc=1))
    assert gate.main() == 2
    assert "uv export failed" in capsys.readouterr().out


def test_non_json_output_exits_2(monkeypatch, tools_present, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", fake_run(stdout="not json"))
    assert gate.main() == 2
    assert "not JSON" in capsys.readouterr().out


def test_unexpected_exit_code_exits_2(monkeypatch, tools_present, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(
        gate.subprocess, "run", fake_run(audit_rc=3, stdout=json.dumps(report([])))
    )
    assert gate.main() == 2
    assert "pip-audit exited 3" in capsys.readouterr().out


def test_non_object_json_exits_2(monkeypatch, tools_present, capsys):
    # scenario: dev-process::backend-audit-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", fake_run(stdout="[]"))
    assert gate.main() == 2
    assert "not an object" in capsys.readouterr().out


@pytest.mark.parametrize(
    "dep",
    [
        {"name": "x", "skip_reason": "not on PyPI"},
        {"name": "x", "version": "1.0"},
        {"name": "x", "version": "1.0", "skip_reason": "no hash", "vulns": []},
    ],
)
def test_skipped_dependency_exits_2(monkeypatch, tools_present, capsys, dep):
    # scenario: dev-process::backend-audit-cannot-run
    body = json.dumps({"dependencies": [dep], "fixes": []})
    monkeypatch.setattr(gate.subprocess, "run", fake_run(stdout=body))
    assert gate.main() == 2
    assert "dependencies not audited: x" in capsys.readouterr().out


def test_find_tool_uses_local_bin_fallback(monkeypatch, tmp_path):
    # scenario: dev-process::backend-audit-cannot-run
    (tmp_path / "uv").write_text("")
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    monkeypatch.setattr(gate, "LOCAL_BIN", tmp_path)
    assert gate.find_tool("uv") == str(tmp_path / "uv")
