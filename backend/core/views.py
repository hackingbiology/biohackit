# SPDX-License-Identifier: AGPL-3.0-or-later
"""Manual lab report entry (M02 TG-b). A typed report goes through the same
`LabReport.save` / `LabResult.save` rules as an import; nothing is validated twice
or differently here."""

import math
from datetime import datetime
from decimal import Decimal, localcontext
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from terminology.models import ReferenceRange, Source, Unit
from terminology.selectors import Subject
from terminology.services import normalize_value

from .calculated_markers import compute_ratios
from .completeness import panel_completeness
from .fhir import lab_report_to_fhir_bundle, render_fhir_json
from .getbased_import import EDITED_TEXT, FLAG_TEXT, QUALIFIER
from .models import (
    Biomarker,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultGetbasedProvenance,
    LabResultValidation,
    OrganSystemPanel,
)
from .omop import MEASUREMENT_COLUMNS, OMOP_CDM_VERSION, lab_result_to_omop_measurement
from .phenoage import PhenoAgeRefusal, PhenoAgeResult, evaluate_phenoage
from .phenoage_binding import inputs_from_report
from .plausibility import RangeCandidate, check_plausibility
from .result_ranges import result_ranges

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


def _getbased_provenance(
    prov: LabResultGetbasedProvenance | None,
) -> dict[str, Any] | None:
    """get-based's provenance of a result in plain words; None for any other result."""
    if prov is None:
        return None
    imported = None
    if prov.imported_with_present:
        imported = {
            "model_id": prov.imported_with_model_id or "unknown",
            "provider": prov.imported_with_provider or "unknown",
            "qualifier": QUALIFIER,
        }
    return {
        "flag": prov.flag,
        "flag_text": FLAG_TEXT[prov.flag],  # type: ignore[index]  # a stored flag is a known one
        "edited_label": EDITED_TEXT if prov.manually_edited else None,
        "manually_edited": prov.manually_edited,
        "entry_date": prov.entry_date.isoformat(),
        "has_marker_sources": prov.has_marker_sources,
        "marker_sources": {
            "reported": prov.ms_reported,
            "file": prov.ms_file,
            "at": prov.ms_at,
            "snapshot_id": prov.ms_snapshot_id,
        },
        "imported_with": imported,
    }


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
        "getbased_provenance": _getbased_provenance(
            getattr(result, "getbased_provenance", None)
        ),
    }


def _report_data(report: LabReport) -> dict[str, Any]:
    results = (
        LabResult.objects.filter(report=report)
        .select_related("biomarker__unit", "getbased_provenance")
        .order_by("pk")
    )
    return {
        "id": report.pk,
        "origin": report.origin,
        "import_name": report.import_name,
        "import_source": report.import_source,
        "import_format": report.import_format,
        "import_format_version": report.import_format_version,
        "laboratory": report.laboratory,
        "created_at": report.created_at,
        "original_retained": bool(report.original_file),
        "original_sha256": report.original_sha256,
        "original_size": report.original_size,
        "results": [_result_data(r) for r in results],
    }


def _create_result(
    report: LabReport,
    item: Any,
    validation_state: str = LabResultValidation.ENTERED,
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
        # LabResult rows go with it (CASCADE); the file goes after the commit
        # via the post_delete receiver in core.models.
        with transaction.atomic():
            report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        return Response(_report_data(report))


class LabReportFhirView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: the caller's report as a FHIR R4 collection Bundle. Another user's is a 404."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> HttpResponse:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        return HttpResponse(
            render_fhir_json(lab_report_to_fhir_bundle(report)),
            content_type="application/fhir+json",
        )


class LabReportOmopView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: the caller's non-retracted results as OMOP MEASUREMENT rows (Q80).
    Another user's report is a 404. No concept id is filled (Q69)."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        results = (
            LabResult.objects.filter(report=report)
            .exclude(validation_state=LabResultValidation.RETRACTED)
            .select_related("biomarker")
            .order_by("pk")
        )
        return Response(
            {
                "omop_cdm_version": OMOP_CDM_VERSION,
                "columns": list(MEASUREMENT_COLUMNS),
                "rows": [lab_result_to_omop_measurement(r) for r in results],
            }
        )


class LabReportCalculatedView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: stored ratio definitions computed from this report's results, labelled
    calculated, inputs and dates listed; a missing input gives no value (Q83).
    Another user's report is a 404."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        markers = compute_ratios(report)
        body: dict[str, Any] = {"report_id": report.pk, "markers": markers}
        if not markers:
            body["note"] = "no_definitions_stored"
        return Response(body)


class LabCompletenessView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: per stored organ-system panel, how many expected markers the caller has
    results for and when the newest was collected (Q84). Own data only."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request) -> Response:
        panels = (
            OrganSystemPanel.objects.select_related("source")
            .prefetch_related("expected_biomarkers")
            .order_by("name")
        )
        return Response(
            {"panels": panel_completeness(request.user, panels, timezone.now())}
        )


PHENOAGE_METHOD = "PhenoAge (Levine 2018), docs/research/phenoage-coefficients.md"


def _age_years(request: Request) -> float:
    raw = request.query_params.get("age_years")
    try:
        age = Decimal(raw) if raw is not None else None
        value = float(age) if age is not None and age.is_finite() else None
    except (ArithmeticError, OverflowError):  # decimal.InvalidOperation
        value = None
    if value is None or not math.isfinite(value):
        raise ValidationError({"age_years": "Give age_years as a finite number."})
    return value


