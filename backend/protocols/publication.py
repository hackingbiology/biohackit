# SPDX-License-Identifier: AGPL-3.0-or-later
"""Publish a protocol (M03 TG-k, Q112): a draft is private; a published protocol is public
except the items the owner withholds. The publication pins one version, so later versions stay
private until the owner publishes again. Genomic items are never public (fail closed: no
genomics heightened consent exists yet)."""

from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from rest_framework.exceptions import (  # type: ignore[import-untyped]  # DRF ships no stubs
    ValidationError,
)

from .models import ChangeEvent, Protocol, ProtocolVersion, Publication, State

ITEM_FACETS = ("interventions", "measures")
PRIVATE_INTERVENTION_KEYS = ("product_id", "units_per_day")


def item_keys(snapshot: dict[str, Any]) -> list[str]:
    """Item keys of a version, e.g. `measures[1]`: facet and position in that version."""
    return [
        f"{facet}[{i}]" for facet in ITEM_FACETS for i in range(len(snapshot[facet]))
    ]


def _carry_over(pub: Publication | None, snapshot: dict[str, Any]) -> list[str]:
    """Keys are positional, so earlier withholds carry over only when each withheld item is
    unchanged at the same position; otherwise the owner must say what to withhold."""
    if pub is None or not pub.withheld:
        return []
    old = pub.version.snapshot
    for key in pub.withheld:
        facet, _, rest = key.partition("[")
        i = int(rest.rstrip("]"))
        if i >= len(snapshot[facet]) or snapshot[facet][i] != old[facet][i]:
            raise ValidationError(
                {
                    "withheld_items": "Earlier withheld items no longer match this "
                    "version. Send withheld_items explicitly (an empty list withholds nothing)."
                }
            )
    return list(pub.withheld)


def _clean_withheld(raw: Any, snapshot: dict[str, Any]) -> list[str]:
    if not isinstance(raw, list) or not all(isinstance(k, str) for k in raw):
        raise ValidationError({"withheld_items": "must be a list of item keys."})
    valid = item_keys(snapshot)
    bad = sorted({k for k in raw if k not in valid})
    if bad:
        raise ValidationError(
            {"withheld_items": f"not items of the version being published: {bad}."}
        )
    return [k for k in valid if k in raw]


def _record(
    version: ProtocolVersion,
    actor: AbstractBaseUser,
    old: Any,
    new: Any,
    reason: str,
) -> None:
    ChangeEvent.objects.create(
        version=version,
        field="publication",
        old=old,
        new=new,
        timestamp=timezone.now(),
        actor=actor,
        reason=reason,
    )


def _state(pub: Publication | None) -> dict[str, Any] | None:
    if pub is None:
        return None
    return {
        "published": pub.published,
        "version": pub.version.number,
        "withheld": pub.withheld,
    }


def _need_reason(reason: str) -> None:
    if not reason:
        raise ValidationError({"reason": "A reason is required for this change."})


def publish(
    protocol: Protocol, actor: AbstractBaseUser, raw_withheld: Any, reason: str
) -> Publication:
    """Publish (or re-publish) the latest version. The caller holds the protocol row lock."""
    _need_reason(reason)
    version = protocol.versions.last()
    if protocol.state == State.DRAFT or version is None:
        raise ValidationError(
            {"detail": "A draft is private. Leave Draft before publishing."}
        )
    pub = (
        Publication.objects.filter(protocol=protocol).select_related("version").first()
    )
    if raw_withheld is None:
        withheld = _carry_over(pub, version.snapshot)
    else:
        withheld = _clean_withheld(raw_withheld, version.snapshot)
    old = _state(pub)
    if pub is None:
        pub = Publication(protocol=protocol)
    pub.version, pub.withheld, pub.published = version, withheld, True
    pub.updated_at = timezone.now()
    pub.save()
    _record(version, actor, old, _state(pub), reason)
    return pub


def unpublish(protocol: Protocol, actor: AbstractBaseUser, reason: str) -> Publication:
    _need_reason(reason)
    pub = (
        Publication.objects.filter(protocol=protocol, published=True)
        .select_related("version")
        .first()
    )
    if pub is None:
        raise ValidationError({"detail": "This protocol is not published."})
    old = _state(pub)
    pub.published = False
    pub.updated_at = timezone.now()
    pub.save()
    _record(pub.version, actor, old, _state(pub), reason)
    return pub


def _public_item(facet: str, item: dict[str, Any]) -> dict[str, Any]:
    if facet == "interventions":
        return {k: v for k, v in item.items() if k not in PRIVATE_INTERVENTION_KEYS}
    return dict(item)


def _public_lineage(protocol: Protocol) -> dict[str, Any] | None:
    """Shown only while the source is itself published, so a fork never reveals a source that
    was taken down."""
    version = protocol.forked_from_version
    if (
        version is None
        or not Publication.objects.filter(
            protocol_id=protocol.forked_from_protocol_id, published=True
        ).exists()
    ):
        return None
    return {"protocol": protocol.forked_from_protocol_id, "version": version.number}


def public_data(pub: Publication) -> dict[str, Any]:
    """The public view of the pinned version: no owner data, no withheld or genomic item."""
    snap = pub.version.snapshot
    out: dict[str, Any] = {
        "id": pub.protocol_id,
        "title": snap["title"],
        "origin": pub.protocol.origin,
        "level": snap["level"],
        "state": pub.protocol.state,
        "published_version": pub.version.number,
        "cycles": snap["cycles"],
        "goals": snap["goals"],
    }
    out["forked_from"] = _public_lineage(pub.protocol)
    for facet in ITEM_FACETS:
        out[facet] = [
            _public_item(facet, item)
            for i, item in enumerate(snap[facet])
            if f"{facet}[{i}]" not in pub.withheld and not item.get("genomic")
        ]
    return out
