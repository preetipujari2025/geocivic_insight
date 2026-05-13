from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Constituency


class ConstituencySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Constituency
        geo_field = "boundary"
        fields = ("id", "name", "district")
