import json

# GIS imports temporarily disabled for Windows compatibility
# from django.contrib.gis.geos import Point

# Temporarily comment out model imports to avoid GIS dependencies
# from db.models import Constituency, MLA, MP


def get_constituency(lat, lng):

    # Mahadevapura area
    if 12.99 <= lat <= 13.02 and 77.68 <= lng <= 77.72:
        return {
            "constituency_id": 1,
            "name": "Mahadevapura",
            "district": "Bangalore Urban",
            "geojson": {
                "type": "Polygon",
                "coordinates": [[[77.68, 12.99], [77.72, 12.99],
                                 [77.72, 13.02], [77.68, 13.02],
                                 [77.68, 12.99]]]
            },
            "mla_id": 1,
            "mla_name": "Aravind Limbavali",
            "mla_party": "BJP",
            "mla_achievements_raw": "Built 10 schools. Inaugurated new hospital.",
            "mp_id": 1,
            "mp_name": "PC Mohan",
            "mp_party": "BJP"
        }

    # Shivajinagar area
    elif 12.98 <= lat <= 13.00 and 77.59 <= lng <= 77.62:
        return {
            "constituency_id": 2,
            "name": "Shivajinagar",
            "district": "Bangalore Urban",
            "geojson": {
                "type": "Polygon",
                "coordinates": [[[77.59, 12.98], [77.62, 12.98],
                                 [77.62, 13.00], [77.59, 13.00],
                                 [77.59, 12.98]]]
            },
            "mla_id": 2,
            "mla_name": "Rizwan Arshad",
            "mla_party": "INC",
            "mla_achievements_raw": "Improved roads and schools.",
            "mp_id": 1,
            "mp_name": "PC Mohan",
            "mp_party": "BJP"
        }

    # Outside all constituencies
    return None