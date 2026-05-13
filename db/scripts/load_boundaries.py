"""
load_boundaries.py – Load Karnataka assembly constituency boundaries
from the India_AC shapefile into the PostGIS database.

Usage (from Django shell):
    exec(open("db/scripts/load_boundaries.py").read())

Usage (standalone):
    python db/scripts/load_boundaries.py

Compatibility: Windows · Python 3.10+ · Django 4.2 · PostGIS · GeoDjango
"""

import os
import sys
import time
import re
from pathlib import Path


def _find_project_root() -> Path:
    """
    Locate the Django project root by searching for manage.py.
    Works under both `python script.py` and exec() from Django shell.
    """
    try:
        candidate = Path(__file__).resolve().parent
        for _ in range(5):
            if (candidate / 'manage.py').is_file():
                return candidate
            candidate = candidate.parent
    except NameError:
        pass

    candidate = Path(os.getcwd()).resolve()
    for _ in range(5):
        if (candidate / 'manage.py').is_file():
            return candidate
        candidate = candidate.parent

    return Path(os.getcwd()).resolve()


_PROJECT_ROOT = _find_project_root()

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')

import django  # noqa: E402
try:
    django.setup()
except RuntimeError:
    pass  # Already set up inside Django shell

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon  # noqa: E402
from django.db import transaction                                 # noqa: E402
from db.models import Constituency                               # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SHP_PATH  = _PROJECT_ROOT / 'db' / 'data' / 'India_AC.shp'

KARNATAKA_KEYS = ('ST_NAME', 'STATE_NAME', 'STATE', 'St_Name', 'state_name', 'state')
INVALID_NAMES  = {'nan', 'none', '', 'n/a'}


def _is_karnataka(row_dict: dict) -> bool:
    for key in KARNATAKA_KEYS:
        val = row_dict.get(key, '')
        if val and 'karnataka' in str(val).strip().lower():
            return True
    return False


def _pick_name(row_dict: dict) -> str:
    for key in ('AC_NAME', 'CONSTITUENCY', 'CONST_NAME', 'NAME', 'Ac_Name', 'ac_name', 'name'):
        val = row_dict.get(key, '')
        if val and str(val).strip():
            return str(val).strip()
    return ''


def _clean_name(raw: str) -> str:
    """Title-case, normalise SC/ST tags."""
    name = re.sub(r'\(\s*sc\s*\)', '(SC)', raw.strip(), flags=re.IGNORECASE)
    name = re.sub(r'\(\s*st\s*\)', '(ST)', name, flags=re.IGNORECASE)
    base = re.sub(r'\s*\((SC|ST)\)\s*$', '', name, flags=re.IGNORECASE).strip().title()
    tag  = re.search(r'\((SC|ST)\)\s*$', name, flags=re.IGNORECASE)
    return f"{base} ({tag.group(1).upper()})" if tag else base


def _pick_district(row_dict: dict) -> str:
    for key in ('DIST_NAME', 'DISTRICT', 'DT_NAME', 'dist_name', 'district'):
        val = row_dict.get(key, '')
        if val and str(val).strip():
            return str(val).strip().title()
    return 'Unknown'


def _to_multipolygon(geom: GEOSGeometry) -> MultiPolygon:
    if geom.geom_type == 'MultiPolygon':
        return geom
    if geom.geom_type == 'Polygon':
        return MultiPolygon(geom)
    raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def load_karnataka_constituencies() -> None:
    try:
        import geopandas as gpd
    except ImportError:
        print("[ERROR] geopandas not installed. Run: pip install geopandas")
        return

    shp = SHP_PATH.resolve()
    if not shp.is_file():
        print(f"[ERROR] Shapefile not found: {shp}")
        return

    print(f"[INFO] Reading: {shp}")
    gdf = gpd.read_file(shp)

    if gdf.crs is None:
        print("[WARN] CRS not set; assuming EPSG:4326.")
    elif gdf.crs.to_epsg() != 4326:
        print(f"[INFO] Reprojecting {gdf.crs} → EPSG:4326")
        gdf = gdf.to_crs(epsg=4326)

    karnataka_rows = [
        (idx, row) for idx, row in gdf.iterrows()
        if _is_karnataka(row.to_dict())
    ]
    print(f"[INFO] Karnataka rows in shapefile: {len(karnataka_rows)}\n")

    seen   = set()   # normalised names already inserted
    loaded = 0
    skipped = 0

    with transaction.atomic():
        for seq, (_, row) in enumerate(karnataka_rows, start=1):
            d = row.to_dict()
            try:
                raw_name = _pick_name(d)
                if not raw_name or raw_name.strip().lower() in INVALID_NAMES:
                    print(f"  [{seq:>3}] SKIP – invalid name: {repr(raw_name)}")
                    skipped += 1
                    continue

                name     = _clean_name(raw_name)
                norm_key = re.sub(r'[^a-z0-9]', '', name.lower())

                if norm_key in seen:
                    print(f"  [{seq:>3}] DUP  – skipping duplicate: {name}")
                    skipped += 1
                    continue
                seen.add(norm_key)

                district = _pick_district(d)

                raw_geom = row.geometry
                if raw_geom is None or raw_geom.is_empty:
                    print(f"  [{seq:>3}] SKIP – {name!r} has no geometry.")
                    skipped += 1
                    continue

                geos_geom = GEOSGeometry(raw_geom.wkb_hex, srid=4326)
                boundary  = _to_multipolygon(geos_geom)

                _obj, created = Constituency.objects.update_or_create(
                    name=name,
                    defaults={'district': district, 'boundary': boundary},
                )

                action = 'Created' if created else 'Updated'
                print(f"  [{seq:>3}] {action}: {name}  ({district})")
                loaded += 1

            except Exception as exc:
                print(f"  [{seq:>3}] ERROR – {exc}")
                skipped += 1

    total_in_db = Constituency.objects.count()
    print(
        f"\n{'─' * 55}"
        f"\n  Loaded  : {loaded}"
        f"\n  Skipped : {skipped}"
        f"\n  Total in DB: {total_in_db}"
        f"\n{'─' * 55}"
    )


_start = time.perf_counter()
load_karnataka_constituencies()
print(f"\nElapsed: {time.perf_counter() - _start:.2f}s")