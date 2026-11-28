# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("", views.PublicProtocolListView.as_view()),
    path("<int:pk>/", views.PublicProtocolDetailView.as_view()),
]
