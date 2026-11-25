# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("loinc/", views.LoincSearchView.as_view()),
    path("biomarkers/<str:loinc_code>/ranges/", views.BiomarkerRangesView.as_view()),
]
