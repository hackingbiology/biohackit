# SPDX-License-Identifier: AGPL-3.0-or-later
"""Terminology & reference data (M01 TG2). Every row carries a Source; no invented values."""

from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Upper

from accounts.models import Sex


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


class RangeBase(SourcedModel):
    """Abstract: bounds are in the analyte's own unit (never converted); at least one
    bound is set and low <= high. Concrete rows are structure only: no value is seeded."""

    biomarker = models.ForeignKey(
        "core.Biomarker", on_delete=models.CASCADE, related_name="%(class)s_set"
    )
    low = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    high = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="+")

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=models.Q(low__isnull=False) | models.Q(high__isnull=False),
                name="%(app_label)s_%(class)s_has_a_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(low__isnull=True)
                | models.Q(high__isnull=True)
                | models.Q(low__lte=models.F("high")),
                name="%(app_label)s_%(class)s_low_lte_high",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.low is None and self.high is None:
            raise ValidationError("A range needs at least one bound")
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValidationError("Range low must not exceed high")
        if self.unit_id != self.biomarker.unit_id:
            raise ValidationError("Range unit must equal the analyte's unit")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.source_id is None:
            raise ValidationError(f"{type(self).__name__} requires a source")
        self.clean()
        super().save(*args, **kwargs)


