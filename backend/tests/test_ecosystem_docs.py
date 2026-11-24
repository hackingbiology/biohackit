"""Static checks on docs/ecosystem scans and their links from module proposals."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ECOSYSTEM = REPO / "docs" / "ecosystem"
CHANGES = REPO / "openspec" / "changes"

# Module changes whose scan must exist; m01 joins when its scan task lands.
MODULE_CHANGES = {"m00-foundations": "m00-foundations.md"}

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
    r"api\.github\.com|pypi\.org|registry\.npmjs\.org|raw\.githubusercontent\.com|gnu\.org"
)
_SPDX = re.compile(r"^[A-Za-z0-9.+-]+$")


def _categories() -> set[str]:
    text = (ECOSYSTEM / "README.md").read_text(encoding="utf-8")
    section = text.split("## Decision categories", 1)[1].split("\n## ", 1)[0]
    found = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.M))
    assert found, "no decision categories in README.md"
    return found


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
            decision = fields["Decision"]
            if licence == "unknown":
                assert not compat.startswith("yes"), (
                    f"{where}: unknown licence cannot be AGPL-compatible: yes"
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
