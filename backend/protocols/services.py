# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol create / edit rules: Draft is edited in place; every later change is a new immutable
version with one change event per changed field and a mandatory reason."""

from datetime import date
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.exceptions import (  # type: ignore[import-untyped]  # DRF ships no stubs
    PermissionDenied,
    ValidationError,
)

from .diffing import changed_fields
from .facets import FACETS, MAX_TEXT, clean_facet
from .models import ChangeEvent, History, Level, Protocol, ProtocolVersion, State

TRACKED = ("title", "level", "state", *FACETS)
DRAFT_ONLY = ("in_effect_since", "history", "lineage_note")
TRANSITIONS = {
    State.DRAFT: {State.ACTIVE},
    State.ACTIVE: {State.PAUSED, State.COMPLETED},
    State.PAUSED: {State.ACTIVE, State.COMPLETED},
    State.COMPLETED: set(),
}
IMPORT_REASON = "imported as already running"


def snapshot(protocol: Protocol) -> dict[str, Any]:
    return {name: getattr(protocol, name) for name in TRACKED}


def _choice(raw: Any, choices: type[Any], where: str) -> str:
    if raw not in choices.values:
        raise ValidationError({where: f"must be one of {', '.join(choices.values)}."})
    return str(raw)


def _title(raw: Any) -> str:
    if (
        not isinstance(raw, str)
        or not raw.strip()
        or len(raw.strip()) > 200
        or "\x00" in raw
    ):
        raise ValidationError({"title": "must be 1 to 200 characters of text."})
    return raw.strip()


def _date(raw: Any) -> date | None:
    if raw is None:
        return None
    try:
        parsed = parse_date(raw) if isinstance(raw, str) else None
    except ValueError:
        parsed = None
    if parsed is None:
        raise ValidationError({"in_effect_since": "must be a date as YYYY-MM-DD."})
    return parsed


def _note(raw: Any) -> str:
    if not isinstance(raw, str) or "\x00" in raw or len(raw) > 4 * MAX_TEXT:
        raise ValidationError(
            {"lineage_note": f"must be text of at most {4 * MAX_TEXT} characters."}
        )
    return raw.strip()


def clean_reason(raw: Any) -> str:
    if raw is None:
        return ""
    if not isinstance(raw, str) or "\x00" in raw:
        raise ValidationError({"reason": "must be text."})
    return raw.strip()


def parse_fields(data: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    """Validate the protocol fields present in `data`; unknown or not-allowed keys are a 400."""
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError({"detail": f"Not accepted here: {', '.join(unknown)}."})
    out: dict[str, Any] = {}
    for key, raw in data.items():
        if key == "title":
            out[key] = _title(raw)
        elif key == "level":
            out[key] = _choice(raw, Level, key)
        elif key == "state":
            out[key] = _choice(raw, State, key)
        elif key in FACETS:
            out[key] = clean_facet(key, raw)
        elif key == "in_effect_since":
            out[key] = _date(raw)
        elif key == "history":
            out[key] = _choice(raw, History, key)
        elif key == "lineage_note":
            out[key] = _note(raw)
    return out


def _check_lineage(history: str, note: str) -> None:
    if note and history != History.SYNTHESIZED:
        raise ValidationError(
            {"lineage_note": "is only stored with history=synthesized."}
        )


def _version(
    protocol: Protocol, actor: Any, reason: str, new: dict[str, Any]
) -> ProtocolVersion:
    old = snapshot(protocol)
    events = [e for name in TRACKED for e in changed_fields(old[name], new[name], name)]
    if not events:
        raise ValidationError({"detail": "Nothing changed."})
    now = timezone.now()
    number = protocol.versions.count() + 1
    for name in TRACKED:
        setattr(protocol, name, new[name])
    protocol.save()
    version = ProtocolVersion.objects.create(
        protocol=protocol,
        number=number,
        snapshot=new,
        created_at=now,
        actor=actor,
        reason=reason,
    )
    ChangeEvent.objects.bulk_create(
        ChangeEvent(
            version=version,
            field=e["field"],
            old=e["old"],
            new=e["new"],
            timestamp=now,
            actor=actor,
            reason=reason,
        )
        for e in events
    )
    return version


def edit(
    protocol: Protocol, actor: AbstractBaseUser, fields: dict[str, Any], reason: str
) -> ProtocolVersion | None:
    """Apply validated `fields`. Returns the new version, or None for an in-place Draft edit.
    The caller holds a row lock on `protocol` inside a transaction."""
    new = {**snapshot(protocol), **{k: v for k, v in fields.items() if k in TRACKED}}
    draft_only = {k: v for k, v in fields.items() if k in DRAFT_ONLY}
    if protocol.state == State.DRAFT:
        _check_lineage(
            draft_only.get("history", protocol.history),
            draft_only.get("lineage_note", protocol.lineage_note),
        )
        for key, value in draft_only.items():
            setattr(protocol, key, value)
        if new["state"] == State.DRAFT:
            for name in TRACKED:
                setattr(protocol, name, new[name])
            protocol.save()
            return None
    elif draft_only:
        raise ValidationError(
            {"detail": f"{', '.join(draft_only)} can only change in Draft."}
        )
    if not reason:
        raise ValidationError({"reason": "A reason is required for this change."})
    if (
        new["state"] != protocol.state
        and new["state"] not in TRANSITIONS[State(protocol.state)]
    ):
        raise ValidationError(
            {"state": f"A {protocol.state} protocol cannot become {new['state']}."}
        )
    if protocol.state == State.DRAFT and not new["level"]:
        raise ValidationError(
            {"level": "Choose medical or research before leaving Draft."}
        )
    return _version(protocol, actor, reason, new)


def create(
    actor: AbstractBaseUser, data: dict[str, Any]
) -> tuple[Protocol, ProtocolVersion | None]:
    allowed = {"origin", "already_running", "reason", *TRACKED, *DRAFT_ONLY}
    body = {
        k: v
        for k, v in data.items()
        if k not in ("origin", "already_running", "reason")
    }
    origin = data.get("origin", "community")
    if origin not in ("community", "curated"):
        raise ValidationError({"origin": "must be one of curated, community."})
    if origin == "curated" and not actor.is_staff:  # type: ignore[attr-defined]
        raise PermissionDenied("Only staff can create a curated protocol.")
    running = data.get("already_running", False)
    if not isinstance(running, bool):
        raise ValidationError({"already_running": "must be true or false."})
    if "state" in body:
        raise ValidationError({"state": "A new protocol starts in draft."})
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError({"detail": f"Not accepted here: {', '.join(unknown)}."})
    if "title" not in body:
        raise ValidationError({"title": "is required."})
    fields = parse_fields(body, {*TRACKED, *DRAFT_ONLY})
    reason = clean_reason(data.get("reason"))
    with transaction.atomic():
        protocol = Protocol(
            owner=actor, origin=origin, tracked_since=timezone.localdate()
        )
        for key, value in fields.items():
            setattr(protocol, key, value)
        _check_lineage(protocol.history, protocol.lineage_note)
        protocol.save()
        if not running:
            return protocol, None
        since = protocol.in_effect_since
        if since is None or since > timezone.localdate():
            raise ValidationError(
                {"in_effect_since": "is required, and not in the future."}
            )
        text = f"{IMPORT_REASON}. {reason}" if reason else IMPORT_REASON
        return protocol, edit(protocol, actor, {"state": State.ACTIVE}, text)
