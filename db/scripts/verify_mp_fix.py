"""Quick verification that constituency_name is no longer null."""
import urllib.request
import json

r = urllib.request.urlopen("http://127.0.0.1:8000/api/mps/")
data = json.loads(r.read())

nulls = [m for m in data if m.get("constituency_name") is None]

print(f"Total MPs: {len(data)}")
print(f"Null constituency_name: {len(nulls)}")

print("\n--- Sample API Output (first 3) ---")
print(json.dumps(data[:3], indent=2))

print("\n--- Verification ---")
checks = {
    "Bangalore South": "Tejasvi Surya",
    "Bangalore North": "Shobha Karandlaje",
    "Mandya": "H.D. Kumaraswamy",
}
for seat, expected_name in checks.items():
    mp = next((m for m in data if m["constituency_name"] == seat), None)
    if mp and expected_name.lower() in mp["name"].lower():
        print(f"  [OK] {mp['name']} -> {seat}")
    else:
        print(f"  [FAIL] {seat}: {mp}")

# MLA check
r2 = urllib.request.urlopen("http://127.0.0.1:8000/api/mlas/")
mlas = json.loads(r2.read())
print(f"\n--- MLA API intact: {len(mlas)} MLAs ---")

if len(nulls) == 0:
    print("\n=== ALL GOOD: No null constituency_name values ===")
else:
    print(f"\n=== PROBLEM: {len(nulls)} entries still have null ===")
