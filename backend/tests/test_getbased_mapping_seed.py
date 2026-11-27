# SPDX-License-Identifier: AGPL-3.0-or-later
"""Loading GetbasedMarkerMapping rows through seed_reference (X01 part 2c). Every code, key
and commit here is a synthetic test fixture, never seed data (Q91, Q79)."""

import json
from datetime import date

import pytest
from django.core.management import call_command

from core.getbased_import import build_preview
from core.models import Biomarker, BiomarkerRole, GetbasedMarkerMapping
from terminology.models import Source, Unit
from terminology.seed_loader import SeedError, inspect_seed_dir, load_dir

SRC = {
    "name": "TEST FIXTURE",
    "version": "",
    "licence": "TEST LICENCE",
    "url": "https://example.invalid/fixture",
    "retrieved_at": "2026-01-01",
}
SHA = "c" * 40
PATH = "js/marker-schema/test-fixture.ts"
LOINC = "0000-0"  # synthetic fixture code, not a real LOINC code
UCUM = "xa/L"  # synthetic fixture unit
NO_CITATION = {"unit": None, "unit_source_path": None, "unit_source_commit": None}


@pytest.fixture
def base(db):
    source = Source.objects.create(
        name="fixture base",
        licence="test only",
        url="https://example.org/base",
        retrieved_at=date(2026, 1, 1),
    )
    unit = Unit.objects.create(ucum_code=UCUM, display=UCUM, source=source)
    Biomarker.objects.create(
        name="fixture analyte",
        loinc_code=LOINC,
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


def measured(key="fx.a", **over):
    fields = {
        "getbased_key": key,
        "kind": "measured",
        "biomarker": LOINC,
        "unit": UCUM,
        "unit_source_path": PATH,
        "unit_source_commit": SHA,
    }
    fields.update(over)
    return {"model": "getbased_marker_mapping", "source": SRC, "fields": fields}


def calculated(key="calculatedRatios.fx", **over):
    fields = {
        "getbased_key": key,
        "kind": "calculated",
        "biomarker": None,
        **NO_CITATION,
    }
    fields.update(over)
    return {"model": "getbased_marker_mapping", "source": SRC, "fields": fields}


def write(tmp_path, name, rows):
    (tmp_path / name).write_text(json.dumps({"rows": rows}))


def snapshot():
    return list(
        GetbasedMarkerMapping.objects.order_by("getbased_key").values_list(
            "getbased_key",
            "kind",
            "biomarker__loinc_code",
            "unit__ucum_code",
            "unit_source_path",
            "unit_source_commit",
            "source_id",
        )
    )


def export_with(markers):
    body = {
        "version": 2,
        "profile": {},
        "entries": [{"date": "2026-01-02", "markers": markers}],
    }
    return json.dumps(body).encode()


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
def test_valid_file_loads_and_is_idempotent(base, tmp_path):
    write(tmp_path, "a.json", [measured(), calculated()])
    assert "getbased_marker_mapping: created 2, updated 0" in load_dir(tmp_path)
    first = snapshot()
    assert len(first) == 2
    assert "getbased_marker_mapping: created 0, updated 2" in load_dir(tmp_path)
    assert snapshot() == first
    assert inspect_seed_dir(tmp_path) == []


CASES = [
    ("no_source", lambda: {**measured(), "source": None}, "missing source"),
    (
        "unknown_biomarker",
        lambda: measured(biomarker="9999-9"),
        "biomarker '9999-9' does not exist",
    ),
    (
        "calculated_with_biomarker",
        lambda: calculated(biomarker=LOINC),
        "calculated row",
    ),
    ("calculated_with_unit", lambda: calculated(unit=UCUM), "calculated row"),
    (
        "measured_ratio_key",
        lambda: measured(key="calculatedRatios.fx"),
        "can only be a calculated row",
    ),
    (
        "unit_without_citation",
        lambda: measured(unit_source_path=None, unit_source_commit=None),
        "set together or not at all",
    ),
    ("bad_commit", lambda: measured(unit_source_commit="C" * 40), "40 lowercase hex"),
    ("short_commit", lambda: measured(unit_source_commit="short"), "40 lowercase hex"),
    ("unknown_kind", lambda: measured(kind="derived"), "kind must be"),
    ("blank_key", lambda: measured(key=" "), "getbased_key must be a non-blank"),
    ("unknown_unit", lambda: measured(unit="nope/L"), "unit 'nope/L' does not exist"),
    (
        "measured_no_biomarker",
        lambda: measured(biomarker=None),
        "biomarker is required",
    ),
]


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
@pytest.mark.parametrize(
    ("make", "expected"), [(c[1], c[2]) for c in CASES], ids=[c[0] for c in CASES]
)
def test_invalid_row_aborts_only_its_file(base, tmp_path, make, expected):
    write(tmp_path, "a.json", [measured("fx.ok")])
    write(tmp_path, "b.json", [measured("fx.first"), make()])
    with pytest.raises(SeedError) as exc:
        load_dir(tmp_path)
    message = str(exc.value)
    assert message.startswith("b.json row 1: ")
    assert expected in message
    keys = list(GetbasedMarkerMapping.objects.values_list("getbased_key", flat=True))
    assert keys == ["fx.ok"]


def test_update_changes_existing_row(base, tmp_path):
    write(tmp_path, "a.json", [measured()])
    load_dir(tmp_path)
    write(tmp_path, "a.json", [measured(**NO_CITATION)])
    assert "getbased_marker_mapping: created 0, updated 1" in load_dir(tmp_path)
    row = GetbasedMarkerMapping.objects.get()
    assert row.unit is None and row.unit_source_commit == ""


def test_command_loads_mapping_rows(base, tmp_path):
    write(tmp_path, "a.json", [measured()])
    call_command("seed_reference", dir=str(tmp_path))
    assert GetbasedMarkerMapping.objects.count() == 1


def test_inspect_ignores_other_rows_and_reports_bad_source(tmp_path):
    write(
        tmp_path,
        "a.json",
        [{"model": "unit", "fields": {}}, "x", {**measured(), "source": {}}],
    )
    problems = inspect_seed_dir(tmp_path)
    assert all("warning" not in p for p in problems)
    assert any("a.json row 2: missing source.name" in p for p in problems)


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
# scenario: biomarkers-and-labs::markers-matched-through-a-cited-mapping-or-not-recognised
def test_measured_without_unit_loads_warns_and_is_unit_not_verified(base, tmp_path):
    write(tmp_path, "a.json", [measured("fx.nounit", **NO_CITATION)])
    load_dir(tmp_path)
    row = GetbasedMarkerMapping.objects.get()
    assert (
        row.unit is None and row.unit_source_path == "" and row.unit_source_commit == ""
    )
    assert inspect_seed_dir(tmp_path) == [
        "a.json row 0: warning: measured key 'fx.nounit' has no unit citation"
    ]
    (out,) = build_preview(export_with({"fx.nounit": 1}))["rows"]
    assert out["reason"] == "not recognised: unit not verified"


# scenario: biomarkers-and-labs::markers-matched-through-a-cited-mapping-or-not-recognised
# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_loaded_rows_drive_the_preview(base, tmp_path):
    write(tmp_path, "a.json", [measured("fx.a"), calculated("fx.deny")])
    load_dir(tmp_path)
    rows = {
        r["marker"]: r
        for r in build_preview(export_with({"fx.a": 5, "fx.deny": 7}))["rows"]
    }
    assert rows["fx.a"]["status"] == "matched"
    assert rows["fx.a"]["loinc_code"] == LOINC
    assert rows["fx.a"]["unit"] == UCUM
    assert rows["fx.a"]["unit_source"] == f"{PATH}@{SHA}"
    assert rows["fx.deny"]["reason"] == "not imported: calculated"
