# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol (mutable only while Draft) and its immutable versions (M03 TG-f, Q109 plain model)."""

from typing import Any, NoReturn

from django.conf import settings
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
