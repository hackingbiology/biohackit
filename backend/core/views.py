# SPDX-License-Identifier: AGPL-3.0-or-later
"""Manual lab report entry (M02 TG-b). A typed report goes through the same
`LabReport.save` / `LabResult.save` rules as an import; nothing is validated twice
or differently here."""

from datetime import datetime
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from terminology.models import ReferenceRange, Source

from .models import (
    Biomarker,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from .plausibility import RangeCandidate, check_plausibility

TEXT_FIELDS = ("laboratory", "method", "device")
TIME_FIELDS = ("collected_at", "reported_at")


# Abuse protection, not scientific limits (see docs/api-labs.md).
MAX_REPORTED_VALUE_CHARS = 40
MAX_RESULTS_PER_REPORT = 200
MAX_LENGTH = {"laboratory": 200, "method": 200, "device": 200, "reported_unit": 64}


def _text(raw: Any, name: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError({name: f"{name} must be text."})
    if "\x00" in raw:
        raise ValidationError({name: f"{name} must not contain NUL characters."})
    limit = MAX_LENGTH[name]
    text = raw.strip()
    if len(text) > limit:
        raise ValidationError({name: f"{name} must be at most {limit} characters."})
    return text


def _time(raw: Any, name: str) -> datetime | None:
    if raw is None:
        return None
    try:
        parsed = parse_datetime(raw) if isinstance(raw, str) else None
    except ValueError:  # well-formed but impossible, e.g. month 13 or 30 February
        parsed = None
    if parsed is None or parsed.utcoffset() is None:
        raise ValidationError(
            {name: f"{name} must be an ISO 8601 date and time with a UTC offset."}
        )
    return parsed


def _source_data(source: Source) -> dict[str, Any]:
    return {
        "id": source.pk,
        "name": source.name,
        "version": source.version,
        "licence": source.licence,
        "url": source.url,
        "retrieved_at": source.retrieved_at.isoformat(),
    }


def _matches(stored: str, given: str | None) -> bool:
    return stored == "" or (given is not None and stored.casefold() == given.casefold())


def _plausibility(result: LabResult) -> dict[str, Any]:
    ranges = ReferenceRange.objects.filter(biomarker=result.biomarker).select_related(
        "unit", "source"
    )
    by_id = {r.pk: r for r in ranges}
    outcome = check_plausibility(
        result.reported_value,
        result.reported_unit,
        result.normalised_value,
        result.normalised_unit,
        [
            RangeCandidate(
                low=r.low,
                high=r.high,
                unit=r.unit.ucum_code,
                source_id=r.source_id,
                stratified=any(
                    x is not None for x in (r.age_min_years, r.age_max_years, r.sex)
                )
                or r.ancestry is not None
                or r.population != ""
                or not _matches(r.lab, result.laboratory)
                or not _matches(r.method, result.method),
            )
            for r in by_id.values()
        ],
    )
    source = (
        None
        if outcome.source_id is None
        else _source_data(
            next(r.source for r in by_id.values() if r.source_id == outcome.source_id)
        )
    )
    return {"status": outcome.status, "range_source": source}


def _result_data(result: LabResult) -> dict[str, Any]:
    return {
        "id": result.pk,
        "loinc_code": result.biomarker.loinc_code,
        "laboratory": result.laboratory,
        "method": result.method,
        "device": result.device,
        "collected_at": result.collected_at,
        "reported_at": result.reported_at,
        "reported_value": str(result.reported_value),
        "reported_unit": result.reported_unit,
        "normalised_value": (
            None if result.normalised_value is None else str(result.normalised_value)
        ),
        "normalised_unit": result.normalised_unit,
        "validation_state": result.validation_state,
        "aggregation_eligible": result.aggregation_eligible,
        "plausibility": _plausibility(result),
    }


def _report_data(report: LabReport) -> dict[str, Any]:
    results = (
        LabResult.objects.filter(report=report)
        .select_related("biomarker__unit")
        .order_by("pk")
    )
    return {
        "id": report.pk,
        "origin": report.origin,
        "import_name": report.import_name,
        "laboratory": report.laboratory,
        "created_at": report.created_at,
        "results": [_result_data(r) for r in results],
    }


def _create_result(
    report: LabReport,
    item: Any,
    validation_state: str = LabResultValidation.UNREVIEWED,
) -> LabResult:
    if not isinstance(item, dict):
        raise ValidationError({"non_field_errors": "Each result must be an object."})
    code = item.get("loinc_code")
    if not isinstance(code, str) or not code.strip():
        raise ValidationError({"loinc_code": "Give the LOINC code of the analyte."})
    if "\x00" in code:
        raise ValidationError(
            {"loinc_code": "loinc_code must not contain NUL characters."}
        )
    biomarker = (
        Biomarker.objects.select_related("unit").filter(loinc_code=code.strip()).first()
    )
    if biomarker is None:
        raise ValidationError({"loinc_code": f"Unknown LOINC code: {code.strip()}."})
    value = item.get("reported_value")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            {"reported_value": "reported_value must be a decimal number in a string."}
        )
    if len(value.strip()) > MAX_REPORTED_VALUE_CHARS:
        raise ValidationError(
            {
                "reported_value": "reported_value is too long "
                f"(at most {MAX_REPORTED_VALUE_CHARS} characters)."
            }
        )
    unit = _text(item.get("reported_unit"), "reported_unit")
    if unit is None or not unit.strip():
        raise ValidationError({"reported_unit": "Give the unit as reported."})
    extra: dict[str, Any] = {n: _text(item.get(n), n) for n in TEXT_FIELDS}
    extra.update({n: _time(item.get(n), n) for n in TIME_FIELDS})
    result = LabResult(
        report=report,
        biomarker=biomarker,
        reported_value=value.strip(),
        reported_unit=unit.strip(),
        validation_state=validation_state,
        **extra,
    )
    result.save()
    return result


def _django_errors(exc: DjangoValidationError) -> dict[str, Any]:
    if hasattr(exc, "error_dict"):
        return {k: [str(m) for m in v] for k, v in exc.message_dict.items()}
    return {"non_field_errors": list(exc.messages)}


def _field_errors(exc: Any) -> dict[str, Any]:
    if isinstance(exc, DjangoValidationError):
        return _django_errors(exc)
    detail = exc.detail
    return {
        k: [str(m) for m in (v if isinstance(v, list) else [v])]
        for k, v in detail.items()
    }


class LabReportCreateView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST: type in a lab report and its results. origin is always `manual`, owner is the
    caller. All rows are stored in one transaction; the first invalid result rolls back
    everything and the 400 names the result index and field."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        data = request.data
        if not isinstance(data, dict):
            raise ValidationError({"non_field_errors": "Send a JSON object."})
        results = data.get("results")
        if not isinstance(results, list) or not results:
            raise ValidationError({"results": "Give at least one result."})
        if len(results) > MAX_RESULTS_PER_REPORT:
            raise ValidationError(
                {"results": f"At most {MAX_RESULTS_PER_REPORT} results per report."}
            )
        laboratory = _text(data.get("laboratory"), "laboratory")
        try:
            with transaction.atomic():
                report = LabReport(
                    owner=request.user,
                    origin=LabReportOrigin.MANUAL,
                    laboratory=laboratory,
                )
                report.save()
                for index, item in enumerate(results):
                    try:
                        _create_result(report, item)
                    except (DjangoValidationError, ValidationError) as exc:
                        raise ValidationError(
                            {"results": {str(index): _field_errors(exc)}}
                        ) from exc
        except DjangoValidationError as exc:
            raise ValidationError(_django_errors(exc)) from exc
        return Response(_report_data(report), status=status.HTTP_201_CREATED)


class LabReportDetailView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: a report of the caller. DELETE: roll back an import (report and results).
    Another user's report is a 404; a manual report cannot be rolled back (409)."""

    http_method_names = ["get", "delete", "head", "options"]

    def delete(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        if report.origin != LabReportOrigin.IMPORT:
            return Response(
                {"detail": "Only an import can be rolled back; a typed report cannot."},
                status=status.HTTP_409_CONFLICT,
            )
        report.delete()  # LabResult rows go with it (CASCADE); nothing else is touched
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        return Response(_report_data(report))
