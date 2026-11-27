# SPDX-License-Identifier: AGPL-3.0-or-later
"""Substance API (M03 TG-a): read for any signed-in user, write for staff only (Q114)."""

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.permissions import (  # type: ignore[import-untyped]  # DRF ships no stubs
    SAFE_METHODS,
    BasePermission,
    IsAuthenticated,
)
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from . import services
from .models import Substance, SubstanceCode


class StaffWritesOnly(BasePermission):  # type: ignore[misc]  # base is Any: DRF untyped
    message = "Only staff can create or edit substances."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.method in SAFE_METHODS or getattr(request.user, "is_staff", False)
        )


def _code_data(code: SubstanceCode) -> dict[str, Any]:
    return {
        "id": code.pk,
        "system": code.system,
        "code": code.code,
        "source": code.source,
        "fetched_on": code.fetched_on.isoformat(),
        "provisional": code.provisional,
    }


def _substance_data(substance: Substance) -> dict[str, Any]:
    return {
        "id": substance.pk,
        "name": substance.name,
        "substance_class": substance.substance_class,
        "class_source": substance.class_source,
        "class_fetched_on": (
            substance.class_fetched_on.isoformat()
            if substance.class_fetched_on
            else None
        ),
        "codes": [_code_data(c) for c in substance.codes.all()],
    }


def _body(request: Request) -> dict[str, Any]:
    if not isinstance(request.data, dict):
        raise ValidationError({"detail": "Send a JSON object."})
    return dict(request.data)


class _Base(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    permission_classes = [IsAuthenticated, StaffWritesOnly]


class SubstanceListCreateView(_Base):
    def get(self, request: Request) -> Response:
        rows = Substance.objects.prefetch_related("codes")
        return Response([_substance_data(s) for s in rows])

    def post(self, request: Request) -> Response:
        try:
            substance = services.create_substance(_body(request))
        except services.SubstanceError as exc:
            raise ValidationError(exc.errors) from None
        return Response(_substance_data(substance), status=status.HTTP_201_CREATED)


class SubstanceDetailView(_Base):
    def get(self, request: Request, pk: int) -> Response:
        return Response(_substance_data(get_object_or_404(Substance, pk=pk)))

    def patch(self, request: Request, pk: int) -> Response:
        substance = get_object_or_404(Substance, pk=pk)
        try:
            services.update_substance(substance, _body(request))
        except services.SubstanceError as exc:
            raise ValidationError(exc.errors) from None
        return Response(_substance_data(substance))


class CodeCreateView(_Base):
    def post(self, request: Request, pk: int) -> Response:
        substance = get_object_or_404(Substance, pk=pk)
        try:
            code = services.add_code(substance, _body(request))
        except services.SubstanceError as exc:
            raise ValidationError(exc.errors) from None
        return Response(_code_data(code), status=status.HTTP_201_CREATED)


class CodeDetailView(_Base):
    def patch(self, request: Request, pk: int, code_id: int) -> Response:
        code = get_object_or_404(SubstanceCode, pk=code_id, substance_id=pk)
        try:
            services.update_code(code, _body(request))
        except services.SubstanceError as exc:
            raise ValidationError(exc.errors) from None
        return Response(_code_data(code))
