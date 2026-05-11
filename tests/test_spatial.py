"""
test_spatial.py – Pytest suite for ``db.spatial.get_constituency()``.

These tests assume the database has been seeded with the three test
constituencies created by ``db/scripts/create_test_data.py``:

    • Mahadevapura  (Bangalore Urban)
    • Shivajinagar  (Bangalore Urban)
    • Mysuru Rural   (Mysuru)

Run:
    pytest tests/test_spatial.py -v

Compatibility: Windows · Python 3.10+ · Django 4.2 · PostGIS · GeoDjango
"""

# ---------------------------------------------------------------------------
# 1. Bootstrap Django before any ORM / model imports
# ---------------------------------------------------------------------------
import pytest
import os
import sys
import django

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
django.setup()

# ---------------------------------------------------------------------------
# 2. Django-dependent imports
# ---------------------------------------------------------------------------
from db.spatial import get_constituency  # noqa: E402


# ---------------------------------------------------------------------------
# 3. Tests
# ---------------------------------------------------------------------------

class TestMahadevapuraLookup:
    """Point-in-polygon lookup for the Mahadevapura constituency."""

    # Centre of the Mahadevapura test polygon
    LAT, LNG = 13.005, 77.70

    def test_mahadevapura_center(self):
        """A point at the centre of Mahadevapura must resolve correctly."""
        result = get_constituency(self.LAT, self.LNG)

        assert result is not None
        assert result['name'] == 'Mahadevapura'
        assert result['district'] == 'Bangalore Urban'
        assert 'geojson' in result
        assert result['mla_name'] != ''

    def test_return_has_all_required_keys(self):
        """The response dict must contain every key the API contract promises."""
        result = get_constituency(self.LAT, self.LNG)

        required_keys = [
            'constituency_id',
            'name',
            'district',
            'geojson',
            'mla_id',
            'mla_name',
            'mla_party',
            'mp_name',
            'mp_party',
        ]

        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_geojson_is_dict(self):
        """The ``geojson`` value must be a parsed dict with a valid type."""
        result = get_constituency(self.LAT, self.LNG)

        assert isinstance(result['geojson'], dict)
        assert 'type' in result['geojson']
        assert result['geojson']['type'] == 'Polygon'


class TestShivajinagar:
    """Point-in-polygon lookup for the Shivajinagar constituency."""

    def test_shivajinagar_center(self):
        """A point at the centre of Shivajinagar must resolve correctly."""
        result = get_constituency(12.995, 77.605)

        assert result is not None
        assert result['name'] == 'Shivajinagar'


class TestNoMatch:
    """Behaviour when the queried point falls outside all constituencies."""

    def test_point_outside_all_constituencies(self):
        """A point at (0, 0) — the Gulf of Guinea — must return None."""
        result = get_constituency(0.0, 0.0)

        assert result is None
