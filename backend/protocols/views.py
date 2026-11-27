# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only protocol API (M03 TG-f part 1). Another user's protocol is a 404."""

from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from . import services
from .diffing import diff_snapshots
from .facets import is_per_weight, missing_in_draft
from .models import Protocol, ProtocolVersion, State

BACKFILL_NOTE = (
    "You can add past measurements and earlier changes as history if you remember them. "
    "This is invited, not required."
)


def _intervention_data(item: dict[str, Any]) -> dict[str, Any]:
    """The stored item exactly as stored, with the posology keys always present. A
    per-weight item has `absolute_dose: null`: nothing derives an absolute dose from it."""
    out = {
        **item,
        "basis": item.get("basis", "absolute"),
        "provenance": item.get("provenance", ""),
        "provenance_source": item.get("provenance_source", ""),
    }
    if is_per_weight(out):
        out["absolute_dose"] = None
    return out


def _protocol_data(protocol: Protocol) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": protocol.pk,
        "title": protocol.title,
        "state": protocol.state,
        "origin": protocol.origin,
        "level": protocol.level,
        "in_effect_since": protocol.in_effect_since.isoformat()
        if protocol.in_effect_since
        else None,
        "tracked_since": protocol.tracked_since.isoformat(),
        "history": protocol.history,
        "lineage_note": protocol.lineage_note,
        "interventions": [_intervention_data(i) for i in protocol.interventions],
        "cycles": protocol.cycles,
        "measures": protocol.measures,
        "goals": protocol.goals,
        "latest_version": protocol.versions.count() or None,
    }
    if protocol.state == State.DRAFT:
        data["missing"] = missing_in_draft(
            protocol.interventions, protocol.goals, protocol.measures, protocol.level
        )
    return data


def _version_data(version: ProtocolVersion) -> dict[str, Any]:
    return {
        "number": version.number,
        "created_at": version.created_at.isoformat(),
        "actor": version.actor_id,
        "reason": version.reason,
        "snapshot": version.snapshot,
        "events": [
            {
                "field": e.field,
                "old": e.old,
                "new": e.new,
                "timestamp": e.timestamp.isoformat(),
                "actor": e.actor_id,
                "reason": e.reason,
            }
            for e in version.events.all()
        ],
    }


def _body(request: Request) -> dict[str, Any]:
    if not isinstance(request.data, dict):
        raise ValidationError({"detail": "The body must be a JSON object."})
    return dict(request.data)


def _mine(request: Request, pk: int) -> Protocol:
    return get_object_or_404(Protocol, pk=pk, owner=request.user)


def _result(protocol: Protocol, version: ProtocolVersion | None) -> dict[str, Any]:
    data = _protocol_data(protocol)
    if version is not None:
        data["version"] = _version_data(version)
    return data


class ProtocolListCreateView(APIView):
    def get(self, request: Request) -> Response:
        protocols = Protocol.objects.filter(owner=request.user)
        return Response([_protocol_data(p) for p in protocols])

    def post(self, request: Request) -> Response:
        protocol, version = services.create(request.user, _body(request))
        data = _result(protocol, version)
        if protocol.in_effect_since is not None and version is not None:
            data["notes"] = [BACKFILL_NOTE]
        return Response(data, status=status.HTTP_201_CREATED)


class ProtocolDetailView(APIView):
    def get(self, request: Request, pk: int) -> Response:
        return Response(_protocol_data(_mine(request, pk)))

    def patch(self, request: Request, pk: int) -> Response:
        body = _body(request)
        reason = services.clean_reason(body.pop("reason", None))
        acknowledge = services.clean_acknowledge(body.pop("acknowledge", None))
        with transaction.atomic():
            protocol = get_object_or_404(
                Protocol.objects.select_for_update(), pk=pk, owner=request.user
            )
            fields = services.parse_fields(
                body, {*services.TRACKED, *services.DRAFT_ONLY}
            )
            version = services.edit(protocol, request.user, fields, reason, acknowledge)
        return Response(_result(protocol, version))


class VersionListView(APIView):
    def get(self, request: Request, pk: int) -> Response:
        versions = _mine(request, pk).versions.prefetch_related("events")
        return Response([_version_data(v) for v in versions])


class VersionDetailView(APIView):
    """Read-only on purpose: a created version has no update or delete route."""

    def get(self, request: Request, pk: int, number: int) -> Response:
        version = get_object_or_404(_mine(request, pk).versions, number=number)
        return Response(_version_data(version))


class DiffView(APIView):
    def get(self, request: Request, pk: int) -> Response:
        protocol = _mine(request, pk)
        numbers = []
        for name in ("from", "to"):
            raw = request.query_params.get(name, "")
            if not raw.isdecimal():
                raise ValidationError({name: "is required: a version number."})
            numbers.append(int(raw))
        old = get_object_or_404(protocol.versions, number=numbers[0])
        new = get_object_or_404(protocol.versions, number=numbers[1])
        result = diff_snapshots(
            old.snapshot, new.snapshot, f"v{old.number}", f"v{new.number}"
        )
        return Response({"from": old.number, "to": new.number, **result})
