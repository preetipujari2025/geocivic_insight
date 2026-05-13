#!/usr/bin/env python

import csv
import os
import re
import difflib

from db.models import MLA, Constituency


def normalize_constituency_name(name):

    if not name:
        return ""

    name = str(name).strip().lower()

    # remove SC/ST tags
    name = re.sub(r'\(sc\)', '', name)
    name = re.sub(r'\(st\)', '', name)

    # remove dots, spaces, hyphens
    name = name.replace('.', '')
    name = name.replace('-', '')
    name = name.replace(' ', '')

    # remove special chars
    name = re.sub(r'[^a-z0-9]', '', name)

    return name.strip()


def load_mlas_from_csv():

    csv_file_path = os.path.join(
        'db',
        'data',
        'karnataka_mlas.csv'
    )

    print(f"\nLoading MLA data from: {csv_file_path}\n")

    loaded_count = 0
    updated_count = 0
    skipped_count = 0

    constituencies = Constituency.objects.all()

    with open(csv_file_path, 'r', encoding='utf-8') as file:

        reader = csv.DictReader(file)

        for row_num, row in enumerate(reader, start=2):

            try:

                constituency_name = row['constituency'].strip()
                name = row['name'].strip()
                party = row['party'].strip()
                education = row['education'].strip()

                # skip invalid rows
                if constituency_name.lower() in ['nan', 'none', '']:
                    skipped_count += 1
                    continue

                if not name:
                    skipped_count += 1
                    continue

                csv_normalized = normalize_constituency_name(
                    constituency_name
                )

                constituency = None

                # ----------------------------------------
                # Stage 1 - exact normalized match
                # ----------------------------------------

                for db_constituency in constituencies:

                    db_normalized = normalize_constituency_name(
                        db_constituency.name
                    )

                    if csv_normalized == db_normalized:

                        constituency = db_constituency

                        print(
                            f"Exact Match: "
                            f"{constituency_name} "
                            f"-> "
                            f"{db_constituency.name}"
                        )

                        break

                # ----------------------------------------
                # Stage 2 - fuzzy intelligent match
                # ----------------------------------------

                if not constituency:

                    best_match = None
                    best_score = 0

                    for db_constituency in constituencies:

                        db_normalized = normalize_constituency_name(
                            db_constituency.name
                        )

                        similarity = difflib.SequenceMatcher(
                            None,
                            csv_normalized,
                            db_normalized
                        ).ratio()

                        if similarity > best_score:

                            best_score = similarity
                            best_match = db_constituency

                    if best_match and best_score >= 0.55:

                        constituency = best_match

                        print(
                            f"Fuzzy Match: "
                            f"{constituency_name} "
                            f"-> "
                            f"{best_match.name} "
                            f"(score={best_score:.2f})"
                        )

                # ----------------------------------------
                # Skip if still not found
                # ----------------------------------------

                if not constituency:

                    print(
                        f"Skipping: "
                        f"{constituency_name}"
                    )

                    skipped_count += 1
                    continue

                # ----------------------------------------
                # Create / Update MLA
                # ----------------------------------------

                mla, created = MLA.objects.update_or_create(
                    constituency=constituency,
                    defaults={
                        'name': name,
                        'party': party,
                        'education': education,
                        'term_start': 2023,
                        'term_end': None,
                        'achievements_raw': '',
                        'source_url': ''
                    }
                )

                if created:

                    loaded_count += 1

                    print(
                        f"Created MLA: "
                        f"{name} "
                        f"({party}) "
                        f"- "
                        f"{constituency.name}"
                    )

                else:

                    updated_count += 1

                    print(
                        f"Updated MLA: "
                        f"{name} "
                        f"({party}) "
                        f"- "
                        f"{constituency.name}"
                    )

            except Exception as e:

                print(f"Error on row {row_num}: {str(e)}")

                skipped_count += 1

    print("\n==============================")
    print("MLA Loading Summary")
    print("==============================")
    print(f"MLAs Created : {loaded_count}")
    print(f"MLAs Updated : {updated_count}")
    print(f"MLAs Skipped : {skipped_count}")
    print(f"Total MLAs   : {MLA.objects.count()}")
    print("==============================\n")


print("\nStarting Karnataka MLA loading...\n")

load_mlas_from_csv()

print("\nMLA loading completed.\n")