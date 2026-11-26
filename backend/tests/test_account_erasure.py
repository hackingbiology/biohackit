# SPDX-License-Identifier: AGPL-3.0-or-later
"""Account erasure, 'delete everything' path (S01, Q57)."""

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from accounts.models import Profile, User
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    Measurement,
)
from terminology.models import Source, Unit

URL = "/api/auth/me/erase/"
PW = "correct-horse-9"
DELETE = {"choice": "delete_everything", "confirm": True}


def make_user(email: str) -> User:
    user = User.objects.create_user(email=email, password=PW)
    Profile.objects.get_or_create(
        user=user, defaults={"display_name": email.split("@")[0]}
    )
    return user


def make_report(user: User) -> LabReport:
    report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    report.original_file.save("x.csv", ContentFile(b"a,b\n"), save=True)
    return report


def make_biomarker() -> tuple[Unit, Biomarker]:
    source = Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )
    unit = Unit.objects.create(ucum_code="u1", display="u1", source=source)
    biomarker = Biomarker.objects.create(
        name="synthetic",
        loinc_code="T-1",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )
    return unit, biomarker


def client_for(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user)
    return c


def stored(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


@pytest.mark.django_db
def test_notice_states_clones_and_choices():
    # scenario: accounts-and-profiles::clones-are-disclosed
    # scenario: accounts-and-profiles::erasure-offers-a-research-retention-choice
    r = client_for(make_user("a@example.com")).get(URL)
    assert r.status_code == 200
    assert "already cloned" in r.data["notice"]
    assert "outside" in r.data["notice"]
    assert r.data["choices"]["delete_everything"]["available"] is True
    keep = r.data["choices"]["keep_for_research"]
    assert keep["available"] is False
    assert keep["reason"] == "de-identification not implemented yet"
    assert keep["consent"] == "analytics-and-open-data"


@pytest.mark.django_db
def test_confirm_required(private_root):
    user = make_user("a@example.com")
    make_report(user)
    c = client_for(user)
    assert (
        c.post(URL, {"choice": "delete_everything"}, format="json").status_code == 400
    )
    bad = {"choice": "delete_everything", "confirm": "yes"}
    assert c.post(URL, bad, format="json").status_code == 400
    assert User.objects.filter(pk=user.pk).exists()
    assert len(stored(private_root)) == 1


@pytest.mark.django_db
def test_keep_for_research_refused_and_nothing_deleted(private_root):
    user = make_user("a@example.com")
    make_report(user)
    body = {"choice": "keep_for_research", "confirm": True}
    r = client_for(user).post(URL, body, format="json")
    assert r.status_code == 409
    assert r.data["detail"] == "de-identification not implemented yet"
    assert User.objects.filter(pk=user.pk).exists()
    assert LabReport.objects.filter(owner=user).count() == 1
    assert len(stored(private_root)) == 1


@pytest.mark.django_db(transaction=True)
def test_delete_everything_removes_data_and_file(private_root):
    # scenario: accounts-and-profiles::erasure-on-request
    user = make_user("a@example.com")
    other = make_user("b@example.com")
    report = make_report(user)
    other_report = make_report(other)
    unit, biomarker = make_biomarker()
    for owner, rep in ((user, report), (other, other_report)):
        LabResult.objects.create(
            report=rep, biomarker=biomarker, reported_value="1", reported_unit="u1"
        )
        Measurement.objects.create(
            user=owner,
            biomarker=biomarker,
            time=datetime(2026, 11, 26, tzinfo=UTC),
            value=Decimal("1"),
            unit_ucum="u1",
            source="synthetic",
        )
    other_file = Path(other_report.original_file.path)
    assert len(stored(private_root)) == 2
    r = client_for(user).post(URL, DELETE, format="json")
    assert r.status_code == 200
    assert "outside" in r.data["notice"]
    assert not User.objects.filter(pk=user.pk).exists()
    assert not Profile.objects.filter(user_id=user.pk).exists()
    assert not LabReport.objects.filter(owner_id=user.pk).exists()
    assert not LabResult.objects.filter(report_id=report.pk).exists()
    assert not Measurement.objects.filter(user_id=user.pk).exists()
    assert LabResult.objects.filter(report=other_report).count() == 1
    assert Measurement.objects.filter(user=other).count() == 1
    assert stored(private_root) == [other_file]
    assert User.objects.filter(pk=other.pk).exists()
    assert LabReport.objects.filter(owner=other).count() == 1


@pytest.mark.django_db
def test_token_stops_authenticating_after_erasure():
    # scenario: accounts-and-profiles::erasure-on-request
    user = make_user("a@example.com")
    c = APIClient()
    creds = {"email": "a@example.com", "password": PW}
    token = c.post("/api/auth/token/", creds, format="json")
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.data['access']}")
    assert c.get("/api/auth/me/").status_code == 200
    c.post(URL, DELETE, format="json")
    assert not User.objects.filter(pk=user.pk).exists()
    assert c.get("/api/auth/me/").status_code == 401


@pytest.mark.django_db
def test_unauthenticated_gets_401():
    c = APIClient()
    assert c.get(URL).status_code == 401
    assert c.post(URL, DELETE, format="json").status_code == 401