class LabReportPhenoAgeView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: PhenoAge computed from the caller's report; age_years is a request
    parameter and nothing is stored. Another user's report is a 404."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> Response:
        report = get_object_or_404(LabReport, pk=pk, owner=request.user)
        age = _age_years(request)
        bound = inputs_from_report(report, age)
        if isinstance(bound, PhenoAgeRefusal):
            return Response({"refusal": {"reason": bound.reason, "field": bound.field}})
        outcome = evaluate_phenoage(bound.inputs)
        if not isinstance(outcome, PhenoAgeResult):
            return Response(
                {"refusal": {"reason": outcome.reason, "field": outcome.field}}
            )
        return Response(
            {
                "phenoage_years": outcome.phenoage_years,
                "mortality_score": outcome.mortality_score,
                "xb": outcome.xb,
                "constants_version": outcome.constants_version,
                "inputs": [
                    {
                        "field": u.field,
                        "lab_result_id": u.lab_result_id,
                        "value": u.value,
                        "unit": u.unit,
                        "converted": u.converted,
                    }
                    for u in bound.used
                ],
                "method": PHENOAGE_METHOD,
            }
        )


MAX_UNIT_CHARS = 64


def _target_unit(request: Request) -> str:
    raw = request.query_params.get("unit")
    if not raw or len(raw) > MAX_UNIT_CHARS:
        raise ValidationError(
            {
                "unit": f"Give unit as a UCUM code of at most {MAX_UNIT_CHARS} characters."
            }
        )
    if "\x00" in raw:
        raise ValidationError({"unit": "unit must not contain NUL characters."})
    if not Unit.objects.filter(ucum_code=raw).exists():
        raise ValidationError({"unit": f"Unknown UCUM unit: {raw}."})
    return raw


class LabResultConvertView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: the caller's result shown in the UCUM unit named by `unit`, using only a stored,
    sourced UnitConversion (Q81). The reported value and unit are always returned and
    nothing is written. Retracted results stay viewable. Another user's result is a 404."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> Response:
        result = get_object_or_404(
            LabResult.objects.select_related("biomarker"),
            pk=pk,
            report__owner=request.user,
        )
        target = _target_unit(request)
        reported = str(result.reported_value)
        body: dict[str, Any] = {
            "result_id": result.pk,
            "reported_value": reported,
            "reported_unit": result.reported_unit,
            "value": reported,
            "unit": result.reported_unit,
            "converted": False,
            "reason": None,
            "conversion_source": None,
        }
        if target == result.reported_unit:
            body["reason"] = "same_unit"
            return Response(body)
        try:
            # 20-digit value x 30-digit factor needs <= 50 digits: prec 60 never rounds.
            with localcontext() as ctx:
                ctx.prec = 60
                outcome = normalize_value(
                    result.reported_value,
                    result.reported_unit,
                    target,
                    biomarker=result.biomarker,
                )
        except DjangoValidationError:
            body["reason"] = "no_conversion_known"
            return Response(body)
        body.update(
            value=str(outcome.value),
            unit=target,
            converted=True,
            conversion_source=_source_data(Source.objects.get(pk=outcome.source_id)),
        )
        return Response(body)


class LabResultRangesView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """GET: the caller's result against its reference range, optimal range and safety
    threshold, kept separate, each with provenance and a computed status (Q82). The
    subject is unknown (no profile data stored). Retracted results stay viewable.
    Another user's result is a 404."""

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, pk: int) -> Response:
        result = get_object_or_404(
            LabResult.objects.select_related("biomarker__unit"),
            pk=pk,
            report__owner=request.user,
        )
        return Response(
            {
                "result_id": result.pk,
                "reported_value": str(result.reported_value),
                "reported_unit": result.reported_unit,
                **result_ranges(result, Subject()),
            }
        )


# States the owner may set. `entered` is the starting state; `source_verified` needs an
# attached original and a deterministic check, which do not exist yet (Q63, Q75).
OWNER_SETTABLE_STATES = (
    LabResultValidation.USER_CONFIRMED,
    LabResultValidation.DISPUTED,
    LabResultValidation.RETRACTED,
)


class LabResultValidationView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """PATCH: the owner changes the validation state of one of their results.
    Eligibility is recomputed by `LabResult.save`. A retracted result stays retracted.
    Another user's or a missing result is a 404."""

    http_method_names = ["patch", "options"]

    def patch(self, request: Request, pk: int) -> Response:
        result = get_object_or_404(
            LabResult.objects.select_related("biomarker__unit", "report"),
            pk=pk,
            report__owner=request.user,
        )
        data = request.data
        state = data.get("validation_state") if isinstance(data, dict) else None
        if state not in OWNER_SETTABLE_STATES:
            allowed = ", ".join(OWNER_SETTABLE_STATES)
            raise ValidationError(
                {"validation_state": f"validation_state must be one of: {allowed}."}
            )
        if (
            result.validation_state == LabResultValidation.RETRACTED
            and state != LabResultValidation.RETRACTED
        ):
            raise ValidationError(
                {"validation_state": "A retracted result stays retracted."}
            )
        result.set_validation_state(state)
        return Response(_result_data(result))
