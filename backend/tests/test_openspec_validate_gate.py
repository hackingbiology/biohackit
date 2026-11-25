"""Offline tests of the openspec validate gate: every subprocess call is faked."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "openspec" / "validate_gate.py"
spec = importlib.util.spec_from_file_location("openspec_validate_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def report(valid: bool) -> str:
    issues = [
        {"level": "ERROR", "path": "a/spec.md", "line": 3, "message": "bad header"}
    ]
    items = [
        {"id": "good", "type": "spec", "valid": True, "issues": []},
        {
            "id": "broken",
            "type": "change",
            "valid": valid,
            "issues": [] if valid else issues,
        },
    ]
    return json.dumps({"items": items})


class FakeRun:
    def __init__(
        self, rc: int = 0, stdout: str = "{}", error: Exception | None = None
    ) -> None:
        self.rc = rc
        self.stdout = stdout
        self.error = error
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if self.error:
            raise self.error
        return subprocess.CompletedProcess(cmd, self.rc, self.stdout, "boom")


@pytest.fixture
def pnpm_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")


def test_invalid_item_rejected(monkeypatch, pnpm_present, capsys):
    # scenario: dev-process::invalid-specification-rejected
    monkeypatch.setattr(gate.subprocess, "run", FakeRun(1, report(False)))
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "change broken" in out
    assert "a/spec.md:3: bad header" in out


def test_valid_items_pass(monkeypatch, pnpm_present, capsys):
    # scenario: dev-process::valid-specifications-pass
    monkeypatch.setattr(gate.subprocess, "run", FakeRun(0, report(True)))
    assert gate.main() == 0
    assert "2 items valid" in capsys.readouterr().out


def test_command_runs_from_repo_root_without_touching_frontend(
    monkeypatch, pnpm_present
):
    # scenario: dev-process::valid-specifications-pass
    run = FakeRun(0, report(True))
    monkeypatch.setattr(gate.subprocess, "run", run)
    gate.main()
    cmd, kwargs = run.calls[0]
    assert cmd[:3] == ["/bin/pnpm", "dlx", gate.OPENSPEC]
    assert "--dir" not in cmd and "frontend" not in " ".join(cmd)
    assert kwargs["cwd"] == gate.ROOT
    assert kwargs["timeout"] == gate.TIMEOUT_SECONDS
    assert gate.OPENSPEC.rsplit("@", 1)[1][0].isdigit()


def test_missing_pnpm_fails_closed(monkeypatch, capsys):
    # scenario: dev-process::specification-validator-cannot-run
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    assert gate.main() == 2
    assert "cannot run" in capsys.readouterr().out


@pytest.mark.parametrize(
    "run",
    [
        FakeRun(2, ""),
        FakeRun(1, report(True)),
        FakeRun(0, "not json"),
        FakeRun(0, "[]"),
        FakeRun(0, json.dumps({"items": []})),
        FakeRun(0, json.dumps({"items": [{"id": "x"}]})),
        FakeRun(error=subprocess.TimeoutExpired("pnpm", 1)),
        FakeRun(error=FileNotFoundError("pnpm")),
    ],
)
def test_cli_failures_fail_closed(monkeypatch, pnpm_present, run, capsys):
    # scenario: dev-process::specification-validator-cannot-run
    monkeypatch.setattr(gate.subprocess, "run", run)
    assert gate.main() == 2
    assert "cannot run" in capsys.readouterr().out
