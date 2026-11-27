# SPDX-License-Identifier: AGPL-3.0-or-later
"""get-based archive preview, library and API (X01 part 2a). Fictitious fixtures only: no
real person, synthetic Biomarker/LOINC codes (loinc.org is unreachable, Q79)."""

import json
import logging
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.middleware.csrf import _get_new_csrf_string
from django.test import Client
from rest_framework.test import APIClient

from accounts.models import User
from core.getbased_import import GetbasedImportError, build_preview
from core.models import (
    Biomarker,
    BiomarkerRole,
    GetbasedMarkerMapping,
    LabReport,
    LabResult,
)
from terminology.models import Source, Unit

URL = "/api/labs/imports/getbased/preview/"
SHA = "b" * 40
PATH = "js/marker-schema/synthetic.ts"
IDENTITY = {
    "name": "Test Person",
    "sex": "female",
    "dob": "1900-01-01",
    "location": "Nowhere Synthetic",
    "notes": "synthetic private note",
    "avatar": "synthetic-avatar",
}
SECRETS = ["Test Person", "1900-01-01", "Nowhere Synthetic", "synthetic private note"]


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
    body.update({"chat": [{"text": "synthetic chat"}], "wallet": {"nodeUrl": "x"}})
    return body


def bundle(profiles, version=2):
    return {"version": version, "type": "database", "profiles": profiles}


def profile(pid, entries):
    return {
        "id": pid,
        **IDENTITY,
        "data": {"entries": entries},
        "nutrition": {"meals": ["synthetic meal"]},
        "chat": [{"text": "synthetic chat"}],
    }


def raw(obj):
    return json.dumps(obj).encode()


def rows_of(obj):
    return build_preview(raw(obj))["rows"]


def post(client, obj, name="export.json", **extra):
    data = obj if isinstance(obj, bytes) else raw(obj)
    f = SimpleUploadedFile(name, data, content_type="application/json")
    return client.post(URL, {"file": f, **extra}, format="multipart")


def counts():
    return LabReport.objects.count(), LabResult.objects.count()


# scenario: biomarkers-and-labs::markers-matched-through-a-cited-mapping-or-not-recognised
# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
def test_matched_row_shows_loinc_unit_source_and_citation(mappings):
    (row,) = rows_of(single([entry({"syn.a": 1})]))
    assert row["status"] == "matched"
    assert row["loinc_code"] == "0000-0"
    assert row["unit"] == "xa/L"
    assert row["mapping_source"] == "synthetic mapping source v0"
    assert row["unit_source"] == f"{PATH}@{SHA}"
    assert row["date"] == "2026-01-02"


# scenario: biomarkers-and-labs::markers-matched-through-a-cited-mapping-or-not-recognised
def test_no_mapping_is_not_recognised_and_names_never_match(mappings, analyte):
    (row,) = rows_of(single([entry({"syn name": 1})]))
    assert row["status"] == "not_recognised"
    assert row["reason"] == (
        "not recognised: no mapping stored for this get-based marker"
    )
    assert row["loinc_code"] is None


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
def test_measured_row_without_unit_is_unit_not_verified_and_blocks(mappings):
    preview = build_preview(raw(single([entry({"syn.nounit": 1, "syn.a": 2})])))
    reasons = {r["marker"]: r["reason"] for r in preview["rows"]}
    assert reasons["syn.nounit"] == "not recognised: unit not verified"
    assert preview["can_confirm"] is False


# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_calculated_ratio_group_and_deny_list_are_left_out(mappings):
    rows = rows_of(single([entry({"calculatedRatios.x": 1, "syn.denied": 2})]))
    assert {r["reason"] for r in rows} == {"not imported: calculated"}
    assert {r["status"] for r in rows} == {"not_imported"}


# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_derived_from_is_left_out_with_its_reason_and_can_still_confirm(mappings):
    body = single(
        [
            entry(
                {"syn.a": 1, "syn.other": 3},
                markerSources={"syn.other": {"derivedFrom": ["syn.a"]}},
            )
        ]
    )
    preview = build_preview(raw(body))
    other = next(r for r in preview["rows"] if r["marker"] == "syn.other")
    assert other["reason"] == (
        "not imported: calculated by get-based from other markers, not measured"
    )
    assert preview["summary"]["left_out"] == 1
    assert preview["summary"]["left_out_calculated"] == 1
    assert preview["can_confirm"] is True


# scenario: biomarkers-and-labs::deleted-markers-are-not-imported
def test_deleted_marker_is_left_out_and_does_not_block(mappings):
    body = single([entry({"syn.a": 1, "syn.b": 2}, deletedMarkers={"syn.b": 5})])
    preview = build_preview(raw(body))
    gone = next(r for r in preview["rows"] if r["marker"] == "syn.b")
    assert gone["reason"] == "not imported: deleted in get-based"
    assert preview["summary"]["left_out_deleted"] == 1
    assert preview["can_confirm"] is True


