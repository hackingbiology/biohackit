"""Offline tests of the mutmut gate: every subprocess call is faked."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "mutmut" / "mutmut_gate.py"
spec = importlib.util.spec_from_file_location("mutmut_gate", SCRIPT)
assert spec and spec.loader
gate: ModuleType = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

SURVIVOR = "terminology.services.x_normalize_value__mutmut_7"
ALL_KILLED = (
    "Survived 0\n    terminology.services.x_normalize_value__mutmut_6: killed\n"
    f"    {SURVIVOR}: killed\n    terminology.services.x__unit__mutmut_1: timeout\n"
)
WITH_SURVIVOR = ALL_KILLED.replace(f"{SURVIVOR}: killed", f"{SURVIVOR}: survived")
DIFF = (
    "--- terminology/services.py\n+++ terminology/services.py\n-    a = 1\n+    a = 2\n"
)


class FakeRun:
    """Answers `mutmut run|results|show` by subcommand."""

    def __init__(
        self,
        results: str = ALL_KILLED,
        rc: dict[str, int] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.results = results
        self.rc = rc or {}
        self.error = error
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        if self.error:
            raise self.error
        sub = cmd[cmd.index("mutmut") + 1]
        out = {"run": "", "results": self.results, "show": DIFF}[sub]
        return subprocess.CompletedProcess(cmd, self.rc.get(sub, 0), out, "boom")


@pytest.fixture
def uv_present(monkeypatch):
    monkeypatch.setattr(gate.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(gate, "prepare_scratch", lambda scratch, targets: None)


def run_main(monkeypatch, fake: FakeRun) -> int:
    monkeypatch.setattr(gate.subprocess, "run", fake)
    return gate.main()


def test_surviving_mutant_rejected(monkeypatch, uv_present, capsys):
    # scenario: dev-process::surviving-mutant-rejected
    assert run_main(monkeypatch, FakeRun(WITH_SURVIVOR)) == 1
    out = capsys.readouterr().out
    assert "backend/terminology/services.py" in out
    assert SURVIVOR in out
    assert "+    a = 2" in out


def test_accepted_survivor_with_reason_passes(monkeypatch, uv_present, tmp_path):
    # scenario: dev-process::all-mutants-killed
    accepted = tmp_path / "accepted.txt"
    accepted.write_text(f"{SURVIVOR} # equivalent mutant\n")
    monkeypatch.setattr(gate, "ACCEPTED_FILE", accepted)
    assert run_main(monkeypatch, FakeRun(WITH_SURVIVOR)) == 0


def test_all_mutants_killed(monkeypatch, uv_present, capsys):
    # scenario: dev-process::all-mutants-killed
    fake = FakeRun(ALL_KILLED)
    assert run_main(monkeypatch, fake) == 0
    assert "backend/terminology/services.py: 3/3 killed" in capsys.readouterr().out
    command = fake.calls[0]
    assert gate.MUTMUT in command
    assert "--isolated" in command and "--frozen" in command


def test_uv_missing_cannot_run(monkeypatch, capsys):
    # scenario: dev-process::mutation-run-cannot-complete
    monkeypatch.setattr(gate.shutil, "which", lambda name: None)
    assert gate.main() == 2
    assert "uv not found" in capsys.readouterr().out


def test_timeout_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::mutation-run-cannot-complete
    error = subprocess.TimeoutExpired("uv", 1)
    assert run_main(monkeypatch, FakeRun(error=error)) == 2


def test_start_failure_cannot_run(monkeypatch, uv_present):
    # scenario: dev-process::mutation-run-cannot-complete
    assert run_main(monkeypatch, FakeRun(error=OSError("nope"))) == 2


@pytest.mark.parametrize("sub", ["run", "results"])
def test_mutmut_crash_cannot_run(monkeypatch, uv_present, sub):
    # scenario: dev-process::mutation-run-cannot-complete
    assert run_main(monkeypatch, FakeRun(rc={sub: 1})) == 2


@pytest.mark.parametrize(
    "results",
    [
        "garbage",
        ALL_KILLED.replace("killed", "not checked", 1),
        ALL_KILLED + "    other.module.x_f__mutmut_1: killed\n",
        "    other.module.x_f__mutmut_1: killed\n",
    ],
)
def test_unreadable_results_cannot_run(monkeypatch, uv_present, results):
    # scenario: dev-process::mutation-run-cannot-complete
    assert run_main(monkeypatch, FakeRun(results)) == 2


def test_target_file_problems_cannot_run(tmp_path):
    # scenario: dev-process::mutation-run-cannot-complete
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "m.py").write_text("x = 1\n")
    (tmp_path / "backend" / "test_m.py").write_text("")
    cases = {
        "missing": None,
        "empty": "# only a comment\n\n",
        "ghost": "backend/ghost.py backend/test_m.py\n",
        "ghost-test": "backend/m.py backend/ghost_test.py\n",
        "no-test": "backend/m.py\n",
        "outside": "tools/x.py backend/test_m.py\n",
    }
    for name, text in cases.items():
        path = tmp_path / f"{name}.txt"
        if text is not None:
            path.write_text(text)
        with pytest.raises(gate.GateError):
            gate.read_targets(path, tmp_path)


def test_accepted_survivor_without_reason_cannot_run(tmp_path, monkeypatch, uv_present):
    # scenario: dev-process::mutation-run-cannot-complete
    bad = tmp_path / "accepted.txt"
    for text in (f"{SURVIVOR}\n", f"{SURVIVOR} #\n", f"{SURVIVOR} #   \n"):
        bad.write_text(text)
        with pytest.raises(gate.GateError):
            gate.read_accepted(bad)
    monkeypatch.setattr(gate, "ACCEPTED_FILE", bad)
    assert run_main(monkeypatch, FakeRun()) == 2


def test_real_config_lists_unit_conversion():
    assert [t.path for t in gate.read_targets()] == ["backend/terminology/services.py"]
    assert gate.read_targets()[0].module == "terminology.services"
    assert all(gate.read_accepted().values())


def test_scratch_config_isolates_original_code(tmp_path):
    target = gate.Target(
        "backend/terminology/services.py", ("tests/test_terminology.py",)
    )
    config = gate.mutmut_config([target], ["core", "terminology"])
    assert 'only_mutate = ["terminology/services.py"]' in config
    assert "django_find_project=false" in config
