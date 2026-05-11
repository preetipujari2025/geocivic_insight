"""
create_test_data.py - Standalone script to seed the PostGIS database with
sample constituency, MLA, MP, and election-result records for local
development and testing.

Usage:
    python db/scripts/create_test_data.py

Compatibility: Windows, Python 3.10+, Django 4.2, PostGIS, GeoDjango
"""

# ---------------------------------------------------------------------------
# 1. Bootstrap Django before any ORM / model imports
# ---------------------------------------------------------------------------
import django
import os
import sys

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
from db.models import Constituency, MLA, MP, ElectionResult  # noqa: E402
from django.contrib.gis.geos import GEOSGeometry              # noqa: E402
from django.db import transaction                              # noqa: E402

# ---------------------------------------------------------------------------
# 3. Test-data definitions
# ---------------------------------------------------------------------------
CONSTITUENCIES = [
    {
        'name': 'Mahadevapura',
        'district': 'Bangalore Urban',
        'wkt': (
            'POLYGON ((77.68 12.99, 77.72 12.99, '
            '77.72 13.02, 77.68 13.02, 77.68 12.99))'
        ),
        'lok_sabha_seat': 'Bangalore North',
    },
    {
        'name': 'Shivajinagar',
        'district': 'Bangalore Urban',
        'wkt': (
            'POLYGON ((77.59 12.98, 77.62 12.98, '
            '77.62 13.01, 77.59 13.01, 77.59 12.98))'
        ),
        'lok_sabha_seat': 'Bangalore North',
    },
    {
        'name': 'Mysuru Rural',
        'district': 'Mysuru',
        'wkt': (
            'POLYGON ((76.60 12.28, 76.65 12.28, '
            '76.65 12.32, 76.60 12.32, 76.60 12.28))'
        ),
        'lok_sabha_seat': 'Mysuru',
    },
]

ELECTION_YEARS = [2018, 2023]

# ---------------------------------------------------------------------------
# 4. Seed logic
# ---------------------------------------------------------------------------

def _wipe_existing_data():
    """Delete all records in dependency-safe order (children first)."""
    counts = {
        'ElectionResult': ElectionResult.objects.count(),
        'MLA': MLA.objects.count(),
        'MP': MP.objects.count(),
        'Constituency': Constituency.objects.count(),
    }

    ElectionResult.objects.all().delete()
    MLA.objects.all().delete()
    MP.objects.all().delete()
    Constituency.objects.all().delete()

    for model_name, count in counts.items():
        if count:
            print(f"  Deleted {count} existing {model_name} record(s)")

    print()


def _create_election_results(constituency):
    """Generate synthetic election results for each configured year."""
    for year in ELECTION_YEARS:
        result = ElectionResult.objects.create(
            constituency=constituency,
            year=year,
            winner_name=f"Winner {constituency.name} {year}",
            winner_party="Test Party",
            winner_votes=85_000,
            runner_up_name=f"Runner-up {constituency.name} {year}",
            runner_up_votes=62_000,
            total_votes=160_000,
            turnout_percent=68.5,
        )
        print(f"    Created ElectionResult: {result}")


def main():
    """Seed the database with three constituencies and their related records."""
    print("=" * 55)
    print("  GeoCivic Insight - Test Data Seeder")
    print("=" * 55)
    print()

    # --- Wipe ---------------------------------------------------------------
    print("[1/3] Clearing existing data ...")
    _wipe_existing_data()

    # --- Create -------------------------------------------------------------
    print("[2/3] Creating test records ...\n")

    with transaction.atomic():
        for entry in CONSTITUENCIES:
            # Constituency
            boundary = GEOSGeometry(entry['wkt'])
            constituency = Constituency.objects.create(
                name=entry['name'],
                district=entry['district'],
                boundary=boundary,
            )
            print(f"  Created constituency: {constituency.name}")

            # MLA
            mla = MLA.objects.create(
                constituency=constituency,
                name=f"Test MLA for {constituency.name}",
                party="Test Party",
                education="B.E. Computer Science",
                term_start=2023,
                achievements_raw=(
                    "Built 5 schools. "
                    "Inaugurated new park. "
                    "Completed 3km road work. "
                    "Launched women's self-help group."
                ),
            )
            print(f"    Created MLA: {mla.name}")

            # MP
            mp = MP.objects.create(
                constituency=constituency,
                name=f"Test MP for {constituency.name}",
                party="Test Party",
                lok_sabha_seat=entry['lok_sabha_seat'],
                term_start=2024,
            )
            print(f"    Created MP: {mp.name}")

            # Election results
            _create_election_results(constituency)

            print()  # visual spacer between constituencies

    # --- Summary ------------------------------------------------------------
    print("[3/3] Summary\n")
    print(f"  Constituencies  : {Constituency.objects.count()}")
    print(f"  MLAs            : {MLA.objects.count()}")
    print(f"  MPs             : {MP.objects.count()}")
    print(f"  Election Results: {ElectionResult.objects.count()}")
    print()
    print("Test data created successfully [OK]")


# ---------------------------------------------------------------------------
# 5. CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    main()
