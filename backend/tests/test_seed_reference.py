# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from terminology.models import Source, Unit, UnitConversion
from terminology.seed_loader import SEED_DIR, inspect_seed_dir

SRC = {
    "name": "TEST FIXTURE",
    "version": "",
    "licence": "TEST LICENCE",
    "url": "https://example.invalid/fixture",
    "retrieved_at": "2026-01-01",
}


def unit(code, source=SRC):
    row = {"model": "unit", "fields": {"ucum_code": code, "display": code.upper()}}
    if source is not None:
        row["source"] = source
    return row


def conv(a, b, factor="1.5"):
    return {
        "model": "unit_conversion",
        "source": SRC,
        "fields": {"from_unit": a, "to_unit": b, "factor": factor, "biomarker": None},
    }


def write(tmp_path, name, rows):
    (tmp_path / name).write_text(json.dumps({"rows": rows}))


def counts():
    return Source.objects.count(), Unit.objects.count(), UnitConversion.objects.count()


def run(tmp_path):
    call_command("seed_reference", dir=str(tmp_path))


# scenario: terminology-reference-data::unsourced-seed-row
def test_valid_file_loads_and_is_idempotent(db, tmp_path):
    write(tmp_path, "a.json", [unit("tfx1"), unit("tfx2"), conv("tfx1", "tfx2")])
    run(tmp_path)
    first = counts()
    assert first == (1, 2, 1)
    snapshot = list(UnitConversion.objects.values("factor", "source__licence"))
    run(tmp_path)
    assert counts() == first
    assert list(UnitConversion.objects.values("factor", "source__licence")) == snapshot


# scenario: terminology-reference-data::unsourced-seed-row
def test_unsourced_row_aborts_whole_file(db, tmp_path):
    write(tmp_path, "bad.json", [unit("tfx1"), unit("tfx2", source=None)])
    with pytest.raises(CommandError) as err:
        run(tmp_path)
    assert "bad.json row 1" in str(err.value)
    assert counts() == (0, 0, 0)


@pytest.mark.parametrize("key", ["name", "licence", "url", "retrieved_at"])
@pytest.mark.parametrize("mode", ["missing", "blank"])
# scenario: terminology-reference-data::unsourced-seed-row
def test_incomplete_source_aborts(db, tmp_path, key, mode):
    src = {k: v for k, v in SRC.items() if k != key}
    if mode == "blank":
        src[key] = "   "
    write(tmp_path, "x.json", [unit("tfx1"), unit("tfx2", source=src)])
    with pytest.raises(CommandError, match=f"x.json row 1: missing source.{key}"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


def test_earlier_file_stays_committed(db, tmp_path):
    write(tmp_path, "a.json", [unit("tfx1")])
    write(tmp_path, "b.json", [unit("tfx2", source=None)])
    with pytest.raises(CommandError, match="b.json row 0"):
        run(tmp_path)
    assert counts() == (1, 1, 0)


BAD_FIELDS = {"ucum_code": "t", "display": "t", "x": 1}


@pytest.mark.parametrize(
    "row,message",
    [
        ({"model": "nope", "source": SRC, "fields": {}}, "unknown model"),
        ({"model": "unit", "source": SRC, "fields": {"ucum_code": "t"}}, "display"),
        ({"model": "unit", "source": SRC, "fields": BAD_FIELDS}, "fields: x"),
        (
            {"model": "unit", "source": {**SRC, "retrieved_at": "nope"}, "fields": {}},
            "ISO date",
        ),
        ("text", "not an object"),
        ({"model": "unit", "source": SRC}, "missing fields"),
    ],
)
def test_malformed_rows_abort(db, tmp_path, row, message):
    write(tmp_path, "m.json", [row])
    with pytest.raises(CommandError, match=message):
        run(tmp_path)


@pytest.mark.parametrize("factor", [1.5, "abc", "NaN"])
def test_factor_must_be_decimal_string(db, tmp_path, factor):
    rows = [unit("tfx1"), unit("tfx2"), conv("tfx1", "tfx2", factor)]
    write(tmp_path, "f.json", rows)
    with pytest.raises(CommandError, match="f.json row 2: factor"):
        run(tmp_path)


def test_bad_json_and_shape(db, tmp_path):
    (tmp_path / "j.json").write_text("{")
    with pytest.raises(CommandError, match="j.json: cannot read JSON"):
        run(tmp_path)
    (tmp_path / "j.json").write_text("[]")
    with pytest.raises(CommandError, match="'rows' list"):
        run(tmp_path)


def test_missing_directory(db, tmp_path):
    with pytest.raises(CommandError, match="not a directory"):
        run(tmp_path / "absent")


def test_factor_keeps_decimal_precision(db, tmp_path):
    exact = "0.123456789012"
    rows = [unit("tfx1"), unit("tfx2"), conv("tfx1", "tfx2", exact)]
    write(tmp_path, "a.json", rows)
    run(tmp_path)
    assert UnitConversion.objects.get().factor == Decimal(exact)


def test_unknown_unit_not_auto_created(db, tmp_path):
    write(tmp_path, "a.json", [unit("tfx1"), conv("tfx1", "ghost")])
    with pytest.raises(CommandError, match="a.json row 1: to unit 'ghost'"):
        run(tmp_path)
    assert counts() == (0, 0, 0)
    write(tmp_path, "a.json", [unit("tfx1"), conv("ghost", "tfx1")])
    with pytest.raises(CommandError, match="from unit 'ghost'"):
        run(tmp_path)


def test_unknown_biomarker_aborts(db, tmp_path):
    row = conv("tfx1", "tfx2")
    row["fields"]["biomarker"] = "0000-0"
    write(tmp_path, "a.json", [unit("tfx1"), unit("tfx2"), row])
    with pytest.raises(CommandError, match="biomarker '0000-0'"):
        run(tmp_path)


def test_update_changes_existing_values(db, tmp_path):
    write(tmp_path, "a.json", [unit("tfx1")])
    run(tmp_path)
    changed = {**unit("tfx1"), "fields": {"ucum_code": "tfx1", "display": "New"}}
    write(tmp_path, "a.json", [changed])
    run(tmp_path)
    assert Unit.objects.get().display == "New"


def test_output_summary(db, tmp_path, capsys):
    write(tmp_path, "a.json", [unit("tfx1")])
    run(tmp_path)
    run(tmp_path)
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "getbased_marker_mapping: created 0, updated 0",
        "unit: created 1, updated 0",
        "unit_conversion: created 0, updated 0",
        "getbased_marker_mapping: created 0, updated 0",
        "unit: created 0, updated 1",
        "unit_conversion: created 0, updated 0",
    ]


