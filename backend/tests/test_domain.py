# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date, timedelta
from decimal import Decimal
from importlib import import_module
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    Intervention,
    InterventionSubtype,
    Measurement,
)
from terminology.models import Source, Unit, UnitConversion

migration_0003 = import_module("core.migrations.0004_coded_biomarker_data")


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="m@example.com", password="correct-horse-battery-9"
    )


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="test fixture",
        licence="test only",
        url="https://example.org/test-fixture",
        retrieved_at=date(2026, 11, 25),
    )


@pytest.fixture
def mg_l(source):
    return Unit.objects.create(ucum_code="mg/L", display="mg/L", source=source)


@pytest.fixture
def biomarker(mg_l, source):
    return Biomarker.objects.create(
        name="hs-CRP",
        loinc_code="30522-7",
        role=BiomarkerRole.SAFETY,
        unit=mg_l,
        source=source,
    )


def make(user, biomarker, **kw):
    return Measurement.objects.create(
        user=user,
        biomarker=biomarker,
        time=kw.pop("time", timezone.now()),
        value="1.2",
        unit_ucum="mg/L",
        source="manual",
        **kw,
    )


def test_intervention_cycle_schema_stored(db):
    schema = {"pattern": "pulsed", "on_days": [1, 2, 3]}
    i = Intervention.objects.create(
        name="dasatinib 100 mg",
        subtype=InterventionSubtype.SUBSTANCE,
        cycle_schema=schema,
    )
    i.refresh_from_db()
    assert i.cycle_schema == schema


# scenario: domain-model::method-and-lab-are-mandatory-metadata
# scenario: biomarkers-and-labs::coding-is-mandatory-for-a-measurement
def test_measurement_aggregation_eligibility(user, biomarker):
    full = make(user, biomarker, laboratory="Lab X", method="immunoturbidimetry")
    no_method = make(user, biomarker, laboratory="Lab X")
    none = make(user, biomarker)
    assert full.is_aggregation_eligible is True
    assert no_method.is_aggregation_eligible is False
    assert none.is_aggregation_eligible is False


def test_measurement_hypertable_insert(user, biomarker):
    now = timezone.now()
    make(user, biomarker, time=now)
    hit = Measurement.objects.filter(
        time__gte=now - timedelta(hours=1), time__lte=now + timedelta(hours=1)
    )
    assert hit.count() == 1


def test_measurement_table_is_hypertable(db):
    with connection.cursor() as c:
        c.execute(
            "SELECT count(*) FROM timescaledb_information.hypertables WHERE hypertable_name='core_measurement'"
        )
        assert c.fetchone()[0] == 1


def test_biomarker_roles_distinct():
    assert {r.value for r in BiomarkerRole} == {"efficacy", "safety", "baseline"}


def _biomarker(**kw):
    return Biomarker(name="x", role=BiomarkerRole.SAFETY, **kw)


# scenario: terminology-reference-data::missing-code
def test_biomarker_without_loinc_code_fails(mg_l, source):
    with pytest.raises(ValidationError, match="LOINC"):
        _biomarker(loinc_code="", unit=mg_l, source=source).save()


# scenario: terminology-reference-data::blank-loinc-code
def test_biomarker_with_whitespace_loinc_code_fails(mg_l, source):
    with pytest.raises(ValidationError, match="LOINC"):
        _biomarker(loinc_code="   ", unit=mg_l, source=source).save()


# scenario: terminology-reference-data::blank-loinc-code
def test_measurement_with_whitespace_loinc_code_fails(user, biomarker):
    biomarker.loinc_code = "   "
    with pytest.raises(ValidationError, match="coded analyte"):
        _unsaved_measurement(user, biomarker).save()


# scenario: terminology-reference-data::missing-code
def test_biomarker_without_unit_fails(source):
    with pytest.raises(ValidationError, match="UCUM unit"):
        _biomarker(loinc_code="TEST-1", source=source).save()


