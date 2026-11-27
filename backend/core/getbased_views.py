# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only preview and confirm of a get-based archive (X01 parts 2a and 2b). The
preview stores nothing. The confirm parses the same upload again and stores one report
with its results and their provenance in one transaction; the original file is never
kept. The same authentication as the CSV import (Q86)."""

from typing import Any

from django.db import transaction
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from .getbased_import import (
    GetbasedImportError,
    build_confirm_plan,
    build_preview,
    store_plan,
)

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_PROFILE_ID_CHARS = 200


ORIGINAL_NOT_KEPT = (
    "the archive holds identity and other non-lab data, so it is not kept"
)


def _read_upload(request: Request) -> tuple[bytes, str | None]:
    """The upload bytes and the optional profile id, with the bounds shared by preview
    and confirm."""
    upload = request.FILES.get("file")
    if upload is None:
        raise ValidationError({"file": "Send the get-based export as 'file'."})
    if upload.size > MAX_FILE_BYTES:
        raise ValidationError(
            {"file": f"The file is larger than {MAX_FILE_BYTES // (1024 * 1024)} MiB."}
        )
    profile_id = request.data.get("profile_id")
    if profile_id is not None and (
        not isinstance(profile_id, str) or len(profile_id) > MAX_PROFILE_ID_CHARS
    ):
        raise ValidationError({"profile_id": "Send one profile id as text."})
    return upload.read(), profile_id


class GetbasedPreviewView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST multipart `file` and optional `profile_id`: the preview, or the profile ids
    to choose from. 400 for an unreadable or unsupported file or an unknown profile."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        raw, profile_id = _read_upload(request)
        try:
            return Response(build_preview(raw, profile_id))
        except GetbasedImportError as exc:
            raise ValidationError({"file": str(exc)}) from exc


class GetbasedConfirmView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST the same multipart `file` and `profile_id` as the preview. 400 listing the rows
    while any is not recognised (nothing stored); otherwise 201 with the new report id, the
    number stored and the rows left out. Every result is stored `entered`."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        raw, profile_id = _read_upload(request)
        try:
            plan = build_confirm_plan(raw, profile_id)
            if plan.not_recognised:
                return Response(
                    {
                        "detail": "Some rows are not recognised; nothing was stored. "
                        f"Rows: {len(plan.not_recognised)}",
                        "rows": plan.not_recognised,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not plan.candidates:
                raise ValidationError({"file": "The profile has no result to import."})
            with transaction.atomic():
                report = store_plan(plan, request.user)
        except GetbasedImportError as exc:
            raise ValidationError({"file": str(exc)}) from exc
        body: dict[str, Any] = {
            "report_id": report.pk,
            "stored_count": len(plan.candidates),
            "left_out": {
                "calculated": plan.left_out_calculated,
                "deleted": plan.left_out_deleted,
            },
            "original_retained": False,
            "original_not_retained_reason": ORIGINAL_NOT_KEPT,
        }
        return Response(body, status=status.HTTP_201_CREATED)
