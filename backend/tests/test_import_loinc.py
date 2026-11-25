# SPDX-License-Identifier: AGPL-3.0-or-later
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from terminology.loinc_importer import DEFAULT_DIR
from terminology.models import LoincTerm, Source
from terminology.seed_loader import SEED_DIR, inspect_seed_dir

FIXTURE = Path(__file__).parent / "fixtures" / "loinc_synthetic"
HEADER = (
    "LOINC_NUM,COMPONENT,PROPERTY,TIME_ASPCT,SYSTEM,SCALE_TYP,METHOD_TYP,CLASS,"
    "LONG_COMMON_NAME,SHORTNAME,STATUS"
)


def run(directory, version="TEST-1"):
    call_command("import_loinc", str(directory), release_version=version)


def snapshot():
    return list(LoincTerm.objects.order_by("loinc_num").values())


# scenario: terminology-reference-data::loinc-release-absent
def test_absent_release_fails_cleanly(db, tmp_path):
    with pytest.raises(CommandError) as err:
        run(tmp_path / "nope")
    assert "data/vendor/loinc" in str(err.value)
    assert "licence" in str(err.value)
    assert LoincTerm.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::loinc-release-absent
def test_absent_release_exit_code_and_no_traceback(tmp_path):
    result = subprocess.run(
        [sys.executable, "manage.py", "import_loinc", str(tmp_path / "nope")],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "data/vendor/loinc" in result.stderr
    assert "Traceback" not in result.stderr


def test_default_dir_is_git_ignored_vendor_dir():
    assert DEFAULT_DIR.parts[-3:] == ("data", "vendor", "loinc")
    repo = DEFAULT_DIR.parents[2]
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "data/vendor/loinc/Loinc.csv"],
        cwd=repo,
        check=False,
    )
    assert ignored.returncode == 0


def test_missing_release_version_is_rejected(db):
    with pytest.raises(CommandError, match="release-version"):
        run(FIXTURE, version=" ")
    assert LoincTerm.objects.count() == 0


# scenario: terminology-reference-data::loinc-import-is-idempotent
def test_import_is_idempotent(db):
    run(FIXTURE)
    first = snapshot()
    assert len(first) == 3
    LoincTerm.objects.filter(loinc_num="SYN-0001").update(featured=True)
    run(FIXTURE)
    again = snapshot()
    assert len(again) == 3
    assert [r for r in again if r["loinc_num"] != "SYN-0001"] == [
        r for r in first if r["loinc_num"] != "SYN-0001"
    ]
    assert LoincTerm.objects.get(loinc_num="SYN-0001").featured is True
    assert Source.objects.count() == 1


def test_import_updates_changed_values(db, tmp_path):
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    run(tmp_path)
    text = (tmp_path / "Loinc.csv").read_text().replace("TRIAL", "ACTIVE")
    (tmp_path / "Loinc.csv").write_text(text)
    run(tmp_path)
    assert LoincTerm.objects.get(loinc_num="SYN-0002").status == "ACTIVE"


def test_table_found_in_loinctable_subdir(db, tmp_path):
    (tmp_path / "LoincTable").mkdir()
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "LoincTable" / "Loinc.csv")
    run(tmp_path)
    assert LoincTerm.objects.count() == 3


# scenario: terminology-reference-data::loinc-import-records-its-version-as-source
def test_import_records_version_as_source(db):
    run(FIXTURE, version="TEST-9")
    source = Source.objects.get(name="LOINC", version="TEST-9")
    assert source.url == "https://loinc.org/license/"
    assert "unverified" in source.licence
    assert source.retrieved_at is not None
    assert set(LoincTerm.objects.values_list("source_id", flat=True)) == {source.pk}


# scenario: terminology-reference-data::malformed-loinc-release-aborts-the-import
def test_missing_column_aborts(db, tmp_path):
    (tmp_path / "Loinc.csv").write_text("LOINC_NUM,COMPONENT\nSYN-1,x\n")
    with pytest.raises(CommandError, match=r"Loinc\.csv line 1: missing column"):
        run(tmp_path)
    assert LoincTerm.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::malformed-loinc-release-aborts-the-import
def test_empty_loinc_num_rolls_back_everything(db, tmp_path):
    good = "SYN-1,SYNTHETIC TEST TERM,p,Pt,s,Qn,,C,SYNTHETIC TEST TERM,SYNTHETIC TEST TERM,ACTIVE"
    bad = " ,SYNTHETIC TEST TERM,p,Pt,s,Qn,,C,SYNTHETIC TEST TERM,SYNTHETIC TEST TERM,ACTIVE"
    (tmp_path / "Loinc.csv").write_text(f"{HEADER}\n{good}\n{bad}\n")
    with pytest.raises(CommandError, match=r"Loinc\.csv line 3: empty LOINC_NUM"):
        run(tmp_path)
    assert LoincTerm.objects.count() == 0
    assert Source.objects.count() == 0


GOOD = "SYN-1,SYNTHETIC TEST TERM,p,Pt,s,Qn,,C,SYNTHETIC TEST TERM,SYNTHETIC TEST TERM,ACTIVE"


# scenario: terminology-reference-data::malformed-loinc-release-aborts-the-import
@pytest.mark.parametrize(
    ("row", "message"),
    [
        (GOOD + ",extra", r"line 3: expected 11 fields"),
        ("SYN-2,SYNTHETIC TEST TERM", r"line 3: expected 11 fields"),
        ("X" * 11 + GOOD[5:], r"line 3: loinc_num is 11 characters, maximum 10"),
        (
            GOOD.replace("SYN-1", "SYN-2").replace(
                "TERM,ACTIVE", "S" * 101 + ",ACTIVE"
            ),
            r"line 3: short_name",
        ),
    ],
)
def test_bad_rows_abort_with_file_and_line(db, tmp_path, row, message):
    (tmp_path / "Loinc.csv").write_text(f"{HEADER}\n{GOOD}\n{row}\n")
    with pytest.raises(CommandError, match=message):
        run(tmp_path)
    assert LoincTerm.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::malformed-loinc-release-aborts-the-import
def test_overlong_release_version_rejected(db):
    with pytest.raises(CommandError, match="release-version"):
        run(FIXTURE, version="v" * 65)
    assert Source.objects.count() == 0


def test_blank_loinc_num_rejected_by_model(db):
    source = Source.objects.create(
        name="T", licence="t", url="https://example.invalid/", retrieved_at="2026-01-01"
    )
    with pytest.raises(Exception, match="loinc_num"):
        LoincTerm(loinc_num="  ", source=source).save()


# scenario: terminology-reference-data::seed-contents
def test_fixture_is_synthetic_and_outside_seed_dir():
    assert SEED_DIR not in FIXTURE.parents
    lines = (FIXTURE / "Loinc.csv").read_text().splitlines()[1:]
    for line in lines:
        cells = line.split(",")
        assert cells[8].startswith("SYNTHETIC TEST TERM")
        assert cells[9].startswith("SYNTHETIC TEST TERM")
    assert inspect_seed_dir(SEED_DIR) == []
