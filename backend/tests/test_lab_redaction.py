# SPDX-License-Identifier: AGPL-3.0-or-later
"""Opt-in deterministic PII redaction for the CSV lab import (M02 TG-d part 1).
Synthetic names and IDs only."""

from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabResult
from core.redaction import PLACEHOLDER, redact_text
from terminology.models import Source, Unit

PREVIEW = "/api/labs/imports/csv/preview/"
CONFIRM = "/api/labs/imports/csv/confirm/"
HEAD = "loinc_code,value,unit,collected_at,reported_at,laboratory,method\n"
ROW = "0000-0,1,xa/L,,,Mario Rossi lab ID-7,method of mario\n"


@pytest.fixture
def client(db):
    c = APIClient()
    c.force_authenticate(
        User.objects.create_user(email="a@example.com", password="correct-horse-9")
    )
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
    f = SimpleUploadedFile(name, content.encode(), content_type="text/csv")
    return client.post(url, {"file": f, **extra}, format="multipart")


def counts():
    return LabReport.objects.count(), LabResult.objects.count()


# scenario: biomarkers-and-labs::user-opts-to-obfuscate
def test_preview_with_terms_shows_removals_with_offsets(client, analyte):
    resp = post(client, PREVIEW, HEAD + ROW, redact_terms=["mario", "ID-7"])
    body = resp.json()
    assert resp.status_code == 200
    removals = body["redaction"]["removals"]
    assert body["redaction"]["applied"] is True
    got = [
        (r["row"], r["column"], r["term_index"], r["start"], r["end"], r["line"])
        for r in removals
    ]
    assert got == [
        (1, "laboratory", 0, 0, 5, 1),
        (1, "laboratory", 1, 16, 20, 1),
        (1, "method", 0, 10, 15, 1),
    ]
    assert all(r["replacement"] == PLACEHOLDER for r in removals)
    text = resp.content.decode()
    assert "Mario" not in text and "ID-7" not in text
    assert body["rows"][0]["status"] == "recognised"
    assert counts() == (0, 0)


# scenario: biomarkers-and-labs::user-opts-to-obfuscate
def test_confirm_stores_placeholder_only(client, analyte):
    resp = post(
        client,
        CONFIRM,
        HEAD + ROW,
        name="mario-rossi.csv",
        laboratory="Rossi Lab",
        redact_terms=["Mario", "ID-7", "rossi"],
    )
    assert resp.status_code == 201
    report = LabReport.objects.get()
    result = LabResult.objects.get()
    stored = " ".join(
        str(x).lower()
        for x in (
            report.import_name,
            report.laboratory,
            result.laboratory,
            result.method,
        )
    )
    for term in ("mario", "rossi", "id-7"):
        assert term not in stored
    assert PLACEHOLDER.lower() in stored


def test_without_terms_nothing_changes(client, analyte):
    body = post(client, PREVIEW, HEAD + ROW).json()
    assert body["redaction"] == {"applied": False, "removals": []}
    assert [r["status"] for r in body["rows"]] == ["recognised"]
    assert post(client, CONFIRM, HEAD + ROW, name="mario.csv").status_code == 201
    assert LabResult.objects.get().laboratory == "Mario Rossi lab ID-7"
    assert LabReport.objects.get().import_name == "mario.csv"


def test_longest_term_wins_in_import(client, analyte):
    terms = ["Mario", "Mario Rossi"]
    body = post(client, PREVIEW, HEAD + ROW, redact_terms=terms).json()
    first = body["redaction"]["removals"][0]
    assert (first["term_index"], first["start"], first["end"]) == (1, 0, 11)


@pytest.mark.parametrize("terms", [[""], ["  "], ["a"] * 21, ["x" * 201]])
@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_bad_terms_give_400_naming_field(client, analyte, url, terms):
    resp = post(client, url, HEAD + ROW, redact_terms=terms)
    assert resp.status_code == 400
    assert "redact_terms" in resp.json()
    assert counts() == (0, 0)


