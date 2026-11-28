# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol (mutable only while Draft) and its immutable versions (M03 TG-f, Q109 plain model)."""

from typing import Any, NoReturn

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ImmutableRecordError(RuntimeError):
    """Raised on any attempt to change or delete a created version or change event."""


class ImmutableQuerySet(models.QuerySet):
    def update(self, **kwargs: Any) -> NoReturn:  # type: ignore[override]
        raise ImmutableRecordError(
            "Created versions and change events cannot be updated."
        )

    def delete(self) -> NoReturn:
        raise ImmutableRecordError(
            "Created versions and change events cannot be deleted."
        )


class ImmutableModel(models.Model):
    objects = ImmutableQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ImmutableRecordError(
                "A created version or change event cannot be changed."
            )
        # Always INSERT: a new instance carrying an existing pk must collide
        # (IntegrityError) instead of silently overwriting the stored row.
        kwargs.pop("force_update", None)
        kwargs["force_insert"] = True
        super().save(**kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise ImmutableRecordError(
            "Created versions and change events cannot be deleted."
        )


class State(models.TextChoices):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Origin(models.TextChoices):
    CURATED = "curated"
    COMMUNITY = "community"


class Level(models.TextChoices):
    MEDICAL = "medical"
    RESEARCH = "research"


class History(models.TextChoices):
    ANALYTIC = "analytic"
    SYNTHESIZED = "synthesized"


class Protocol(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="protocols"
    )
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=10, choices=State.choices, default=State.DRAFT)
    origin = models.CharField(
        max_length=10, choices=Origin.choices, default=Origin.COMMUNITY
    )
    # Chosen by the user; never inferred from content. Empty until chosen.
    level = models.CharField(
        max_length=10, choices=Level.choices, blank=True, default=""
    )
    in_effect_since = models.DateField(null=True, blank=True)
    tracked_since = models.DateField()
    history = models.CharField(
        max_length=12, choices=History.choices, default=History.ANALYTIC
    )
    lineage_note = models.TextField(blank=True, default="")
    interventions = models.JSONField(default=list)
    cycles = models.JSONField(default=list)
    measures = models.JSONField(default=list)
    goals = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    # Lineage of a fork (TG-f part 2a): the source and the exact published version copied.
    forked_from_protocol = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forks",
    )
    forked_from_version = models.ForeignKey(
        "ProtocolVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forks",
    )

    class Meta:
        ordering = ["id"]


class ProtocolVersion(ImmutableModel):
    protocol = models.ForeignKey(
        Protocol, on_delete=models.CASCADE, related_name="versions"
    )
    number = models.PositiveIntegerField()
    snapshot = models.JSONField()
    created_at = models.DateTimeField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    reason = models.TextField()

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["protocol", "number"], name="protocol_version_number"
            )
        ]


class ChangeEvent(ImmutableModel):
    version = models.ForeignKey(
        ProtocolVersion, on_delete=models.CASCADE, related_name="events"
    )
    field = models.CharField(max_length=200)
    old = models.JSONField(null=True)
    new = models.JSONField(null=True)
    timestamp = models.DateTimeField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    reason = models.TextField()

    class Meta:
        ordering = ["id"]


class Publication(models.Model):
    """Public status of a protocol: pins one version; `withheld` lists item keys such as
    `measures[1]` (position in the pinned version) kept out of public views. Mutable by
    design: every change is also recorded as a ChangeEvent."""

    protocol = models.OneToOneField(
        Protocol, on_delete=models.CASCADE, related_name="publication"
    )
    version = models.ForeignKey(
        ProtocolVersion, on_delete=models.RESTRICT, related_name="+"
    )
    withheld = models.JSONField(default=list)
    published = models.BooleanField(default=True)
    updated_at = models.DateTimeField()


