"""AI surfaces map: committed JSON in sync, exact AI set, deterministic rows, real references."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "ai-surfaces.md"
SCRIPT = REPO / "tools" / "docs" / "export_ai_surfaces.py"
OUTPUT = REPO / "frontend" / "src" / "content" / "ai-surfaces.json"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_ai_surfaces", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()
DATA = exporter.parse(SOURCE.read_text(encoding="utf-8"))


def test_committed_json_matches_exporter_output() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == exporter.render(DATA)


def test_check_flag_reports_stale_output(tmp_path: Path) -> None:
    stale = tmp_path / "out.json"
    stale.write_text("{}\n", encoding="utf-8")
    assert exporter.main(["--check"], SOURCE, stale) == 1
    assert exporter.main([], SOURCE, stale) == 0
    assert exporter.main(["--check"], SOURCE, stale) == 0


# scenario: ai-uses-and-attribution::the-numbers-are-not-ai
def test_ai_surfaces_are_exactly_the_three_sanctioned() -> None:
    names = [row["surface"].lower() for row in DATA["ai"]]
    assert len(names) == 3
    assert "extraction" in names[0]
    assert "narration" in names[1]
    assert "evidence-review generation" in names[2]
    assert all(row["kind"] == "AI" for row in DATA["ai"])


# scenario: ai-uses-and-attribution::the-numbers-are-not-ai
def test_required_numbers_are_listed_as_deterministic() -> None:
    rows = DATA["deterministic"]
    assert all(row["kind"] == "deterministic" for row in rows)
    text = " ".join(row["surface"].lower() for row in rows)
    for required in ("safety threshold", "index", "percentile", "trend", "schedule"):
        assert required in text


# scenario: ai-uses-and-attribution::the-numbers-are-not-ai
def test_every_reference_exists() -> None:
    for row in DATA["ai"] + DATA["deterministic"]:
        assert row["status"] in {"implemented", "specified"}
        path, _, requirement = row["where"].partition(": ")
        target = REPO / path
        assert target.is_file(), row["where"]
        if requirement:
            assert f"### Requirement: {requirement}\n" in target.read_text(
                encoding="utf-8"
            ), row["where"]
        else:
            assert row["status"] == "implemented", row["where"]


# scenario: ai-uses-and-attribution::the-numbers-are-not-ai
def test_malformed_table_row_is_rejected() -> None:
    text = "# T\n\n## AI surfaces\n\n| surface | k | w | s |\n|---|---|---|---|\n| a | AI | b |\n"
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(text)
