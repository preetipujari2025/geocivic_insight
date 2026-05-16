"""Test the find-representatives API endpoint."""
import urllib.request
import json

BASE = "http://127.0.0.1:8000/api"

print("=" * 60)
print("  Find Representatives API Test")
print("=" * 60)

# Test 1: Valid Bangalore coordinates (Mahadevapura area)
print("\n[1] Testing with lat=12.9716, lng=77.5946 ...")
try:
    r = urllib.request.urlopen(f"{BASE}/find-representatives/?lat=12.9716&lng=77.5946")
    data = json.loads(r.read())
    print(f"    Status: {r.status}")
    print(f"    Response:")
    print(json.dumps(data, indent=4))
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"    HTTP {e.code}: {body}")

# Test 2: Missing params -> 400
print("\n[2] Testing missing params ...")
try:
    r = urllib.request.urlopen(f"{BASE}/find-representatives/")
    print(f"    Unexpected success: {r.status}")
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    print(f"    HTTP {e.code}: {body['error']}")
    assert e.code == 400, f"Expected 400, got {e.code}"
    print("    [OK] Correct 400 error")

# Test 3: Outside Karnataka -> 404
print("\n[3] Testing outside Karnataka (Mumbai) ...")
try:
    r = urllib.request.urlopen(f"{BASE}/find-representatives/?lat=19.0760&lng=72.8777")
    print(f"    Unexpected success: {r.status}")
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    print(f"    HTTP {e.code}: {body['error']}")
    assert e.code == 404, f"Expected 404, got {e.code}"
    print("    [OK] Correct 404 error")

# Test 4: Existing APIs still work
print("\n[4] Verifying existing APIs ...")
r = urllib.request.urlopen(f"{BASE}/mlas/")
mlas = json.loads(r.read())
print(f"    /api/mlas/ -> {len(mlas)} MLAs")

r = urllib.request.urlopen(f"{BASE}/mps/")
mps = json.loads(r.read())
print(f"    /api/mps/  -> {len(mps)} MPs")

r = urllib.request.urlopen(f"{BASE}/constituencies/")
constits = json.loads(r.read())
print(f"    /api/constituencies/ -> {len(constits)} constituencies")

print("    [OK] All existing APIs intact")

print("\n" + "=" * 60)
print("  ALL TESTS COMPLETE")
print("=" * 60)
