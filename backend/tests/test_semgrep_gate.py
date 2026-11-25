"""Offline tests of the semgrep gate: every subprocess call is faked."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "semgrep" / "semgrep_gate.py"
spec = importlib.util.spec_from_file_location("semgrep_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def finding(level: str) -> dict:
    return {
        "check_id": "rule.x",
        "path": "backend/a.py",
        "start": {"line": 7},
        "extra": {"severity": level, "message": "bad thing\nmore"},
    }


def report(
    *levels: str, errors: list | None = None, scanned: list | None = None
) -> str:
    files = ["backend/tests/t.py", "frontend/src/a.ts"] if scanned is None else scanned
    return json.dumps(
        {
            "results": [finding(lv) for lv in levels],
            "errors": errors or [],
            "paths": {"scanned": files},
        }
    )


class FakeRun:
    def __init__(
        self, rc: int = 0, stdout: str = "{}", error: Exception | None = None
    ) -> None:
        self.rc = rc
        self.stdout = stdout
        self.error = error
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        if self.error:
            raise self.error
        return subprocess.CompletedProcess(cmd, self.rc, self.stdout, "boom")


@pytest.fixture
def uvx_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")


def run_main(monkeypatch, fake: FakeRun) -> int:
    monkeypatch.setattr(gate.subprocess, "run", fake)
    return gate.main()


def test_error_finding_fails(monkeypatch, uvx_present, capsys):
    assert run_main(monkeypatch, FakeRun(0, report("ERROR"))) == 1
    out = capsys.readouterr().out
    assert "backend/a.py:7 rule.x bad thing" in out


def test_warning_and_info_pass(monkeypatch, uvx_present, capsys):
    assert run_main(monkeypatch, FakeRun(0, report("WARNING", "INFO"))) == 0
    assert "WARNING backend/a.py:7" in capsys.readouterr().out


def test_empty_results_pass(monkeypatch, uvx_present, capsys):
    assert run_main(monkeypatch, FakeRun(0, report())) == 0
    assert "p/django on backend: 0 results" in capsys.readouterr().out


def test_uvx_missing_fails_closed(monkeypatch, capsys):
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    assert gate.main() == 2
    assert "uvx not found" in capsys.readouterr().out


def test_non_json_fails_closed(monkeypatch, uvx_present):
    assert run_main(monkeypatch, FakeRun(0, "not json")) == 2


def test_scan_errors_fail_closed(monkeypatch, uvx_present, capsys):
    errors = [{"level": "error", "message": "rules failed to load"}]
    assert run_main(monkeypatch, FakeRun(0, report(errors=errors))) == 2
    assert "rules failed to load" in capsys.readouterr().out


def test_warn_level_errors_fail_closed(monkeypatch, uvx_present, capsys):
    errors = [{"level": "warn", "message": "partial parse"}]
    assert run_main(monkeypatch, FakeRun(0, report(errors=errors))) == 2
    assert "partial parse" in capsys.readouterr().out


def test_required_path_not_scanned_fails_closed(monkeypatch, uvx_present, capsys):
    only_src = report(scanned=["backend/app/x.py", "frontend/src/a.ts"])
    assert run_main(monkeypatch, FakeRun(0, only_src)) == 2
    assert "backend/tests/" in capsys.readouterr().out


def test_missing_paths_fails_closed(monkeypatch, uvx_present):
    bare = json.dumps({"results": [], "errors": []})
    assert run_main(monkeypatch, FakeRun(0, bare)) == 2


def test_missing_results_fails_closed(monkeypatch, uvx_present):
    assert run_main(monkeypatch, FakeRun(0, json.dumps({"errors": []}))) == 2


def test_nonzero_exit_fails_closed(monkeypatch, uvx_present):
    assert run_main(monkeypatch, FakeRun(2, report())) == 2


def test_timeout_and_oserror_fail_closed(monkeypatch, uvx_present):
    timeout = subprocess.TimeoutExpired("uvx", 1)
    assert run_main(monkeypatch, FakeRun(error=timeout)) == 2
    assert run_main(monkeypatch, FakeRun(error=OSError("denied"))) == 2


def test_command_pins_version_and_both_rulesets(monkeypatch, uvx_present):
    fake = FakeRun(0, report())
    assert run_main(monkeypatch, fake) == 0
    assert len(fake.calls) == 2
    for cmd in fake.calls:
        assert gate.SEMGREP in cmd
        assert "--metrics=off" in cmd
    assert ["p/django", "p/typescript"] == [
        c[c.index("--config") + 1] for c in fake.calls
    ]
    assert [c[-1] for c in fake.calls] == ["backend", "frontend/src"]
    assert gate.SEMGREP == "semgrep==1.187.0"
