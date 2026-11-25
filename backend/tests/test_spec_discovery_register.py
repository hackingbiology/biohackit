"""Consistency of docs/spec-discovery/*.md registers with the OpenSpec files."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUSES = {"covered", "added", "out-of-scope"}
Titles = dict[str, set[str]]


@dataclass(frozen=True)
class Row:
    source: str
    feature: str
    status: str
    requirement: str
    notes: str


def parse_register(text: str) -> list[Row]:
    """Return the data rows of the first-column-'Source' markdown table."""
    rows: list[Row] = []
    in_table = False
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [
            c.replace("\\|", "|").strip()
            for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])
        ]
        if cells[0] == "Source":
            in_table = True
            continue
        if not in_table or set(cells[0]) <= set("-: "):
            continue
        cells += [""] * (5 - len(cells))
        rows.append(Row(*cells[:5]))
    return rows


def collect_titles(base: Path, pattern: str) -> Titles:
    """Map capability -> requirement titles for spec files matching pattern."""
    out: Titles = {}
    for path in sorted(base.glob(pattern)):
        if "archive" in path.parts:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("### Requirement:"):
                out.setdefault(path.parent.name, set()).add(
                    line.split(":", 1)[1].strip()
                )
    return out


def _exists(requirement: str, titles: Titles) -> bool:
    cap, _, title = requirement.strip("`").partition("/")
    return title in titles.get(cap, set())


def check_rows(
    rows: list[Row], specs: Titles, changes: Titles, root: Path
) -> list[str]:
    errors: list[str] = []
    for r in rows:
        where = f"{r.source!r}"
        source_file = r.source.split(" § ")[0].strip("`")
        if not (root / source_file).is_file():
            errors.append(f"{where}: source file {source_file} does not exist")
        if r.status not in STATUSES:
            errors.append(f"{where}: unknown status {r.status!r}")
        elif r.status == "out-of-scope":
            if not r.notes:
                errors.append(f"{where}: out-of-scope row needs a reason in Notes")
        elif r.status == "covered":
            if not _exists(r.requirement, specs):
                hint = (
                    " (only in an open change: use 'added')"
                    if _exists(r.requirement, changes)
                    else ""
                )
                errors.append(
                    f"{where}: requirement {r.requirement!r} not found in openspec/specs{hint}"
                )
        else:
            if _exists(r.requirement, specs):
                errors.append(
                    f"{where}: added requirement {r.requirement!r} is already in openspec/specs"
                )
            elif not _exists(r.requirement, changes):
                errors.append(
                    f"{where}: added requirement {r.requirement!r} not in an open change"
                )
    return errors


def _titles(cap: str, *names: str) -> Titles:
    return {cap: set(names)}


def _row(
    status: str,
    requirement: str = "cap/Req",
    notes: str = "",
    source: str = "docs/foundation.md § 1",
) -> Row:
    return Row(source, "feature", status, requirement, notes)


def test_parse_register_reads_rows_and_skips_header() -> None:
    text = "intro\n| Source | Feature | Status | Requirement | Notes |\n|---|---|---|---|---|\n| a.md § 1 | f | covered | c/R | |\n"
    assert parse_register(text) == [Row("a.md § 1", "f", "covered", "c/R", "")]


# scenario: dev-process::register-rows-resolve
def test_real_registers_resolve() -> None:
    specs = collect_titles(ROOT / "openspec/specs", "*/spec.md")
    changes = collect_titles(ROOT / "openspec/changes", "*/specs/*/spec.md")
    registers = sorted((ROOT / "docs/spec-discovery").glob("*.md"))
    assert registers
    for reg in registers:
        rows = parse_register(reg.read_text(encoding="utf-8"))
        assert rows, reg
        assert check_rows(rows, specs, changes, ROOT) == []


# scenario: dev-process::register-rows-resolve
def test_covered_row_with_missing_requirement_fails() -> None:
    errors = check_rows([_row("covered")], _titles("cap", "Other"), {}, ROOT)
    assert any("not found" in e for e in errors)


# scenario: dev-process::register-rows-resolve
def test_covered_row_resolving_only_to_open_change_fails() -> None:
    errors = check_rows([_row("covered")], {}, _titles("cap", "Req"), ROOT)
    assert any("use 'added'" in e for e in errors)


# scenario: dev-process::register-rows-resolve
def test_missing_source_file_and_empty_out_of_scope_notes_fail() -> None:
    bad = [_row("out-of-scope", source="nope/missing.md § 1")]
    errors = check_rows(bad, {}, {}, ROOT)
    assert any("does not exist" in e for e in errors)
    assert any("reason" in e for e in errors)


# scenario: dev-process::register-rows-resolve
def test_unknown_status_fails() -> None:
    assert any("unknown status" in e for e in check_rows([_row("done")], {}, {}, ROOT))


# scenario: dev-process::unspecified-feature-captured
def test_added_row_must_point_to_open_change() -> None:
    changes = _titles("cap", "Req")
    assert check_rows([_row("added")], {}, changes, ROOT) == []
    assert any(
        "not in an open change" in e for e in check_rows([_row("added")], {}, {}, ROOT)
    )


# scenario: dev-process::unspecified-feature-captured
def test_added_row_already_in_specs_fails() -> None:
    specs = _titles("cap", "Req")
    errors = check_rows([_row("added")], specs, _titles("cap", "Req"), ROOT)
    assert any("already in openspec/specs" in e for e in errors)


# scenario: dev-process::register-rows-resolve
def test_part_c_registers_exist_and_resolve() -> None:
    specs = collect_titles(ROOT / "openspec/specs", "*/spec.md")
    changes = collect_titles(ROOT / "openspec/changes", "*/specs/*/spec.md")
    sources = {
        "getbased-reuse.md": "docs/getbased-reuse-analysis.md",
        "presentation.md": "docs/presentation/biohackit-deck.pdf",
        "slides.md": "docs/slides/hacking-biology-project-presentation.pdf",
        "competitive-landscape.md": "docs/analysis/competitive-landscape.html",
    }
    for name, source in sources.items():
        path = ROOT / "docs/spec-discovery" / name
        assert path.is_file(), name
        rows = parse_register(path.read_text(encoding="utf-8"))
        assert rows, name
        assert all(r.source.startswith(source + " § ") for r in rows), name
        assert check_rows(rows, specs, changes, ROOT) == []


# scenario: dev-process::unspecified-feature-captured
def test_linked_data_scenario_excludes_withheld_entities() -> None:
    path = (
        ROOT
        / "openspec/changes/s01-spec-discovery/specs/analytics-and-open-data/spec.md"
    )
    text = path.read_text(encoding="utf-8")
    assert "each public entity carries its standard codes" in text
    assert "no identifier or link for a withheld entity" in text
    assert "- **AND** the dataset contains no reference to a withheld item" in text


# scenario: dev-process::register-rows-resolve
def test_project_spec_register_is_checked_and_a_bad_title_breaks_it() -> None:
    names = {p.name for p in (ROOT / "docs/spec-discovery").glob("*.md")}
    assert {"whitepaper.md", "project-spec.md"} <= names
    specs = collect_titles(ROOT / "openspec/specs", "*/spec.md")
    changes = collect_titles(ROOT / "openspec/changes", "*/specs/*/spec.md")
    text = (ROOT / "docs/spec-discovery/project-spec.md").read_text(encoding="utf-8")
    rows = parse_register(text)
    source = "docs/hackingbiology-project-spec.md"
    assert all(r.source.startswith(source) for r in rows)
    assert check_rows(rows, specs, changes, ROOT) == []
    covered = next(r for r in rows if r.status == "covered")
    bad = replace(covered, requirement="protocols/No such requirement")
    assert check_rows([bad], specs, changes, ROOT)


COMPETITIVE_LANDSCAPE_SECTIONS = (
    "What this maps",
    "Category map",
    "Feature matrix",
    "Where the cells are empty",
    "Where biohack.it sits",
    "Emerging “Biohacker OS”",
)


# scenario: dev-process::register-rows-resolve
def test_competitive_landscape_register_covers_all_sections() -> None:
    path = ROOT / "docs/spec-discovery/competitive-landscape.md"
    rows = parse_register(path.read_text(encoding="utf-8"))
    prefix = "docs/analysis/competitive-landscape.html § "
    cited = {r.source[len(prefix) :] for r in rows}
    assert cited == set(COMPETITIVE_LANDSCAPE_SECTIONS)
    html = (ROOT / "docs/analysis/competitive-landscape.html").read_text(
        encoding="utf-8"
    )
    h2 = re.findall(r"<h2>(.*?)</h2>", html, re.S)
    titles = [unescape(re.sub(r"<[^>]+>", "", h)).strip() for h in h2]
    assert len(titles) == len(COMPETITIVE_LANDSCAPE_SECTIONS)
    for title, section in zip(titles, COMPETITIVE_LANDSCAPE_SECTIONS, strict=True):
        assert title.startswith(section)


SPECS_HTML_PART1_SECTIONS = (
    "Principles & product posture",
    "Domain Model (cross-cutting)",
    "AI Uses, Provenance & Previous Work (cross-cutting)",
    "Data Standards & Typing (scientific validity)",
    "Scientific Method & Evidence (cross-cutting)",
    "Statistical Methodology (cross-cutting)",
    "Related Initiatives (ecosystem landscape)",
    "Accounts & Profiles",
    "Management & Delegation (Mentor / Longevity Doctor / Clinic)",
    "Protocols (M1 — Protocol Builder & Library)",
    "Interventions & Substance Catalog",
    "Biomarkers & Lab Data — the Blood Layer (M2)",
    "Measurement Planning (M3 — Scheduling & Measurement Planner)",
    "Safety Guardrails (M7)",
)

SPECS_HTML_PART2_SECTIONS = (
    "Daily Log & Adherence (M13)",
    "Dashboards & Doctor View (M5)",
    "Community & Social (M6)",
    "N-of-1 Studies",
    "Procurement & Inventory (M4)",
    "Pills Management (M4 — daily intake orchestration)",
    "Therapeutics Management (periodic treatments)",
    "Exercise Reporting",
    "Nutrition Management",
    "Evidence Layer (M11)",
    "Analytics & Open Data (M8)",
    "Genomics (M9 — minimal interpretation, public by default)",
    "Agent Access (MCP)",
)


# scenario: dev-process::register-rows-resolve
def test_specs_html_register_covers_all_sections() -> None:
    specs = collect_titles(ROOT / "openspec/specs", "*/spec.md")
    changes = collect_titles(ROOT / "openspec/changes", "*/specs/*/spec.md")
    path = ROOT / "docs/spec-discovery/specs-html.md"
    assert path.is_file()
    rows = parse_register(path.read_text(encoding="utf-8"))
    prefix = "docs/specs/biohackit-specification.html § "
    assert rows
    assert all(r.source.startswith(prefix) for r in rows)
    cited = {r.source[len(prefix) :] for r in rows}
    assert cited == set(SPECS_HTML_PART1_SECTIONS) | set(SPECS_HTML_PART2_SECTIONS)
    html = (ROOT / "docs/specs/biohackit-specification.html").read_text(
        encoding="utf-8"
    )
    h2 = re.findall(r'<h2 class="ct">(.*?)</h2>', html, re.S)
    assert cited == {unescape(re.sub(r"<[^>]+>", "", h)).strip() for h in h2}
    assert check_rows(rows, specs, changes, ROOT) == []
    covered = next(r for r in rows if r.status == "covered")
    bad = replace(covered, requirement="protocols/No such requirement")
    assert check_rows([bad], specs, changes, ROOT)
