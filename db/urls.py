from django.urls import path

from .views import (
    MLAListView,
    MLADetailView,
    ConstituencyListView,
    ConstituencyDetailView,
)

urlpatterns = [
    # MLA APIs
    path('mlas/', MLAListView.as_view(), name='mla-list'),
    path('mlas/<int:pk>/', MLADetailView.as_view(), name='mla-detail'),

    # Constituency APIs
    path('constituencies/', ConstituencyListView.as_view(), name='constituency-list'),
    path('constituencies/<int:pk>/', ConstituencyDetailView.as_view(), name='constituency-detail'),
]