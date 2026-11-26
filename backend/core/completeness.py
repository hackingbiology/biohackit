# SPDX-License-Identifier: AGPL-3.0-or-later
"""Completeness and freshness per organ system (M02 TG-h part 1). Deterministic.

Each stored OrganSystemPanel lists its expected Biomarkers. For one user, across all of
their reports, a marker is present when a LabResult exists that is not disputed or
retracted. Freshness is the newest `collected_at`, else `reported_at`. No panel or
marker list is written here. No AI, nothing is stored.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from .calculated_markers import _iso, _source_dict
from .models import Biomarker, LabResult, OrganSystemPanel
from .phenoage_binding import EXCLUDED_STATES


def _newest_dates(user: Any, biomarker_ids: set[int]) -> dict[int, datetime | None]:
    """Biomarker id to its newest result date (None: present, no dated result)."""
    newest: dict[int, datetime | None] = {}
    results = (
        LabResult.objects.filter(report__owner=user, biomarker_id__in=biomarker_ids)
        .exclude(validation_state__in=EXCLUDED_STATES)
        .only("biomarker_id", "collected_at", "reported_at")
    )
    for result in results:
        date = result.collected_at or result.reported_at
        current = newest.get(result.biomarker_id)
        newest[result.biomarker_id] = (
            date
            if current is None or (date is not None and date > current)
            else current
        )
    return newest


def _marker(biomarker: Biomarker) -> dict[str, Any]:
    return {"biomarker_id": biomarker.pk, "loinc_code": biomarker.loinc_code}


def _one(
    panel: OrganSystemPanel, newest: dict[int, datetime | None], now: datetime
) -> dict[str, Any]:
    expected = sorted(panel.expected_biomarkers.all(), key=lambda b: b.pk)
    present = [b for b in expected if b.pk in newest]
    missing = [b for b in expected if b.pk not in newest]
    dates = [d for b in present if (d := newest[b.pk]) is not None]
    last = max(dates) if dates else None
    return {
        "name": panel.name,
        "source": _source_dict(panel.source),
        "expected_count": len(expected),
        "present_count": len(present),
        "present": [_marker(b) for b in present],
        "missing": [_marker(b) for b in missing],
        "last_collected_at": _iso(last),
        "age_days": None if last is None else (now - last).days,
        "sparse": len(present) < len(expected),
    }


def panel_completeness(
    user: Any, panels: Iterable[OrganSystemPanel], now: datetime
) -> list[dict[str, Any]]:
    """Completeness and freshness of each panel from this user's results."""
    panel_list = list(panels)
    ids = {b.pk for p in panel_list for b in p.expected_biomarkers.all()}
    newest = _newest_dates(user, ids)
    return [_one(p, newest, now) for p in panel_list]
