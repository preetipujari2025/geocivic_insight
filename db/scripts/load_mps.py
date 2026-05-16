"""
load_mps.py - Load verified 2024 Karnataka Lok Sabha MP data from CSV into PostGIS database.
Usage:  python db/scripts/load_mps.py
"""
import os, sys, csv, time
from pathlib import Path


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
from db.models import MP

CSV_PATH = _ROOT / 'db' / 'data' / 'karnataka_mps_clean.csv'


def read_csv(path):
    """Read MP CSV and return list of row dicts."""
    rows = []
    seen = set()
    dups = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            seat = row.get('lok_sabha_seat', '').strip()
            if not seat:
                continue
            if seat in seen:
                dups.append(seat)
                continue
            seen.add(seat)
            rows.append({
                'lok_sabha_seat': seat,
                'name': row.get('name', '').strip(),
                'party': row.get('party', '').strip(),
                'term_start': int(row.get('term_start', 2024)),
                'term_end': int(row.get('term_end', 2029)),
            })
    if dups:
        print(f"\n[WARN] {len(dups)} duplicate seat(s) in CSV (kept first):")
        for d in dups:
            print(f"  - {d}")
    return rows


def load_mps():
    print('=' * 60)
    print('  Karnataka Lok Sabha MP Loader (CSV -> PostGIS)')
    print('  Source: 2024 Lok Sabha Election Results')
    print('=' * 60)

    if not CSV_PATH.is_file():
        print(f"[ERROR] CSV not found: {CSV_PATH}")
        return

    # ── Step 1: Read CSV ──────────────────────────────────────
    print(f"\n[1/4] Reading CSV ...")
    csv_rows = read_csv(CSV_PATH)
    print(f"  Unique seats in CSV: {len(csv_rows)}")

    # ── Step 2: Clear old MP records ──────────────────────────
    print("\n[2/4] Clearing existing MP records ...")
    old_count = MP.objects.count()
    MP.objects.all().delete()
    print(f"  Deleted {old_count} old MP(s)")

    # ── Step 3: Create new MP records ─────────────────────────
    print("\n[3/4] Creating MP records ...\n")
    created = 0
    skipped = 0

    with transaction.atomic():
        for row in csv_rows:
            # Check for duplicate by lok_sabha_seat (safety)
            if MP.objects.filter(lok_sabha_seat=row['lok_sabha_seat']).exists():
                print(f"  [SKIP] {row['lok_sabha_seat']} already exists")
                skipped += 1
                continue

            MP.objects.create(
                constituency=None,  # Lok Sabha seats span multiple assembly constituencies
                name=row['name'],
                party=row['party'],
                lok_sabha_seat=row['lok_sabha_seat'],
                term_start=row['term_start'],
                term_end=row['term_end'],
            )
            created += 1
            print(f"  [{created:3d}] {row['lok_sabha_seat']:30s} <- {row['name']} ({row['party']})")

    # ── Step 4: Validation ────────────────────────────────────
    total = MP.objects.count()
    print(f"\n{'=' * 60}")
    print(f"  RESULTS")
    print(f"{'=' * 60}")
    print(f"  Created  : {created}")
    print(f"  Updated  : 0")
    print(f"  Skipped  : {skipped}")
    print(f"  Total MPs: {total}")
    print(f"{'=' * 60}")

    # Duplicate checks
    from django.db.models import Count
    dup_seats = MP.objects.values('lok_sabha_seat').annotate(cnt=Count('id')).filter(cnt__gt=1)
    dup_names = MP.objects.values('name').annotate(cnt=Count('id')).filter(cnt__gt=1)

    print(f"\n{'=' * 60}")
    print(f"  VALIDATION")
    print(f"{'=' * 60}")

    checks_passed = True

    if total == 28:
        print(f"  [OK] MP count = {total}")
    else:
        print(f"  [!!] Expected 28 MPs, found {total}")
        checks_passed = False

    if not dup_seats.exists():
        print(f"  [OK] No duplicate Lok Sabha seats")
    else:
        print(f"  [!!] Duplicate seats found!")
        for d in dup_seats:
            print(f"       - {d['lok_sabha_seat']} x{d['cnt']}")
        checks_passed = False

    if not dup_names.exists():
        print(f"  [OK] No duplicate MP names")
    else:
        print(f"  [!!] Duplicate MP names found!")
        checks_passed = False

    # Party breakdown
    parties = MP.objects.values('party').annotate(cnt=Count('id')).order_by('-cnt')
    print(f"\n  Party Breakdown:")
    for p in parties:
        print(f"    {p['party']:10s} : {p['cnt']}")

    # Manual validation
    print(f"\n{'-' * 60}")
    print(f"  MANUAL VALIDATION")
    print(f"{'-' * 60}")
    validations = {
        'Bangalore South': 'Tejasvi Surya',
        'Bangalore North': 'Shobha Karandlaje',
        'Bangalore Rural': 'Dr. C.N. Manjunath',
        'Mandya': 'H.D. Kumaraswamy',
    }
    for seat, expected_mp in validations.items():
        try:
            mp = MP.objects.get(lok_sabha_seat=seat)
            if expected_mp.lower() in mp.name.lower():
                print(f"  [OK] {seat:25s} -> {mp.name} ({mp.party})")
            else:
                print(f"  [!!] {seat:25s} -> {mp.name} (expected: {expected_mp})")
                checks_passed = False
        except MP.DoesNotExist:
            print(f"  [!!] {seat:25s} -> NOT FOUND!")
            checks_passed = False

    print(f"\n{'=' * 60}")
    if checks_passed:
        print(f"  ALL CHECKS PASSED")
    else:
        print(f"  SOME CHECKS FAILED - Review output above")
    print(f"{'=' * 60}")


_start = time.perf_counter()
load_mps()
print(f"\nElapsed: {time.perf_counter() - _start:.2f}s")
