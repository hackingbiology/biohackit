# SPDX-License-Identifier: AGPL-3.0-or-later
"""Substance API (M03 TG-a): read for any signed-in user, write for staff only (Q114)."""

from collections.abc import Callable
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.permissions import (  # type: ignore[import-untyped]  # DRF ships no stubs
    SAFE_METHODS,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from . import services, synonyms
from .models import (
    ReviewStatus,
    Substance,
    SubstanceCode,
    SubstanceReviewItem,
    SubstanceSynonym,
)


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


class _StaffBase(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    permission_classes = [IsAuthenticated, IsAdminUser]


def _synonym_data(synonym: SubstanceSynonym) -> dict[str, Any]:
    return {
        "id": synonym.pk,
        "substance": synonym.substance_id,
        "name": synonym.name,
        "language": synonym.language,
        "source": synonym.source,
        "reviewer": synonym.reviewer_id,
        "reviewed_at": synonym.reviewed_at.isoformat() if synonym.reviewed_at else None,
    }


def _item_data(item: SubstanceReviewItem) -> dict[str, Any]:
    return {
        "id": item.pk,
        "submitted_name": item.submitted_name,
        "language": item.language,
        "reason": item.reason,
        "candidate_substance_ids": item.candidate_substance_ids,
        "status": item.status,
        "created_at": item.created_at.isoformat(),
        "resolved_by": item.resolved_by_id,
        "resolved_substance": item.resolved_substance_id,
    }


def _run(call: Callable[[], Any]) -> Any:
    try:
        return call()
    except services.SubstanceError as exc:
        raise ValidationError(exc.errors) from None


class SynonymListCreateView(_StaffBase):
    def get(self, request: Request) -> Response:
        return Response([_synonym_data(s) for s in SubstanceSynonym.objects.all()])

    def post(self, request: Request) -> Response:
        synonym = _run(lambda: synonyms.create_synonym(_body(request)))
        return Response(_synonym_data(synonym), status=status.HTTP_201_CREATED)


class SynonymApproveView(_StaffBase):
    def post(self, request: Request, synonym_id: int) -> Response:
        synonym = get_object_or_404(SubstanceSynonym, pk=synonym_id)
        _run(lambda: synonyms.approve_synonym(synonym, request.user))
        return Response(_synonym_data(synonym))


class ReviewQueueView(_StaffBase):
    def get(self, request: Request) -> Response:
        wanted = request.query_params.get("status", ReviewStatus.OPEN)
        if wanted not in ReviewStatus.values:
            raise ValidationError({"status": "Use open, resolved or rejected."})
        rows = SubstanceReviewItem.objects.filter(status=wanted)
        return Response([_item_data(i) for i in rows])


class ReviewItemResolveView(_StaffBase):
    def post(self, request: Request, item_id: int) -> Response:
        item = get_object_or_404(SubstanceReviewItem, pk=item_id)
        body = _body(request)
        _run(lambda: synonyms.resolve_item(item, body.get("substance"), request.user))
        return Response(_item_data(item))


class ReviewItemRejectView(_StaffBase):
    def post(self, request: Request, item_id: int) -> Response:
        item = get_object_or_404(SubstanceReviewItem, pk=item_id)
        _run(lambda: synonyms.reject_item(item, request.user))
        return Response(_item_data(item))


class ResolveNameView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        body = _body(request)
        language = body.get("language")
        if language is not None and not isinstance(language, str):
            raise ValidationError({"language": "Enter text."})
        name = body.get("name")
        if not isinstance(name, str):
            raise ValidationError({"name": "Enter text."})
        result = _run(lambda: synonyms.resolve_name(name, language))
        substance = result.substance
        candidates = Substance.objects.filter(pk__in=result.candidate_ids)
        return Response(
            {
                "status": result.status,
                "reason": result.reason,
                "substance": _substance_data(substance) if substance else None,
                "codes": [_code_data(c) for c in substance.codes.all()]
                if substance
                else [],
                "review_item_id": result.review_item.pk if result.review_item else None,
                "candidates": (
                    [{"id": s.pk, "name": s.name} for s in candidates]
                    if request.user.is_staff and not substance
                    else []
                ),
            }
        )


class CodeDetailView(_Base):
    def patch(self, request: Request, pk: int, code_id: int) -> Response:
        code = get_object_or_404(SubstanceCode, pk=code_id, substance_id=pk)
        try:
            services.update_code(code, _body(request))
        except services.SubstanceError as exc:
            raise ValidationError(exc.errors) from None
        return Response(_code_data(code))
