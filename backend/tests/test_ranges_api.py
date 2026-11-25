# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ranges read API. All values are synthetic test fixtures, not reference data."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole
from terminology.models import (
    OptimalRange,
    ReferenceRange,
    SafetyThreshold,
    Source,
    Unit,
)

URL = "/api/terminology/biomarkers/TEST-1/ranges/"
SOURCE_KEYS = {"name", "version", "licence", "url", "retrieved_at"}


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="test fixture",
        licence="test only",
        url="https://example.org/test-fixture",
        retrieved_at=date(2026, 11, 25),
    )


@pytest.fixture
def unit(source):
    return Unit.objects.create(ucum_code="mg/L", display="mg/L", source=source)


@pytest.fixture
def biomarker(unit, source):
    return Biomarker.objects.create(
        name="test analyte",
        loinc_code="TEST-1",
        role=BiomarkerRole.SAFETY,
        unit=unit,
        source=source,
    )


@pytest.fixture
def client(db):
    user = User.objects.create_user(
        email="r@example.com", password="correct-horse-battery-9"
    )
    api = APIClient()
    api.force_authenticate(user)
    return api


def make(model, biomarker, unit, source, low, high, **kw):
    return model.objects.create(
        biomarker=biomarker,
        unit=unit,
        source=source,
        low=Decimal(low),
        high=Decimal(high),
        **kw,
    )


def optimal(biomarker, unit, source, **kw):
    fields = {
        "population": "synthetic population",
        "endpoint": "synthetic endpoint",
        "evidence_grade": "synthetic grade",
        "last_reviewed": date(2026, 1, 1),
        **kw,
    }
    return make(OptimalRange, biomarker, unit, source, "14", "16", **fields)


# scenario: terminology-reference-data::reference-normal-but-optimal-out
def test_reference_within_while_optimal_above(client, biomarker, unit, source):
    make(ReferenceRange, biomarker, unit, source, "10", "20")
    optimal(biomarker, unit, source)
    body = client.get(URL, {"value": "18"}).json()
    assert body["reference"][0]["status"] == "within"
    assert body["optimal"]["status"] == "above"
    assert body["value"] == "18"


# scenario: terminology-reference-data::complete-provenance
def test_complete_optimal_returned_with_all_provenance(client, biomarker, unit, source):
    optimal(biomarker, unit, source)
    opt = client.get(URL).json()["optimal"]
    assert set(opt["source"]) == SOURCE_KEYS
    assert opt["source"]["name"] == "test fixture"
    assert opt["unit"] == "mg/L"
    assert opt["low"] == "14.000000"  # decimals are strings
    for key in ("population", "endpoint", "evidence_grade", "last_reviewed"):
        assert opt[key]
    assert opt["status"] is None


# scenario: terminology-reference-data::incomplete-provenance
def test_optimal_without_endpoint_is_null_over_http(client, biomarker, unit, source):
    optimal(biomarker, unit, source, endpoint=None)
    body = client.get(URL, {"value": "15"}).json()
    assert body["optimal"] is None
    assert "synthetic population" not in str(body)


def test_reference_and_safety_shape(client, biomarker, unit, source):
    make(ReferenceRange, biomarker, unit, source, "10", "20", lab="L", method="M")
    make(SafetyThreshold, biomarker, unit, source, "1", "50")
    body = client.get(URL, {"value": "60"}).json()
    ref, safe = body["reference"][0], body["safety"][0]
    assert (ref["lab"], ref["method"], ref["population"]) == ("L", "M", "")
    assert set(ref["source"]) == SOURCE_KEYS
    assert ref["status"] == "above" and safe["status"] == "above"
    assert body["biomarker"] == {
        "loinc_code": "TEST-1",
        "name": "test analyte",
        "unit": "mg/L",
    }


@pytest.mark.parametrize("value", ["10", "20"])
def test_bounds_are_inclusive(client, biomarker, unit, source, value):
    make(ReferenceRange, biomarker, unit, source, "10", "20")
    body = client.get(URL, {"value": value}).json()
    assert body["reference"][0]["status"] == "within"


def test_below(client, biomarker, unit, source):
    make(ReferenceRange, biomarker, unit, source, "10", "20")
    assert client.get(URL, {"value": "9.9"}).json()["reference"][0]["status"] == "below"


def test_no_value_gives_null_status(client, biomarker, unit, source):
    make(ReferenceRange, biomarker, unit, source, "10", "20")
    body = client.get(URL).json()
    assert body["reference"][0]["status"] is None
    assert body["value"] is None


def test_biomarker_without_ranges(client, biomarker):
    r = client.get(URL)
    assert r.status_code == 200
    body = r.json()
    assert (body["reference"], body["optimal"], body["safety"]) == ([], None, [])


@pytest.mark.parametrize("value", ["abc", "NaN", "Infinity", "-Infinity", ""])
def test_bad_value_is_400(client, biomarker, value):
    r = client.get(URL, {"value": value})
    assert r.status_code == 400
    assert "value" in r.json()


def test_unknown_code_is_404(client, biomarker):
    assert client.get("/api/terminology/biomarkers/NOPE/ranges/").status_code == 404


def test_anonymous_rejected(biomarker):
    assert APIClient().get(URL).status_code in (401, 403)


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_write_methods_not_allowed(client, biomarker, method):
    assert getattr(client, method)(URL).status_code == 405
