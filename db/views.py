from rest_framework import generics

from .models import MLA, Constituency
from .serializers import MLASerializer, ConstituencySerializer


# =========================
# MLA APIs
# =========================

class MLAListView(generics.ListAPIView):
    queryset = MLA.objects.all()
    serializer_class = MLASerializer


class MLADetailView(generics.RetrieveAPIView):
    queryset = MLA.objects.all()
    serializer_class = MLASerializer


# =========================
# Constituency APIs
# =========================

class ConstituencyListView(generics.ListAPIView):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer


class ConstituencyDetailView(generics.RetrieveAPIView):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer