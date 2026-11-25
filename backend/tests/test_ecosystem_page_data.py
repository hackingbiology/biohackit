"""Ecosystem page data: exporter parses the scans and the committed JSON stays in sync."""

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

REPO = Path(__file__).resolve().parents[2]
ECOSYSTEM = REPO / "docs" / "ecosystem"
SCRIPT = REPO / "tools" / "ecosystem" / "export_page_data.py"
OUTPUT = REPO / "frontend" / "src" / "content" / "ecosystem.json"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_page_data", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()

SCAN = """# Scan title

## Area

### Alpha
- **URL:** https://example.org/alpha
- **Licence:** unknown
- **AGPL-compatible:** unknown — question Q1
- **Decision:** learn-from only

### Beta
- **URL:** https://example.org/beta
- **Licence:** MIT
- **Provisional:** yes, because
"""

GIVEBACK = """# Give-back register

| date | upstream project | proposed contribution | status | link |
|---|---|---|---|---|
| 2026-01-01 | org/repo | Add a licence | proposed | https://example.org/repo |
"""


def _fixture(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Readme\n### Not an entry\n", encoding="utf-8")
    (docs / "a-scan.md").write_text(SCAN, encoding="utf-8")
    (docs / "GIVEBACK.md").write_text(GIVEBACK, encoding="utf-8")
    return docs


def test_every_entry_is_exported_with_verbatim_fields(tmp_path: Path) -> None:
    # scenario: ecosystem-reuse::page-lists-every-scan-entry
    data = exporter.build(_fixture(tmp_path))
    assert [s["file"] for s in data["scans"]] == ["a-scan.md"]
    scan = data["scans"][0]
    assert scan["title"] == "Scan title"
    alpha, beta = scan["entries"]
    assert alpha["name"] == "Alpha"
    assert alpha["fields"]["Licence"] == "unknown"
    assert alpha["fields"]["AGPL-compatible"] == "unknown — question Q1"
    assert "Provisional" not in alpha["fields"]
    assert "Decision" not in beta["fields"]
    assert beta["fields"]["Provisional"] == "yes, because"


def test_repo_entry_counts_match_headings() -> None:
    # scenario: ecosystem-reuse::page-lists-every-scan-entry
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    headings = sum(
        len(re.findall(r"^### ", p.read_text(encoding="utf-8"), re.M))
        for p in ECOSYSTEM.glob("*.md")
        if p.name not in {"README.md", "GIVEBACK.md"}
    )
    assert sum(len(s["entries"]) for s in data["scans"]) == headings
    for scan in data["scans"]:
        for entry in scan["entries"]:
            assert entry["fields"]["URL"].startswith("https://")


def test_giveback_rows_map_to_objects(tmp_path: Path) -> None:
    # scenario: ecosystem-reuse::page-lists-give-back-proposals
    data = exporter.build(_fixture(tmp_path))
    assert data["giveback"] == [
        {
            "date": "2026-01-01",
            "upstream": "org/repo",
            "contribution": "Add a licence",
            "status": "proposed",
            "link": "https://example.org/repo",
        }
    ]


def test_repo_giveback_count_matches_table() -> None:
    # scenario: ecosystem-reuse::page-lists-give-back-proposals
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rows = [
        line
        for line in (ECOSYSTEM / "GIVEBACK.md").read_text(encoding="utf-8").splitlines()
        if re.match(r"^\| \d{4}-\d{2}-\d{2} \|", line)
    ]
    assert len(data["giveback"]) == len(rows)


def test_committed_json_matches_exporter() -> None:
    # scenario: ecosystem-reuse::page-data-stays-in-sync-with-the-scans
    assert exporter.main(["--check"]) == 0


def test_modified_docs_make_check_fail(tmp_path: Path) -> None:
    # scenario: ecosystem-reuse::page-data-stays-in-sync-with-the-scans
    docs = _fixture(tmp_path)
    out = tmp_path / "ecosystem.json"
    assert exporter.main([], docs, out) == 0
    assert exporter.main(["--check"], docs, out) == 0
    (docs / "a-scan.md").write_text(
        SCAN + "\n### Gamma\n- **URL:** https://example.org/g\n"
    )
    assert exporter.main(["--check"], docs, out) == 1
