"""
One-time utility: reads India_AC.shp, extracts Karnataka constituencies,
deduplicates, cleans names, and writes db/fixtures/constituencies.json.
Run from project root: venv\Scripts\python.exe db/scripts/export_constituencies_json.py
"""
import json
import re
import sys
from pathlib import Path

try:
    import geopandas as gpd
except ImportError:
    sys.exit("[ERROR] geopandas not installed. Run: pip install geopandas")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SHP_PATH     = PROJECT_ROOT / "db" / "data" / "India_AC.shp"
OUT_PATH     = PROJECT_ROOT / "db" / "fixtures" / "constituencies.json"

KARNATAKA_KEYS = ("ST_NAME", "STATE_NAME", "STATE", "St_Name", "state_name", "state")

def is_karnataka(row):
    for k in KARNATAKA_KEYS:
        v = row.get(k, "")
        if v and "karnataka" in str(v).strip().lower():
            return True
    return False

def pick_name(row):
    for k in ("AC_NAME", "CONSTITUENCY", "CONST_NAME", "NAME", "Ac_Name", "ac_name", "name"):
        v = row.get(k, "")
        if v and str(v).strip():
            return str(v).strip()
    return ""

def pick_district(row):
    for k in ("DIST_NAME", "DISTRICT", "DT_NAME", "dist_name", "district"):
        v = row.get(k, "")
        if v and str(v).strip():
            return str(v).strip().title()
    return "Unknown"

def clean_name(raw: str) -> str:
    """
    Produce a clean, human-readable constituency name:
    - Title-case
    - Normalize SC/ST tags: keep them in parentheses, upper-cased → (SC) / (ST)
    - Strip leading/trailing whitespace
    - Remove clearly invalid entries
    """
    name = raw.strip()
    # Normalise SC/ST suffixes to consistent format
    name = re.sub(r'\(\s*sc\s*\)', '(SC)', name, flags=re.IGNORECASE)
    name = re.sub(r'\(\s*st\s*\)', '(ST)', name, flags=re.IGNORECASE)
    # Title-case everything except the tag
    base = re.sub(r'\s*\((SC|ST)\)\s*$', '', name, flags=re.IGNORECASE)
    tag  = re.search(r'\((SC|ST)\)\s*$', name, flags=re.IGNORECASE)
    base = base.strip().title()
    if tag:
        name = f"{base} ({tag.group(1).upper()})"
    else:
        name = base
    return name

print(f"Reading: {SHP_PATH}")
gdf = gpd.read_file(SHP_PATH)
print(f"Total rows in shapefile: {len(gdf)}")
print(f"Columns: {list(gdf.columns)}")

karnataka = [(i, row) for i, row in gdf.iterrows() if is_karnataka(row.to_dict())]
print(f"Karnataka rows found: {len(karnataka)}")

seen_normalized = {}   # normalized_key → first entry
results = []

INVALID = {"nan", "none", "", "n/a"}

for _, row in karnataka:
    d = row.to_dict()
    raw_name = pick_name(d)
    if not raw_name or raw_name.strip().lower() in INVALID:
        print(f"  SKIP invalid name: {repr(raw_name)}")
        continue

    name     = clean_name(raw_name)
    district = pick_district(d)

    # Deduplicate by normalized key (no spaces, lower, no punctuation)
    norm_key = re.sub(r'[^a-z0-9]', '', name.lower())
    if norm_key in seen_normalized:
        print(f"  DUP  skipped: {name!r}  (already have: {seen_normalized[norm_key]!r})")
        continue

    seen_normalized[norm_key] = name
    results.append({"name": name, "district": district})

results.sort(key=lambda x: x["name"])

print(f"\nUnique constituencies: {len(results)}")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Written to: {OUT_PATH}")
