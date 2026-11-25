"""Changelog: committed JSON in sync, cited commits and changes exist."""

import importlib.util
import re
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "CHANGELOG.md"
SCRIPT = REPO / "tools" / "docs" / "export_changelog.py"
OUTPUT = REPO / "frontend" / "src" / "content" / "changelog.json"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_changelog", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()
DATA = exporter.parse(SOURCE.read_text(encoding="utf-8"))


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False
    )


def _mainline() -> str:
    """The ref whose history cited commits must belong to."""
    for ref in ("main", "origin/main"):
        if (
            _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode
            == 0
        ):
            return ref
    return "HEAD"


def _commit_exists(short: str, mainline: str | None = None) -> bool:
    """True when the commit exists and is an ancestor of the mainline."""
    if _git("cat-file", "-e", f"{short}^{{commit}}").returncode != 0:
        return False
    target = mainline or _mainline()
    return _git("merge-base", "--is-ancestor", short, target).returncode == 0


def _change_exists(change: str) -> bool:
    if change == "archive" or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", change):
        return False
    openspec = REPO / "openspec"
    return any(
        (openspec / base / change).is_dir()
        for base in ("changes", "changes/archive", "specs")
    )


def _unresolved(data: dict[str, Any]) -> list[str]:
    bad: list[str] = []
    for day in data["days"]:
        for e in day["entries"]:
            if not _commit_exists(e["commit"]) or not _change_exists(e["change"]):
                bad.append(f"{e['change']} {e['commit']}")
    return bad


# scenario: dev-process::changelog-page-in-sync
def test_committed_json_matches_exporter_output() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == exporter.render(DATA)


# scenario: dev-process::changelog-page-in-sync
def test_check_flag_reports_stale_output(tmp_path: Path) -> None:
    stale = tmp_path / "out.json"
    stale.write_text("{}\n", encoding="utf-8")
    assert exporter.main(["--check"], SOURCE, stale) == 1
    assert exporter.main([], SOURCE, stale) == 0
    assert exporter.main(["--check"], SOURCE, stale) == 0
    stale.write_text(stale.read_text(encoding="utf-8").replace("guide", "gide"))
    assert exporter.main(["--check"], SOURCE, stale) == 1


# scenario: dev-process::changelog-entries-resolve
def test_history_is_complete_enough_to_check_commits() -> None:
    shallow = _git("rev-parse", "--is-shallow-repository").stdout.strip()
    assert shallow != "true", (
        "shallow clone: cannot verify cited commits; fetch full history "
        "(actions/checkout fetch-depth: 0)"
    )


# scenario: dev-process::changelog-entries-resolve
def test_every_cited_commit_and_change_exists() -> None:
    assert sum(len(d["entries"]) for d in DATA["days"]) >= 10
    assert _unresolved(DATA) == []


# scenario: dev-process::changelog-entries-resolve
def test_bad_commit_and_bad_change_are_named() -> None:
    good = DATA["days"][0]["entries"][0]
    ghost_commit = {"change": good["change"], "commit": "0000000", "summary": "x"}
    ghost_change = {
        "change": "no-such-change",
        "commit": good["commit"],
        "summary": "x",
    }
    odd = [
        {"change": c, "commit": good["commit"], "summary": "x"}
        for c in ("..", "archive")
    ]
    bad = {
        "days": [
            {
                "date": "2026-01-01",
                "entries": [good, ghost_commit, ghost_change, *odd],
            }
        ]
    }
    assert _unresolved(bad) == [
        f"{good['change']} 0000000",
        f"no-such-change {good['commit']}",
        f".. {good['commit']}",
        f"archive {good['commit']}",
    ]


# scenario: dev-process::changelog-entries-resolve
def test_malformed_row_and_bad_date_heading_are_rejected() -> None:
    head = "# T\n\n## 2026-11-25\n\n| change | commit | what changed |\n|---|---|---|\n"
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(head + "| a |\n")
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(head + "| a | zzz | b |\n")
    for row in (
        "|  | 02c9898 | text |",
        "| --- | 02c9898 | text |",
        "| .. | 02c9898 | t |",
    ):
        with pytest.raises(ValueError, match="line 7"):
            exporter.parse(head + row + "\n")
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(head + "| a-b | 02c9898 |  |\n")
    with pytest.raises(ValueError, match="line 3"):
        exporter.parse("# T\n\n## 25 November\n")
    with pytest.raises(ValueError, match="line 3"):
        exporter.parse("# T\n\n## 2026-13-45\n")


# scenario: dev-process::changelog-entries-resolve
def test_commit_not_in_mainline_history_is_rejected() -> None:
    head = _git("rev-parse", "HEAD").stdout.strip()
    parent = _git("rev-parse", "HEAD~1").stdout.strip()
    assert _commit_exists(head, head)
    assert _commit_exists(parent, head)
    assert not _commit_exists(head, parent)


# scenario: dev-process::changelog-entries-resolve
def test_cited_change_matches_commit_trailer_when_present() -> None:
    for day in DATA["days"]:
        for e in day["entries"]:
            body = _git("log", "-1", "--format=%b", e["commit"]).stdout
            trailers = [
                ln.split(":", 1)[1].strip()
                for ln in body.splitlines()
                if ln.startswith("Change:")
            ]
            if trailers:
                assert e["change"] == trailers[-1], f"{e['change']} {e['commit']}"


# scenario: dev-process::changelog-entries-resolve
def test_dates_are_newest_first_and_text_is_plain() -> None:
    dates = [d["date"] for d in DATA["days"]]
    assert dates == sorted(dates, reverse=True)
    for day in DATA["days"]:
        for e in day["entries"]:
            assert "http" not in e["summary"] and "www." not in e["summary"]
