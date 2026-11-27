# SPDX-License-Identifier: AGPL-3.0-or-later
"""Substance catalog metadata (M03 TG-a): names, class and cited external code strings.

Only code strings are stored, each with its source and fetch date (Q105, Q106). No
terminology release, synonym list, ATC tree or DDD table lives here.
"""

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
