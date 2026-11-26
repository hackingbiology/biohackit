# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lab result validation states (Q63): eligibility rule, owner endpoint, data mapping.
Synthetic rows only."""

import importlib
from datetime import date
from decimal import Decimal

import pytest
from django.apps import apps
from rest_framework.test import APIClient

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from terminology.models import Source, Unit, UnitConversion

STATES = ["entered", "user_confirmed", "source_verified", "disputed", "retracted"]
migration = importlib.import_module("core.migrations.0009_lab_result_validation_states")


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def other(db):
    return User.objects.create_user(email="b@example.com", password="correct-horse-9")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


@pytest.fixture
def analyte(db):
    source = Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )
    unit = Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)
    return Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


def make(owner, analyte, state="entered", laboratory="Lab X", method="Method Y"):
    report = LabReport.objects.create(owner=owner, origin=LabReportOrigin.MANUAL)
    return LabResult.objects.create(
        report=report,
        biomarker=analyte,
        reported_value=Decimal("2"),
        reported_unit="xa/L",
        laboratory=laboratory,
        method=method,
        validation_state=state,
    )


def url(row):
    return f"/api/labs/results/{row.pk}/validation/"


def test_state_values_and_default():
    assert LabResultValidation.values == STATES
    field = LabResult._meta.get_field("validation_state")
    assert field.default == "entered"
    assert all(len(v) <= field.max_length for v in STATES)


def test_new_manual_result_starts_as_entered(client, analyte):
    # scenario: biomarkers-and-labs::a-new-result-starts-as-entered
    body = {
        "results": [
            {"loinc_code": "0000-0", "reported_value": "2", "reported_unit": "xa/L"}
        ]
    }
    resp = client.post("/api/labs/reports/", body, format="json")
    assert resp.status_code == 201
    assert resp.json()["results"][0]["validation_state"] == "entered"
    assert LabResult.objects.get().validation_state == "entered"


@pytest.mark.parametrize("state", STATES)
def test_only_confirmed_results_are_eligible(user, analyte, state):
    # scenario: biomarkers-and-labs::only-confirmed-results-are-aggregation-eligible
    row = make(user, analyte, state)
    assert row.aggregation_eligible is (state in ("user_confirmed", "source_verified"))
    bare = make(user, analyte, state, laboratory=None, method=None)
    assert bare.aggregation_eligible is False


def test_retracted_result_is_kept_but_excluded(client, user, analyte):
    # scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
    row = make(user, analyte, "user_confirmed")
    assert row.aggregation_eligible is True
    resp = client.patch(url(row), {"validation_state": "retracted"}, format="json")
    assert resp.status_code == 200
    kept = LabResult.objects.get(pk=row.pk)
    assert kept.reported_value == Decimal("2")
    assert kept.aggregation_eligible is False


def test_owner_confirms_a_result(client, user, analyte):
    # scenario: biomarkers-and-labs::the-owner-confirms-a-result
    row = make(user, analyte)
    resp = client.patch(url(row), {"validation_state": "user_confirmed"}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_state"] == "user_confirmed"
    assert data["aggregation_eligible"] is True
    assert LabResult.objects.get(pk=row.pk).aggregation_eligible is True


def test_confirming_without_method_is_not_eligible(client, user, analyte):
    # scenario: biomarkers-and-labs::the-owner-confirms-a-result
    row = make(user, analyte, method=None)
    resp = client.patch(url(row), {"validation_state": "user_confirmed"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["aggregation_eligible"] is False


def test_other_users_result_is_404_and_unchanged(client, other, analyte):
    # scenario: biomarkers-and-labs::the-owner-confirms-a-result
    row = make(other, analyte)
    resp = client.patch(url(row), {"validation_state": "user_confirmed"}, format="json")
    assert resp.status_code == 404
    assert LabResult.objects.get(pk=row.pk).validation_state == "entered"
    assert (
        client.patch(
            "/api/labs/results/99999/validation/", {}, format="json"
        ).status_code
        == 404
    )


def test_requires_authentication(user, analyte):
    row = make(user, analyte)
    resp = APIClient().patch(url(row), {"validation_state": "disputed"}, format="json")
    assert resp.status_code in (401, 403)


@pytest.mark.parametrize("value", ["source_verified", "entered", "bogus", None, 3])
def test_owner_cannot_set_other_states(client, user, analyte, value):
    # scenario: biomarkers-and-labs::source-verification-cannot-be-self-declared
    row = make(user, analyte)
    resp = client.patch(url(row), {"validation_state": value}, format="json")
    assert resp.status_code == 400
    assert "validation_state" in resp.json()
    assert LabResult.objects.get(pk=row.pk).validation_state == "entered"


def test_retracted_stays_retracted(client, user, analyte):
    # scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
    row = make(user, analyte, "retracted")
    resp = client.patch(url(row), {"validation_state": "user_confirmed"}, format="json")
    assert resp.status_code == 400
    assert "validation_state" in resp.json()
    assert LabResult.objects.get(pk=row.pk).validation_state == "retracted"


def test_disputed_can_be_confirmed_again(client, user, analyte):
    row = make(user, analyte, "disputed")
    resp = client.patch(url(row), {"validation_state": "user_confirmed"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["aggregation_eligible"] is True


def test_data_migration_maps_old_states_and_recomputes(user, analyte):
    old = make(user, analyte)
    LabResult.objects.filter(pk=old.pk).update(
        validation_state="reviewed", aggregation_eligible=False
    )
    unreviewed = make(user, analyte)
    LabResult.objects.filter(pk=unreviewed.pk).update(
        validation_state="unreviewed", aggregation_eligible=True
    )
    migration.forwards(apps, None)
    assert LabResult.objects.get(pk=old.pk).validation_state == "user_confirmed"
    assert LabResult.objects.get(pk=old.pk).aggregation_eligible is True
    assert LabResult.objects.get(pk=unreviewed.pk).validation_state == "entered"
    assert LabResult.objects.get(pk=unreviewed.pk).aggregation_eligible is False
    migration.backwards(apps, None)
    assert LabResult.objects.get(pk=old.pk).validation_state == "reviewed"
    assert LabResult.objects.get(pk=unreviewed.pk).validation_state == "unreviewed"
    assert LabResult.objects.get(pk=unreviewed.pk).aggregation_eligible is True


def test_migration_reverse_refuses_unmappable_states(user, analyte):
    make(user, analyte, "disputed")
    with pytest.raises(RuntimeError, match="Cannot reverse"):
        migration.backwards(apps, None)
    assert LabResult.objects.get().validation_state == "disputed"


def test_state_change_keeps_stored_normalisation(client, user, analyte):
    # scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
    unit_b = Unit.objects.create(
        ucum_code="xb/L", display="xb/L", source=analyte.source
    )
    factor = UnitConversion.objects.create(
        from_unit=unit_b,
        to_unit=analyte.unit,
        factor=Decimal("3"),
        source=analyte.source,
    )
    row = make(user, analyte, "user_confirmed")
    row.reported_unit = "xb/L"
    row.reported_value = Decimal("5")
    row.save()
    assert row.normalised_value == Decimal("15")
    factor.factor = Decimal("4")  # a later change must not touch stored values
    factor.save()
    resp = client.patch(url(row), {"validation_state": "retracted"}, format="json")
    assert resp.status_code == 200
    kept = LabResult.objects.get(pk=row.pk)
    assert kept.validation_state == "retracted"
    assert kept.normalised_value == Decimal("15")
    assert kept.normalised_source == analyte.source