class StratifiedRange(RangeBase):
    """Abstract: optional strata, null = all. Age band in whole years, min inclusive,
    max exclusive. Ancestry is free text (no vocabulary defined, Q50)."""

    age_min_years = models.PositiveSmallIntegerField(null=True, blank=True)
    age_max_years = models.PositiveSmallIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=Sex.choices, null=True, blank=True)
    ancestry = models.CharField(max_length=100, null=True, blank=True)

    class Meta(RangeBase.Meta):
        abstract = True
        constraints = [
            *RangeBase.Meta.constraints,
            models.CheckConstraint(
                condition=models.Q(age_min_years__isnull=True)
                | models.Q(age_max_years__isnull=True)
                | models.Q(age_min_years__lt=models.F("age_max_years")),
                name="%(app_label)s_%(class)s_age_min_lt_max",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if (
            self.age_min_years is not None
            and self.age_max_years is not None
            and self.age_min_years >= self.age_max_years
        ):
            raise ValidationError("age_min_years must be below age_max_years")
        if self.sex is not None:
            self.sex = self.sex.strip() or None
        if self.sex is not None and self.sex not in Sex.values:
            raise ValidationError(f"sex must be one of {', '.join(Sex.values)}")
        if self.ancestry is not None:
            self.ancestry = self.ancestry.strip() or None


class ReferenceRange(StratifiedRange):
    lab = models.CharField(max_length=200, blank=True, default="")
    method = models.CharField(max_length=200, blank=True, default="")
    population = models.CharField(max_length=200, blank=True, default="")
    evidence_grade = models.CharField(max_length=100, null=True, blank=True)


class OptimalRange(StratifiedRange):
    """Provenance fields are nullable so incomplete rows can exist; the selector
    `displayable_optimal_range` gates what is shown. evidence_grade is free text naming
    the grading system of the cited source (Q49)."""

    population = models.CharField(max_length=200, null=True, blank=True)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    evidence_grade = models.CharField(max_length=100, null=True, blank=True)
    last_reviewed = models.DateField(null=True, blank=True)


class SafetyThreshold(RangeBase):
    pass


class LoincTerm(SourcedModel):
    """One row of the LOINC core table (Loinc.csv), user-supplied (Q10).

    OMOP CONCEPT mapping: concept_code = loinc_num, concept_name = long_common_name,
    vocabulary = source (Source.name 'LOINC', Source.version = release).
    `loinc_class` holds the CLASS column (`class` is a Python keyword).
    """

    loinc_num = models.CharField(max_length=10, unique=True)
    component = models.CharField(max_length=255, blank=True, default="")
    property = models.CharField(max_length=255, blank=True, default="")
    time_aspect = models.CharField(max_length=255, blank=True, default="")
    system = models.CharField(max_length=255, blank=True, default="")
    scale_type = models.CharField(max_length=255, blank=True, default="")
    method_type = models.CharField(max_length=255, blank=True, default="")
    loinc_class = models.CharField(max_length=255, blank=True, default="")
    long_common_name = models.CharField(max_length=255, blank=True, default="")
    short_name = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=255, blank=True, default="")
    featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            GinIndex(
                fields=["long_common_name"],
                name="loinc_trgm_long_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["short_name"],
                name="loinc_trgm_short_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["component"],
                name="loinc_trgm_comp_idx",
                opclasses=["gin_trgm_ops"],
            ),
            models.Index(Upper("loinc_num"), name="loinc_num_upper_idx"),
            GinIndex(
                SearchVector(
                    "long_common_name", "short_name", "component", config="simple"
                ),
                name="loinc_fts_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.loinc_num

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.loinc_num = self.loinc_num.strip()
        if not self.loinc_num:
            raise ValidationError("loinc_num must not be blank")
        super().save(*args, **kwargs)


class LoincConsumerName(SourcedModel):
    """One row of ConsumerName.csv (plain-language name of a LOINC term), user-supplied.

    OMOP CONCEPT_SYNONYM mapping: concept = term, concept_synonym_name = consumer_name,
    language = English (the file carries no language column).
    """

    term = models.ForeignKey(
        LoincTerm, on_delete=models.CASCADE, related_name="consumer_names"
    )
    consumer_name = models.CharField(max_length=1000)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["term", "consumer_name"], name="uniq_loinc_consumer_name"
            )
        ]
        indexes = [
            GinIndex(
                fields=["consumer_name"],
                name="loinc_trgm_cn_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self) -> str:
        return self.consumer_name


class LoincLinguisticVariant(SourcedModel):
    """One row of a per-language LinguisticVariants file (e.g. it-IT, zh-CN).

    OMOP CONCEPT_SYNONYM mapping: concept = term, concept_synonym_name = display_name
    (or long_common_name), language = `language` (BCP 47 tag).
    """

    term = models.ForeignKey(
        LoincTerm, on_delete=models.CASCADE, related_name="linguistic_variants"
    )
    language = models.CharField(max_length=10)
    component = models.CharField(max_length=255, blank=True, default="")
    system = models.CharField(max_length=255, blank=True, default="")
    short_name = models.CharField(max_length=255, blank=True, default="")
    long_common_name = models.CharField(max_length=255, blank=True, default="")
    related_names = models.TextField(blank=True, default="")
    display_name = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["term", "language"], name="uniq_loinc_variant_term_language"
            )
        ]
        indexes = [
            GinIndex(
                fields=["long_common_name"],
                name="loinc_trgm_lv_long_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["short_name"],
                name="loinc_trgm_lv_short_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["component"],
                name="loinc_trgm_lv_comp_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["display_name"],
                name="loinc_trgm_lv_disp_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self) -> str:
        return f"{self.term_id} {self.language}"


class LoincPart(SourcedModel):
    """One row of Part.csv, user-supplied.

    OMOP CONCEPT mapping: concept_code = part_number, concept_name = part_display_name,
    vocabulary_id = LOINC, concept_class_id derived from part_type_name.
    """

    part_number = models.CharField(max_length=100, unique=True)
    part_type_name = models.CharField(max_length=255, blank=True, default="")
    part_name = models.CharField(max_length=1000, blank=True, default="")
    part_display_name = models.CharField(max_length=1000, blank=True, default="")
    status = models.CharField(max_length=100, blank=True, default="")

    def __str__(self) -> str:
        return self.part_number


class LoincPartLink(SourcedModel):
    """One row of LoincPartLink_Primary.csv: a LOINC term linked to a part.

    OMOP CONCEPT_RELATIONSHIP mapping: concept_1 = term, concept_2 = part, the
    relationship derives from the part's type (link_type_name, property kept as given).
    """

    term = models.ForeignKey(
        LoincTerm, on_delete=models.CASCADE, related_name="part_links"
    )
    part = models.ForeignKey(
        LoincPart, on_delete=models.CASCADE, related_name="term_links"
    )
    link_type_name = models.CharField(max_length=255, blank=True, default="")
    property = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["term", "part", "link_type_name", "property"],
                name="uniq_loinc_part_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.term_id} -> {self.part_id}"


class LoincAnswerList(SourcedModel):
    """One answer list (LL id) of AnswerList.csv, user-supplied.

    OMOP CONCEPT mapping: concept_code = answer_list_id (LL...), concept_name = name,
    vocabulary_id = LOINC; `oid` is the list's OID as given.
    """

    answer_list_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=1000, blank=True, default="")
    oid = models.CharField(max_length=1000, blank=True, default="")

    def __str__(self) -> str:
        return self.answer_list_id


class LoincAnswer(SourcedModel):
    """One answer (LA id, AnswerStringId) of an answer list.

    OMOP CONCEPT mapping: concept_code = answer_code (LA...), concept_name =
    display_text; CONCEPT_RELATIONSHIP list -> answer, ordered by `sequence`.
    """

    answer_list = models.ForeignKey(
        LoincAnswerList, on_delete=models.CASCADE, related_name="answers"
    )
    answer_code = models.CharField(max_length=100)
    local_answer_code = models.CharField(max_length=100, blank=True, default="")
    sequence = models.PositiveIntegerField(null=True, blank=True)
    display_text = models.CharField(max_length=1000, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer_list", "answer_code"], name="uniq_loinc_answer"
            )
        ]

    def __str__(self) -> str:
        return f"{self.answer_list_id} {self.answer_code}"


class LoincAnswerListLink(SourcedModel):
    """One row of LoincAnswerListLink.csv: a LOINC term uses an answer list.

    OMOP CONCEPT_RELATIONSHIP mapping: concept_1 = term, concept_2 = answer list,
    link_type (AnswerListLinkType, e.g. NORMATIVE) kept as given.
    """

    term = models.ForeignKey(
        LoincTerm, on_delete=models.CASCADE, related_name="answer_list_links"
    )
    answer_list = models.ForeignKey(
        LoincAnswerList, on_delete=models.CASCADE, related_name="term_links"
    )
    link_type = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["term", "answer_list", "link_type"],
                name="uniq_loinc_answer_list_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.term_id} -> {self.answer_list_id}"
