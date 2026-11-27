# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubstanceListCreateView.as_view()),
    path("resolve/", views.ResolveNameView.as_view()),
    path("extractions/", views.ExtractionCreateView.as_view()),
    path("extractions/<int:extraction_id>/", views.ExtractionDetailView.as_view()),
    path(
        "extractions/<int:extraction_id>/items/<int:item_id>/decide/",
        views.ExtractionDecideView.as_view(),
    ),
    path(
        "extractions/<int:extraction_id>/commit/", views.ExtractionCommitView.as_view()
    ),
    path("synonyms/", views.SynonymListCreateView.as_view()),
    path("synonyms/<int:synonym_id>/approve/", views.SynonymApproveView.as_view()),
    path("review-queue/", views.ReviewQueueView.as_view()),
    path("review-queue/<int:item_id>/resolve/", views.ReviewItemResolveView.as_view()),
    path("review-queue/<int:item_id>/reject/", views.ReviewItemRejectView.as_view()),
    path("<int:pk>/", views.SubstanceDetailView.as_view()),
    path("<int:pk>/codes/", views.CodeCreateView.as_view()),
    path("<int:pk>/codes/<int:code_id>/", views.CodeDetailView.as_view()),
]
