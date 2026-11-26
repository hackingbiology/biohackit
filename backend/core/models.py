# SPDX-License-Identifier: AGPL-3.0-or-later
"""Base domain stubs (M00 TG3). Full logic arrives in M01 (ranges) and M03 (interventions)."""

from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from terminology.models import SourcedModel, Unit
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


class AnalyteCategory(models.TextChoices):
    BLOOD = "blood", "Blood"
    BODY_COMPOSITION = "body_composition", "Body composition (DEXA)"
    MICROBIOME = "microbiome", "Microbiome"


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
    # Q66: NULL = uncategorised (treated as blood); set only with a cited source.
    category = models.CharField(
        max_length=32, choices=AnalyteCategory.choices, null=True, blank=True
    )
    category_source = models.ForeignKey(
        "terminology.Source",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    @property
    def requires_provenance_before_storing(self) -> bool:
        """DEXA and microbiome analytes need laboratory and method to be stored;
        blood and uncategorised analytes are stored and flagged instead (Q66)."""
        return self.category in (
            AnalyteCategory.BODY_COMPOSITION,
            AnalyteCategory.MICROBIOME,
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not (self.loinc_code or "").strip():
            raise ValidationError("Biomarker requires a LOINC code")
        if self.unit_id is None:
            raise ValidationError("Biomarker requires a UCUM unit")
        if self.source_id is None:
            raise ValidationError("Biomarker requires a source")
        if self.category is not None and self.category not in AnalyteCategory.values:
            raise ValidationError("Biomarker category is not a known category")
        if (self.category is None) != (self.category_source_id is None):
            raise ValidationError(
                "Biomarker category and its source are set together: "
                "a category needs a cited source, and a source needs a category"
            )
        self._check_unit_change_keeps_ranges_consistent()
        self._check_recategorising_keeps_results_provenanced()
        super().save(*args, **kwargs)

    def _check_recategorising_keeps_results_provenanced(self) -> None:
        """A DEXA or microbiome category cannot be set while stored results of this
        analyte lack laboratory or method: they would be unprovenanced (Q66)."""
        if self.pk is None or not self.requires_provenance_before_storing:
            return
        lacking = (
            LabResult.objects.filter(biomarker_id=self.pk)
            .filter(
                models.Q(laboratory__isnull=True)
                | models.Q(laboratory="")
                | models.Q(method__isnull=True)
                | models.Q(method="")
            )
            .values_list("pk", flat=True)
        )
        ids = list(lacking[:10])
        if ids:
            raise ValidationError(
                "Biomarker cannot become DEXA or microbiome while stored results "
                f"lack a laboratory or method; add provenance first (result ids: {ids})"
            )

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


class LabReportOrigin(models.TextChoices):
    MANUAL = "manual", "Manual entry"
    IMPORT = "import", "Import"


class LabResultValidation(models.TextChoices):
    # The five states Fabio chose for Q63 (2026-11-26).
    ENTERED = "entered", "Entered"
    USER_CONFIRMED = "user_confirmed", "Confirmed by the user"
    SOURCE_VERIFIED = "source_verified", "Verified against the source"
    DISPUTED = "disputed", "Disputed"
    RETRACTED = "retracted", "Retracted"


# Aggregations and public statistics use only these states and above (Q63).
AGGREGATION_STATES = frozenset(
    {LabResultValidation.USER_CONFIRMED, LabResultValidation.SOURCE_VERIFIED}
)


def private_storage() -> FileSystemStorage:
    """Private store for retained originals: no base_url, so it can never yield a URL."""
    return FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT, base_url=None)


def original_upload_to(instance: "LabReport", filename: str) -> str:
    """Generated name only (the report pk); the user's file name can hold PII."""
    return f"lab-reports/{instance.pk}.csv"


class LabReport(models.Model):
    """One laboratory report: groups results and records where they came from."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    origin = models.CharField(max_length=16, choices=LabReportOrigin.choices)
    import_name = models.CharField(max_length=200, blank=True, default="")
    laboratory = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Retained original of an import (private, never served; Q57, Q65).
    original_file = models.FileField(
        upload_to=original_upload_to,
        storage=private_storage,
        null=True,
        blank=True,
    )
    original_sha256 = models.CharField(max_length=64, null=True, blank=True)
    original_size = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.origin not in LabReportOrigin.values:
            raise ValidationError("A LabReport requires an origin: manual or import")
        if self.origin == LabReportOrigin.IMPORT and not self.import_name.strip():
            raise ValidationError("An imported LabReport requires an import name")
        super().save(*args, **kwargs)


@receiver(post_delete, sender=LabReport)
def delete_retained_original(
    sender: type[LabReport], instance: LabReport, **kwargs: Any
) -> None:
    """Remove the private file once the row delete commits (rollback, owner cascade; Q65)."""
    if instance.original_file:
        storage = instance.original_file.storage
        name = instance.original_file.name
        transaction.on_commit(lambda: storage.delete(name))


def _stripped(value: str | None) -> str | None:
    """Trimmed text, or None when empty or whitespace-only."""
    return (value or "").strip() or None


class LabResult(models.Model):
    """Lab-measured value of a coded analyte, separate from `Measurement` (Q61).
    The value and unit stay as reported; the normalised pair is filled only when
    a stored conversion exists. A result is always kept, never rejected for its unit."""

    report = models.ForeignKey(LabReport, on_delete=models.CASCADE)
    biomarker = models.ForeignKey(Biomarker, on_delete=models.PROTECT)
    laboratory = models.CharField(max_length=200, null=True, blank=True)
    method = models.CharField(max_length=200, null=True, blank=True)
    device = models.CharField(max_length=200, null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    reported_at = models.DateTimeField(null=True, blank=True)
    reported_value = models.DecimalField(max_digits=20, decimal_places=6)
    reported_unit = models.CharField(max_length=64)
    reported_unit_ref = models.ForeignKey(
        "terminology.Unit",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )
    normalised_value = models.DecimalField(
        max_digits=30, decimal_places=12, null=True, blank=True, editable=False
    )
    normalised_unit = models.CharField(
        max_length=64, null=True, blank=True, editable=False
    )
    normalised_source = models.ForeignKey(
        "terminology.Source",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )  # source of the stored factor; NULL for identity or no normalisation
    validation_state = models.CharField(
        max_length=16,
        choices=LabResultValidation.choices,
        default=LabResultValidation.ENTERED,
    )
    aggregation_eligible = models.BooleanField(default=False, editable=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.laboratory = _stripped(self.laboratory)
        self.method = _stripped(self.method)
        if not self.laboratory:
            # only when the report states it
            self.laboratory = _stripped(self.report.laboratory)
        self._require_provenance()
        self._normalise()
        self.aggregation_eligible = self._eligible()
        super().save(*args, **kwargs)

    def _eligible(self) -> bool:
        return bool(
            self.laboratory
            and self.method
            and self.validation_state in AGGREGATION_STATES
        )

    def set_validation_state(self, state: str) -> None:
        """Change only the state and the eligibility flag. Stored values and their
        normalisation are kept as they were (audit), so `_normalise` is not re-run."""
        self.validation_state = state
        self.aggregation_eligible = self._eligible()
        super().save(update_fields=["validation_state", "aggregation_eligible"])

    def _require_provenance(self) -> None:
        """DEXA and microbiome results are refused without laboratory and method."""
        if not self.biomarker.requires_provenance_before_storing:
            return
        missing = [
            name
            for name in ("laboratory", "method")
            if not (getattr(self, name) or "").strip()
        ]
        if missing:
            raise ValidationError(
                "This result cannot be stored yet. Please provide: "
                + " and ".join(missing)
                + "."
            )

    def _exact_reported_value(self) -> Decimal:
        """The reported value, unchanged, or ValidationError if the column cannot
        hold it exactly (never rounded: the stored value is what the lab reported)."""
        field = self._meta.get_field("reported_value")
        max_digits = int(field.max_digits)  # type: ignore[attr-defined]
        places = int(field.decimal_places)  # type: ignore[attr-defined]
        try:
            value = Decimal(str(self.reported_value))
        except ArithmeticError as exc:
            raise ValidationError(
                {"reported_value": "reported_value is not a number."}
            ) from exc
        if not value.is_finite():
            raise ValidationError({"reported_value": "reported_value must be finite."})
        # Drop trailing zeros on the digit tuple itself: Decimal.normalize() would
        # round to the ambient context precision (28 digits) and hide real digits.
        sign, digits, raw_exponent = value.as_tuple()
        del sign
        exponent = int(raw_exponent)
        if not any(digits):
            digits, exponent = (0,), 0
        else:
            trailing = next((i for i, d in enumerate(reversed(digits)) if d), 0)
            if trailing:
                digits, exponent = digits[:-trailing], exponent + trailing
        if -exponent > places:
            raise ValidationError(
                {"reported_value": f"reported_value allows at most {places} decimals."}
            )
        if len(digits) + exponent > max_digits - places:
            raise ValidationError(
                {
                    "reported_value": "reported_value allows at most "
                    f"{max_digits - places} digits before the decimal point."
                }
            )
        return value

    def _normalise(self) -> None:
        self.reported_unit_ref = Unit.objects.filter(
            ucum_code=self.reported_unit
        ).first()
        self.normalised_value = None
        self.normalised_unit = None
        self.normalised_source = None
        self.reported_value = self._exact_reported_value()
        if self.reported_unit_ref is None:
            return
        try:
            result = normalize_value(
                self.reported_value,
                self.reported_unit,
                self.biomarker.unit.ucum_code,
                self.biomarker,
            )
        except ValidationError:  # no stored conversion: keep as reported
            return
        self.normalised_value = result.value
        self.normalised_unit = result.unit
        self.normalised_source_id = result.source_id


class CalculatedRatioDefinition(SourcedModel):
    """A plain quotient marker: numerator / denominator, each input in a stated UCUM
    unit. The cited `source` states the method and unit convention. Nothing is seeded
    (Q83); the ratio is computed per report in code and never stored."""

    name = models.CharField(max_length=100, unique=True)
    numerator = models.ForeignKey(Biomarker, on_delete=models.PROTECT, related_name="+")
    denominator = models.ForeignKey(
        Biomarker, on_delete=models.PROTECT, related_name="+"
    )
    numerator_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="+")
    denominator_unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "numerator",
                    "denominator",
                    "numerator_unit",
                    "denominator_unit",
                ],
                name="uniq_calculated_ratio_inputs",
            ),
            models.CheckConstraint(
                condition=~models.Q(numerator=models.F("denominator")),
                name="calculated_ratio_inputs_differ",
            ),
        ]

    def clean(self) -> None:
        if self.source_id is None:
            raise ValidationError({"source": "A ratio definition requires a source"})
        if self.numerator_id == self.denominator_id:
            raise ValidationError("Numerator and denominator must differ")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class OrganSystemPanel(SourcedModel):
    """A named group of expected Biomarkers (an organ system). The cited `source`
    states where the grouping comes from. Nothing is seeded (Q84); completeness and
    freshness are computed in code and never stored."""

    name = models.CharField(max_length=100, unique=True)
    expected_biomarkers = models.ManyToManyField(
        Biomarker, related_name="+", blank=True
    )

    def clean(self) -> None:
        if self.source_id is None:
            raise ValidationError({"source": "An organ-system panel requires a source"})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
