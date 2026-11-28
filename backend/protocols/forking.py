# SPDX-License-Identifier: AGPL-3.0-or-later
"""Fork a published protocol (M03 TG-f part 2a). The copy is the caller's own Draft; it records
the source protocol and the exact published version, and copies only what the public view of that
version shows (no withheld item, no genomic item). The source is never changed."""

from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.shortcuts import get_object_or_404
from django.utils import timezone

from substances.models import Product

from .models import Origin, Protocol, Publication
from .publication import ITEM_FACETS


def _copied(facet: str, snapshot: dict[str, Any], withheld: list[str]) -> list[Any]:
    return [
        dict(item)
        for i, item in enumerate(snapshot[facet])
        if f"{facet}[{i}]" not in withheld and not item.get("genomic")
    ]


def _own_products(actor: AbstractBaseUser, interventions: list[Any]) -> list[Any]:
    """A product belongs to its owner: the fork keeps `product_id` only for the forking user's
    own products and drops it (with the daily units tied to it) otherwise."""
    wanted = {i["product_id"] for i in interventions if i.get("product_id") is not None}
    own = set(
        Product.objects.filter(owner=actor, pk__in=wanted).values_list("pk", flat=True)
    )
    for item in interventions:
        if item.get("product_id") not in own:
            item.pop("product_id", None)
            item.pop("units_per_day", None)
    return interventions


def fork(actor: AbstractBaseUser, source_id: int) -> Protocol:
    """404 unless the source has an active publication (no hint that it exists otherwise)."""
    pub = get_object_or_404(
        Publication.objects.select_related("protocol", "version"),
        protocol_id=source_id,
        published=True,
    )
    snap = pub.version.snapshot
    items = {f: _copied(f, snap, pub.withheld) for f in ITEM_FACETS}
    return Protocol.objects.create(
        owner=actor,
        title=snap["title"],
        origin=Origin.COMMUNITY,
        level=snap["level"],
        tracked_since=timezone.localdate(),
        interventions=_own_products(actor, items["interventions"]),
        measures=items["measures"],
        forked_from_protocol=pub.protocol,
        forked_from_version=pub.version,
    )
