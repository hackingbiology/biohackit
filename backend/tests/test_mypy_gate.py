"""Offline tests of the mypy gate: every subprocess call is faked."""

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "mypy" / "mypy_gate.py"
spec = importlib.util.spec_from_file_location("mypy_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

OK = "Success: no issues found in 6 source files\n"
BAD = (
    "backend/terminology/models.py:47:16: error: Incompatible return value type "
    '(got "int", expected "str")  [return-value]\n'
    "Found 1 error in 1 file (checked 6 source files)\n"
)


class FakeRun:
    def __init__(
        self, rc: int = 0, stdout: str = OK, error: Exception | None = None
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
def uv_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")


def run_main(monkeypatch, fake: FakeRun) -> int:
    monkeypatch.setattr(gate.subprocess, "run", fake)
    return gate.main()


def test_type_error_in_strict_app_rejected(monkeypatch, uv_present, capsys):
    # scenario: dev-process::type-error-in-strict-app-rejected
    assert run_main(monkeypatch, FakeRun(1, BAD)) == 1
    out = capsys.readouterr().out
    assert "backend/terminology/models.py:47:16: Incompatible return value" in out


def test_strict_apps_type_clean(monkeypatch, uv_present, capsys):
    # scenario: dev-process::strict-apps-type-clean
    fake = FakeRun(0, OK)
    assert run_main(monkeypatch, fake) == 0
    assert "backend/terminology" in capsys.readouterr().out
    command = fake.calls[0]
    assert gate.MYPY in command and gate.DJANGO_STUBS in command
    assert "--isolated" in command and "--frozen" in command


def test_uv_missing_cannot_run(monkeypatch, capsys):
    # scenario: dev-process::type-checker-cannot-run
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    assert gate.main() == 2
    assert "uv not found" in capsys.readouterr().out


def test_timeout_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::type-checker-cannot-run
    error = subprocess.TimeoutExpired("uv", 1)
    assert run_main(monkeypatch, FakeRun(error=error)) == 2


def test_crash_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::type-checker-cannot-run
    assert run_main(monkeypatch, FakeRun(2, "")) == 2


def test_unparseable_output_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::type-checker-cannot-run
    assert run_main(monkeypatch, FakeRun(0, "garbage")) == 2
    assert run_main(monkeypatch, FakeRun(1, "garbage")) == 2


def test_start_failure_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::type-checker-cannot-run
    assert run_main(monkeypatch, FakeRun(error=OSError("nope"))) == 2


def test_apps_file_problems_cannot_run(tmp_path):
    # scenario: dev-process::type-checker-cannot-run
    missing = tmp_path / "none.txt"
    with pytest.raises(gate.GateError):
        gate.read_apps(missing, tmp_path)
    empty = tmp_path / "empty.txt"
    empty.write_text("# only a comment\n\n")
    with pytest.raises(gate.GateError):
        gate.read_apps(empty, tmp_path)
    ghost = tmp_path / "ghost.txt"
    ghost.write_text("backend/ghost\n")
    with pytest.raises(gate.GateError):
        gate.read_apps(ghost, tmp_path)


def test_real_apps_file_lists_terminology():
    assert "backend/terminology" in gate.read_apps()