# scenario: terminology-reference-data::missing-code
def test_biomarker_without_source_fails(mg_l):
    with pytest.raises(ValidationError, match="source"):
        _biomarker(loinc_code="TEST-1", unit=mg_l).save()


def test_biomarker_loinc_code_is_unique(biomarker, mg_l, source):
    with pytest.raises(IntegrityError), transaction.atomic():
        _biomarker(loinc_code=biomarker.loinc_code, unit=mg_l, source=source).save()


def _unsaved_measurement(user, biomarker, unit_ucum="mg/L"):
    return Measurement(
        user=user,
        biomarker=biomarker,
        time=timezone.now(),
        value="1",
        unit_ucum=unit_ucum,
        source="manual",
    )


# scenario: terminology-reference-data::missing-code
# scenario: biomarkers-and-labs::coding-is-mandatory-for-a-measurement
def test_measurement_with_unstored_unit_fails(user, biomarker):
    with pytest.raises(ValidationError, match="Unknown UCUM unit"):
        _unsaved_measurement(user, biomarker, "furlongs").save()
    assert Measurement.objects.count() == 0


# scenario: terminology-reference-data::missing-code
def test_measurement_with_uncoded_analyte_fails(user, biomarker):
    biomarker.loinc_code = ""
    with pytest.raises(ValidationError, match="coded analyte"):
        _unsaved_measurement(user, biomarker).save()


# scenario: terminology-reference-data::missing-code
def test_measurement_with_analyte_without_unit_fails(user):
    analyte = _biomarker(loinc_code="TEST-1")
    with pytest.raises(ValidationError, match="coded analyte"):
        _unsaved_measurement(user, analyte).save()


def test_measurement_without_stored_conversion_fails(user, biomarker, source):
    Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    with pytest.raises(ValidationError, match="No conversion g/L -> mg/L"):
        _unsaved_measurement(user, biomarker, "g/L").save()


def test_measurement_in_convertible_unit_keeps_as_reported(user, biomarker, source):
    g_l = Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    # Synthetic test-only factor, not reference data.
    UnitConversion.objects.create(
        from_unit=g_l, to_unit=biomarker.unit, factor=Decimal("2"), source=source
    )
    _unsaved_measurement(user, biomarker, "g/L").save()
    m = Measurement.objects.get()
    assert (m.value, m.unit_ucum) == (Decimal("1"), "g/L")


def _fake_apps(rows, units, sources):
    def model(items):
        return SimpleNamespace(
            objects=SimpleNamespace(
                all=lambda: items, filter=lambda **kw: _FilterResult(items, kw)
            )
        )

    models_ = {"Biomarker": model(rows), "Unit": model(units), "Source": model(sources)}
    return SimpleNamespace(get_model=lambda _app, name: models_[name])


class _FilterResult(list):
    def __init__(self, items, kw):
        super().__init__(i for i in items if i.name == kw["name"])


def _row(pk, loinc_code, unit_ucum):
    saved: list[str] = []
    return SimpleNamespace(
        pk=pk,
        loinc_code=loinc_code,
        unit_ucum=unit_ucum,
        save=lambda update_fields: saved.extend(update_fields),
        saved=saved,
    )


def test_migration_0004_empty_table_is_noop():
    migration_0003.map_units(_fake_apps([], [], []), None)


def test_migration_0004_fails_loudly_naming_uncoded_rows(monkeypatch):
    monkeypatch.setenv(migration_0003.SOURCE_ENV, "s")
    rows = [_row(7, "", "mg/L"), _row(8, "TEST-1", "furlongs")]
    unit = SimpleNamespace(ucum_code="mg/L")
    apps = _fake_apps(rows, [unit], [SimpleNamespace(name="s")])
    with pytest.raises(RuntimeError) as exc:
        migration_0003.map_units(apps, None)
    msg = str(exc.value)
    assert "no loinc_code: ids [7]" in msg
    assert "no stored terminology.Unit: ids [8]" in msg
    assert rows[0].loinc_code == ""
    assert rows[0].saved == []