@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_redaction_that_overlong_name_gives_400(client, analyte, url):
    name = "q-" * 97 + ".csv"
    resp = post(client, url, HEAD + ROW, name=name, redact_terms=["q"])
    assert resp.status_code == 400
    assert "redact_terms" in resp.json()
    assert counts() == (0, 0)


@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_redaction_that_overlong_laboratory_gives_400(client, analyte, url):
    resp = post(client, url, HEAD + ROW, laboratory="q-" * 97, redact_terms=["q"])
    assert resp.status_code == 400
    assert "redact_terms" in resp.json()
    assert counts() == (0, 0)


@pytest.mark.parametrize(
    ("hit", "term"),
    [
        ("loinc_code", "0000"),
        ("value", "1"),
        ("unit", "xa"),
        ("collected_at", "2026"),
        ("reported_at", "2026"),
    ],
)
def test_term_in_structured_column_blocks_row(client, analyte, hit, term):
    cells = {
        "loinc_code": "0000-0",
        "value": "1",
        "unit": "xa/L",
        "collected_at": "",
        "reported_at": "",
    }
    if hit in ("collected_at", "reported_at"):
        cells[hit] = "2026-01-01"
    csv_text = HEAD + ",".join(cells.values()) + ",,\n"
    row = post(client, PREVIEW, csv_text, redact_terms=[term]).json()["rows"][0]
    assert row["status"] == "not_recognised"
    assert row["reason"].startswith(hit)
    assert "matches a redaction term" in row["reason"]
    assert post(client, CONFIRM, csv_text, redact_terms=[term]).status_code == 400
    assert counts() == (0, 0)


def test_overlapping_terms_starting_apart_redact_both(client, analyte):
    row = "0000-0,1,xa/L,,,Anna Maria Rossi,\n"
    terms = ["Anna Maria", "Maria Rossi"]
    body = post(client, PREVIEW, HEAD + row, redact_terms=terms).json()
    removals = body["redaction"]["removals"]
    assert [(r["start"], r["end"]) for r in removals] == [(0, 16)]
    assert post(client, CONFIRM, HEAD + row, redact_terms=terms).status_code == 201
    assert LabResult.objects.get().laboratory == PLACEHOLDER


def test_too_many_removals_gives_400(client, analyte):
    rows = "0000-0,1,xa/L,,,q q q q q q,\n" * 200
    resp = post(client, PREVIEW, HEAD + rows, redact_terms=["q"])
    assert resp.status_code == 400
    assert "redact_terms" in resp.json()
    assert counts() == (0, 0)


def test_too_many_rows_rejected_before_redaction(client, analyte):
    rows = ROW * 201
    resp = post(client, PREVIEW, HEAD + rows, redact_terms=["mario"])
    assert resp.status_code == 400
    assert "file" in resp.json()


def test_redact_text_overlap_keeps_nothing_of_longer_match():
    result = redact_text("Anna Maria Rossi", ["Anna Maria", "Maria Rossi"])
    assert "Rossi" not in result.redacted
    assert result.redacted == PLACEHOLDER
    assert [(r.start, r.end, r.line) for r in result.removals] == [(0, 16, 1)]


def test_redact_text_adjacent_spans_merge_and_name_longest():
    result = redact_text("AB\nCDE", ["AB", "CDE"])
    assert [(r.start, r.end, r.line, r.term_index) for r in result.removals] == [
        (0, 2, 1, 0),
        (3, 6, 2, 1),
    ]
    merged = redact_text("ABCDE", ["AB", "CDE"])
    assert [(r.start, r.end, r.term_index) for r in merged.removals] == [(0, 5, 1)]


def test_redact_text_is_deterministic_and_does_not_echo():
    text = "Anna visits\nanna again; ANNA"
    first = redact_text(text, ["anna"])
    assert first == redact_text(text, ["anna"])
    assert first.redacted == (
        PLACEHOLDER + " visits\n" + PLACEHOLDER + " again; " + PLACEHOLDER
    )
    spans = [(r.start, r.end, r.line) for r in first.removals]
    assert spans == [(0, 4, 1), (12, 16, 2), (24, 28, 2)]
    assert "anna" not in repr(first.removals).lower()


