import json

from django.contrib.gis.geos import Point

from db.models import Constituency, MLA, MP


def get_constituency(lat, lng):
    try:
        point = Point(lng, lat)  # GIS convention: longitude first, latitude second

        # Query the constituency whose boundary contains the point
        try:
            constituency = Constituency.objects.get(boundary__contains=point)
        except Constituency.DoesNotExist:
            return None
        except Constituency.MultipleObjectsReturned:
            constituency = Constituency.objects.filter(boundary__contains=point).first()

        if constituency is None:
            return None

        # Get the most recent MLA and MP by term start year
        mla = constituency.mla.order_by('-term_start').first()
        mp = constituency.mp.order_by('-term_start').first()

        return {
            "constituency_id": constituency.id,
            "name": constituency.name,
            "district": constituency.district,
            "geojson": json.loads(constituency.boundary.geojson),
            "mla_id": mla.id if mla else None,
            "mla_name": mla.name if mla else "Data not available",
            "mla_party": mla.party if mla else "",
            "mla_education": mla.education if mla else "",
            "mla_achievements_raw": mla.achievements_raw if mla else "",
            "mp_id": mp.id if mp else None,
            "mp_name": mp.name if mp else "Data not available",
            "mp_party": mp.party if mp else "",
        }

    except Exception as e:
        print(f"[get_constituency] Error: {e}")
        return None
