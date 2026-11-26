# SPDX-License-Identifier: AGPL-3.0-or-later
"""Completeness and freshness per organ system (M02 TG-h part 1). Synthetic rows only:
the panel, analytes and source are test fixtures, not seeded data (Q84)."""

from datetime import UTC, date, datetime

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from accounts.models import User
from core.completeness import panel_completeness
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
    OrganSystemPanel,
)
from terminology.models import Source, Unit

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=UTC)


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def other(db):
    return User.objects.create_user(email="b@example.com", password="correct-horse-9")


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def markers(source):
    unit = Unit.objects.create(ucum_code="u1", display="u1", source=source)
    return [
        Biomarker.objects.create(
            name=f"synthetic {i}",
            loinc_code=f"T-{i}",
            role=BiomarkerRole.BASELINE,
            unit=unit,
            source=source,
        )
        for i in range(13)
    ]


@pytest.fixture
def panel(markers, source):
    p = OrganSystemPanel.objects.create(name="synthetic system", source=source)
    p.expected_biomarkers.set(markers)
    return p


def report_for(owner):
    return LabReport.objects.create(owner=owner, origin=LabReportOrigin.MANUAL)


def add(owner, biomarker, **kw):
    return LabResult.objects.create(
        report=report_for(owner),
        biomarker=biomarker,
        reported_value="1",
        reported_unit="u1",
        **kw,
    )


def run(user, panel):
    (entry,) = panel_completeness(user, [panel], NOW)
    return entry


# scenario: biomarkers-and-labs::sparse-metabolic-panel
def test_sparse_panel_six_of_thirteen_four_months_old(user, panel, markers):
    for i, m in enumerate(markers[:6]):
        add(user, m, collected_at=datetime(2026, 7, 26 - i, 8, 0, tzinfo=UTC))
    entry = run(user, panel)
    assert entry["name"] == "synthetic system"
    assert entry["source"]["name"] == "synthetic fixture"
    assert entry["expected_count"] == 13
    assert entry["present_count"] == 6
    assert len(entry["present"]) == 6
    assert len(entry["missing"]) == 7
    assert entry["missing"][0]["loinc_code"] == "T-6"
    assert entry["sparse"] is True
    assert entry["last_collected_at"].startswith("2026-07-26T08:00")
    assert entry["age_days"] == 123


def test_other_users_results_not_counted(user, other, panel, markers):
    add(other, markers[0], collected_at=datetime(2026, 11, 1, tzinfo=UTC))
    entry = run(user, panel)
    assert entry["present_count"] == 0
    assert entry["last_collected_at"] is None
    assert entry["age_days"] is None


def test_counts_across_reports(user, panel, markers):
    add(user, markers[0], collected_at=datetime(2026, 10, 1, tzinfo=UTC))
    add(user, markers[1], collected_at=datetime(2026, 11, 1, tzinfo=UTC))
    entry = run(user, panel)
    assert entry["present_count"] == 2
    assert entry["age_days"] == 25


@pytest.mark.parametrize(
    "state", [LabResultValidation.DISPUTED, LabResultValidation.RETRACTED]
)
def test_disputed_and_retracted_excluded(user, panel, markers, state):
    result = add(user, markers[0], collected_at=datetime(2026, 11, 1, tzinfo=UTC))
    result.set_validation_state(state)
    entry = run(user, panel)
    assert entry["present_count"] == 0
    assert entry["last_collected_at"] is None


def test_reported_at_is_the_fallback_date(user, panel, markers):
    add(user, markers[0], reported_at=datetime(2026, 11, 16, 12, 0, tzinfo=UTC))
    entry = run(user, panel)
    assert entry["present_count"] == 1
    assert entry["age_days"] == 10


def test_undated_result_counts_but_has_no_freshness(user, panel, markers):
    add(user, markers[0])
    entry = run(user, panel)
    assert entry["present_count"] == 1
    assert entry["last_collected_at"] is None
    assert entry["age_days"] is None


def test_empty_panel_is_zero_of_zero(user, source):
    empty = OrganSystemPanel.objects.create(name="empty", source=source)
    entry = run(user, empty)
    assert entry["expected_count"] == 0
    assert entry["present_count"] == 0
    assert entry["sparse"] is False
    assert entry["last_collected_at"] is None


def test_complete_panel_is_not_sparse(user, panel, markers):
    for m in markers:
        add(user, m, collected_at=datetime(2026, 11, 26, tzinfo=UTC))
    entry = run(user, panel)
    assert entry["present_count"] == 13
    assert entry["sparse"] is False


def test_panel_without_source_is_rejected(db):
    with pytest.raises(ValidationError):
        OrganSystemPanel.objects.create(name="no source")


def test_api_lists_panels_by_name_for_the_caller_only(user, other, panel, markers):
    OrganSystemPanel.objects.create(name="a first", source=panel.source)
    add(user, markers[0], collected_at=datetime(2026, 11, 1, tzinfo=UTC))
    add(other, markers[1], collected_at=datetime(2026, 11, 1, tzinfo=UTC))
    client = APIClient()
    client.force_authenticate(user)
    response = client.get("/api/labs/completeness/")
    assert response.status_code == 200
    names = [p["name"] for p in response.json()["panels"]]
    assert names == ["a first", "synthetic system"]
    assert response.json()["panels"][1]["present_count"] == 1


def test_api_with_no_panels_is_empty(user):
    client = APIClient()
    client.force_authenticate(user)
    response = client.get("/api/labs/completeness/")
    assert response.status_code == 200
    assert response.json() == {"panels": []}


def test_api_requires_authentication(db):
    response = APIClient().get("/api/labs/completeness/")
    assert response.status_code in (401, 403)
