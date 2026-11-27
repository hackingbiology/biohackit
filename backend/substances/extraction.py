# SPDX-License-Identifier: AGPL-3.0-or-later
"""Batch resolve with an input-output diff and a staged commit (M03 TG-c).

Reuses the TG-b resolver (`synonyms.resolve_name`); nothing here matches a name itself.
The counts are computed from the stored items, so submitted = recognised + not
understood always holds. No LLM and no network call is made: `proposed` values come
from the caller and pass through the constrained-column validator.
"""

from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import (
    Extraction,
    ExtractionAmbiguity,
    ExtractionDecision,
    ExtractionItem,
    ExtractionItemStatus,
    Substance,
    SubstanceCode,
    normalise_name,
)
from .services import SubstanceError
from .synonyms import resolve_name
from .validator import validate_proposal

# A code parameter (Q121), not a cited limit.
MAX_ENTRIES = 50
PROPOSAL_TARGET = SubstanceCode
PROPOSAL_FIELDS = ("system", "code", "source")


def _has_nul(value: Any) -> bool:
    return isinstance(value, str) and "\x00" in value


def _entries(body: dict[str, Any]) -> list[dict[str, Any]]:
    entries = body.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SubstanceError({"entries": "Send at least one name."})
    if len(entries) > MAX_ENTRIES:
        raise SubstanceError({"entries": f"Send at most {MAX_ENTRIES} names at once."})
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise SubstanceError({"entries": "Each entry needs a name."})
        proposed = entry.get("proposed", {})
        if not isinstance(proposed, dict):
            raise SubstanceError({"entries": "Proposed values must be an object."})
        if any(_has_nul(k) or _has_nul(v) for k, v in proposed.items()):
            raise SubstanceError({"entries": "Enter text."})
    return entries


def _add_item(extraction: Extraction, position: int, entry: dict[str, Any]) -> None:
    language = entry.get("language")
    if language is not None and not isinstance(language, str):
        raise SubstanceError({"entries": "Language must be text."})
    result = resolve_name(entry["name"], language)
    resolved = result.substance is not None
    checked = validate_proposal(
        PROPOSAL_TARGET, entry.get("proposed", {}), PROPOSAL_FIELDS
    )
    item = ExtractionItem.objects.create(
        extraction=extraction,
        position=position,
        submitted_name=entry["name"].strip(),
        normalised_name=normalise_name(entry["name"]),
        language=(language or "").strip(),
        status=(
            ExtractionItemStatus.RESOLVED
            if resolved
            else ExtractionItemStatus.NOT_UNDERSTOOD
        ),
        substance=result.substance,
        review_item=result.review_item,
        candidate_substance_ids=result.candidate_ids if not resolved else [],
        accepted_fields=checked.accepted,
        notes=checked.notes,
    )
    ExtractionAmbiguity.objects.bulk_create(
        ExtractionAmbiguity(item=item, field=a.field, value=a.value, reason=a.reason)
        for a in checked.ambiguous
    )


def submit(owner: Any, body: dict[str, Any]) -> Extraction:
    """Resolve every entry and stage the result; nothing is committed."""
    entries = _entries(body)
    with transaction.atomic():
        extraction = Extraction.objects.create(owner=owner)
        for position, entry in enumerate(entries):
            _add_item(extraction, position, entry)
    return extraction


def summary(extraction: Extraction) -> dict[str, int]:
    """The diff counts, computed from the stored items."""
    items = extraction.items.all()
    recognised = sum(1 for i in items if i.status == ExtractionItemStatus.RESOLVED)
    return {
        "submitted": len(items),
        "recognised": recognised,
        "not_understood": len(items) - recognised,
    }


def _require_open(extraction: Extraction) -> None:
    if extraction.committed_at is not None:
        raise SubstanceError({"detail": "This extraction is already committed."})


def decide(
    extraction: Extraction, item: ExtractionItem, body: dict[str, Any], user: Any
) -> ExtractionItem:
    """Correct a not-understood name with a substance, or confirm it as left out.

    The same normalised name elsewhere in the extraction gets the same decision (Q120).
    A correction is recorded with actor and time; it creates no synonym (Q122).
    """
    _require_open(extraction)
    if item.status != ExtractionItemStatus.NOT_UNDERSTOOD:
        raise SubstanceError({"detail": "This name was already recognised."})
    decision = body.get("decision")
    if decision not in ExtractionDecision.values:
        raise SubstanceError({"decision": "Use corrected or left_out."})
    substance: Substance | None = None
    if decision == ExtractionDecision.CORRECTED:
        substance_id = body.get("substance")
        if not isinstance(substance_id, int) or isinstance(substance_id, bool):
            raise SubstanceError({"substance": "Choose a substance."})
        substance = Substance.objects.filter(pk=substance_id).first()
        if substance is None:
            raise SubstanceError({"substance": "Choose a substance."})
    extraction.items.filter(
        status=ExtractionItemStatus.NOT_UNDERSTOOD,
        normalised_name=item.normalised_name,
    ).update(
        decision=decision,
        decided_substance=substance,
        decided_by=user,
        decided_at=timezone.now(),
    )
    item.refresh_from_db()
    return item


def commit(extraction: Extraction) -> Extraction:
    """Close the extraction once every not-understood name has a decision."""
    _require_open(extraction)
    undecided = extraction.items.filter(
        status=ExtractionItemStatus.NOT_UNDERSTOOD, decision=""
    ).count()
    if undecided:
        raise SubstanceError(
            {"detail": f"Decide the {undecided} name(s) not understood before saving."}
        )
    extraction.committed_at = timezone.now()
    extraction.save()
    return extraction
