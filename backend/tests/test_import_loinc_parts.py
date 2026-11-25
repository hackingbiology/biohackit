# SPDX-License-Identifier: AGPL-3.0-or-later
"""Optional Part / LoincPartLink_Primary import (M01 TG-LOINC D1).

All data below is synthetic test data written into tmp_path; none is stored or seeded.
"""

import shutil
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from terminology.models import LoincPart, LoincPartLink, LoincTerm, Source

FIXTURE = Path(__file__).parent / "fixtures" / "loinc_synthetic"
PART_FILE = "AccessoryFiles/PartFile/Part.csv"
LINK_FILE = "AccessoryFiles/PartFile/LoincPartLink_Primary.csv"
PART_HEADER = '"PartNumber","PartTypeName","PartName","PartDisplayName","Status"'
LINK_HEADER = (
    '"LoincNumber","LongCommonName","PartNumber","PartName","PartCodeSystem",'
    '"PartTypeName","LinkTypeName","Property"'
)
PROP = "http://example.invalid/property/"


def link_line(code: str, part: str, kind: str = "COMPONENT") -> str:
    cells = [code, "Synthetic long", part, "Synthetic part", "sys", kind, "Primary"]
    cells.append(PROP + kind)
    return ",".join(f'"{c}"' for c in cells)


@pytest.fixture
def release(tmp_path: Path) -> Path:
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    (tmp_path / "AccessoryFiles" / "PartFile").mkdir(parents=True)
    (tmp_path / PART_FILE).write_text(
        f"{PART_HEADER}\n"
        '"SYNP-1","COMPONENT","synthetic comp","Synthetic comp display","ACTIVE"\n'
        '"SYNP-2","SYSTEM","synthetic sys","Synthetic sys display","ACTIVE"\n'
        '"SYNP-3","METHOD","synthetic method","Synthetic method display","DEPRECATED"\n'
    )
    (tmp_path / LINK_FILE).write_text(
        f"{LINK_HEADER}\n"
        f"{link_line('SYN-0001', 'SYNP-1')}\n"
        f"{link_line('SYN-0001', 'SYNP-2', 'SYSTEM')}\n"
        f"{link_line('SYN-0002', 'SYNP-1')}\n"
    )
    return tmp_path


def run(directory: Path) -> str:
    out = StringIO()
    call_command("import_loinc", str(directory), release_version="TEST-1", stdout=out)
    return out.getvalue()


def snapshot() -> tuple[list[dict], list[dict]]:
    return (
        list(LoincPart.objects.order_by("part_number").values()),
        list(LoincPartLink.objects.order_by("id").values()),
    )


# scenario: terminology-reference-data::loinc-parts-imported
def test_parts_imported_and_idempotent(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    parts = {p.part_number: p for p in LoincPart.objects.all()}
    assert set(parts) == {"SYNP-1", "SYNP-2", "SYNP-3"}
    assert parts["SYNP-1"].part_type_name == "COMPONENT"
    assert parts["SYNP-1"].part_name == "synthetic comp"
    assert parts["SYNP-1"].part_display_name == "Synthetic comp display"
    assert parts["SYNP-3"].status == "DEPRECATED"
    assert {p.source_id for p in parts.values()} == {source.pk}
    assert "LoincPart: created 3, updated 0" in output
    first = snapshot()
    assert "LoincPart: created 0, updated 3" in run(release)
    assert snapshot() == first


# scenario: terminology-reference-data::loinc-part-links-imported-as-relationships
def test_part_links_imported_and_not_duplicated(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    links = LoincPartLink.objects.order_by("id")
    assert [(k.term.loinc_num, k.part.part_number) for k in links] == [
        ("SYN-0001", "SYNP-1"),
        ("SYN-0001", "SYNP-2"),
        ("SYN-0002", "SYNP-1"),
    ]
    assert links[1].link_type_name == "Primary"
    assert links[1].property == PROP + "SYSTEM"
    assert {k.source_id for k in links} == {source.pk}
    assert "LoincPartLink: created 3, updated 0" in output
    first = snapshot()
    assert "LoincPartLink: created 0, updated 3" in run(release)
    assert snapshot() == first


# scenario: terminology-reference-data::loinc-part-links-imported-as-relationships
def test_link_removed_from_file_is_deleted(db, release):
    run(release)
    (release / LINK_FILE).write_text(
        f"{LINK_HEADER}\n{link_line('SYN-0001', 'SYNP-1')}\n"
    )
    run(release)
    assert LoincPartLink.objects.count() == 1


# scenario: terminology-reference-data::loinc-part-links-imported-as-relationships
def test_links_resolve_against_parts_already_in_database(db, release):
    run(release)
    (release / PART_FILE).unlink()
    output = run(release)
    assert PART_FILE in output
    assert LoincPartLink.objects.count() == 3


# scenario: terminology-reference-data::part-link-to-an-unknown-part-aborts-the-import
def test_unknown_part_rolls_back_everything(db, release):
    path = release / LINK_FILE
    lines = path.read_text().splitlines()
    path.write_text("\n".join([*lines, link_line("SYN-0001", "SYNP-999")]) + "\n")
    with pytest.raises(CommandError) as err:
        run(release)
    assert f"LoincPartLink_Primary.csv line {len(lines) + 1}:" in str(err.value)
    assert "SYNP-999" in str(err.value)
    assert LoincTerm.objects.count() == 0
    assert LoincPart.objects.count() == 0
    assert LoincPartLink.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::accessory-row-for-an-unknown-loinc-code-aborts-the-import
def test_part_link_with_unknown_loinc_code_aborts(db, release):
    path = release / LINK_FILE
    lines = path.read_text().splitlines()
    path.write_text("\n".join([*lines, link_line("SYN-9999", "SYNP-1")]) + "\n")
    with pytest.raises(CommandError, match=r"Primary\.csv line 5:.*SYN-9999"):
        run(release)
    assert LoincPart.objects.count() == 0
    assert LoincPartLink.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::accessory-row-for-an-unknown-loinc-code-aborts-the-import
def test_part_file_missing_column_aborts(db, release):
    (release / PART_FILE).write_text('"PartNumber"\n"SYNP-1"\n')
    with pytest.raises(CommandError, match=r"Part\.csv line 1: missing column"):
        run(release)
    assert LoincTerm.objects.count() == 0


# scenario: terminology-reference-data::optional-loinc-accessory-files-absent
def test_release_imports_without_part_folder(db, tmp_path):
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    output = run(tmp_path)
    assert LoincTerm.objects.count() == 3
    assert LoincPart.objects.count() == 0
    assert LoincPartLink.objects.count() == 0
    assert PART_FILE in output
    assert LINK_FILE in output
