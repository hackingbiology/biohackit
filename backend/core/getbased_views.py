# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only preview of a get-based archive (X01 part 2a). Stores nothing: no report, no
result, no retained original. The same authentication as the CSV import (Q86)."""

from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from .getbased_import import GetbasedImportError, build_preview

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_PROFILE_ID_CHARS = 200


class GetbasedPreviewView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST multipart `file` and optional `profile_id`: the preview, or the profile ids
    to choose from. 400 for an unreadable or unsupported file or an unknown profile."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "Send the get-based export as 'file'."})
        if upload.size > MAX_FILE_BYTES:
            raise ValidationError(
                {
                    "file": f"The file is larger than {MAX_FILE_BYTES // (1024 * 1024)} MiB."
                }
            )
        profile_id = request.data.get("profile_id")
        if profile_id is not None and (
            not isinstance(profile_id, str) or len(profile_id) > MAX_PROFILE_ID_CHARS
        ):
            raise ValidationError({"profile_id": "Send one profile id as text."})
        try:
            return Response(build_preview(upload.read(), profile_id))
        except GetbasedImportError as exc:
            raise ValidationError({"file": str(exc)}) from exc
