# SPDX-License-Identifier: AGPL-3.0-or-later
"""Range serializers. Decimals are strings (DRF default), never floats. `status` is
computed only by `services.range_status` and only when the context carries a value."""

from decimal import Decimal
from typing import Any, Literal

from rest_framework import serializers  # type: ignore[import-untyped]  # DRF ships no stubs

from core.models import Biomarker

from .models import (
    LoincTerm,
    OptimalRange,
    RangeBase,
    ReferenceRange,
    SafetyThreshold,
    Source,
)
from .services import range_status


class SourceSerializer(serializers.ModelSerializer[Source]):  # type: ignore[misc]  # base is Any: DRF untyped
    class Meta:
        model = Source
        fields = ["name", "version", "licence", "url", "retrieved_at"]


class LoincTermSerializer(serializers.ModelSerializer[LoincTerm]):  # type: ignore[misc]  # base is Any: DRF untyped
    source = SourceSerializer()

    class Meta:
        model = LoincTerm
        fields = [
            "loinc_num",
            "long_common_name",
            "short_name",
            "component",
            "system",
            "property",
            "scale_type",
            "status",
            "source",
        ]


class BiomarkerSerializer(serializers.ModelSerializer[Biomarker]):  # type: ignore[misc]  # base is Any: DRF untyped
    unit = serializers.CharField(source="unit.ucum_code")

    class Meta:
        model = Biomarker
        fields = ["loinc_code", "name", "unit"]


class _RangeSerializer(serializers.ModelSerializer[Any]):  # type: ignore[misc]  # base is Any: DRF untyped
    unit = serializers.CharField(source="unit.ucum_code")
    source = SourceSerializer()
    status = serializers.SerializerMethodField()

    def get_status(self, obj: RangeBase) -> Literal["below", "within", "above"] | None:
        value: Decimal | None = self.context.get("value")
        if value is None:
            return None
        return range_status(value, obj.low, obj.high)


class ReferenceRangeSerializer(_RangeSerializer):
    class Meta:
        model = ReferenceRange
        fields = [
            "low",
            "high",
            "unit",
            "source",
            "status",
            "lab",
            "method",
            "population",
        ]


class OptimalRangeSerializer(_RangeSerializer):
    class Meta:
        model = OptimalRange
        fields = [
            "low",
            "high",
            "unit",
            "source",
            "status",
            "population",
            "endpoint",
            "evidence_grade",
            "last_reviewed",
        ]


class SafetyThresholdSerializer(_RangeSerializer):
    class Meta:
        model = SafetyThreshold
        fields = ["low", "high", "unit", "source", "status"]
