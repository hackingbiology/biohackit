# SPDX-License-Identifier: AGPL-3.0-or-later
"""Base domain stubs (M00 TG3). Full logic arrives in M01 (ranges) and M03 (interventions)."""

from django.conf import settings
from django.db import models


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
    """Stub. The three distinct ranges (reference / optimal / safety) land in M01,
    each with source and population."""

    loinc_code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=16, choices=BiomarkerRole.choices)
    unit_ucum = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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

    def save(self, *args, **kwargs):
        # Domain rule: without lab AND method a measurement is not aggregation-eligible.
        self.is_aggregation_eligible = bool(self.laboratory and self.method)
        super().save(*args, **kwargs)
