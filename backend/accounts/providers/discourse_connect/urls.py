# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("discourse_connect/login/", views.login, name="discourse_connect_login"),
    path(
        "discourse_connect/callback/",
        views.callback,
        name="discourse_connect_callback",
    ),
]
