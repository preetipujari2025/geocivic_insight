"""
load_mlas.py - Load verified 2023 Karnataka MLA data from CSV into PostGIS database.
Usage:  python db/scripts/load_mlas.py
"""
import os, sys, csv, re, time
from pathlib import Path
from collections import OrderedDict

def _find_root():
    try:
        c = Path(__file__).resolve().parent
        for _ in range(5):
            if (c / 'manage.py').is_file(): return c
            c = c.parent
    except NameError: pass
    c = Path(os.getcwd()).resolve()
    for _ in range(5):
        if (c / 'manage.py').is_file(): return c
        c = c.parent
    return Path(os.getcwd()).resolve()

_ROOT = _find_root()
if str(_ROOT) not in sys.path: sys.path.insert(0, str(_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
import django
try: django.setup()
except RuntimeError: pass

from django.db import transaction
from db.models import MLA, Constituency

CSV_PATH = _ROOT / 'db' / 'data' / 'karnataka_mlas_clean.csv'

def normalize(name):
    """Normalize constituency name for matching: lowercase, strip SC/ST tags, remove non-alphanumeric."""
    s = name.strip().lower()
    s = re.sub(r'\s*\(\s*sc\s*\)\s*', '', s)
    s = re.sub(r'\s*\(\s*st\s*\)\s*', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def read_csv(path):
    """Read CSV and return OrderedDict keyed by normalized constituency name."""
    data = OrderedDict()
    dups = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            c = row.get('constituency', '').strip()
            if not c: continue
            key = normalize(c)
            if key in data:
                dups.append((c, data[key]['constituency']))
                continue
            data[key] = {
                'constituency': c,
                'name': row.get('name', '').strip(),
                'party': row.get('party', '').strip(),
                'education': row.get('education', '').strip(),
            }
    if dups:
        print(f"\n[WARN] {len(dups)} duplicate(s) in CSV (kept first):")
        for d, o in dups:
            print(f"  '{d}' dup of '{o}'")
    return data

def load_mlas():
    print('=' * 60)
    print('  Karnataka MLA Loader (CSV -> PostGIS)')
    print('  Source: 2023 Karnataka Assembly Election Results')
    print('=' * 60)

    if not CSV_PATH.is_file():
        print(f"[ERROR] CSV not found: {CSV_PATH}")
        return

    print(f"\n[1/4] Reading CSV ...")
    csv_data = read_csv(CSV_PATH)
    print(f"  Unique CSV rows: {len(csv_data)}")

    print("\n[2/4] Loading DB constituencies ...")
    all_const = list(Constituency.objects.all().order_by('name'))
    print(f"  Constituencies in DB: {len(all_const)}")
    if not all_const:
        print("[ERROR] No constituencies. Run load_boundaries.py first.")
        return

    db_lookup = {}
    for c in all_const:
        db_lookup[normalize(c.name)] = c

    print("\n[3/4] Clearing existing MLAs ...")
    old = MLA.objects.count()
    MLA.objects.all().delete()
    print(f"  Deleted {old} old MLA(s)")

    print("\n[4/4] Creating MLAs ...\n")
    created = 0
    skipped = 0
    unmatched_csv = []
    matched_db_norms = set()

    with transaction.atomic():
        for csv_norm, row in csv_data.items():
            db_const = db_lookup.get(csv_norm)

            if not db_const:
                unmatched_csv.append(row['constituency'])
                skipped += 1
                continue

            db_norm = normalize(db_const.name)
            if db_norm in matched_db_norms:
                skipped += 1
                continue
            matched_db_norms.add(db_norm)

            MLA.objects.create(
                constituency=db_const,
                name=row['name'],
                party=row['party'],
                education=row['education'],
                term_start=2023,
                term_end=2028,
                achievements_raw='',
                source_url='https://results.eci.gov.in/',
            )
            created += 1
            print(f"  [{created:3d}] {db_const.name:40s} <- {row['name']} ({row['party']})")

    total_m = MLA.objects.count()
    total_c = Constituency.objects.count()
    print(f"\n{'-'*60}")
    print(f"  Created (verified data)  : {created}")
    print(f"  Skipped (unmatched CSV)  : {skipped}")
    print(f"  Total MLAs in DB         : {total_m}")
    print(f"  Total Constituencies     : {total_c}")
    print(f"{'-'*60}")

    if unmatched_csv:
        print(f"\n[WARN] {len(unmatched_csv)} CSV names unmatched:")
        for n in sorted(unmatched_csv):
            print(f"  - {n}")

    unmatched_db = [c.name for c in all_const if normalize(c.name) not in matched_db_norms]
    if unmatched_db:
        print(f"\n[WARN] {len(unmatched_db)} DB constituencies have NO MLA:")
        for n in sorted(unmatched_db):
            print(f"  - {n}")

    # Duplicate checks
    from django.db.models import Count
    dup_mlas = MLA.objects.values('name').annotate(cnt=Count('id')).filter(cnt__gt=1)
    dup_const = MLA.objects.values('constituency').annotate(cnt=Count('id')).filter(cnt__gt=1)

    print(f"\n{'='*60}")
    print(f"  VALIDATION RESULTS")
    print(f"{'='*60}")

    checks_passed = True

    if total_m == 224:
        print(f"  [OK] MLA count = {total_m}")
    else:
        print(f"  [!!] Expected 224 MLAs, found {total_m}")
        checks_passed = False

    if total_c == 224:
        print(f"  [OK] Constituency count = {total_c}")
    else:
        print(f"  [!!] Expected 224 constituencies, found {total_c}")
        checks_passed = False

    if total_m == total_c:
        print(f"  [OK] MLA count matches constituency count")
    else:
        print(f"  [!!] MISMATCH: {total_m} MLAs vs {total_c} constituencies")
        checks_passed = False

    if not dup_const.exists():
        print(f"  [OK] No duplicate constituency assignments")
    else:
        print(f"  [!!] Duplicate constituency assignments found!")
        checks_passed = False

    # Mandatory manual validation
    print(f"\n{'-'*60}")
    print(f"  MANDATORY MANUAL VALIDATION")
    print(f"{'-'*60}")
    validations = {
        'Varuna': 'Siddaramaiah',
        'Kanakapura': 'D. K. Shivakumar',
        'Shiggaon': 'Basavaraj Bommai',
        'Mahadevapura': 'Manjula S',
    }
    for const_name, expected_mla in validations.items():
        try:
            mla = MLA.objects.get(constituency__name=const_name)
            if expected_mla.lower() in mla.name.lower():
                print(f"  [OK] {const_name:20s} -> {mla.name} ({mla.party})")
            else:
                print(f"  [!!] {const_name:20s} -> {mla.name} (expected: {expected_mla})")
                checks_passed = False
        except MLA.DoesNotExist:
            print(f"  [!!] {const_name:20s} -> NO MLA FOUND!")
            checks_passed = False

    print(f"\n{'='*60}")
    if checks_passed:
        print(f"  ALL CHECKS PASSED")
    else:
        print(f"  SOME CHECKS FAILED - Review output above")
    print(f"{'='*60}")

_start = time.perf_counter()
load_mlas()
print(f"\nElapsed: {time.perf_counter() - _start:.2f}s")