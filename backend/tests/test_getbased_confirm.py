# SPDX-License-Identifier: AGPL-3.0-or-later
"""get-based archive confirm, provenance and undo (X01 part 2b). Fictitious fixtures only:
synthetic Biomarker/LOINC codes and units, no real person (loinc.org is unreachable, Q79)."""

import json
import logging
from datetime import date
from decimal import Decimal

import pytest
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, models, transaction
from rest_framework.test import APIClient

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    GetbasedMarkerMapping,
    LabReport,
    LabResult,
    LabResultGetbasedProvenance,
)
from terminology.models import Source, Unit

URL = "/api/labs/imports/getbased/confirm/"
SHA = "b" * 40
PATH = "js/marker-schema/synthetic.ts"
QUALIFIER = "last import into this date; the model for this value is unknown"
IDENTITY = {
    "name": "Test Person",
    "sex": "female",
    "dob": "1900-01-01",
    "location": "Nowhere Synthetic",
    "notes": "synthetic private note",
    "avatar": "synthetic-avatar",
}
SECRETS = [
    "Test Person",
    "1900-01-01",
    "Nowhere Synthetic",
    "synthetic private note",
    "synthetic chat",
    "synthetic meal",
    "synthetic-wallet-node",
]


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic mapping source",
        version="v0",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 27),
    )


@pytest.fixture
def unit(source):
    return Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)


