# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only unit conversion view of a stored lab result (M02 TG-l part 1)."""

from datetime import date
from decimal import Decimal, localcontext

import pytest
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


def make_source(name):
    return Source.objects.create(
        name=name,
        version="t1",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def source(db):
    return make_source("synthetic conversion fixture")


@pytest.fixture
def units(source):
    return {
        code: Unit.objects.create(ucum_code=code, display=code, source=source)
        for code in ("xa/L", "xb/L", "xc/L")
    }


@pytest.fixture
def analyte(source, units):
    return Biomarker.objects.create(
        name="synthetic 0000-0",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=units["xa/L"],
        source=source,
    )


@pytest.fixture
def result(user, analyte):
    report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    return LabResult.objects.create(
        report=report, biomarker=analyte, reported_value="3.5", reported_unit="xa/L"
    )


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def convert(user, result, unit=None):
    params = {} if unit is None else {"unit": unit}
    return client_for(user).get(f"/api/labs/results/{result.pk}/convert/", params)


def test_stored_conversion_shows_value_and_source(user, result, units, source):
    # scenario: biomarkers-and-labs::a-us-unit-result-is-shown-in-si
    UnitConversion.objects.create(
        from_unit=units["xa/L"], to_unit=units["xb/L"], factor="2.5", source=source
    )
    data = convert(user, result, "xb/L").json()
    assert data["converted"] is True
    assert Decimal(data["value"]) == Decimal("3.5") * Decimal("2.5")
    assert data["unit"] == "xb/L"
    assert Decimal(data["reported_value"]) == Decimal("3.5")
    assert data["reported_unit"] == "xa/L"
    assert data["conversion_source"] == {
        "id": source.pk,
        "name": source.name,
        "version": "t1",
        "licence": "test only",
        "url": "https://example.org/synthetic",
        "retrieved_at": "2026-11-26",
    }


def test_analyte_specific_conversion_is_preferred(user, result, units, source, analyte):
    other = make_source("specific")
    UnitConversion.objects.create(
        from_unit=units["xa/L"], to_unit=units["xb/L"], factor="2", source=source
    )
    UnitConversion.objects.create(
        from_unit=units["xa/L"],
        to_unit=units["xb/L"],
        factor="10",
        biomarker=analyte,
        source=other,
    )
    data = convert(user, result, "xb/L").json()
    assert Decimal(data["value"]) == Decimal("35")
    assert data["conversion_source"]["id"] == other.pk


def test_no_conversion_known_shows_reported_value(user, result):
    # scenario: biomarkers-and-labs::no-conversion-known
    response = convert(user, result, "xc/L")
    data = response.json()
    assert response.status_code == 200
    assert data["converted"] is False
    assert data["reason"] == "no_conversion_known"
    assert data["conversion_source"] is None
    assert (data["value"], data["unit"]) == (data["reported_value"], "xa/L")


def test_inverse_conversion_is_not_used(user, result, units, source):
    UnitConversion.objects.create(
        from_unit=units["xb/L"], to_unit=units["xa/L"], factor="2", source=source
    )
    assert convert(user, result, "xb/L").json()["reason"] == "no_conversion_known"


def test_same_unit(user, result):
    data = convert(user, result, "xa/L").json()
    assert data["converted"] is False
    assert data["reason"] == "same_unit"
    assert data["conversion_source"] is None


def test_retracted_result_is_viewable(user, result):
    result.set_validation_state(LabResultValidation.RETRACTED)
    assert convert(user, result, "xa/L").status_code == 200


def test_unauthenticated_and_other_user(user, result):
    url = f"/api/labs/results/{result.pk}/convert/"
    assert APIClient().get(url, {"unit": "xa/L"}).status_code in (401, 403)
    other = User.objects.create_user(email="b@example.com", password="correct-horse-9")
    assert convert(other, result, "xa/L").status_code == 404


@pytest.mark.parametrize("unit", [None, "", "x" * 65, "nope/L", "a\x00b"])
def test_bad_unit_is_400_naming_unit(user, result, unit):
    response = convert(user, result, unit)
    assert response.status_code == 400
    assert "unit" in response.json()


def test_nothing_is_written(user, result, units, source):
    UnitConversion.objects.create(
        from_unit=units["xa/L"], to_unit=units["xb/L"], factor="2", source=source
    )
    before = LabResult.objects.filter(pk=result.pk).values().get()
    convert(user, result, "xb/L")
    assert LabResult.objects.filter(pk=result.pk).values().get() == before


def test_conversion_is_exact_beyond_28_digits(user, analyte, units, source):
    report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    big = LabResult.objects.create(
        report=report,
        biomarker=analyte,
        reported_value="12345678901234.123456",
        reported_unit="xa/L",
    )
    factor = "123456789012345678.123456789012"
    UnitConversion.objects.create(
        from_unit=units["xa/L"], to_unit=units["xb/L"], factor=factor, source=source
    )
    data = convert(user, big, "xb/L").json()
    with localcontext() as ctx:
        ctx.prec = 100
        expected = Decimal("12345678901234.123456") * Decimal(factor)
    assert len(expected.as_tuple().digits) > 28
    assert Decimal(data["value"]) == expected
