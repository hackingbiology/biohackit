# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProtocolListCreateView.as_view()),
    path("<int:pk>/", views.ProtocolDetailView.as_view()),
    path("<int:pk>/versions/", views.VersionListView.as_view()),
    path("<int:pk>/versions/<int:number>/", views.VersionDetailView.as_view()),
    path("<int:pk>/ingredient-totals/", views.IngredientTotalsView.as_view()),
    path("<int:pk>/publish/", views.PublishView.as_view()),
    path("<int:pk>/unpublish/", views.UnpublishView.as_view()),
    path("<int:pk>/diff/", views.DiffView.as_view()),
]
