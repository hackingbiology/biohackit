# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("reports/", views.LabReportCreateView.as_view()),
    path("reports/<int:pk>/", views.LabReportDetailView.as_view()),
]
