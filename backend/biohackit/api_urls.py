# SPDX-License-Identifier: AGPL-3.0-or-later
# biohack.it — open-source biohacking platform
# Copyright (C) HackingBiology 2026 — https://biohack.it
# Full license text: https://www.gnu.org/licenses/agpl-3.0.html


# Auth and resource endpoints are registered here by each app as they are
# built (TG2 adds accounts/auth, TG3 adds domain stubs, etc.).
from django.urls import include, path

urlpatterns: list = [
    path("", include("accounts.urls")),
    path("terminology/", include("terminology.urls")),
    path("labs/", include("core.urls")),
    path("protocols/", include("protocols.urls")),
]
