from django.urls import path

from .views import (
    MLAListView,
    MLADetailView,
    MPListView,
    MPDetailView,
    ConstituencyListView,
    ConstituencyDetailView,
    FindRepresentativesView,
)

urlpatterns = [
    # MLA APIs
    path('mlas/', MLAListView.as_view(), name='mla-list'),
    path('mlas/<int:pk>/', MLADetailView.as_view(), name='mla-detail'),

    # MP APIs
    path('mps/', MPListView.as_view(), name='mp-list'),
    path('mps/<int:pk>/', MPDetailView.as_view(), name='mp-detail'),

    # Constituency APIs
    path('constituencies/', ConstituencyListView.as_view(), name='constituency-list'),
    path('constituencies/<int:pk>/', ConstituencyDetailView.as_view(), name='constituency-detail'),

    # Representative Lookup API
    path('find-representatives/', FindRepresentativesView.as_view(), name='find-representatives'),
]