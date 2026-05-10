"""
load_boundaries.py – Standalone script to import constituency GeoJSON
boundary data into the PostGIS database.

Usage:
    python db/scripts/load_boundaries.py                         # uses default fixture path
    python db/scripts/load_boundaries.py path/to/custom.geojson  # custom file

Compatibility: Windows · Python 3.10+ · Django 4.2 · PostGIS · GeoDjango
"""

# ---------------------------------------------------------------------------
# 1. Bootstrap Django before any ORM / model imports
# ---------------------------------------------------------------------------
import django
import os
import sys
import json
import time
from pathlib import Path

# Resolve the project root (two levels up from this script)
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
django.setup()

# ---------------------------------------------------------------------------
# 2. Django-dependent imports (safe only after django.setup())
# ---------------------------------------------------------------------------
from db.models import Constituency                       # noqa: E402
from django.contrib.gis.geos import GEOSGeometry         # noqa: E402
from django.db import transaction                         # noqa: E402

# ---------------------------------------------------------------------------
# Default fixture path (relative to the project root)
# ---------------------------------------------------------------------------
DEFAULT_GEOJSON_PATH = os.path.join(
    _PROJECT_ROOT, 'db', 'fixtures', 'constituencies.json'
)


# ---------------------------------------------------------------------------
# 3. Core loader
# ---------------------------------------------------------------------------
def load_from_geojson(filepath: str) -> None:
    """
    Parse a GeoJSON FeatureCollection and upsert each feature into the
    ``Constituency`` table.

    * Reads the file as UTF-8 to handle multilingual constituency names.
    * Handles both ``Polygon`` and ``MultiPolygon`` geometry types
      (``MultiPolygon`` is coerced to ``Polygon`` via the largest component
      when the model field is ``PolygonField``).
    * Wraps all writes in an atomic transaction so a partial failure
      does not leave the database in an inconsistent state — individual
      feature errors are caught and logged without aborting the batch.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to a GeoJSON file whose root object is
        a ``FeatureCollection``.
    """
    resolved_path = Path(filepath).resolve()

    if not resolved_path.is_file():
        print(f"[ERROR] File not found: {resolved_path}")
        sys.exit(1)

    # --- Read & parse -------------------------------------------------------
    with open(resolved_path, encoding='utf-8') as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Invalid JSON in {resolved_path}: {exc}")
            sys.exit(1)

    features = data.get('features')
    if not features:
        print("[WARN] No features found in the GeoJSON file.")
        return

    print(f"[INFO] Found {len(features)} feature(s) to process.\n")

    loaded = 0
    skipped = 0

    # --- Process features ---------------------------------------------------
    with transaction.atomic():
        for idx, feature in enumerate(features, start=1):
            try:
                properties = feature.get('properties', {})

                # Constituency name — try common GeoJSON property keys
                name = (
                    properties.get('CONSTITUENCY_NAME')
                    or properties.get('name')
                )
                if not name:
                    print(
                        f"  [{idx}] SKIP – no constituency name found in "
                        f"properties: {list(properties.keys())}"
                    )
                    skipped += 1
                    continue

                # District
                district = (
                    properties.get('DISTRICT_NAME')
                    or properties.get('district', 'Unknown')
                )

                # Geometry → GEOSGeometry
                raw_geometry = feature.get('geometry')
                if not raw_geometry:
                    print(f"  [{idx}] SKIP – '{name}' has no geometry.")
                    skipped += 1
                    continue

                geometry_str = json.dumps(raw_geometry)
                boundary = GEOSGeometry(geometry_str)

                # If the model expects a Polygon but the GeoJSON supplies a
                # MultiPolygon, extract the largest component polygon so the
                # insert doesn't fail with a geometry-type mismatch.
                if boundary.geom_type == 'MultiPolygon':
                    boundary = max(boundary, key=lambda poly: poly.area)

                # Upsert
                _obj, created = Constituency.objects.update_or_create(
                    name=name,
                    defaults={
                        'district': district,
                        'boundary': boundary,
                    },
                )

                action = 'Created' if created else 'Updated'
                print(f"  [{idx}] {action}: {name}  (district: {district})")
                loaded += 1

            except Exception as e:
                print(f"  [{idx}] Error loading feature: {e}")
                skipped += 1

    # --- Summary ------------------------------------------------------------
    print(
        f"\n{'─' * 50}"
        f"\n  Loaded : {loaded}"
        f"\n  Skipped: {skipped}"
        f"\n  Total  : {loaded + skipped}"
        f"\n{'─' * 50}"
    )


# ---------------------------------------------------------------------------
# 4. CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_GEOJSON_PATH

    print(f"Loading from {filepath}")
    print(f"{'─' * 50}\n")

    start = time.perf_counter()
    load_from_geojson(filepath)
    elapsed = time.perf_counter() - start

    print(f"\nDone. Total constituencies: {Constituency.objects.count()}")
    print(f"Elapsed: {elapsed:.2f}s")
