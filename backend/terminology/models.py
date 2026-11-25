# SPDX-License-Identifier: AGPL-3.0-or-later
"""Terminology & reference data (M01 TG2). Every row carries a Source; no invented values."""

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=64, blank=True, default="")
    licence = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    retrieved_at = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"], name="uniq_source_name_version"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.version}".strip()


class SourcedModel(models.Model):
    """Abstract base: source is mandatory (NOT NULL) and validated on save."""

    source = models.ForeignKey(Source, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.source_id is None:
            raise ValidationError(f"{type(self).__name__} requires a source")
        super().save(*args, **kwargs)


class Unit(SourcedModel):
    ucum_code = models.CharField(max_length=64, unique=True)
    display = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.ucum_code


class UnitConversion(SourcedModel):
    """normalised = as_reported * factor. `biomarker` null = applies to any analyte."""

    from_unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name="conversions_from"
    )
    to_unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name="conversions_to"
    )
    factor = models.DecimalField(max_digits=30, decimal_places=12)
    biomarker = models.ForeignKey(
        "core.Biomarker", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_unit", "to_unit", "biomarker"],
                name="uniq_conversion",
                nulls_distinct=False,
            )
        ]
