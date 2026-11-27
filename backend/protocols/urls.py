# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProtocolListCreateView.as_view()),
    path("<int:pk>/", views.ProtocolDetailView.as_view()),
    path("<int:pk>/versions/", views.VersionListView.as_view()),
    path("<int:pk>/versions/<int:number>/", views.VersionDetailView.as_view()),
    path("<int:pk>/diff/", views.DiffView.as_view()),
]
