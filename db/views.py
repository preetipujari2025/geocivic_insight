from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point

from .models import MLA, MP, Constituency
from .serializers import MLASerializer, MPSerializer, ConstituencySerializer
from .loksabha_mapping import get_loksabha_seat


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


# =========================
# Find Representatives API
# =========================

class FindRepresentativesView(APIView):
    """
    GET /api/find-representatives/?lat=12.9716&lng=77.5946

    Accepts latitude + longitude, finds the Karnataka Assembly constituency
    polygon containing that point, and returns both the MLA and the MP.
    """

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')

        # ── Validate params ──────────────────────────────────
        if lat is None or lng is None:
            return Response(
                {"error": "Both 'lat' and 'lng' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            return Response(
                {"error": "'lat' and 'lng' must be valid numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Point-in-polygon lookup ──────────────────────────
        point = Point(lng, lat, srid=4326)

        constituency = Constituency.objects.filter(
            boundary__contains=point
        ).first()

        if not constituency:
            return Response(
                {"error": "Location is outside Karnataka or no matching constituency found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── Find MLA ─────────────────────────────────────────
        mla = constituency.mla.first()  # related_name='mla'
        mla_data = None
        if mla:
            mla_data = {
                "name": mla.name,
                "party": mla.party,
            }

        # ── Find MP via Lok Sabha mapping ────────────────────
        ls_seat = get_loksabha_seat(constituency.name)
        mp_data = None
        if ls_seat:
            mp = MP.objects.filter(lok_sabha_seat=ls_seat).first()
            if mp:
                mp_data = {
                    "name": mp.name,
                    "lok_sabha_seat": mp.lok_sabha_seat,
                    "party": mp.party,
                }

        # ── Build response ───────────────────────────────────
        return Response({
            "location": {
                "lat": lat,
                "lng": lng,
            },
            "constituency": {
                "name": constituency.name,
            },
            "mla": mla_data,
            "mp": mp_data,
        })