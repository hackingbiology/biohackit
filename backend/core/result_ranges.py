# SPDX-License-Identifier: AGPL-3.0-or-later
"""A stored lab result placed against its three ranges (M02 TG-m part 1).

The laboratory reference range, the longevity-optimal range and the safety threshold are
returned separately and never merged. Status rule, per range: `below` if value < low,
`above` if value > high, `inside` otherwise (bounds inclusive, a null bound is open);
`no_range` if no range applies (no bounds returned); `not_comparable` if the result has no
value in the analyte's unit. Nothing is converted here: only a stored normalised value is
used (Q82)."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from terminology.models import ReferenceRange, SafetyThreshold, Source
from terminology.selectors import (
    Subject,
    _applies,
    _most_specific,
    _norm,
    displayable_optimal_range,
)

from .models import LabResult

NO_VALUE_REASON = "no_value_in_analyte_unit"


@dataclass(frozen=True)
class Comparison:
    value: Decimal | None
    unit: str | None
    converted: bool = False
    source: Source | None = None


def comparison_value(result: LabResult) -> Comparison:
    """reported_value if reported in the analyte's unit, else the stored normalised
    value if it is in that unit, else nothing."""
    unit = result.biomarker.unit
    if result.reported_unit_ref_id == unit.pk:
        return Comparison(result.reported_value, unit.ucum_code)
    if result.normalised_value is not None and result.normalised_unit == unit.ucum_code:
        return Comparison(
            result.normalised_value, unit.ucum_code, True, result.normalised_source
        )
    return Comparison(None, None)


def status_of(value: Decimal, low: Decimal | None, high: Decimal | None) -> str:
    if low is not None and value < low:
        return "below"
    if high is not None and value > high:
        return "above"
    return "inside"


def _source(source: Source) -> dict[str, Any]:
    return {"name": source.name, "version": source.version, "url": source.url}


def _bounds(row: Any, unit: str) -> dict[str, Any]:
    return {
        "low": None if row.low is None else str(row.low),
        "high": None if row.high is None else str(row.high),
        "unit": unit,
        "source": _source(row.source),
    }


def _no_range() -> dict[str, Any]:
    return {"status": "no_range"}


def _with_status(body: dict[str, Any], row: Any, cmp: Comparison) -> dict[str, Any]:
    if cmp.value is None:
        body["status"] = "not_comparable"
        body["reason"] = NO_VALUE_REASON
    else:
        body["status"] = status_of(cmp.value, row.low, row.high)
    return body


def _lab_method_match(row: ReferenceRange) -> int:
    return int(_norm(row.lab) is not None) + int(_norm(row.method) is not None)


def _reference_row(result: LabResult, subject: Subject) -> ReferenceRange | None:
    lab, method = _norm(result.laboratory), _norm(result.method)
    rows = [
        r
        for r in ReferenceRange.objects.filter(
            biomarker=result.biomarker, unit=result.biomarker.unit
        ).select_related("source")
        if _norm(r.lab) in (None, lab) and _norm(r.method) in (None, method)
    ]
    if not rows:
        return None
    applicable = [r for r in rows if _applies(r, subject)]
    if not applicable:
        return None
    top = max(_lab_method_match(r) for r in applicable)
    return _most_specific(
        [r for r in applicable if _lab_method_match(r) == top], subject
    )


def _reference(result: LabResult, subject: Subject, cmp: Comparison) -> dict[str, Any]:
    row = _reference_row(result, subject)
    if row is None:
        return _no_range()
    body = _bounds(row, result.biomarker.unit.ucum_code)
    body.update(
        lab=row.lab,
        method=row.method,
        population=row.population,
        evidence_grade=row.evidence_grade,
    )
    return _with_status(body, row, cmp)


def _optimal(result: LabResult, subject: Subject, cmp: Comparison) -> dict[str, Any]:
    row = displayable_optimal_range(result.biomarker, subject)
    if row is None:
        return _no_range()
    body = _bounds(row, result.biomarker.unit.ucum_code)
    body.update(
        population=row.population,
        endpoint=row.endpoint,
        evidence_grade=row.evidence_grade,
        last_reviewed=row.last_reviewed.isoformat() if row.last_reviewed else None,
    )
    return _with_status(body, row, cmp)


def _safety(result: LabResult, cmp: Comparison) -> dict[str, Any]:
    rows = list(
        SafetyThreshold.objects.filter(
            biomarker=result.biomarker, unit=result.biomarker.unit
        ).select_related("source")
    )
    if not rows:
        return _no_range()
    if len(rows) > 1:
        return {"status": "no_range", "reason": "ambiguous_several_thresholds"}
    body = _bounds(rows[0], result.biomarker.unit.ucum_code)
    return _with_status(body, rows[0], cmp)


def result_ranges(result: LabResult, subject: Subject) -> dict[str, Any]:
    """The three ranges for one result, each with provenance and a computed status.
    A result with no value in the analyte's unit is `not_comparable` for every range that
    exists; a missing range stays `no_range`."""
    cmp = comparison_value(result)
    return {
        "reference_range": _reference(result, subject, cmp),
        "optimal_range": _optimal(result, subject, cmp),
        "safety_threshold": _safety(result, cmp),
        "comparison_value": None if cmp.value is None else str(cmp.value),
        "comparison_unit": cmp.unit,
        "converted": cmp.converted,
        "conversion_source": None if cmp.source is None else _source(cmp.source),
    }