@pytest.mark.parametrize("term", ["", "   "])
def test_redact_text_rejects_blank_term(term):
    with pytest.raises(ValueError):
        redact_text("x", [term])


# scenario: biomarkers-and-labs::user-opts-to-obfuscate
@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
@pytest.mark.parametrize("column", ["laboratory", "method"])
def test_cell_overflowing_only_after_redaction_names_redact_terms(
    client, analyte, url, column
):
    cell = "q-" * 100  # 200 characters: within the limit before redaction
    lab = cell if column == "laboratory" else "lab"
    method = cell if column == "method" else "m"
    row = "0000-0,1,xa/L,,," + lab + "," + method + "\n"
    resp = post(client, url, HEAD + row, redact_terms=["q"])
    assert resp.status_code == 400
    assert "redact_terms" in resp.json()
    assert "file" not in resp.json()
    assert counts() == (0, 0)


@pytest.mark.parametrize("terms", [[], ["zzz"]])
def test_cell_over_limit_in_file_names_file(client, analyte, terms):
    row = "0000-0,1,xa/L,,," + "a" * 201 + ",m\n"
    resp = post(client, PREVIEW, HEAD + row, redact_terms=terms)
    assert resp.status_code == 400
    assert "file" in resp.json()
    assert "redact_terms" not in resp.json()


def test_whitespace_padded_cell_is_rejected_not_scanned(client, analyte):
    # Chosen behaviour: the csv module's own 128 KiB field limit rejects the padded cell
    # as a file problem before any term is scanned; a smaller padded cell is stripped by
    # both the bounds check and the redaction, so the padding is never scanned.
    pad = " " * (1024 * 1024 - 300)
    row = "0000-0,1,xa/L,,,x" + pad + ",m\n"
    resp = post(client, PREVIEW, HEAD + row, redact_terms=["a", "b", "c", "d"])
    assert resp.status_code == 400
    assert "file" in resp.json()
    assert "redact_terms" not in resp.json()
    small = "0000-0,1,xa/L,,,zq" + " " * 100000 + ",m\n"
    ok = post(client, PREVIEW, HEAD + small, redact_terms=["zq"])
    assert ok.status_code == 200
    removals = ok.json()["redaction"]["removals"]
    assert [(r["column"], r["start"], r["end"]) for r in removals] == [
        ("laboratory", 0, 2)
    ]


def test_redact_text_overlapping_hits_in_repeated_text():
    result = redact_text("aaaa", ["aa"])
    assert [(r.start, r.end, r.term_index) for r in result.removals] == [(0, 4, 0)]
    assert result.redacted == PLACEHOLDER


def test_redact_text_case_insensitive_multiline_lines():
    result = redact_text("x\nMarIo\nmario", ["MARIO"])
    spans = [(r.start, r.end, r.line) for r in result.removals]
    assert spans == [(2, 7, 2), (8, 13, 3)]
    assert result.redacted == "x\n" + PLACEHOLDER + "\n" + PLACEHOLDER


# scenario: biomarkers-and-labs::user-opts-to-obfuscate
@pytest.mark.parametrize(
    ("text", "term"),
    [
        ("ΚΩΣΤΑΣΑΚΗΣ", "ΚΩΣΤΑΣ"),
        ("ΟΣΑ", "ΟΣ"),
        ("İLKER", "ilker"),
        ("Roſſi", "rossi"),
    ],
)
def test_redact_text_keeps_regex_case_rules_for_unicode(text, term):
    result = redact_text(text, [term])
    assert len(result.removals) == 1
    assert PLACEHOLDER in result.redacted


def test_redaction_module_has_no_per_term_regex_scan():
    import core.redaction as module

    with open(module.__file__) as handle:
        assert "finditer" not in handle.read()
