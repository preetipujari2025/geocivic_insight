from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('locate/', views.locate_view, name='locate'),
    path('search/', views.search_view, name='search'),
]
