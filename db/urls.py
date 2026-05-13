from django.urls import path
from .views import ConstituencyListView

urlpatterns = [
    path("constituencies/", ConstituencyListView.as_view()),
]