# scenario: biomarkers-and-labs::preview-before-anything-is-saved
def test_value_text_is_exact_and_booleans_and_other_types_are_not_numbers(mappings):
    text = '{"version":2,"entries":[{"date":"2026-01-02","markers":{"syn.a":0.10,"syn.b":true,"syn.c":"x","syn.d":null,"syn.e":3}}]}'
    rows = {r["marker"]: r for r in build_preview(text.encode())["rows"]}
    assert rows["syn.a"]["value"] == "0.10"
    assert rows["syn.e"]["value"] == "3"
    for key in ("syn.b", "syn.c", "syn.d"):
        assert rows[key]["status"] == "not_recognised"
        assert rows[key]["reason"] == "not recognised: the value is not a number"
        assert rows[key]["value"] is None


def test_date_must_be_yyyy_mm_dd(mappings):
    for bad in ("02/01/2026", "2026-13-45", None, "2026-01-02T10:00:00"):
        (row,) = rows_of(single([entry({"syn.a": 1}, day=bad)]))
        assert row["status"] == "not_recognised"
        assert row["reason"] == "not recognised: date not in YYYY-MM-DD form"
        assert row["date"] is None


def test_entries_without_markers_and_malformed_parts_are_skipped(mappings):
    body = single([{"date": "2026-01-02"}, "junk", entry({"syn.a": 1})])
    body["entries"][2]["markerSources"] = "junk"
    body["entries"][2]["deletedMarkers"] = "junk"
    assert len(rows_of(body)) == 1


def test_empty_mapping_table_makes_everything_not_recognised(db):
    preview = build_preview(raw(single([entry({"syn.a": 1})])))
    assert preview["summary"]["matched"] == 0
    assert preview["can_confirm"] is False


# scenario: biomarkers-and-labs::preview-before-anything-is-saved
def test_flags_follow_the_fail_closed_rules(mappings):
    markers = {f"syn.{c}": 1 for c in "abcdef"}
    sources = {
        "syn.a": {"snapshotId": "s1"},
        "syn.b": {"file": "f.pdf", "manuallyEdited": True},
        "syn.c": {"reported": True},
        "syn.d": None,
    }
    with_model = entry(
        markers,
        markerSources=sources,
        importedWith={"provider": "", "modelId": "synthetic-model"},
    )
    flags = {r["marker"]: r["flags"] for r in rows_of(single([with_model]))}
    ai = flags["syn.a"][0]
    assert ai["code"] == "ai_read"
    assert ai["text"] == "read by an AI model, check against your report"
    assert (ai["model_id"], ai["provider"]) == ("synthetic-model", "unknown")
    assert ai["qualifier"] == (
        "last import into this date; the model for this value is unknown"
    )
    assert [f["code"] for f in flags["syn.b"]] == ["ai_read", "edited_after_import"]
    assert flags["syn.c"][0]["text"] == (
        "origin not shown in get-based, check against your report"
    )
    assert flags["syn.d"][0]["text"] == "origin unknown, check against your report"
    assert flags["syn.e"][0]["code"] == "origin_unknown"
    without = entry(markers, markerSources=sources)
    code = {r["marker"]: r["flags"][0]["code"] for r in rows_of(single([without]))}
    assert code["syn.a"] == "may_be_ai_read"


# scenario: biomarkers-and-labs::exactly-one-profile-is-imported
def test_bundle_with_two_profiles_and_no_choice_lists_ids_only(mappings):
    body = bundle(
        [profile("p1", [entry({"syn.a": 1})]), profile("p2", [entry({"syn.a": 2})])]
    )
    out = build_preview(raw(body))
    assert out["status"] == "choose_profile"
    assert out["profile_ids"] == ["p1", "p2"]
    assert "rows" not in out
    assert not any(s in json.dumps(out) for s in SECRETS)


# scenario: biomarkers-and-labs::exactly-one-profile-is-imported
def test_chosen_profile_only_and_unknown_profile_rejected(mappings):
    body = bundle(
        [profile("p1", [entry({"syn.a": 1})]), profile("p2", [entry({"syn.x": 2})])]
    )
    out = build_preview(raw(body), "p2")
    assert [r["marker"] for r in out["rows"]] == ["syn.x"]
    with pytest.raises(GetbasedImportError):
        build_preview(raw(body), "nope")


def test_single_profile_bundle_needs_no_choice_and_profile_without_data(mappings):
    only = bundle([profile("p1", [entry({"syn.a": 1})])])
    assert len(build_preview(raw(only))["rows"]) == 1
    bare = bundle([{"id": "p1"}])
    assert build_preview(raw(bare), "p1")["rows"] == []


def test_single_client_export_rejects_a_profile_id(mappings):
    with pytest.raises(GetbasedImportError):
        build_preview(raw(single([entry({"syn.a": 1})])), "p1")


