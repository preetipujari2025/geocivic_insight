"""
validate_data.py - Validate Karnataka MLA & Constituency data integrity.
Usage:  python db/scripts/validate_data.py
"""
import os, sys
from pathlib import Path
from collections import Counter

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

from db.models import MLA, Constituency

def validate():
    print('=' * 60)
    print('  GeoCivic Insight - Data Validation')
    print('=' * 60)
    passed = 0
    failed = 0

    def check(label, condition, detail=''):
        nonlocal passed, failed
        if condition:
            print(f"  [OK]   {label}")
            passed += 1
        else:
            print(f"  [FAIL] {label}")
            if detail: print(f"         {detail}")
            failed += 1

    const_count = Constituency.objects.count()
    mla_count = MLA.objects.count()

    print(f"\n-- Record Counts --")
    check("Constituency count == 224", const_count == 224, f"Found {const_count}")
    check("MLA count == 224", mla_count == 224, f"Found {mla_count}")

    print(f"\n-- Duplicate Checks --")
    names = list(Constituency.objects.values_list('name', flat=True))
    name_counts = Counter(names)
    dups = {k: v for k, v in name_counts.items() if v > 1}
    check("No duplicate constituency names", len(dups) == 0,
          f"Duplicates: {dups}" if dups else '')

    mla_cids = list(MLA.objects.values_list('constituency_id', flat=True))
    id_counts = Counter(mla_cids)
    dup_mlas = {k: v for k, v in id_counts.items() if v > 1}
    check("No duplicate MLAs per constituency", len(dup_mlas) == 0,
          f"{len(dup_mlas)} constituencies have >1 MLA" if dup_mlas else '')
    if dup_mlas:
        for cid, cnt in dup_mlas.items():
            c = Constituency.objects.get(pk=cid)
            print(f"         - {c.name} (id={cid}): {cnt} MLAs")

    print(f"\n-- Referential Integrity --")
    orphan = MLA.objects.filter(constituency__isnull=True).count()
    check("Every MLA linked to a constituency", orphan == 0,
          f"{orphan} MLA(s) without constituency")

    const_with_mla = set(MLA.objects.values_list('constituency_id', flat=True))
    all_cids = set(Constituency.objects.values_list('id', flat=True))
    missing = all_cids - const_with_mla
    check("Every constituency has at least one MLA", len(missing) == 0,
          f"{len(missing)} constituency(ies) without MLA")
    if missing:
        for cid in sorted(missing):
            c = Constituency.objects.get(pk=cid)
            print(f"         - {c.name} (id={cid})")

    print(f"\n-- Boundary Checks --")
    null_b = Constituency.objects.filter(boundary__isnull=True).count()
    check("All constituencies have boundaries", null_b == 0,
          f"{null_b} with NULL boundary")

    print(f"\n-- Data Quality --")
    placeholder = MLA.objects.filter(party='Data Pending').count()
    real = mla_count - placeholder
    print(f"  [i] MLAs with real CSV data : {real}")
    print(f"  [i] Placeholder MLAs        : {placeholder}")

    print(f"\n{'='*60}")
    total = passed + failed
    if failed == 0:
        print(f"  ALL {total} CHECKS PASSED")
    else:
        print(f"  {failed}/{total} CHECK(S) FAILED")
    print(f"{'='*60}")

if __name__ == '__main__':
    validate()
else:
    validate()
