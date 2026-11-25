"""Architecture doc: committed JSON in sync, cited repo paths and requirements exist."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "architecture.md"
SCRIPT = REPO / "tools" / "docs" / "export_architecture.py"
OUTPUT = REPO / "frontend" / "src" / "content" / "architecture.json"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_architecture", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()
DATA = exporter.parse(SOURCE.read_text(encoding="utf-8"))


# scenario: dev-process::architecture-page-in-sync
def test_committed_json_matches_exporter_output() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == exporter.render(DATA)


# scenario: dev-process::architecture-page-in-sync
def test_check_flag_reports_stale_output(tmp_path: Path) -> None:
    stale = tmp_path / "out.json"
    stale.write_text("{}\n", encoding="utf-8")
    assert exporter.main(["--check"], SOURCE, stale) == 1
    assert exporter.main([], SOURCE, stale) == 0
    assert exporter.main(["--check"], SOURCE, stale) == 0


# scenario: dev-process::architecture-components-exist
def test_every_built_component_path_exists() -> None:
    assert len(DATA["built"]) > 10
    for row in DATA["built"]:
        assert (REPO / row["path"]).exists(), row["component"]


# scenario: dev-process::architecture-components-exist
def test_every_specified_row_cites_an_existing_requirement() -> None:
    assert DATA["specified"]
    for row in DATA["specified"]:
        path, _, requirement = row["requirement"].partition(": ")
        target = REPO / path
        assert target.is_file(), row["component"]
        assert requirement, row["component"]
        assert f"### Requirement: {requirement}\n" in target.read_text(
            encoding="utf-8"
        ), row["component"]


# scenario: dev-process::architecture-components-exist
def test_malformed_table_row_is_rejected() -> None:
    text = "# T\n\n## Built components\n\n| component | l | p | u |\n|---|---|---|---|\n| a | b |\n"
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(text)
