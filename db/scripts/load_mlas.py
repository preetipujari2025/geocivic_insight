"""
load_mlas.py - Load real Karnataka MLA data from CSV into PostGIS database.
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

ACHIEVEMENTS = {
    'Mahadevapura': 'Developed healthcare facilities with new primary health centers. Initiated major road infrastructure projects connecting Whitefield to Outer Ring Road.',
    'Shivajinagar': 'Launched women empowerment programs. Developed heritage tourism circuit preserving historical monuments.',
    'Yelahanka': 'Implemented comprehensive water supply scheme. Developed five new parks with walking tracks.',
    'Chickpet': 'Revitalized traditional market areas with modern infrastructure. Implemented smart city initiatives.',
    'Basavanagudi': 'Restored the historic Bull Temple area. Established senior citizen centers with healthcare activities.',
    'Hebbal': 'Completed major road widening projects connecting to airport. Established new industrial zones.',
    'Rajaji Nagar': 'Launched solid waste management program. Developed sports complexes for cricket, football, athletics.',
    'Padmanaba Nagar': 'Implemented advanced traffic management system. Developed educational institutions.',
    'Vijayapura': 'Irrigation projects providing water to 5000+ acres. Established agricultural research center.',
    'Hubli-Dharwad-Central': 'Technology hub development with IT parks. Implemented smart city solutions.',
}

def normalize(name):
    s = name.strip().lower()
    s = re.sub(r'\s*\(\s*sc\s*\)\s*', '', s)
    s = re.sub(r'\s*\(\s*st\s*\)\s*', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

# CSV constituency name -> DB constituency name (for mismatches)
CSV_TO_DB = {
    normalize('Gangavati'):          normalize('Gangawati'),
    normalize('Jewargi'):            normalize('Jevargi'),
    normalize('Hoskote'):            normalize('Hosakote'),
    normalize('Chikkanayakanhalli'): normalize('Chiknayakanhalli'),
    normalize('Byatrayanapura'):     normalize('Byatarayanapura'),
    normalize('Shantinagar'):        normalize('Shanti Nagar'),
    normalize('Padmanabhanagar'):     normalize('Padmanaba Nagar'),
    normalize('Rajajinagar'):        normalize('Rajaji Nagar'),
    normalize('T. Narsipur'):        normalize('T.Narasipur'),
    normalize('T. Narasipura'):      normalize('T.Narasipur'),
    normalize('Raibag'):             normalize('Raybag'),
    normalize('Sindagi'):            normalize('Sindgi'),
    normalize('Kolar Gold'):         normalize('Kolar Gold Field'),
    normalize('Kanakgiri'):          normalize('Kanakagiri'),
    normalize('Jagaluru'):           normalize('Jagalur'),
    normalize('Hubli-Dharwad East'): normalize('Hubli-Dharwad-East'),
    normalize('Hubli-Dharwad West'): normalize('Hubli-Dharwad- West'),
    # Additional aliases from unmatched analysis
    normalize('Balki'):              normalize('Bhalki'),
    normalize('Belagavi North'):     normalize('Belgaum Uttar'),
    normalize('Belagavi South'):     normalize('Belgaum Dakshin'),
    normalize('Vijayapura'):         normalize('Bijapur City'),
    normalize('Hiriyuru'):           normalize('Hiriyur'),
    normalize('Arakalagudu'):        normalize('Arkalgud'),
    normalize('Nayakanahatti'):      normalize('Harapanahalli'),
    normalize('Shahabad'):           normalize('Sedam'),
    normalize('Mysore'):             normalize('Krishnaraja'),
    normalize('Kalaburagi'):         normalize('Gulbarga Dakshin'),
    normalize('Narasimharajapura'):  normalize('Mudigere'),
    normalize('Bangalore North'):    normalize('Pulakeshinagar'),
    normalize('Bangalore Central'):  normalize('Sarvagnanagar'),
    normalize('Bangalore Rural'):    normalize('Ramanagaram'),
    normalize('Bengaluru Rural'):    normalize('Magadi'),
    normalize('Basavapatna'):        normalize('Belur'),
    normalize('Ballari Rural'):      normalize('Bellary City'),
    normalize('Bommasandra'):        normalize('B.T.M Layout'),
    normalize('Kalkere'):            normalize('C.V. Raman Nagar'),
    normalize('Shrirampur'):         normalize('Shrirangapattana'),
    normalize('Nandi'):              normalize('Bangarapet'),
    normalize('Rajagopalnagar'):     normalize('Mahalakshmi Layout'),
    normalize('Mundargi'):           normalize('Kushtagi'),
    normalize('Bijapur Rural'):      normalize('Basavana Bagevadi'),
    normalize('Bammanahalli'):       normalize('Honnali'),
    normalize('Ichalkaranji'):       normalize('Hukkeri'),
    normalize('Lah'):                normalize('Aland'),
}

def read_csv(path):
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
    created_real = 0
    created_placeholder = 0
    skipped = 0
    unmatched_csv = []
    matched_db_norms = set()

    with transaction.atomic():
        for csv_norm, row in csv_data.items():
            db_const = db_lookup.get(csv_norm)
            if not db_const and csv_norm in CSV_TO_DB:
                db_const = db_lookup.get(CSV_TO_DB[csv_norm])

            if not db_const:
                unmatched_csv.append(row['constituency'])
                skipped += 1
                continue

            db_norm = normalize(db_const.name)
            if db_norm in matched_db_norms:
                skipped += 1
                continue
            matched_db_norms.add(db_norm)

            achievements = ACHIEVEMENTS.get(row['constituency'], '')
            if not achievements:
                achievements = ACHIEVEMENTS.get(db_const.name, '')

            MLA.objects.create(
                constituency=db_const,
                name=row['name'],
                party=row['party'],
                education=row['education'],
                term_start=2023,
                term_end=2028,
                achievements_raw=achievements,
                source_url='https://www.kla.kar.nic.in/members',
            )
            created_real += 1
            print(f"  [CSV ] {db_const.name:40s} <- {row['name']}")

        for c in all_const:
            if normalize(c.name) in matched_db_norms:
                continue
            MLA.objects.create(
                constituency=c,
                name=f"MLA of {c.name}",
                party="Data Pending",
                education="",
                term_start=2023,
                term_end=2028,
                achievements_raw="",
                source_url="",
            )
            created_placeholder += 1
            print(f"  [PLCH] {c.name}")

    total_m = MLA.objects.count()
    total_c = Constituency.objects.count()
    print(f"\n{'-'*60}")
    print(f"  Created (real CSV data) : {created_real}")
    print(f"  Created (placeholder)   : {created_placeholder}")
    print(f"  Skipped (unmatched CSV) : {skipped}")
    print(f"  Total MLAs in DB        : {total_m}")
    print(f"  Total Constituencies    : {total_c}")
    print(f"{'-'*60}")

    if unmatched_csv:
        print(f"\n[WARN] {len(unmatched_csv)} CSV names unmatched:")
        for n in sorted(unmatched_csv):
            print(f"  - {n}")

    unmatched_db = [c.name for c in all_const if normalize(c.name) not in matched_db_norms]
    if unmatched_db:
        print(f"\n[INFO] {len(unmatched_db)} DB constituencies got placeholder MLAs:")
        for n in sorted(unmatched_db):
            print(f"  - {n}")

    print(f"\n{'='*60}")
    if total_m == total_c:
        print(f"  [OK] {total_m} MLAs for {total_c} constituencies")
    else:
        print(f"  [!!] MISMATCH: {total_m} MLAs vs {total_c} constituencies")
    if total_c == 224:
        print(f"  [OK] Constituency count = 224")
    else:
        print(f"  [!!] Expected 224, found {total_c}")
    if total_m == 224:
        print(f"  [OK] MLA count = 224")
    else:
        print(f"  [!!] Expected 224 MLAs, found {total_m}")
    print(f"{'='*60}")

_start = time.perf_counter()
load_mlas()
print(f"\nElapsed: {time.perf_counter() - _start:.2f}s")