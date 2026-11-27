# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import getbased_views, lab_import, views

urlpatterns = [
    path("completeness/", views.LabCompletenessView.as_view()),
    path("reports/", views.LabReportCreateView.as_view()),
    path("reports/<int:pk>/", views.LabReportDetailView.as_view()),
    path("reports/<int:pk>/fhir/", views.LabReportFhirView.as_view()),
    path("reports/<int:pk>/omop/", views.LabReportOmopView.as_view()),
    path("reports/<int:pk>/calculated/", views.LabReportCalculatedView.as_view()),
    path("reports/<int:pk>/phenoage/", views.LabReportPhenoAgeView.as_view()),
    path("results/<int:pk>/convert/", views.LabResultConvertView.as_view()),
    path("results/<int:pk>/ranges/", views.LabResultRangesView.as_view()),
    path("results/<int:pk>/validation/", views.LabResultValidationView.as_view()),
    path("imports/csv/preview/", lab_import.CsvPreviewView.as_view()),
    path("imports/csv/confirm/", lab_import.CsvConfirmView.as_view()),
    path("imports/getbased/preview/", getbased_views.GetbasedPreviewView.as_view()),
]
