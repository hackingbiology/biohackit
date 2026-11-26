# SPDX-License-Identifier: AGPL-3.0-or-later
"""Manual lab entry API (M02 TG-b). Synthetic rows only: no real ranges or factors."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from core.plausibility import RangeCandidate, check_plausibility
from terminology.models import ReferenceRange, Source, Unit, UnitConversion

URL = "/api/labs/reports/"


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
def source(db):
    return Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def unit_a(source):
    return Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)


@pytest.fixture
def unit_b(source):
    return Unit.objects.create(ucum_code="xb/L", display="xb/L", source=source)


@pytest.fixture
def analyte(unit_a, source):
    return Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit_a,
        source=source,
    )


def body(**item):
    item.setdefault("loinc_code", "0000-0")
    item.setdefault("reported_value", "2.5")
    item.setdefault("reported_unit", "xa/L")
    return {"results": [item]}


def test_requires_authentication(db, analyte):
    resp = APIClient().post(URL, body(), format="json")
    assert resp.status_code in (401, 403)
    assert LabReport.objects.count() == 0


def test_other_users_report_is_404(client, other, analyte):
    report = LabReport.objects.create(owner=other, origin=LabReportOrigin.MANUAL)
    assert client.get(f"{URL}{report.pk}/").status_code == 404


def test_owner_can_read_report(client, analyte):
    created = client.post(URL, body(), format="json").json()
    got = client.get(f"{URL}{created['id']}/")
    assert got.status_code == 200
    assert Decimal(got.json()["results"][0]["reported_value"]) == Decimal("2.5")


# scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
@pytest.mark.parametrize(
    "extra",
    [
        {"laboratory": "Lab X", "method": "Method Y", "device": "D1"},
        {"laboratory": "Lab X"},
        {},
    ],
)
def test_typed_value_equals_directly_created(client, user, analyte, extra):
    resp = client.post(
        URL,
        {**body(), "laboratory": None, "results": [body(**extra)["results"][0]]},
        format="json",
    )
    assert resp.status_code == 201
    data = resp.json()
    report = LabReport.objects.get(pk=data["id"])
    assert report.origin == "manual" and report.owner == user
    stored = LabResult.objects.get(report=report)
    direct_report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    direct = LabResult.objects.create(
        report=direct_report,
        biomarker=analyte,
        reported_value=Decimal("2.5"),
        reported_unit="xa/L",
        **extra,
    )
    for name in (
        "laboratory",
        "method",
        "device",
        "reported_value",
        "reported_unit",
        "validation_state",
        "aggregation_eligible",
        "normalised_value",
    ):
        assert getattr(stored, name) == getattr(direct, name), name
    row = data["results"][0]
    assert row["validation_state"] == "unreviewed"
    assert row["aggregation_eligible"] is direct.aggregation_eligible
    assert row["aggregation_eligible"] is bool(
        extra.get("laboratory") and extra.get("method")
    )


# scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
def test_overlong_reported_value_is_rejected_and_nothing_stored(client, analyte):
    # '1.' + 39 zeros is an exact value the model would store, so only the
    # length bound can reject it.
    resp = client.post(URL, body(reported_value="1." + "0" * 39), format="json")
    assert resp.status_code == 400
    message = resp.json()["results"]["0"]["reported_value"][0]
    assert "too long" in message
    assert LabReport.objects.count() == 0 and LabResult.objects.count() == 0


# scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
def test_reported_value_of_exactly_40_characters_passes_the_length_check(
    client, analyte
):
    value = "1." + "0" * 38
    assert len(value) == 40
    resp = client.post(URL, body(reported_value=value), format="json")
    assert resp.status_code == 201
    assert Decimal(resp.json()["results"][0]["reported_value"]) == Decimal("1")


# scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
def test_too_many_results_is_rejected_and_nothing_stored(client, analyte):
    item = body()["results"][0]
    resp = client.post(URL, {"results": [item] * 201}, format="json")
    assert resp.status_code == 400
    assert "results" in resp.json()
    assert LabReport.objects.count() == 0 and LabResult.objects.count() == 0


def test_report_laboratory_is_inherited_like_the_model(client, analyte):
    payload = {**body(method="M"), "laboratory": "Lab R"}
    row = client.post(URL, payload, format="json").json()["results"][0]
    assert row["laboratory"] == "Lab R"
    assert row["aggregation_eligible"] is True


def test_normalised_filled_only_with_stored_conversion(client, analyte, unit_b, source):
    row = client.post(URL, body(reported_unit="xb/L"), format="json").json()["results"][
        0
    ]
    assert row["normalised_value"] is None and row["normalised_unit"] is None
    UnitConversion.objects.create(
        from_unit=unit_b, to_unit=analyte.unit, factor=Decimal("2"), source=source
    )
    row = client.post(
        URL, body(reported_unit="xb/L", reported_value="3"), format="json"
    ).json()["results"][0]
    assert Decimal(row["normalised_value"]) == Decimal("6")
    assert row["normalised_unit"] == "xa/L"
    assert Decimal(row["reported_value"]) == Decimal("3")


def test_one_invalid_result_stores_nothing(client, analyte):
    good = body()["results"][0]
    bad = body(reported_value="1.1234567")["results"][0]
    resp = client.post(URL, {"results": [good, bad]}, format="json")
    assert resp.status_code == 400
    assert "reported_value" in resp.json()["results"]["1"]
    assert LabReport.objects.count() == 0 and LabResult.objects.count() == 0


def test_unknown_loinc_and_number_value_are_400(client, analyte):
    r = client.post(URL, body(loinc_code="nope"), format="json")
    assert r.status_code == 400 and "loinc_code" in r.json()["results"]["0"]
    r = client.post(URL, body(reported_value=2.5), format="json")
    assert r.status_code == 400 and "reported_value" in r.json()["results"]["0"]
    assert LabReport.objects.count() == 0


def test_dexa_without_provenance_is_400(client, analyte, source):
    from core.models import AnalyteCategory

    analyte.category = AnalyteCategory.BODY_COMPOSITION
    analyte.category_source = source
    analyte.save()
    r = client.post(URL, body(), format="json")
    assert r.status_code == 400
    assert LabReport.objects.count() == 0


def test_empty_results_and_naive_time_are_400(client, analyte):
    assert client.post(URL, {"results": []}, format="json").status_code == 400
    r = client.post(URL, body(collected_at="2026-01-01T10:00:00"), format="json")
    assert r.status_code == 400
    r = client.post(URL, body(collected_at="2026-01-01T10:00:00Z"), format="json")
    assert r.status_code == 201


def make_range(analyte, source, **kw):
    kw.setdefault("low", Decimal("1"))
    kw.setdefault("high", Decimal("3"))
    return ReferenceRange.objects.create(
        biomarker=analyte, unit=analyte.unit, source=source, **kw
    )


def plaus(client, **item):
    r = client.post(URL, body(**item), format="json")
    assert r.status_code == 201
    return r.json()["results"][0]["plausibility"]


def test_plausibility_within_and_outside(client, analyte, source):
    make_range(analyte, source)
    within = plaus(client, reported_value="2")
    assert within["status"] == "within"
    assert within["range_source"]["name"] == "synthetic fixture"
    outside = plaus(client, reported_value="9")
    assert outside["status"] == "outside"
    assert outside["range_source"]["url"] == "https://example.org/synthetic"
    assert LabResult.objects.count() == 2  # outside is stored, never rejected


def test_plausibility_not_checked(client, analyte, unit_b, source):
    assert plaus(client)["status"] == "not_checked"
    make_range(analyte, source)
    p = plaus(client, reported_unit="xb/L")
    assert p == {"status": "not_checked", "range_source": None}
    make_range(analyte, source, low=Decimal("0"), high=Decimal("1"), sex="F")
    assert plaus(client)["status"] == "within"  # stratified row is ignored
    make_range(analyte, source, low=Decimal("5"), high=Decimal("6"))
    assert plaus(client)["status"] == "not_checked"  # ambiguous
    assert LabResult.objects.count() == 4


def test_plausibility_uses_normalised_unit(client, analyte, unit_b, source):
    make_range(analyte, source)
    UnitConversion.objects.create(
        from_unit=unit_b, to_unit=analyte.unit, factor=Decimal("2"), source=source
    )
    assert plaus(client, reported_unit="xb/L", reported_value="1")["status"] == "within"
    assert (
        plaus(client, reported_unit="xb/L", reported_value="2")["status"] == "outside"
    )


def cand(**kw):
    base = dict(
        low=Decimal("1"), high=Decimal("3"), unit="u", source_id=7, stratified=False
    )
    return RangeCandidate(**{**base, **kw})


def test_check_plausibility_pure():
    d = Decimal
    assert check_plausibility(d(2), "u", None, None, [cand()]).source_id == 7
    assert check_plausibility(d(1), "u", None, None, [cand()]).status == "within"
    assert check_plausibility(d(3), "u", None, None, [cand()]).status == "within"
    assert check_plausibility(d("0.9"), "u", None, None, [cand()]).status == "outside"
    assert check_plausibility(d(2), "v", None, None, [cand()]).status == "not_checked"
    assert check_plausibility(d(2), "u", None, None, []).status == "not_checked"
    assert (
        check_plausibility(d(2), "u", None, None, [cand(stratified=True)]).status
        == "not_checked"
    )
    assert check_plausibility(d(2), "v", d(9), "u", [cand()]).status == "outside"
    assert (
        check_plausibility(d(2), "u", None, None, [cand(), cand()]).status
        == "not_checked"
    )
    assert (
        check_plausibility(d(5), "u", None, None, [cand(high=None)]).status == "within"
    )


@pytest.mark.parametrize(
    "item",
    [
        {"collected_at": "2026-13-01T10:00:00Z"},
        {"collected_at": "2026-02-30T10:00:00Z"},
        {"laboratory": "x" * 201},
        {"method": "x" * 201},
        {"device": "x" * 201},
        {"reported_unit": "x" * 65},
        {"method": "a\x00b"},
    ],
)
def test_bad_dates_and_overlong_text_are_400_not_500(client, analyte, item):
    r = client.post(URL, body(**item), format="json")
    assert r.status_code == 400
    assert next(iter(item)) in r.json()["results"]["0"]
    assert LabReport.objects.count() == 0 and LabResult.objects.count() == 0


def test_report_laboratory_too_long_is_400(client, analyte):
    r = client.post(URL, {**body(), "laboratory": "x" * 201}, format="json")
    assert r.status_code == 400 and "laboratory" in r.json()
    assert LabReport.objects.count() == 0


def test_padded_text_is_stripped_before_storage(client, analyte):
    padded = "x" * 200 + "   "
    r = client.post(URL, {**body(device=padded), "laboratory": padded}, format="json")
    assert r.status_code == 201
    assert LabReport.objects.get().laboratory == "x" * 200
    assert LabResult.objects.get().device == "x" * 200


def test_check_plausibility_ignores_ranges_in_other_units():
    d = Decimal
    other = cand(unit="w", source_id=8)
    out = check_plausibility(d(2), "u", None, None, [cand(), other])
    assert (out.status, out.source_id) == ("within", 7)


def test_range_with_population_lab_or_method_is_not_guessed(client, analyte, source):
    make_range(analyte, source, population="pregnancy")
    assert plaus(client)["status"] == "not_checked"
    make_range(analyte, source, lab="Lab A")
    assert plaus(client)["status"] == "not_checked"
    assert plaus(client, laboratory="Lab B")["status"] == "not_checked"
    ReferenceRange.objects.all().delete()
    make_range(analyte, source, lab="Lab A", method="LC-MS")
    assert plaus(client, laboratory="lab a", method="LC-MS")["status"] == "within"
    assert plaus(client, laboratory="Lab A")["status"] == "not_checked"
