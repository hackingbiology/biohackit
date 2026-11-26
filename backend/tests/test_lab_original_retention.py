# SPDX-License-Identifier: AGPL-3.0-or-later
"""Private retention of the original CSV of a confirmed import (M02 TG-g part 1)."""

import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import get_resolver
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from terminology.models import Source, Unit

PREVIEW = "/api/labs/imports/csv/preview/"
CONFIRM = "/api/labs/imports/csv/confirm/"
HEAD = "loinc_code,value,unit,collected_at,reported_at,laboratory,method\n"
GOOD = HEAD + "0000-0,2.5,xa/L,,,,\n"


@pytest.fixture
def client(db):
    user = User.objects.create_user(email="a@example.com", password="correct-horse-9")
    c = APIClient()
    c.force_authenticate(user)
    c.user = user
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


def post(client, url, content, name="labs.csv", **extra):
    data = content if isinstance(content, bytes) else content.encode()
    file = SimpleUploadedFile(name, data, content_type="text/csv")
    return client.post(url, {"file": file, **extra}, format="multipart")


def files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


# scenario: biomarkers-and-labs::rollback-removes-the-retained-original
def test_rollback_removes_the_retained_original(
    client, analyte, private_root, django_capture_on_commit_callbacks
):
    body = GOOD.encode()
    resp = post(client, CONFIRM, body)
    assert resp.status_code == 201
    data = resp.json()
    (stored,) = files(private_root)
    assert stored.read_bytes() == body
    assert data["original_retained"] is True
    assert data["original_sha256"] == hashlib.sha256(body).hexdigest()
    assert data["original_size"] == len(body)
    with django_capture_on_commit_callbacks(execute=True):
        assert client.delete(f"/api/labs/reports/{data['id']}/").status_code == 204
    assert files(private_root) == []
    assert LabReport.objects.count() == 0
    assert LabResult.objects.count() == 0


def test_refused_confirm_leaves_no_file(client, analyte, private_root):
    resp = post(client, CONFIRM, HEAD + "0000-0,2.5,xa/L,,,,\n9999-9,1,xa/L,,,,\n")
    assert resp.status_code == 400
    assert LabReport.objects.count() == 0
    assert files(private_root) == []


def test_preview_never_writes_a_file(client, analyte, private_root):
    assert post(client, PREVIEW, GOOD).status_code == 200
    assert files(private_root) == []
    assert LabReport.objects.count() == 0


def test_redaction_opt_in_retains_nothing(client, analyte, private_root):
    resp = post(client, CONFIRM, GOOD, name="Jane Doe.csv", redact_terms=["Jane Doe"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_retained"] is False
    assert data["original_sha256"] is None
    assert data["original_size"] is None
    assert "original_not_retained_reason" in data
    assert files(private_root) == []


def test_rollback_leaves_other_files_and_manual_report(
    client, analyte, private_root, django_capture_on_commit_callbacks
):
    first = post(client, CONFIRM, GOOD).json()["id"]
    second = post(client, CONFIRM, GOOD.replace("2.5", "7")).json()["id"]
    manual = LabReport.objects.create(owner=client.user, origin=LabReportOrigin.MANUAL)
    LabResult.objects.create(
        report=manual,
        biomarker=analyte,
        reported_value=Decimal("9"),
        reported_unit="xa/L",
    )
    with django_capture_on_commit_callbacks(execute=True):
        assert client.delete(f"/api/labs/reports/{first}/").status_code == 204
    (left,) = files(private_root)
    assert left.read_bytes() == GOOD.replace("2.5", "7").encode()
    assert LabReport.objects.get(pk=second).original_file.name.endswith(left.name)
    assert LabReport.objects.filter(pk=manual.pk).exists()
    assert client.delete(f"/api/labs/reports/{manual.pk}/").status_code == 409
    assert files(private_root) == [left]


def test_import_without_file_still_rolls_back(
    client, analyte, django_capture_on_commit_callbacks
):
    report = LabReport.objects.create(
        owner=client.user, origin=LabReportOrigin.IMPORT, import_name="x.csv"
    )
    with django_capture_on_commit_callbacks(execute=True):
        assert client.delete(f"/api/labs/reports/{report.pk}/").status_code == 204
    assert LabReport.objects.count() == 0


def test_stored_name_has_no_user_text(client, analyte, private_root):
    resp = post(client, CONFIRM, GOOD, name="jane-doe-123.csv", laboratory="Jane Lab")
    (stored,) = files(private_root)
    assert stored.name == f"{resp.json()['id']}.csv"
    assert "jane" not in str(stored).lower()


def test_report_and_fhir_expose_no_path(client, analyte, private_root):
    report_id = post(client, CONFIRM, GOOD, name="secret-name.csv").json()["id"]
    detail = client.get(f"/api/labs/reports/{report_id}/").content.decode()
    fhir = client.get(f"/api/labs/reports/{report_id}/fhir/").content.decode()
    for text in (detail, fhir):
        assert str(private_root) not in text
        assert "lab-reports" not in text
    assert json.loads(detail)["original_retained"] is True


def _walk(patterns):
    for p in patterns:
        if hasattr(p, "url_patterns"):
            yield from _walk(p.url_patterns)
        else:
            yield p


def test_no_url_pattern_serves_private_media(client, analyte, private_root):
    from django.conf import settings
    from django.views.static import serve

    root = str(settings.PRIVATE_MEDIA_ROOT)
    for p in _walk(get_resolver().url_patterns):
        assert getattr(p.callback, "__wrapped__", p.callback) is not serve
        assert root not in str(p.default_args.get("document_root", ""))
    report_id = post(client, CONFIRM, GOOD).json()["id"]
    for path in (
        f"/lab-reports/{report_id}.csv",
        f"/private_media/lab-reports/{report_id}.csv",
    ):
        assert client.get(path).status_code == 404
    assert not root.startswith(str(settings.STATIC_ROOT))


def test_owner_cascade_delete_removes_file(
    client, analyte, private_root, django_capture_on_commit_callbacks
):
    post(client, CONFIRM, GOOD)
    assert len(files(private_root)) == 1
    with django_capture_on_commit_callbacks(execute=True):
        client.user.delete()
    assert files(private_root) == []
