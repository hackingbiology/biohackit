# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import lab_import, views

urlpatterns = [
    path("reports/", views.LabReportCreateView.as_view()),
    path("reports/<int:pk>/", views.LabReportDetailView.as_view()),
    path("reports/<int:pk>/fhir/", views.LabReportFhirView.as_view()),
    path("reports/<int:pk>/phenoage/", views.LabReportPhenoAgeView.as_view()),
    path("results/<int:pk>/validation/", views.LabResultValidationView.as_view()),
    path("imports/csv/preview/", lab_import.CsvPreviewView.as_view()),
    path("imports/csv/confirm/", lab_import.CsvConfirmView.as_view()),
]
