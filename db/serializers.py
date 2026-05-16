from rest_framework import serializers
from .models import MLA, MP, Constituency


class ConstituencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituency
        fields = "__all__"


class MLASerializer(serializers.ModelSerializer):
    constituency = ConstituencySerializer(read_only=True)

    class Meta:
        model = MLA
        fields = "__all__"


class MPSerializer(serializers.ModelSerializer):
    constituency_name = serializers.CharField(
        source='lok_sabha_seat', read_only=True
    )

    class Meta:
        model = MP
        fields = [
            'id',
            'name',
            'party',
            'lok_sabha_seat',
            'term_start',
            'term_end',
            'constituency_name',
        ]
