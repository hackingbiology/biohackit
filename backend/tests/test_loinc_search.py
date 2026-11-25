# SPDX-License-Identifier: AGPL-3.0-or-later
"""LOINC search API. All rows are SYNTHETIC (99999-x codes), never real LOINC content."""

from datetime import date

import pytest
from django.db import connection
from rest_framework.test import APIClient

from accounts.models import User
from terminology.models import LoincTerm, Source
from terminology.search import search_loinc

URL = "/api/terminology/loinc/"
SOURCE_KEYS = {"name", "version", "licence", "url", "retrieved_at"}
RESULT_KEYS = {
    "loinc_num",
    "long_common_name",
    "short_name",
    "component",
    "system",
    "property",
    "scale_type",
    "status",
    "source",
}


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="LOINC",
        version="SYNTHETIC-1",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 25),
    )


@pytest.fixture
def term(source):
    return LoincTerm.objects.create(
        loinc_num="99999-1",
        long_common_name="Synthetic glucose test analyte",
        short_name="Syn Glu",
        component="Glucose",
        system="Blood",
        property="MCnc",
        scale_type="Qn",
        status="ACTIVE",
        source=source,
    )


@pytest.fixture
def api(db):
    user = User.objects.create_user(email="s@example.org", password="x-test-pass-1")
    client = APIClient()
    client.force_authenticate(user)
    return client


def codes(response):
    return [r["loinc_num"] for r in response.json()["results"]]


# scenario: terminology-reference-data::loinc-search-by-name
def test_search_by_name(api, term):
    LoincTerm.objects.create(
        loinc_num="99999-2",
        long_common_name="Synthetic sodium test",
        source=term.source,
    )
    response = api.get(URL, {"q": "glucose"})
    assert response.status_code == 200
    assert codes(response) == ["99999-1"]


# scenario: terminology-reference-data::loinc-search-tolerates-a-typo
def test_search_tolerates_typo(api, term):
    assert codes(api.get(URL, {"q": "glucse"})) == ["99999-1"]


# scenario: terminology-reference-data::loinc-search-tolerates-a-typo
def test_typo_in_a_word_inside_a_long_name(api, source):
    LoincTerm.objects.create(
        loinc_num="99996-1",
        long_common_name="Synthetic fructosamine in serum analyte",
        short_name="Syn Other",
        component="Other",
        source=source,
    )
    assert codes(api.get(URL, {"q": "fructosmine"})) == ["99996-1"]


# scenario: terminology-reference-data::loinc-search-by-exact-code
def test_search_by_exact_code_first(api, term):
    LoincTerm.objects.create(
        loinc_num="99999-2",
        long_common_name="Synthetic 99999-1 mention",
        source=term.source,
    )
    assert codes(api.get(URL, {"q": " 99999-1 "}))[0] == "99999-1"


# scenario: terminology-reference-data::loinc-search-is-paginated
def test_search_is_paginated_and_bounded(api, source):
    LoincTerm.objects.bulk_create(
        LoincTerm(
            loinc_num=f"99998-{i}",
            long_common_name="Synthetic paged analyte",
            source=source,
        )
        for i in range(101)
    )
    data = api.get(URL, {"q": "paged"}).json()
    assert {"count", "next", "previous", "results"} <= set(data)
    assert data["count"] == 101
    assert len(data["results"]) == 20
    assert data["next"] is not None
    big = api.get(URL, {"q": "paged", "page_size": 1000}).json()
    assert len(big["results"]) == 100
    small = api.get(URL, {"q": "paged", "page_size": 5}).json()
    assert len(small["results"]) == 5


# scenario: terminology-reference-data::loinc-search-rejects-an-empty-query
@pytest.mark.parametrize("params", [{}, {"q": ""}, {"q": "   "}])
def test_empty_query_rejected(api, params):
    response = api.get(URL, params)
    assert response.status_code == 400
    assert response.json() == {"q": "Enter a word or a LOINC code to search."}


# scenario: terminology-reference-data::loinc-search-requires-authentication
def test_anonymous_is_rejected(db):
    assert APIClient().get(URL, {"q": "glucose"}).status_code == 401


# scenario: terminology-reference-data::loinc-search-returns-provenance
def test_result_has_provenance(api, term):
    result = api.get(URL, {"q": "glucose"}).json()["results"][0]
    assert set(result) == RESULT_KEYS
    assert set(result["source"]) == SOURCE_KEYS
    assert result["source"]["version"] == "SYNTHETIC-1"


def test_ordering_is_deterministic(api, source):
    for num in ("99997-3", "99997-1", "99997-2"):
        LoincTerm.objects.create(
            loinc_num=num, long_common_name="Synthetic tie analyte", source=source
        )
    assert codes(api.get(URL, {"q": "tie"})) == ["99997-1", "99997-2", "99997-3"]


def test_trigram_and_fulltext_branches_use_indexes(source):
    LoincTerm.objects.bulk_create(
        LoincTerm(
            loinc_num=f"99998-{i}",
            long_common_name=f"Synthetic analyte number {i}",
            short_name=f"Syn {i}",
            component=f"Comp{i}",
            source=source,
        )
        for i in range(3000)
    )
    with connection.cursor() as cur:
        cur.execute("ANALYZE terminology_loincterm")
        cur.execute("SET LOCAL enable_seqscan = off")
    plan = search_loinc("glucse").explain()
    for index in (
        "loinc_trgm_long_idx",
        "loinc_trgm_short_idx",
        "loinc_trgm_comp_idx",
        "loinc_fts_idx",
    ):
        assert index in plan
