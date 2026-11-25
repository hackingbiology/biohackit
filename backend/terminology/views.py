# SPDX-License-Identifier: AGPL-3.0-or-later
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.generics import ListAPIView  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.pagination import PageNumberPagination  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.throttling import ScopedRateThrottle  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from core.models import Biomarker

from .models import LoincTerm, ReferenceRange, SafetyThreshold
from .search import search_loinc
from .selectors import displayable_optimal_range
from .serializers import (
    BiomarkerSerializer,
    LoincTermSerializer,
    OptimalRangeSerializer,
    ReferenceRangeSerializer,
    SafetyThresholdSerializer,
)

MAX_QUERY_LENGTH = 200


def _parse_value(raw: str | None) -> Decimal | None:
    if raw is None:
        return None
    try:
        value = Decimal(raw.strip())
    except InvalidOperation:
        raise ValidationError({"value": "value must be a decimal number"}) from None
    if not value.is_finite():
        raise ValidationError({"value": "value must be a finite decimal number"})
    return value


class LoincSearchPagination(PageNumberPagination):  # type: ignore[misc]  # base is Any: DRF untyped
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LoincSearchView(ListAPIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """Read-only search of imported LOINC terms: `?q=<name words or LOINC code>`."""

    serializer_class = LoincTermSerializer
    pagination_class = LoincSearchPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "loinc_search"

    def get_queryset(self) -> QuerySet[LoincTerm]:
        q = self.request.query_params.get("q", "").strip()
        if not q:
            raise ValidationError({"q": "Enter a word or a LOINC code to search."})
        if len(q) > MAX_QUERY_LENGTH:
            raise ValidationError(
                {
                    "q": f"Search text is too long. Use at most {MAX_QUERY_LENGTH} characters."
                }
            )
        return search_loinc(q)


class BiomarkerRangesView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """Read-only (GET) reference, optimal and safety ranges of one analyte, kept as three
    separate keys, each with its Source. `optimal` comes only from
    `displayable_optimal_range`, so a row with incomplete provenance never appears.

    With `?value=<decimal>` each range gets its own `status` from `range_status`. The
    value is assumed to be in the analyte's unit: no unit conversion is done here.
    """

    http_method_names = ["get", "head", "options"]

    def get(self, request: Request, loinc_code: str) -> Response:
        biomarker = get_object_or_404(
            Biomarker.objects.select_related("unit"), loinc_code=loinc_code
        )
        value = _parse_value(request.query_params.get("value"))
        ctx: dict[str, Any] = {"value": value}
        reference = ReferenceRange.objects.filter(biomarker=biomarker)
        safety = SafetyThreshold.objects.filter(biomarker=biomarker)
        optimal = displayable_optimal_range(biomarker)
        return Response(
            {
                "biomarker": BiomarkerSerializer(biomarker).data,
                "reference": ReferenceRangeSerializer(
                    reference.select_related("unit", "source").order_by("id"),
                    many=True,
                    context=ctx,
                ).data,
                "optimal": (
                    OptimalRangeSerializer(optimal, context=ctx).data
                    if optimal is not None
                    else None
                ),
                "safety": SafetyThresholdSerializer(
                    safety.select_related("unit", "source").order_by("id"),
                    many=True,
                    context=ctx,
                ).data,
                "value": None if value is None else str(value),
            }
        )