# scenario: biomarkers-and-labs::unknown-archive-format-version-rejected
@pytest.mark.parametrize(
    ("body", "needle"),
    [
        ({"format": "labcharts-backup", "version": 1}, "labcharts-backup"),
        ({"format": "getbased-migration", "version": 1}, "getbased-migration"),
        ({"version": 1, "entries": []}, "version 1"),
        ({"version": 3, "entries": []}, "version 3"),
        ({"entries": []}, "version missing"),
        ({"version": 2.0, "entries": []}, "2.0"),
        ({"version": True, "entries": []}, "version true"),
        ({"type": "database", "profiles": [], "version": 1}, "database"),
        ({"type": "database", "profiles": [], "version": 2}, "no readable profiles"),
        ({"type": "database", "profiles": ["x"], "version": 2}, "no readable"),
        ({"something": "else"}, "Unsupported"),
        ([1, 2], "not an object"),
    ],
)
def test_unsupported_archives_are_rejected_naming_supported_forms(body, needle):
    with pytest.raises(GetbasedImportError) as exc:
        build_preview(json.dumps(body).encode())
    assert needle in str(exc.value)
    if "readable" not in needle:
        assert "version 2" in str(exc.value)


# scenario: biomarkers-and-labs::unknown-archive-format-version-rejected
def test_api_rejects_bad_files_with_400(client, db):
    assert post(client, {"format": "labcharts-backup", "version": 1}).status_code == 400
    assert post(client, b"\xff\xfe\x00").status_code == 400
    assert post(client, b"{not json").status_code == 400
    assert post(client, b"[" * 100000).status_code == 400
    assert post(client, b'{"version":2,"entries":[],"x":NaN}').status_code == 400
    resp = post(client, {"version": 1, "entries": []})
    assert resp.status_code == 400
    assert "version 1" in json.dumps(resp.json())
    assert client.post(URL, {}, format="multipart").status_code == 400


def test_api_bounds_file_size_and_profile_id(client, db, monkeypatch):
    monkeypatch.setattr("core.getbased_views.MAX_FILE_BYTES", 10)
    assert post(client, single([])).status_code == 400
    monkeypatch.undo()
    ok = single([])
    assert post(client, ok, profile_id="x" * 201).status_code == 400
    bad = bundle([profile("p1", [])])
    assert post(client, bad, profile_id="nope").status_code == 400
    assert post(client, bad, profile_id="p1").status_code == 200


# scenario: biomarkers-and-labs::preview-before-anything-is-saved
# scenario: biomarkers-and-labs::identity-and-non-lab-data-are-never-stored
def test_preview_stores_nothing_and_leaks_no_identity(client, mappings, caplog):
    caplog.set_level(logging.DEBUG)
    before = counts()
    body = bundle(
        [profile("p1", [entry({"syn.a": 1})]), profile("p2", [entry({"syn.a": 2})])]
    )
    for extra in ({}, {"profile_id": "p1"}):
        resp = post(client, body, **extra)
        assert resp.status_code == 200
        text = resp.content.decode() + caplog.text
        for secret in [*SECRETS, "synthetic chat", "synthetic meal", "nodeUrl"]:
            assert secret not in text
    out = post(client, single([entry({"syn.a": 1})]))
    assert out.status_code == 200
    assert out.json()["summary"]["matched"] == 1
    assert not any(
        s in out.content.decode() + caplog.text for s in [*SECRETS, "synthetic chat"]
    )
    assert counts() == before


# scenario: biomarkers-and-labs::preview-before-anything-is-saved
def test_anonymous_is_refused_and_session_post_needs_csrf(user, db):
    assert APIClient().post(URL, {}, format="multipart").status_code == 401
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    token = _get_new_csrf_string()
    client.cookies["csrftoken"] = token
    f = SimpleUploadedFile("a.json", raw(single([])), content_type="application/json")
    assert client.post(URL, {"file": f}).status_code == 403
    f2 = SimpleUploadedFile("a.json", raw(single([])), content_type="application/json")
    assert client.post(URL, {"file": f2}, HTTP_X_CSRFTOKEN=token).status_code == 200


# scenario: biomarkers-and-labs::preview-before-anything-is-saved
def test_oversized_marker_map_and_entry_list_are_refused_with_400(
    client, db, monkeypatch
):
    monkeypatch.setattr("core.getbased_import.MAX_ROWS", 3)
    big = {"k." + str(i): 1 for i in range(4)}
    assert post(client, single([entry(big)])).status_code == 400
    small = {"k.a": 1, "k.b": 1}
    assert post(client, single([entry(small)])).status_code == 200
    monkeypatch.setattr("core.getbased_import.MAX_ENTRIES", 1)
    assert post(client, single([entry({}), entry({})])).status_code == 400
