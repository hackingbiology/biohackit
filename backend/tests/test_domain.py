# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    Intervention,
    InterventionSubtype,
    Measurement,
)


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="m@example.com", password="correct-horse-battery-9"
    )


@pytest.fixture
def biomarker(db):
    return Biomarker.objects.create(
        name="hs-CRP", loinc_code="30522-7", role=BiomarkerRole.SAFETY, unit_ucum="mg/L"
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