@pytest.fixture
def analyte(source, unit):
    return Biomarker.objects.create(
        name="syn name",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


@pytest.fixture
def mappings(source, unit, analyte):
    GetbasedMarkerMapping.objects.create(
        getbased_key="syn.a",
        kind="measured",
        biomarker=analyte,
        unit=unit,
        unit_source_path=PATH,
        unit_source_commit=SHA,
        source=source,
    )
    GetbasedMarkerMapping.objects.create(
        getbased_key="syn.nounit", kind="measured", biomarker=analyte, source=source
    )
    GetbasedMarkerMapping.objects.create(
        getbased_key="syn.denied", kind="calculated", source=source
    )


def entry(markers, day="2026-01-02", **extra):
    return {"date": day, "markers": markers, **extra}


def single(entries, version=2):
    body = {"version": version, "profile": dict(IDENTITY), "entries": entries}
    body.update(
        {
            "chat": [{"text": "synthetic chat"}],
            "wallet": {"nodeUrl": "synthetic-wallet-node"},
        }
    )
    return body


def profile(pid, entries):
    return {
        "id": pid,
        **IDENTITY,
        "data": {"entries": entries},
        "nutrition": {"meals": ["synthetic meal"]},
        "chat": [{"text": "synthetic chat"}],
    }


def bundle(profiles, version=2):
    return {"version": version, "type": "database", "profiles": profiles}


def raw(obj):
    return json.dumps(obj).encode()


def post(client, obj, name="export.json", **extra):
    data = obj if isinstance(obj, bytes) else raw(obj)
    f = SimpleUploadedFile(name, data, content_type="application/json")
    return client.post(URL, {"file": f, **extra}, format="multipart")


def counts():
    return (
        LabReport.objects.count(),
        LabResult.objects.count(),
        LabResultGetbasedProvenance.objects.count(),
    )


def four_flags():
    """Four entries, one per origin flag, all of the marker syn.a."""
    return single(
        [
            entry(
                {"syn.a": 1.5},
                day="2026-01-01",
                importedWith={"modelId": "", "provider": "synthetic-provider"},
                markerSources={
                    "syn.a": {
                        "reported": True,
                        "snapshotId": "snap-1",
                        "file": "scan.pdf",
                        "at": 1767259800000,
                        "manuallyEdited": True,
                    }
                },
            ),
            entry(
                {"syn.a": 2},
                day="2026-01-02",
                markerSources={"syn.a": {"file": "scan.pdf", "reported": False}},
            ),
            entry(
                {"syn.a": 3},
                day="2026-01-03",
                markerSources={"syn.a": {"reported": False}},
            ),
            entry({"syn.a": 4}, day="2026-01-04"),
        ]
    )


# scenario: biomarkers-and-labs::origin-of-the-import-is-recorded
def test_confirm_records_origin_format_version_and_file_name(client, mappings):
    response = post(client, four_flags(), name="getbased-Jane-Doe-2026-01-01.json")
    assert response.status_code == 201
    report = LabReport.objects.get()
    assert report.origin == "import"
    assert report.import_source == "getbased"
    assert report.import_format == "getbased-export"
    assert report.import_format_version == 2
    assert report.import_name == "getbased-export.json"
    assert "Jane" not in report.import_name
    assert "Jane" not in str(response.data)
    assert response.data["report_id"] == report.pk
    assert response.data["stored_count"] == 4
    assert response.data["original_retained"] is False
    assert response.data["original_not_retained_reason"] == (
        "the archive holds identity and other non-lab data, so it is not kept"
    )
    assert not report.original_file


# scenario: biomarkers-and-labs::origin-of-the-import-is-recorded
def test_bundle_records_database_format_and_needs_a_chosen_profile(client, mappings):
    body = bundle(
        [
            profile("p1", [entry({"syn.a": 1})]),
            profile("p2", [entry({"syn.a": 2})]),
        ]
    )
    refused = post(client, body)
    assert refused.status_code == 400
    assert counts() == (0, 0, 0)
    assert post(client, body, profile_id="nope").status_code == 400
    ok = post(client, body, profile_id="p2")
    assert ok.status_code == 201
    assert LabReport.objects.get().import_format == "getbased-database"
    assert LabResult.objects.get().reported_value == Decimal("2")


def test_single_client_export_refuses_a_profile_id_and_unsupported_formats(
    client, mappings
):
    assert (
        post(client, single([entry({"syn.a": 1})]), profile_id="x").status_code == 400
    )
    assert post(client, {"format": "labcharts-backup", "version": 2}).status_code == 400
    assert post(client, single([entry({"syn.a": 1})], version=3)).status_code == 400
    assert post(client, b"not json").status_code == 400
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::values-read-by-an-ai-model-are-flagged-and-stay-unconfirmed
# scenario: biomarkers-and-labs::import-origin-without-importedwith-fails-closed
# scenario: biomarkers-and-labs::result-without-markersources-fails-closed
# scenario: biomarkers-and-labs::result-whose-markersources-has-no-import-origin-fails-closed
def test_every_result_is_entered_and_each_flag_is_stored_and_returned(client, mappings):
    post(client, four_flags())
    results = LabResult.objects.order_by("getbased_provenance__entry_date")
    assert [r.validation_state for r in results] == ["entered"] * 4
    assert [r.aggregation_eligible for r in results] == [False] * 4
    assert [r.collected_at for r in results] == [None] * 4
    flags = [r.getbased_provenance.flag for r in results]
    assert flags == [
        "ai_read",
        "may_be_ai_read",
        "origin_not_shown",
        "origin_unknown",
    ]
    api = client.get(f"/api/labs/reports/{LabReport.objects.get().pk}/")
    by_day = {
        r["getbased_provenance"]["entry_date"]: r["getbased_provenance"]
        for r in api.data["results"]
    }
    assert by_day["2026-01-01"]["flag_text"] == (
        "read by an AI model, check against your report"
    )
    assert by_day["2026-01-02"]["flag_text"] == (
        "may have been read by an AI model, check against your report"
    )
    assert by_day["2026-01-03"]["flag_text"] == (
        "origin not shown in get-based, check against your report"
    )
    assert by_day["2026-01-04"]["flag_text"] == (
        "origin unknown, check against your report"
    )
    assert by_day["2026-01-04"]["has_marker_sources"] is False
    assert by_day["2026-01-04"]["imported_with"] is None


# scenario: biomarkers-and-labs::values-read-by-an-ai-model-are-flagged-and-stay-unconfirmed
def test_model_and_provider_are_kept_with_the_qualifier_and_unknown_when_empty(
    client, mappings
):
    post(client, four_flags())
    prov = LabResultGetbasedProvenance.objects.get(entry_date="2026-01-01")
    assert prov.imported_with_present is True
    assert prov.imported_with_model_id is None
    assert prov.imported_with_provider == "synthetic-provider"
    report_id = LabReport.objects.get().pk
    data = client.get(f"/api/labs/reports/{report_id}/").data["results"]
    first = next(
        r["getbased_provenance"]
        for r in data
        if r["getbased_provenance"]["entry_date"] == "2026-01-01"
    )
    assert first["imported_with"] == {
        "model_id": "unknown",
        "provider": "synthetic-provider",
        "qualifier": QUALIFIER,
    }


# scenario: biomarkers-and-labs::per-value-markersources-is-kept
# scenario: biomarkers-and-labs::edited-values-are-labelled
def test_marker_sources_round_trip_verbatim_and_edited_is_labelled(client, mappings):
    post(client, four_flags())
    prov = LabResultGetbasedProvenance.objects.get(entry_date="2026-01-01")
    assert prov.has_marker_sources is True
    assert prov.ms_reported is True
    assert prov.ms_file == "scan.pdf"
    assert prov.ms_at == "1767259800000"
    assert prov.ms_snapshot_id == "snap-1"
    assert prov.manually_edited is True
    assert prov.result.collected_at is None
    report_id = LabReport.objects.get().pk
    api = client.get(f"/api/labs/reports/{report_id}/").data
    shown = {
        r["getbased_provenance"]["entry_date"]: r["getbased_provenance"]
        for r in api["results"]
    }
    assert shown["2026-01-01"]["edited_label"] == "edited in get-based after import"
    assert shown["2026-01-01"]["marker_sources"] == {
        "reported": True,
        "file": "scan.pdf",
        "at": "1767259800000",
        "snapshot_id": "snap-1",
    }
    assert shown["2026-01-02"]["edited_label"] is None
    assert api["import_source"] == "getbased"
    assert api["import_format"] == "getbased-export"
    assert api["import_format_version"] == 2


def test_value_is_exact_and_unit_is_the_cited_mapping_unit(client, mappings):
    body = single(
        [entry({"syn.a": 1.10}), entry({"syn.a": 7}, day="2026-01-03")],
    )
    body["entries"][0]["unit"] = "mg/dL"  # a unit in the archive is never read
    assert post(client, raw(body).replace(b"1.1", b"1.10")).status_code == 201
    stored = {r.reported_value for r in LabResult.objects.all()}
    assert stored == {Decimal("1.1"), Decimal("7")}
    assert {r.reported_unit for r in LabResult.objects.all()} == {"xa/L"}


def test_value_the_result_rules_refuse_rolls_everything_back(client, mappings):
    body = raw(single([entry({"syn.a": 1})])).replace(b"1}", b"0.1234567}")
    response = post(client, body)
    assert response.status_code == 400
    assert "syn.a" in str(response.data)
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::confirm-refused-while-a-row-is-not-recognised
@pytest.mark.parametrize(
    "markers,day",
    [
        ({"syn.a": 1, "syn.unmapped": 2}, "2026-01-02"),
        ({"syn.a": 1, "syn.nounit": 2}, "2026-01-02"),
        ({"syn.a": 1}, "2026-13-45"),
        ({"syn.a": "high"}, "2026-01-02"),
    ],
)
def test_confirm_refused_while_a_row_is_not_recognised(client, mappings, markers, day):
    response = post(client, single([entry(markers, day=day)]))
    assert response.status_code == 400
    assert response.data["rows"]
    assert all(r["status"] == "not_recognised" for r in response.data["rows"])
    assert counts() == (0, 0, 0)


# scenario: biomarkers-and-labs::calculated-values-are-not-stored-as-measured
# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_calculated_and_deleted_rows_are_left_out_and_counted(client, mappings):
    body = single(
        [
            entry(
                {
                    "syn.a": 1,
                    "syn.denied": 2,
                    "calculatedRatios.x": 3,
                    "syn.derived": 4,
                    "syn.gone": 5,
                },
                markerSources={
                    "syn.derived": {"derivedFrom": ["syn.a"]},
                    "syn.a": {"file": "scan.pdf"},
                },
                deletedMarkers={"syn.gone": 9},
            )
        ]
    )
    response = post(client, body)
    assert response.status_code == 201
    assert response.data["stored_count"] == 1
    assert response.data["left_out"] == {"calculated": 3, "deleted": 1}
    assert counts() == (1, 1, 1)


def test_nothing_to_import_is_refused(client, mappings):
    response = post(client, single([entry({"syn.denied": 1})]))
    assert response.status_code == 400
    assert counts() == (0, 0, 0)


def test_confirm_requires_authentication_and_a_file(db, client, mappings):
    assert APIClient().post(URL, {}, format="multipart").status_code in (401, 403)
    assert client.post(URL, {}, format="multipart").status_code == 400


# scenario: biomarkers-and-labs::undo-of-a-confirmed-import
def test_undo_removes_report_results_and_provenance_only(
    client, user, mappings, analyte
):
    other_user = User.objects.create_user(email="b@example.com", password="x-y-z-1234")
    mine = LabReport.objects.create(owner=user, origin="manual")
    LabResult.objects.create(
        report=mine, biomarker=analyte, reported_value="5", reported_unit="xa/L"
    )
    theirs = LabReport.objects.create(
        owner=other_user, origin="import", import_name="theirs.csv"
    )
    other_client = APIClient()
    other_client.force_authenticate(other_user)
    assert post(other_client, four_flags()).status_code == 201
    created = post(client, four_flags()).data["report_id"]
    assert counts() == (4, 9, 8)
    assert other_client.delete(f"/api/labs/reports/{created}/").status_code == 404
    assert client.delete(f"/api/labs/reports/{created}/").status_code == 204
    assert counts() == (3, 5, 4)
    assert LabReport.objects.filter(pk__in=[mine.pk, theirs.pk]).count() == 2
    assert LabResult.objects.filter(report=mine).count() == 1


def test_database_rejects_partial_import_source_fields(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        LabReport.objects.bulk_create(
            [
                LabReport(
                    owner=user,
                    origin="import",
                    import_name="x",
                    import_source="getbased",
                )
            ]
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        LabReport.objects.bulk_create(
            [
                LabReport(
                    owner=user,
                    origin="manual",
                    import_source="getbased",
                    import_format="getbased-export",
                    import_format_version=2,
                )
            ]
        )
    ok = LabReport.objects.create(owner=user, origin="import", import_name="x.csv")
    assert (ok.import_source, ok.import_format, ok.import_format_version) == (
        "",
        "",
        None,
    )


# scenario: biomarkers-and-labs::identity-and-non-lab-data-are-never-stored
def test_identity_chat_nutrition_wallet_appear_nowhere(client, mappings, caplog):
    caplog.set_level(logging.DEBUG)
    body = bundle([profile("p1", [entry({"syn.a": 1}, importedWith={"modelId": "m"})])])
    body["profiles"][0]["data"]["entries"][0]["markerSources"] = {
        "syn.a": {"file": "scan.pdf"}
    }
    response = post(client, body, profile_id="p1")
    assert response.status_code == 201
    haystack = [json.dumps(response.data, default=str), caplog.text]
    for model in apps.get_app_config("core").get_models():
        for obj in model.objects.all():
            for field in model._meta.get_fields():
                if isinstance(field, models.CharField | models.TextField):
                    haystack.append(str(getattr(obj, field.name, "")))
    joined = "\n".join(haystack)
    for secret in SECRETS:
        assert secret not in joined
    assert "p1" not in json.dumps(response.data)
    assert not LabReport.objects.get().original_file
