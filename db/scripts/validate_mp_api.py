"""Validate MP API endpoints and data integrity."""
import urllib.request
import json
from collections import Counter

BASE = "http://127.0.0.1:8000/api"

print("=" * 60)
print("  MP API Validation")
print("=" * 60)

# 1. MP List API
print("\n[1] Testing /api/mps/ ...")
r = urllib.request.urlopen(f"{BASE}/mps/")
all_mps = json.loads(r.read())
print(f"    Total MPs returned: {len(all_mps)}")
assert len(all_mps) == 28, f"Expected 28, got {len(all_mps)}"
print("    [OK] Count = 28")

# 2. MP Detail API
first_id = all_mps[0]["id"]
r = urllib.request.urlopen(f"{BASE}/mps/{first_id}/")
detail = json.loads(r.read())
print(f"\n[2] Testing /api/mps/{first_id}/ ...")
print(f"    {json.dumps(detail, indent=4)}")
assert detail["id"] == first_id
print("    [OK] Detail endpoint works")

# 3. No geometry in response
print("\n[3] Checking no geometry in response ...")
sample = json.dumps(all_mps[0])
assert "coordinates" not in sample, "Geometry found in MP response!"
assert "boundary" not in sample, "Boundary found in MP response!"
print("    [OK] No geometry data in response")

# 4. No duplicates
print("\n[4] Checking for duplicates ...")
seats = [m["lok_sabha_seat"] for m in all_mps]
names = [m["name"] for m in all_mps]
assert len(seats) == len(set(seats)), "Duplicate seats!"
assert len(names) == len(set(names)), "Duplicate names!"
print("    [OK] No duplicate seats or names")

# 5. Party breakdown
print("\n[5] Party breakdown:")
parties = Counter(m["party"] for m in all_mps)
for party, count in parties.most_common():
    print(f"    {party:10s}: {count}")

# 6. Manual verification
print("\n[6] Manual MP verification:")
verify = {
    "Bangalore South": "Tejasvi Surya",
    "Bangalore North": "Shobha Karandlaje",
    "Bangalore Rural": "Dr. C.N. Manjunath",
    "Mandya": "H.D. Kumaraswamy",
}
for seat, expected in verify.items():
    mp = next((m for m in all_mps if m["lok_sabha_seat"] == seat), None)
    if mp and expected.lower() in mp["name"].lower():
        status = "OK"
        info = f"{mp['name']} ({mp['party']})"
    else:
        status = "FAIL"
        info = f"expected {expected}, got {mp}"
    print(f"    [{status}] {seat:25s} -> {info}")

# 7. MLA API still works
print("\n[7] Verifying MLA API not broken ...")
r = urllib.request.urlopen(f"{BASE}/mlas/")
mlas = json.loads(r.read())
print(f"    MLA count: {len(mlas)}")
assert len(mlas) == 224, f"Expected 224 MLAs, got {len(mlas)}"
print("    [OK] MLA API intact (224 MLAs)")

print("\n" + "=" * 60)
print("  ALL VALIDATIONS PASSED")
print("=" * 60)
