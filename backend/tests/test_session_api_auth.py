# SPDX-License-Identifier: AGPL-3.0-or-later
"""The browser sign-in session is accepted by the API, with CSRF enforced (M02 TG-o)."""

from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.middleware.csrf import _get_new_csrf_string
from django.test import Client

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabResult
from terminology.models import Source, Unit

COMPLETENESS = "/api/labs/completeness/"
PREVIEW = "/api/labs/imports/csv/preview/"


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


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
        loinc_code="0000-0",
        name="synthetic analyte",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


def _csv(code: str) -> SimpleUploadedFile:
    body = "loinc_code,value,unit\n" + code + ",1,xa/L\n"
    return SimpleUploadedFile("a.csv", body.encode(), content_type="text/csv")


def _csrf_client(user: User) -> tuple[Client, str]:
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    token = _get_new_csrf_string()
    client.cookies["csrftoken"] = token
    return client, token


def test_session_login_reads_the_api(user):
    client = Client()
    client.force_login(user)
    assert client.get(COMPLETENESS).status_code == 200


def test_anonymous_is_still_refused(db):
    assert Client().get(COMPLETENESS).status_code in (401, 403)


def test_session_post_without_csrf_token_is_refused_and_stores_nothing(user, analyte):
    client, _ = _csrf_client(user)
    resp = client.post(PREVIEW, {"file": _csv("0000-0")})
    assert resp.status_code == 403
    assert LabReport.objects.count() == 0
    assert LabResult.objects.count() == 0


def test_session_post_with_csrf_token_is_accepted(user, analyte):
    client, token = _csrf_client(user)
    resp = client.post(PREVIEW, {"file": _csv("0000-0")}, HTTP_X_CSRFTOKEN=token)
    assert resp.status_code == 200
    assert resp.json()["rows"][0]["status"] == "recognised"
    assert LabReport.objects.count() == 0
