# SPDX-License-Identifier: AGPL-3.0-or-later
# biohack.it — open-source biohacking platform
# Copyright (C) HackingBiology 2026 — https://biohack.it
# Full license text: https://www.gnu.org/licenses/agpl-3.0.html

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    # Auth and app API routes are added in TG2/TG3 as the apps are created.
    # Placeholder so that /api/ returns a 404 rather than a 500 on boot.
    path("api/", include("biohackit.api_urls")),
]
