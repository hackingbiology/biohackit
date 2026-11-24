# SPDX-License-Identifier: AGPL-3.0-or-later
"""Response middleware shared by all apps."""

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class NoIndexMiddleware:
    """Add `X-Robots-Tag: noindex` to every response when settings.NOINDEX."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if settings.NOINDEX:
            response["X-Robots-Tag"] = "noindex"
        return response
