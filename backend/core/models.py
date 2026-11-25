# SPDX-License-Identifier: AGPL-3.0-or-later
"""Base domain stubs (M00 TG3). Full logic arrives in M01 (ranges) and M03 (interventions)."""

from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from terminology.services import normalize_value


class InterventionSubtype(models.TextChoices):
    SUBSTANCE = "substance", "Substance"
    EXERCISE = "exercise", "Exercise"
    DEVICE_THERAPY = "device_therapy", "Device / therapy"
    PROCEDURE = "procedure", "Procedure"
    HORMONAL = "hormonal", "Hormonal"
    NUTRITION_FASTING = "nutrition_fasting", "Nutrition / fasting"


class Intervention(models.Model):
    """Stub. `cycle_schema` holds pattern (continuous|pulsed|titration|on-off),
    on_days/off_days, cycle length etc. — never flattened to a frequency string."""

    name = models.CharField(max_length=200)
    subtype = models.CharField(max_length=32, choices=InterventionSubtype.choices)
    cycle_schema = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BiomarkerRole(models.TextChoices):
    EFFICACY = "efficacy", "Efficacy"
    SAFETY = "safety", "Safety"
    BASELINE = "baseline", "Baseline"


class Biomarker(models.Model):
    """Coded analyte (M01 TG3): LOINC code, UCUM unit and source are mandatory.
    The three ranges (reference / optimal / safety) follow in M01 TG4."""

    loinc_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    long_name = models.CharField(max_length=255, blank=True, default="")
    system = models.CharField(max_length=100, blank=True, default="")
    role = models.CharField(max_length=16, choices=BiomarkerRole.choices)
    unit = models.ForeignKey("terminology.Unit", on_delete=models.PROTECT)
    source = models.ForeignKey("terminology.Source", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not (self.loinc_code or "").strip():
            raise ValidationError("Biomarker requires a LOINC code")
        if self.unit_id is None:
            raise ValidationError("Biomarker requires a UCUM unit")
        if self.source_id is None:
            raise ValidationError("Biomarker requires a source")
        self._check_unit_change_keeps_ranges_consistent()
        super().save(*args, **kwargs)

    def _check_unit_change_keeps_ranges_consistent(self) -> None:
        """Range bounds are stored in the analyte's unit and never converted, so the
        unit cannot change while a range row still uses another unit."""
        if self.pk is None:
            return
        stored = (
            type(self)
            .objects.filter(pk=self.pk)
            .values_list("unit_id", flat=True)
            .first()
        )
        if stored is None or stored == self.unit_id:
            return
        for ranges in (
            self.referencerange_set,
            self.optimalrange_set,
            self.safetythreshold_set,
        ):
            if ranges.exclude(unit_id=self.unit_id).exists():
                raise ValidationError(
                    "Biomarker unit cannot change while range rows use the previous unit"
                )


class Measurement(models.Model):
    """Time-series value with provenance. Backed by a TimescaleDB hypertable on `time`
    (migration 0002; PK is composite (id, time) at DB level)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    biomarker = models.ForeignKey(Biomarker, on_delete=models.PROTECT)
    time = models.DateTimeField()
    value = models.DecimalField(max_digits=20, decimal_places=6)
    unit_ucum = models.CharField(max_length=64)
    source = models.CharField(max_length=200)
    laboratory = models.CharField(max_length=200, null=True, blank=True)
    method = models.CharField(max_length=200, null=True, blank=True)
    is_aggregation_eligible = models.BooleanField(default=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # The analyte must be coded; the unit must be stored and equal to the analyte
        # unit or convertible with a stored factor. value/unit_ucum stay as reported.
        analyte = self.biomarker
        if not (analyte.loinc_code or "").strip() or analyte.unit_id is None:
            raise ValidationError("Measurement requires a coded analyte (LOINC + UCUM)")
        normalize_value(self.value, self.unit_ucum, analyte.unit.ucum_code, analyte)
        # Domain rule: without lab AND method a measurement is not aggregation-eligible.
        self.is_aggregation_eligible = bool(self.laboratory and self.method)
        super().save(*args, **kwargs)
