"""Quick verification script for MLA data."""
import os, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
import django; django.setup()

from db.models import MLA, Constituency
from django.db.models import Count

print("=" * 50)
print("  MLA DATA VERIFICATION")
print("=" * 50)

m_count = MLA.objects.count()
c_count = Constituency.objects.count()
print(f"  MLAs:            {m_count}")
print(f"  Constituencies:  {c_count}")

dup_c = MLA.objects.values('constituency').annotate(c=Count('id')).filter(c__gt=1)
print(f"  Dup assignments: {dup_c.count()}")

no_mla = Constituency.objects.exclude(id__in=MLA.objects.values('constituency'))
print(f"  No MLA:          {no_mla.count()}")

print(f"\n  Party breakdown:")
parties = MLA.objects.values('party').annotate(c=Count('id')).order_by('-c')
for p in parties:
    print(f"    {p['party']:10s}: {p['c']}")

print(f"\n  Key validations:")
checks = [
    ('Varuna', 'Siddaramaiah'),
    ('Kanakapura', 'D. K. Shivakumar'),
    ('Shiggaon', 'Basavaraj Bommai'),
    ('Mahadevapura', 'Manjula S'),
]
for cn, expected in checks:
    try:
        mla = MLA.objects.get(constituency__name=cn)
        ok = expected.lower() in mla.name.lower()
        print(f"    {'OK' if ok else 'FAIL':4s} {cn:20s} -> {mla.name} ({mla.party})")
    except MLA.DoesNotExist:
        print(f"    FAIL {cn:20s} -> NOT FOUND")

print("=" * 50)
