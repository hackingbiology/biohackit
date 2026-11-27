# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubstanceListCreateView.as_view()),
    path("<int:pk>/", views.SubstanceDetailView.as_view()),
    path("<int:pk>/codes/", views.CodeCreateView.as_view()),
    path("<int:pk>/codes/<int:code_id>/", views.CodeDetailView.as_view()),
]
