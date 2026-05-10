from django.contrib.gis import admin
from db.models import Constituency, MLA, MP, ElectionResult


@admin.register(Constituency)
class ConstituencyAdmin(admin.GISModelAdmin):
    list_display = ['name', 'district', 'created_at']
    search_fields = ['name', 'district']


@admin.register(MLA)
class MLAAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'constituency', 'term_start']
    search_fields = ['name', 'party']


@admin.register(MP)
class MPAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'lok_sabha_seat', 'term_start']


@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = [
        'constituency',
        'year',
        'winner_name',
        'winner_party',
        'turnout_percent',
    ]
    list_filter = ['year']
