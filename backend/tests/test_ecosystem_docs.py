"""Static checks on docs/ecosystem scans and their links from module proposals."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ECOSYSTEM = REPO / "docs" / "ecosystem"
CHANGES = REPO / "openspec" / "changes"

# Module changes whose scan must exist.
MODULE_CHANGES = {
    "m00-foundations": "m00-foundations.md",
    "m01-terminology-reference-data": "m01-terminology.md",
}

MANDATORY = (
    "URL",
    "Licence",
    "AGPL-compatible",
    "Last activity",
    "Decision",
    "Verified",
)
BLOCKED_WHEN_INCOMPATIBLE = {"adopt as dependency", "reuse schema or dataset"}
_FIELD = re.compile(r"^- \*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.*)$")
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2}|unknown)$")
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
_SOURCE = re.compile(
    r"api\.github\.com|pypi\.org|registry\.npmjs\.org|raw\.githubusercontent\.com|gnu\.org|cdc\.gov"
)
_SPDX = re.compile(r"^[A-Za-z0-9.+-]+$")
# SPDX id -> row label of the README licence table.
_SPDX_ROW = {
    "MIT": "MIT (Expat)",
    "BSD-2-Clause": "BSD-2-Clause (FreeBSD)",
    "BSD-3-Clause": "BSD-3-Clause (Modified BSD)",
    "Apache-2.0": "Apache-2.0",
    "LGPL-3.0": "LGPL-3.0",
    "LGPL-3.0-only": "LGPL-3.0",
    "LGPL-3.0-or-later": "LGPL-3.0",
    "GPL-3.0": "GPL-3.0",
    "GPL-3.0-only": "GPL-3.0",
    "GPL-3.0-or-later": "GPL-3.0",
    "AGPL-3.0": "AGPL-3.0",
    "AGPL-3.0-only": "AGPL-3.0",
    "AGPL-3.0-or-later": "AGPL-3.0",
    "MPL-2.0": "MPL-2.0",
    "CC-BY-4.0": "CC-BY (data, docs)",
    "CC-BY-SA-4.0": "CC-BY-SA",
    "CC0-1.0": "CC0",
}
DATA_ONLY_ROW = "CC-BY (data, docs)"
DATA_DECISIONS = {"reuse schema or dataset", "learn-from only"}


def _categories() -> set[str]:
    text = (ECOSYSTEM / "README.md").read_text(encoding="utf-8")
    section = text.split("## Decision categories", 1)[1].split("\n## ", 1)[0]
    found = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.M))
    assert found, "no decision categories in README.md"
    return found


def _licence_verdicts() -> dict[str, str]:
    """Parse the README 'Licence compatibility with AGPL-3.0' table: row label -> verdict."""
    text = (ECOSYSTEM / "README.md").read_text(encoding="utf-8")
    section = text.split("## Licence compatibility with AGPL-3.0", 1)[1]
    verdicts: dict[str, str] = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in {"Licence", ""}:
            if not set(cells[0]) <= {"-"}:
                verdicts[cells[0]] = cells[1]
    assert verdicts, "no licence table in README.md"
    return verdicts


def _licence_problem(fields: dict[str, str], verdicts: dict[str, str]) -> str | None:
    """Return why a 'yes' AGPL claim is not backed by the README table, or None."""
    if not fields["AGPL-compatible"].lower().startswith(("yes", "compatible")):
        return None
    row = _SPDX_ROW.get(fields["Licence"])
    verdict = verdicts.get(row, "") if row else ""
    if not verdict.startswith("yes"):
        return f"Licence {fields['Licence']} is not 'yes' in the README table"
    if row == DATA_ONLY_ROW and fields["Decision"] not in DATA_DECISIONS:
        return "CC-BY is compatible for data/docs only"
    return None


def _entries(path: Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            current = entries.setdefault(line[4:].strip(), {})
            continue
        if line.startswith("#"):
            current = None
            continue
        match = _FIELD.match(line)
        if current is not None and match:
            current[match["key"].strip()] = match["value"].strip()
    return entries


def _scans() -> list[Path]:
    scans = sorted(ECOSYSTEM.glob("m*.md"))
    assert scans, "no module scans under docs/ecosystem"
    return scans


# scenario: ecosystem-reuse::scan-entries-are-verified
def test_scan_entries_have_all_mandatory_fields() -> None:
    categories = _categories()
    verdicts = _licence_verdicts()
    for scan in _scans():
        entries = _entries(scan)
        assert entries, f"{scan.name} has no entries"
        for name, fields in entries.items():
            where = f"{scan.name}: {name}"
            for key in MANDATORY:
                assert fields.get(key), f"{where} lacks {key}"
            assert fields["URL"].startswith("https://"), where
            assert fields["Decision"] in categories, where
            assert _DATE.match(fields["Last activity"]), where
            verified = fields["Verified"]
            assert verified == "unknown" or (
                _ISO.search(verified) and _SOURCE.search(verified)
            ), f"{where}: Verified needs a source host and a date"
            licence = fields["Licence"]
            assert licence == "unknown" or _SPDX.match(licence), (
                f"{where}: Licence must be an SPDX id or 'unknown' "
                "(use 'Licence note' for prose)"
            )
            compat = fields["AGPL-compatible"]
            assert re.match(r"^(yes|no|unknown)\b", compat), (
                f"{where}: AGPL-compatible must start with yes, no or unknown"
            )
            decision = fields["Decision"]
            assert _licence_problem(fields, verdicts) is None, (
                f"{where}: {_licence_problem(fields, verdicts)}"
            )
            if compat.startswith("no"):
                assert decision not in BLOCKED_WHEN_INCOMPATIBLE, where
            if "unknown" in compat:
                assert "docs/QUESTIONS.md" in compat, where
                if decision == "adopt as dependency":
                    assert fields.get("Provisional", "").startswith("yes"), (
                        f"{where}: unknown AGPL verdict needs Provisional: yes"
                    )


# scenario: ecosystem-reuse::module-change-cites-its-scan
def test_module_change_links_its_scan() -> None:
    for change, scan_name in MODULE_CHANGES.items():
        assert (ECOSYSTEM / scan_name).is_file(), f"missing scan {scan_name}"
        proposal = (CHANGES / change / "proposal.md").read_text(encoding="utf-8")
        assert f"docs/ecosystem/{scan_name}" in proposal, change


def _synthetic(licence: str, compat: str, decision: str) -> dict[str, str]:
    return {"Licence": licence, "AGPL-compatible": compat, "Decision": decision}


# scenario: ecosystem-reuse::scan-entries-are-verified
def test_gpl_entry_claiming_yes_is_rejected() -> None:
    entry = _synthetic("GPL-3.0", "yes (GPL)", "adopt as dependency")
    assert _licence_problem(entry, _licence_verdicts()) is not None


# scenario: ecosystem-reuse::scan-entries-are-verified
def test_mit_entry_claiming_yes_passes() -> None:
    entry = _synthetic("MIT", "yes (MIT)", "adopt as dependency")
    assert _licence_problem(entry, _licence_verdicts()) is None


# scenario: ecosystem-reuse::scan-entries-are-verified
def test_cc_by_is_yes_for_data_only_and_unknown_licence_is_rejected() -> None:
    verdicts = _licence_verdicts()
    data = _synthetic("CC-BY-4.0", "yes (CC-BY)", "reuse schema or dataset")
    code = _synthetic("CC-BY-4.0", "yes (CC-BY)", "adopt as dependency")
    unknown = _synthetic("unknown", "yes (?)", "learn-from only")
    assert _licence_problem(data, verdicts) is None
    assert _licence_problem(code, verdicts) is not None
    assert _licence_problem(unknown, verdicts) is not None


# scenario: ecosystem-reuse::scan-entries-are-verified
def test_capitalised_or_paraphrased_yes_on_gpl_is_still_checked() -> None:
    verdicts = _licence_verdicts()
    for claim in ("Yes (GPL)", "compatible (GPL)"):
        entry = _synthetic("GPL-3.0", claim, "adopt as dependency")
        assert _licence_problem(entry, verdicts) is not None
        assert not re.match(r"^(yes|no|unknown)\b", claim)
