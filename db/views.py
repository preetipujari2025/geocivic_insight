from rest_framework import generics

from .models import MLA, MP, Constituency
from .serializers import MLASerializer, MPSerializer, ConstituencySerializer


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
# MP APIs
# =========================

class MPListView(generics.ListAPIView):
    queryset = MP.objects.select_related('constituency').all()
    serializer_class = MPSerializer


class MPDetailView(generics.RetrieveAPIView):
    queryset = MP.objects.select_related('constituency').all()
    serializer_class = MPSerializer


# =========================
# Constituency APIs
# =========================

class ConstituencyListView(generics.ListAPIView):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer


class ConstituencyDetailView(generics.RetrieveAPIView):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer