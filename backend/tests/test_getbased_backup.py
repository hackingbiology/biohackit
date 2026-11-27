# SPDX-License-Identifier: AGPL-3.0-or-later
"""get-based full browser backup `labcharts-backup` v1 (X01 part 2d). Fictitious fixtures
built here only: synthetic Biomarker/LOINC codes and units, no real person or key."""

import json
import logging
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import User
from core.getbased_import import GetbasedImportError, build_preview
from core.models import (
    Biomarker,
    BiomarkerRole,
    GetbasedMarkerMapping,
    LabReport,
    LabResult,
    LabResultGetbasedProvenance,
)
from terminology.models import Source, Unit

PREVIEW = "/api/labs/imports/getbased/preview/"
CONFIRM = "/api/labs/imports/getbased/confirm/"
SALT = "synthetic-salt-AAAA"
SECRETS = [
    "synthetic-key-123",
    "synthetic chat",
    SALT,
    "Test Person",
    "synthetic-wallet",
]


@pytest.fixture
def client(db):
    c = APIClient()
    c.force_authenticate(
        User.objects.create_user(email="a@example.com", password="x-9-correct")
    )
    return c


@pytest.fixture
def mappings(db):
    source = Source.objects.create(
        name="synthetic mapping source",
        version="v0",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 27),
    )
    unit = Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)
    analyte = Biomarker.objects.create(
        name="syn name",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )
    GetbasedMarkerMapping.objects.create(
        getbased_key="syn.a",
        kind="measured",
        biomarker=analyte,
        unit=unit,
        unit_source_path="js/marker-schema/synthetic.ts",
        unit_source_commit="b" * 40,
        source=source,
    )


def lab_data(value=1.5):
    return {
        "entries": [
            {
                "date": "2026-01-02",
                "markers": {"syn.a": value},
                "importedWith": {"modelId": "synthetic-model", "provider": "synthetic"},
                "markerSources": {
                    "syn.a": {"file": "scan.pdf", "at": 1767259800000, "reported": True}
                },
            }
        ],
        "chat": "synthetic chat",
    }


def backup(*ids, values=None, **top):
    values = values or {}
    profiles = [
        {
            "profileId": pid,
            "name": "Test Person",
            "keys": {
                "imported": json.dumps(lab_data(values.get(pid, 1.5))),
                "chat": "synthetic chat",
            },
        }
        for pid in ids
    ]
    body = {
        "format": "labcharts-backup",
        "version": 1,
        "createdAt": "2026-01-01T00:00:00Z",
        "encrypted": False,
        "encryptionSalt": None,
        "settings": {"labcharts-api-key": "synthetic-key-123"},
        "profileList": json.dumps([{"id": i, "name": "Test Person"} for i in ids]),
        "profiles": profiles,
        "wearableIDB": None,
        "cycleIDB": None,
        "cycleImportMeta": None,
    }
    body.update(top)
    return body


def post(client, url, body, **extra):
    f = SimpleUploadedFile("b.json", json.dumps(body).encode(), "application/json")
    return client.post(url, {"file": f, **extra}, format="multipart")


def counts():
    return (
        LabReport.objects.count(),
        LabResult.objects.count(),
        LabResultGetbasedProvenance.objects.count(),
    )


# scenario: biomarkers-and-labs::exactly-one-profile-is-imported
def test_single_profile_backup_previewed_and_confirmed(client, mappings, caplog):
    caplog.set_level(logging.DEBUG)
    body = backup("p1")
    preview = post(client, PREVIEW, body)
    assert preview.status_code == 200
    assert preview.data["container"] == "browser backup"
    assert preview.data["version"] == 1
    assert [r["status"] for r in preview.data["rows"]] == ["matched"]
    assert counts() == (0, 0, 0)
    done = post(client, CONFIRM, body)
    assert done.status_code == 201
    report = LabReport.objects.get()
    assert report.import_format == "getbased-labcharts-backup"
    assert report.import_format_version == 1
    assert report.import_name == "getbased-export.json"
    assert LabResult.objects.get().validation_state == "entered"
    prov = LabResultGetbasedProvenance.objects.get()
    assert prov.imported_with_model_id == "synthetic-model"
    assert prov.ms_file == "scan.pdf"
    seen = json.dumps(done.data) + json.dumps(preview.data) + caplog.text
    assert not any(s in seen for s in SECRETS)
    assert client.delete(f"/api/labs/reports/{report.pk}/").status_code == 204
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::exactly-one-profile-is-imported
def test_multi_profile_backup_needs_one_choice(client, mappings):
    body = backup("p1", "p2", values={"p1": 1.5, "p2": 2.5})
    choose = post(client, PREVIEW, body)
    assert choose.data["status"] == "choose_profile"
    assert choose.data["profile_ids"] == ["p1", "p2"]
    assert post(client, CONFIRM, body).status_code == 400
    assert post(client, CONFIRM, body, profile_id="nope").status_code == 400
    assert counts() == (0, 0, 0)
    chosen = post(client, PREVIEW, body, profile_id="p2")
    assert chosen.status_code == 200
    assert json.dumps(chosen.data).count("2.5") >= 1
    assert "1.5" not in json.dumps(chosen.data)
    assert post(client, CONFIRM, body, profile_id="p2").status_code == 201
    assert LabReport.objects.count() == 1
    assert float(LabResult.objects.get().reported_value) == 2.5


def test_profile_without_lab_data_and_unreadable_lab_data(mappings):
    empty = backup("p1")
    del empty["profiles"][0]["keys"]["imported"]
    assert build_preview(json.dumps(empty).encode())["rows"] == []
    array = backup("p1")
    array["profiles"][0]["keys"]["imported"] = "[1]"
    assert build_preview(json.dumps(array).encode())["rows"] == []
    for bad in ("{not json", 7):
        body = backup("p1")
        body["profiles"][0]["keys"]["imported"] = bad
        with pytest.raises(GetbasedImportError):
            build_preview(json.dumps(body).encode())


# scenario: biomarkers-and-labs::archive-whose-lab-store-is-still-locked-by-the-get-based-passphrase
@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_encrypted_backup_is_refused_and_salt_not_echoed(client, mappings, url):
    flagged = backup("p1", encrypted=True, encryptionSalt=SALT)
    value = backup("p1", encryptionSalt=SALT)
    value["profiles"][0]["keys"]["imported"] = "v1:abcd:efgh"
    listed = backup("p1", encryptionSalt=SALT, profileList="v1:abcd:efgh")
    for body in (flagged, value, listed):
        response = post(client, url, body)
        assert response.status_code == 400
        text = json.dumps(response.json())
        assert "still locked with the get-based passphrase" in text
        assert SALT not in text
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::unknown-archive-format-version-rejected
@pytest.mark.parametrize(
    ("version", "needle"), [(2, "version 2"), (None, "missing"), (True, "true")]
)
def test_other_backup_version_is_refused_naming_versions(client, version, needle):
    body = backup("p1")
    if version is None:
        del body["version"]
    else:
        body["version"] = version
    response = post(client, PREVIEW, body)
    assert response.status_code == 400
    text = json.dumps(response.json())
    assert needle in text
    assert "supported backup version is 1" in text
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::unknown-archive-format-version-rejected
def test_migration_archive_and_malformed_backup_still_refused(client):
    migration = post(client, PREVIEW, {"format": "getbased-migration", "version": 1})
    assert "not supported yet" in json.dumps(migration.json())
    for bad in (
        {"format": "labcharts-backup", "version": 1},
        {"format": "labcharts-backup", "version": 1, "profiles": []},
        {"format": "labcharts-backup", "version": 1, "profiles": [{"profileId": 1}]},
    ):
        response = post(client, PREVIEW, bad)
        assert response.status_code == 400
        assert "no readable profiles" in json.dumps(response.json())