class ActivationAcknowledgment(ImmutableModel):
    """Logged heightened acknowledgment given when a protocol became active (append-only)."""

    protocol = models.ForeignKey(
        Protocol, on_delete=models.CASCADE, related_name="acknowledgments"
    )
    version = models.ForeignKey(
        ProtocolVersion, on_delete=models.CASCADE, related_name="acknowledgments"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    timestamp = models.DateTimeField()
    level = models.CharField(max_length=10)
    # Item names as they were at activation, not a live reference.
    animal_derived_items = models.JSONField(default=list)
    statement = models.TextField()

    class Meta:
        ordering = ["id"]


class IntakeState(models.TextChoices):
    """The four stored adherence names (Q150). No rule or default ever sets one."""

    DONE = "done"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    MISSED = "missed"


class IntakeEvent(models.Model):
    """One due intake. `state` is null while pending; only `set_intake_state` writes it."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    protocol = models.ForeignKey(
        Protocol, on_delete=models.CASCADE, related_name="intake_events"
    )
    version = models.ForeignKey(
        ProtocolVersion, on_delete=models.CASCADE, related_name="intake_events"
    )
    # Position of the intervention in version.snapshot["interventions"], as text (Q160).
    intervention_key = models.CharField(max_length=20)
    due_date = models.DateField()
    occurrence_index = models.PositiveIntegerField()
    state = models.CharField(
        max_length=10, choices=IntakeState.choices, null=True, blank=True
    )
    state_set_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    state_set_at = models.DateTimeField(null=True, blank=True)
    entered_amount = models.DecimalField(
        max_digits=30, decimal_places=10, null=True, blank=True
    )
    # UCUM code stored as given; not converted or validated (Q158).
    entered_unit = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["due_date", "occurrence_index", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "intervention_key", "due_date", "occurrence_index"],
                name="intake_event_unique_occurrence",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        state__isnull=True,
                        state_set_by__isnull=True,
                        state_set_at__isnull=True,
                    )
                    | models.Q(
                        state__isnull=False,
                        state_set_by__isnull=False,
                        state_set_at__isnull=False,
                    )
                ),
                name="intake_event_state_actor_time_together",
            ),
            models.CheckConstraint(
                condition=models.Q(entered_amount__isnull=True)
                | ~models.Q(entered_unit=""),
                name="intake_event_amount_needs_unit",
            ),
        ]


class IntakeConstraintKind(models.TextChoices):
    SEPARATE_SLOTS = "separate_slots"
    MIN_DISTANCE_MINUTES = "min_distance_minutes"


class IntakeConstraint(models.Model):
    """A spacing rule between two substances, or between one substance and meals
    (`substance_b` null). Counts as sourced only when `source` is non-blank. Never seeded."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    substance_a = models.ForeignKey(
        "substances.Substance", on_delete=models.CASCADE, related_name="+"
    )
    substance_b = models.ForeignKey(
        "substances.Substance",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    kind = models.CharField(max_length=24, choices=IntakeConstraintKind.choices)
    minutes = models.PositiveIntegerField(null=True, blank=True)
    # Free-text citation; blank means the constraint is listed but not enforced.
    source = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(minutes__isnull=True) | models.Q(minutes__gt=0),
                name="intake_constraint_minutes_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    kind="separate_slots",
                    minutes__isnull=True,
                    substance_b__isnull=False,
                )
                | models.Q(kind="min_distance_minutes", minutes__isnull=False),
                name="intake_constraint_kind_fields",
            ),
        ]

    def clean(self) -> None:
        if self.minutes is not None and self.minutes <= 0:
            raise ValidationError("minutes must be positive.")
        if self.kind == IntakeConstraintKind.SEPARATE_SLOTS:
            if self.minutes is not None:
                raise ValidationError("separate_slots takes no minutes.")
            if self.substance_b_id is None:
                raise ValidationError("separate_slots needs a second substance.")
        elif self.minutes is None:
            raise ValidationError("min_distance_minutes needs minutes.")
