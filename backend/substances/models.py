# SPDX-License-Identifier: AGPL-3.0-or-later
"""Substance catalog metadata (M03 TG-a): names, class and cited external code strings.

Only code strings are stored, each with its source and fetch date (Q105, Q106). No
terminology release, synonym list, ATC tree or DDD table lives here.
"""

from django.conf import settings
from django.db import models


class CodeSystem(models.TextChoices):
    RXCUI = "rxcui"
    PUBCHEM_CID = "pubchem_cid"
    UNII = "unii"
    ATC = "atc"


class Substance(models.Model):
    name = models.CharField(max_length=200)
    # Free-text class label; when set it needs its own source and fetch date.
    substance_class = models.CharField(max_length=200, blank=True, default="")
    class_source = models.CharField(max_length=300, blank=True, default="")
    class_fetched_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(name=""), name="substance_name_set"
            ),
            models.CheckConstraint(
                condition=models.Q(substance_class="")
                | (
                    ~models.Q(class_source="")
                    & models.Q(class_fetched_on__isnull=False)
                ),
                name="substance_class_has_source",
            ),
        ]


class SubstanceCode(models.Model):
    substance = models.ForeignKey(
        Substance, on_delete=models.CASCADE, related_name="codes"
    )
    system = models.CharField(max_length=12, choices=CodeSystem.choices)
    code = models.CharField(max_length=64)
    source = models.CharField(max_length=300)
    fetched_on = models.DateField()
    # Provisional until the licence questions Q105/Q106 are answered.
    provisional = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["substance", "system", "code"], name="substance_code_unique"
            ),
            models.CheckConstraint(
                condition=~models.Q(code="") & ~models.Q(source=""),
                name="substance_code_and_source_set",
            ),
        ]


def normalise_name(name: str) -> str:
    """Case-fold, collapse whitespace and strip: the only normalisation used to match."""
    return " ".join(name.casefold().split())


class SubstanceSynonym(models.Model):
    """A name for a substance in one language, with its source. It resolves only once
    reviewed (reviewer and reviewed_at set by an approval, never by a client)."""

    substance = models.ForeignKey(
        Substance, on_delete=models.CASCADE, related_name="synonyms"
    )
    name = models.CharField(max_length=200)
    normalised_name = models.CharField(max_length=200)
    # BCP 47 tag, kept as typed.
    language = models.CharField(max_length=35)
    source = models.CharField(max_length=300)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["normalised_name", "language", "substance"],
                name="substance_synonym_unique",
            ),
            models.CheckConstraint(
                condition=~models.Q(name="")
                & ~models.Q(normalised_name="")
                & ~models.Q(language="")
                & ~models.Q(source=""),
                name="substance_synonym_fields_set",
            ),
            models.CheckConstraint(
                # reviewer is SET_NULL on account erasure; reviewed_at keeps the review.
                condition=models.Q(reviewer__isnull=True)
                | models.Q(reviewed_at__isnull=False),
                name="substance_synonym_reviewer_needs_date",
            ),
        ]


class ReviewReason(models.TextChoices):
    NO_MATCH = "no_match"
    UNREVIEWED_SYNONYM = "unreviewed_synonym"
    NEAR_MATCH = "near_match"
    SEVERAL_SUBSTANCES = "several_substances"
    NO_CODE = "no_code"


class ReviewStatus(models.TextChoices):
    OPEN = "open"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SubstanceReviewItem(models.Model):
    """A submitted name that did not resolve. It is never dropped and never attached to
    a substance until staff name one."""

    submitted_name = models.CharField(max_length=200)
    normalised_name = models.CharField(max_length=200)
    language = models.CharField(max_length=35, blank=True, default="")
    reason = models.CharField(max_length=20, choices=ReviewReason.choices)
    candidate_substance_ids = models.JSONField(default=list)
    status = models.CharField(
        max_length=10, choices=ReviewStatus.choices, default=ReviewStatus.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    resolved_substance = models.ForeignKey(
        Substance, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["normalised_name", "language"],
                condition=models.Q(status="open"),
                name="substance_review_one_open",
            ),
        ]


class ExtractionItemStatus(models.TextChoices):
    RESOLVED = "resolved"
    NOT_UNDERSTOOD = "not_understood"


class ExtractionDecision(models.TextChoices):
    CORRECTED = "corrected"
    LEFT_OUT = "left_out"


class AmbiguityReason(models.TextChoices):
    NOT_IN_ENUM = "not_in_enum"
    TOO_LONG = "too_long"
    NOT_TEXT = "not_text"
    UNKNOWN_FIELD = "unknown_field"


class Extraction(models.Model):
    """A staged batch resolve owned by one user. Nothing is attached to a protocol or a
    substance until the owner commits it (M03 TG-c)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    committed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]


class ExtractionItem(models.Model):
    extraction = models.ForeignKey(
        Extraction, on_delete=models.CASCADE, related_name="items"
    )
    position = models.PositiveIntegerField()
    submitted_name = models.CharField(max_length=200)
    normalised_name = models.CharField(max_length=200)
    language = models.CharField(max_length=35, blank=True, default="")
    status = models.CharField(max_length=14, choices=ExtractionItemStatus.choices)
    substance = models.ForeignKey(
        Substance, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    review_item = models.ForeignKey(
        SubstanceReviewItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    candidate_substance_ids = models.JSONField(default=list)
    decision = models.CharField(
        max_length=10, choices=ExtractionDecision.choices, blank=True, default=""
    )
    decided_substance = models.ForeignKey(
        Substance, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    # Proposed values that passed the validator, keyed by constrained column.
    accepted_fields = models.JSONField(default=dict)
    # Free-text proposals: wide, never a constrained column.
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["extraction", "position"], name="extraction_item_position"
            ),
        ]


class ExtractionAmbiguity(models.Model):
    """A proposed value the validator refused to write, kept whole (never truncated)."""

    item = models.ForeignKey(
        ExtractionItem, on_delete=models.CASCADE, related_name="ambiguities"
    )
    field = models.TextField()
    value = models.TextField()
    reason = models.CharField(max_length=14, choices=AmbiguityReason.choices)

    class Meta:
        ordering = ["id"]