# scenario: terminology-reference-data::seed-contents
def test_inspector_flags_restricted_and_unsourced(tmp_path):
    write(tmp_path, "ok.json", [unit("tfx1")])
    write(tmp_path, "bad.json", [unit("tfx2", source={**SRC, "licence": " "})])
    (tmp_path / "LOINC.CSV").write_text("")
    (tmp_path / "sct2_Concept.txt").write_text("")
    (tmp_path / "My-SNOMED.json").write_text("{")
    problems = inspect_seed_dir(tmp_path)
    assert "bad.json row 0: missing source.licence" in problems
    assert any(p.startswith("LOINC.CSV") for p in problems)
    assert any(p.startswith("sct2_Concept.txt") for p in problems)
    assert any(p.startswith("My-SNOMED.json: licence-restricted") for p in problems)
    assert not any(p.startswith("ok.json") for p in problems)


BAD_URLS = ["TBD", "javascript:alert(1)", "ftp://example.invalid/x", "not a url"]


# scenario: terminology-reference-data::unsourced-seed-row
@pytest.mark.parametrize("url", BAD_URLS)
def test_invalid_source_url_aborts(db, tmp_path, url):
    write(tmp_path, "a.json", [unit("tfx1"), unit("tfx2", source={**SRC, "url": url})])
    with pytest.raises(CommandError, match=r"a\.json row 1: invalid source\.url"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


# scenario: terminology-reference-data::seed-contents
@pytest.mark.parametrize("url", BAD_URLS)
def test_inspector_flags_invalid_url(tmp_path, url):
    write(tmp_path, "a.json", [unit("tfx1", source={**SRC, "url": url})])
    assert inspect_seed_dir(tmp_path) == ["a.json row 0: invalid source.url"]


# scenario: terminology-reference-data::seed-contents
def test_restricted_file_in_subdirectory_is_flagged(db, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "Loinc.csv").write_text("")
    assert inspect_seed_dir(tmp_path) == [
        "sub/Loinc.csv: licence-restricted release must not be bundled"
    ]
    write(tmp_path, "a.json", [unit("tfx1")])
    with pytest.raises(CommandError, match="sub/Loinc.csv: licence-restricted"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


# scenario: terminology-reference-data::seed-contents
def test_committed_seed_dir_is_clean():
    assert inspect_seed_dir(SEED_DIR) == []


# scenario: terminology-reference-data::seed-contents
def test_command_refuses_restricted_filename(db, tmp_path):
    write(tmp_path, "x_snomed.json", [unit("tfx1")])
    with pytest.raises(CommandError, match="x_snomed.json: licence-restricted"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


@pytest.mark.parametrize("key", ["ucum_code", "display"])
@pytest.mark.parametrize("value", [None, "  ", 5, "x" * 200])
# scenario: terminology-reference-data::unsourced-seed-row
def test_bad_unit_field_values_abort(db, tmp_path, key, value):
    row = unit("tfx1")
    row["fields"][key] = value
    write(tmp_path, "u.json", [row])
    with pytest.raises(CommandError, match=f"u.json row 0: fields.{key}"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


@pytest.mark.parametrize(
    "factor",
    ["0.1234567890123", "1" + "0" * 18, "0", "-2", "0.0000000000001"],
)
def test_factor_range_and_precision_refused(db, tmp_path, factor):
    rows = [unit("tfx1"), unit("tfx2"), conv("tfx1", "tfx2", factor)]
    write(tmp_path, "f.json", rows)
    with pytest.raises(CommandError, match="f.json row 2: factor"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


def test_factor_trailing_zeros_accepted(db, tmp_path):
    rows = [unit("tfx1"), unit("tfx2"), conv("tfx1", "tfx2", "1.5000000000000")]
    write(tmp_path, "f.json", rows)
    run(tmp_path)
    assert UnitConversion.objects.get().factor == Decimal("1.5")


def test_non_string_version_refused(db, tmp_path):
    write(tmp_path, "v.json", [unit("tfx1", source={**SRC, "version": 2.81})])
    with pytest.raises(CommandError, match="v.json row 0: source.version"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


def test_conflicting_source_in_file_refused(db, tmp_path):
    other = {**SRC, "licence": "OTHER"}
    write(tmp_path, "s.json", [unit("tfx1"), unit("tfx2", source=other)])
    with pytest.raises(CommandError, match="s.json row 1: .*different licence"):
        run(tmp_path)
    assert counts() == (0, 0, 0)


def test_conflicting_source_against_db_refused(db, tmp_path):
    write(tmp_path, "a.json", [unit("tfx1")])
    run(tmp_path)
    changed = {**SRC, "url": "https://x.invalid/"}
    write(tmp_path, "a.json", [unit("tfx1", source=changed)])
    with pytest.raises(CommandError, match="different url"):
        run(tmp_path)
    assert Source.objects.get().url == SRC["url"]
