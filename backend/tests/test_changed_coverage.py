"""Unit tests for the changed-file coverage gate (tools/coverage/changed_coverage.py)."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "tools" / "coverage" / "changed_coverage.py"
)
_spec = importlib.util.spec_from_file_location("changed_coverage", SCRIPT)
assert _spec is not None and _spec.loader is not None
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)


def _fake_git(monkeypatch: pytest.MonkeyPatch, names: list[str]) -> list[list[str]]:
    calls: list[list[str]] = []

    def run(args: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="\n".join(names) + "\n")

    monkeypatch.setattr(gate.subprocess, "run", run)
    return calls


def test_below_threshold_is_failing() -> None:
    # scenario: dev-process::under-tested-change-rejected
    report = {"files": {"core/views.py": {"summary": {"percent_covered": 89.9}}}}
    assert gate.evaluate(report, ["backend/core/views.py"]) == [
        ("backend/core/views.py", 89.9)
    ]


def test_at_and_above_threshold_pass() -> None:
    report = {
        "files": {
            "a.py": {"summary": {"percent_covered": 90.0}},
            "b.py": {"summary": {"percent_covered": 100.0}},
        }
    }
    assert gate.evaluate(report, ["backend/a.py", "backend/b.py"]) == []


def test_missing_file_counts_as_zero() -> None:
    # scenario: dev-process::under-tested-change-rejected
    assert gate.evaluate({"files": {}}, ["backend/core/new.py"]) == [
        ("backend/core/new.py", 0.0)
    ]


def test_path_mapping_strips_backend_prefix() -> None:
    report = {"files": {"core/x.py": {"summary": {"percent_covered": 50.0}}}}
    assert gate.evaluate(report, ["backend/core/x.py"]) == [("backend/core/x.py", 50.0)]


def test_changed_files_excludes_tests_migrations_manage_and_non_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # scenario: dev-process::excluded-and-unchanged-files-ignored
    _fake_git(
        monkeypatch,
        [
            "backend/tests/test_x.py",
            "backend/terminology/tests/test_y.py",
            "backend/terminology/migrations/0001_initial.py",
            "backend/manage.py",
            "backend/conftest.py",
            "backend/pyproject.toml",
            "frontend/src/a.py",
            "tools/coverage/changed_coverage.py",
            "docs/README.md",
        ],
    )
    assert gate.changed_files("origin/main") == []


def test_changed_files_keeps_backend_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_git(monkeypatch, ["backend/core/views.py", "backend/tests/test_x.py"])
    assert gate.changed_files("origin/main") == ["backend/core/views.py"]


def test_main_skips_coverage_when_nothing_to_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # scenario: dev-process::excluded-and-unchanged-files-ignored
    calls = _fake_git(monkeypatch, ["backend/manage.py", "README.md"])
    assert gate.main(["x", "origin/main"]) == 0
    assert len(calls) == 1 and calls[0][0] == "git"


def test_deleted_files_are_not_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    # scenario: dev-process::deleted-file-not-required
    calls = _fake_git(monkeypatch, [])
    gate.changed_files("origin/main")
    diff_filter = next(a for a in calls[0] if a.startswith("--diff-filter="))
    assert "D" not in diff_filter