def test_migration_0004_treats_whitespace_code_as_uncoded(monkeypatch):
    monkeypatch.setenv(migration_0003.SOURCE_ENV, "s")
    rows = [_row(3, "  ", "mg/L")]
    apps = _fake_apps(
        rows, [SimpleNamespace(ucum_code="mg/L")], [SimpleNamespace(name="s")]
    )
    with pytest.raises(RuntimeError, match=r"no loinc_code: ids \[3\]"):
        migration_0003.map_units(apps, None)


def test_migration_0004_names_rows_sharing_a_loinc_code(monkeypatch):
    monkeypatch.setenv(migration_0003.SOURCE_ENV, "s")
    rows = [
        _row(4, "TEST-1", "mg/L"),
        _row(5, "TEST-1", "mg/L"),
        _row(6, "TEST-2", "mg/L"),
    ]
    apps = _fake_apps(
        rows, [SimpleNamespace(ucum_code="mg/L")], [SimpleNamespace(name="s")]
    )
    with pytest.raises(RuntimeError) as exc:
        migration_0003.map_units(apps, None)
    assert "duplicate loinc_code TEST-1: ids [4, 5]" in str(exc.value)
    assert "TEST-2" not in str(exc.value)
    assert rows[0].saved == []


def test_migration_0004_never_infers_the_source(monkeypatch):
    monkeypatch.delenv(migration_0003.SOURCE_ENV, raising=False)
    rows = [_row(1, "TEST-1", "mg/L")]
    unit = SimpleNamespace(ucum_code="mg/L")
    only_source = SimpleNamespace(name="only")
    apps = _fake_apps(rows, [unit], [only_source])
    with pytest.raises(RuntimeError, match="BIOHACK_LEGACY_BIOMARKER_SOURCE"):
        migration_0003.map_units(apps, None)
    assert rows[0].saved == []


def test_migration_0004_maps_unit_and_named_source(monkeypatch):
    monkeypatch.setenv(migration_0003.SOURCE_ENV, "named")
    rows = [_row(1, "TEST-1", "mg/L")]
    unit, src = SimpleNamespace(ucum_code="mg/L"), SimpleNamespace(name="named")
    other = SimpleNamespace(name="other")
    migration_0003.map_units(_fake_apps(rows, [unit], [other, src]), None)
    assert (rows[0].unit, rows[0].source) == (unit, src)
    assert rows[0].saved == ["unit", "source"]


@pytest.mark.django_db(transaction=True)
def test_migrations_apply_on_postgres_with_one_coded_row(monkeypatch):
    """Real DB: data step then ALTERs must not hit 'pending trigger events'."""
    from django.db.migrations.executor import MigrationExecutor

    monkeypatch.setenv(migration_0003.SOURCE_ENV, "test fixture")
    executor = MigrationExecutor(connection)
    before = [("core", "0002_measurement_hypertable")]
    latest = executor.loader.graph.leaf_nodes()
    executor.migrate(before)
    old = MigrationExecutor(connection).loader.project_state(before).apps
    src = Source.objects.create(
        name="test fixture",
        licence="test only",
        url="https://example.org/test-fixture",
        retrieved_at=date(2026, 11, 25),
    )
    Unit.objects.create(ucum_code="mg/L", display="mg/L", source=src)
    old.get_model("core", "Biomarker").objects.create(
        name="legacy", loinc_code="TEST-1", unit_ucum="mg/L", role="safety"
    )
    try:
        MigrationExecutor(connection).migrate(latest)
        row = Biomarker.objects.get()
        assert (row.unit.ucum_code, row.source.name) == ("mg/L", "test fixture")
    finally:
        Biomarker.objects.all().delete()
        MigrationExecutor(connection).migrate(latest)
