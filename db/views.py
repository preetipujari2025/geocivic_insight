from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Constituency
from .serializers import ConstituencySerializer


class ConstituencyListView(generics.ListAPIView):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer