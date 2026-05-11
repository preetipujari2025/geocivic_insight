import json

# GIS imports temporarily disabled for Windows compatibility
# from django.contrib.gis.geos import Point

# Temporarily comment out model imports to avoid GIS dependencies
# from db.models import Constituency, MLA, MP


def get_constituency(lat, lng):
    try:
        # Temporarily return mock data since GIS is not available
        # This will be replaced with real GIS queries once dependencies are resolved
        
        # For now, return a mock constituency for testing
        return {
            "constituency_id": 1,
            "name": "Mahadevapura",
            "district": "Bangalore Urban",
            "geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [77.68, 12.99],
                        [77.72, 12.99],
                        [77.72, 13.02],
                        [77.68, 13.02],
                        [77.68, 12.99],
                    ]
                ],
            },
            "mla_id": 1,
            "mla_name": "Mock MLA Name",
            "mla_party": "Mock Party",
            "mla_education": "B.E. Engineering",
            "mla_achievements_raw": "Built 10 schools. Inaugurated new hospital. Completed highway expansion. Launched youth training program.",
            "mp_id": 1,
            "mp_name": "Mock MP Name",
            "mp_party": "Mock Party",
        }
    except Exception as e:
        print(f"Error in get_constituency: {e}")
        return None
