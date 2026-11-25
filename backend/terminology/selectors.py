# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import OptimalRange, ReferenceRange, StratifiedRange

if TYPE_CHECKING:
    from core.models import Biomarker


@dataclass(frozen=True)
class Subject:
    """Who a range is for. None = unknown: it matches only rows with that stratum null."""

    age_years: int | None = None
    sex: str | None = None
    ancestry: str | None = None


def _present(value: str | None) -> bool:
    return bool((value or "").strip())


def _norm(value: str | None) -> str | None:
    return (value or "").strip().casefold() or None


def _has_age_band(row: StratifiedRange) -> bool:
    return row.age_min_years is not None or row.age_max_years is not None


def _age_applies(row: StratifiedRange, age: int | None) -> bool:
    if not _has_age_band(row):
        return True
    if age is None:
        return False
    if row.age_min_years is not None and age < row.age_min_years:
        return False
    return row.age_max_years is None or age < row.age_max_years


def _applies(row: StratifiedRange, subject: Subject) -> bool:
    return (
        _age_applies(row, subject.age_years)
        and (row.sex is None or row.sex == subject.sex)
        and (
            _norm(row.ancestry) is None
            or _norm(row.ancestry) == _norm(subject.ancestry)
        )
    )


def _specificity(row: StratifiedRange) -> int:
    return (
        int(_has_age_band(row))
        + int(row.sex is not None)
        + int(_norm(row.ancestry) is not None)
    )


def _most_specific[R: StratifiedRange](rows: Iterable[R], subject: Subject) -> R | None:
    applicable = [r for r in rows if _applies(r, subject)]
    if not applicable:
        return None
    top = max(_specificity(r) for r in applicable)
    best = [r for r in applicable if _specificity(r) == top]
    return best[0] if len(best) == 1 else None


def _complete(row: OptimalRange, biomarker: "Biomarker") -> bool:
    return (
        row.source_id is not None
        and row.unit_id == biomarker.unit_id
        and _present(row.population)
        and _present(row.endpoint)
        and _present(row.evidence_grade)
        and row.last_reviewed is not None
    )


def displayable_optimal_range(
    biomarker: "Biomarker", subject: Subject | None = None
) -> OptimalRange | None:
    """The most specific complete optimal range applying to the subject; None if none
    applies or several tie at the top specificity (we never guess, Q49)."""
    rows = OptimalRange.objects.filter(biomarker=biomarker)
    complete = [r for r in rows if _complete(r, biomarker)]
    return _most_specific(complete, subject or Subject())


def applicable_reference_range(
    biomarker: "Biomarker", subject: Subject | None = None
) -> ReferenceRange | None:
    """Same rule for reference ranges (a Source is present by construction)."""
    rows = ReferenceRange.objects.filter(biomarker=biomarker)
    same_unit = [r for r in rows if r.unit_id == biomarker.unit_id]
    return _most_specific(same_unit, subject or Subject())
