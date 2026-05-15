from rest_framework import serializers
from .models import MLA, Constituency


class ConstituencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituency
        fields = "__all__"


class MLASerializer(serializers.ModelSerializer):
    constituency = ConstituencySerializer(read_only=True)

    class Meta:
        model = MLA
        fields = "__all__"
