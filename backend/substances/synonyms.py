# SPDX-License-Identifier: AGPL-3.0-or-later
"""Synonyms and name resolution (M03 TG-b).

A name resolves only by exact match, after case and whitespace normalisation, on a
reviewed synonym that points to exactly one substance. Every other outcome is queued as
`ambiguous` and never attached to a substance. Near-matches come from stdlib difflib and
are shown to the reviewer only (Q117, Q118).
"""

from dataclasses import dataclass
from difflib import get_close_matches
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import (
    ReviewReason,
    ReviewStatus,
    Substance,
    SubstanceReviewItem,
    SubstanceSynonym,
    normalise_name,
)
from .services import NAME_MAX, SOURCE_MAX, SubstanceError, _text

LANGUAGE_MAX = 35
# A code parameter (Q117), not a cited threshold: difflib's own default is 0.6.
NEAR_MATCH_CUTOFF = 0.8
NEAR_MATCH_LIMIT = 5
SERVER_FIELDS = ("reviewer", "reviewed_at", "normalised_name")


@dataclass(frozen=True)
class Resolution:
    status: str  # "resolved" | "ambiguous"
    reason: str | None
    substance: Substance | None
    candidate_ids: list[int]
    review_item: SubstanceReviewItem | None


def _normalised(name: str) -> str:
    """Normalise, and refuse a name whose folded form no longer fits its column."""
    normalised = normalise_name(name)
    if len(normalised) > NAME_MAX:
        raise SubstanceError({"name": f"Use at most {NAME_MAX} characters."})
    return normalised


def create_synonym(data: dict[str, Any]) -> SubstanceSynonym:
    """Create an unreviewed synonym; a client cannot send a reviewer."""
    for key in SERVER_FIELDS:
        if key in data:
            raise SubstanceError({key: "This field is set by the server."})
    substance_id = data.get("substance")
    if isinstance(substance_id, bool) or not isinstance(substance_id, int):
        raise SubstanceError({"substance": "Choose a substance."})
    substance = Substance.objects.filter(pk=substance_id).first()
    if substance is None:
        raise SubstanceError({"substance": "Choose a substance."})
    name = _text(data, "name", NAME_MAX, required=True)
    normalised = _normalised(name)
    language = _text(data, "language", LANGUAGE_MAX, required=True)
    source = _text(data, "source", SOURCE_MAX, required=True)
    if SubstanceSynonym.objects.filter(
        substance=substance, normalised_name=normalised, language=language
    ).exists():
        raise SubstanceError({"name": "This synonym is already recorded."})
    return SubstanceSynonym.objects.create(
        substance=substance,
        name=name,
        normalised_name=normalised,
        language=language,
        source=source,
    )


def approve_synonym(synonym: SubstanceSynonym, reviewer: Any) -> SubstanceSynonym:
    if synonym.reviewed_at is not None:
        raise SubstanceError({"detail": "This synonym is already reviewed."})
    synonym.reviewer = reviewer
    synonym.reviewed_at = timezone.now()
    synonym.save()
    return synonym


def _substance_ids(rows: Any) -> list[int]:
    return sorted(set(rows.values_list("substance_id", flat=True)))


def _classify(normalised: str) -> tuple[str, list[int]]:
    """Return (reason, candidate substance ids); reason "resolved" has one candidate."""
    exact = SubstanceSynonym.objects.filter(normalised_name=normalised)
    reviewed = _substance_ids(exact.filter(reviewed_at__isnull=False))
    if len(reviewed) == 1:
        return "resolved", reviewed
    if len(reviewed) > 1:
        return ReviewReason.SEVERAL_SUBSTANCES, reviewed
    unreviewed = _substance_ids(exact)
    if unreviewed:
        return ReviewReason.UNREVIEWED_SYNONYM, unreviewed
    known = SubstanceSynonym.objects.filter(reviewed_at__isnull=False)
    close = get_close_matches(
        normalised,
        sorted(set(known.values_list("normalised_name", flat=True))),
        n=NEAR_MATCH_LIMIT,
        cutoff=NEAR_MATCH_CUTOFF,
    )
    if close:
        return ReviewReason.NEAR_MATCH, _substance_ids(
            known.filter(normalised_name__in=close)
        )
    return ReviewReason.NO_MATCH, []


def _queue(
    submitted: str, normalised: str, language: str, reason: str, ids: list[int]
) -> SubstanceReviewItem:
    """Create the open item, or reuse and refresh the one already open."""
    with transaction.atomic():
        item, created = SubstanceReviewItem.objects.get_or_create(
            normalised_name=normalised,
            language=language,
            status=ReviewStatus.OPEN,
            defaults={
                "submitted_name": submitted,
                "reason": reason,
                "candidate_substance_ids": ids,
            },
        )
        if not created:
            item.reason = reason
            item.candidate_substance_ids = ids
            item.save()
    return item


def resolve_name(name: str, language: str | None = None) -> Resolution:
    """Resolve a name to one substance, or queue it as ambiguous.

    `language` is recorded on a queued item only; it does not filter the match (Q118).
    """
    submitted = _text({"name": name}, "name", NAME_MAX, required=True)
    lang = _text({"language": language or ""}, "language", LANGUAGE_MAX, required=False)
    normalised = _normalised(submitted)
    reason, ids = _classify(normalised)
    if reason == "resolved":
        substance = Substance.objects.get(pk=ids[0])
        if substance.codes.exists():
            return Resolution("resolved", None, substance, ids, None)
        reason = ReviewReason.NO_CODE
    item = _queue(submitted, normalised, lang, reason, ids)
    return Resolution("ambiguous", reason, None, ids, item)


def resolve_item(
    item: SubstanceReviewItem, substance_id: Any, user: Any
) -> SubstanceReviewItem:
    """Staff name the substance for an open item."""
    _require_open(item)
    if isinstance(substance_id, bool) or not isinstance(substance_id, int):
        raise SubstanceError({"substance": "Choose a substance."})
    substance = Substance.objects.filter(pk=substance_id).first()
    if substance is None:
        raise SubstanceError({"substance": "Choose a substance."})
    item.status = ReviewStatus.RESOLVED
    item.resolved_substance = substance
    return _close(item, user)


def reject_item(item: SubstanceReviewItem, user: Any) -> SubstanceReviewItem:
    _require_open(item)
    item.status = ReviewStatus.REJECTED
    return _close(item, user)


def _require_open(item: SubstanceReviewItem) -> None:
    if item.status != ReviewStatus.OPEN:
        raise SubstanceError({"detail": "This item is already closed."})


def _close(item: SubstanceReviewItem, user: Any) -> SubstanceReviewItem:
    item.resolved_by = user
    item.resolved_at = timezone.now()
    item.save()
    return item
