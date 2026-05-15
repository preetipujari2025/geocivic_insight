"""Test all 4 API endpoints."""
import urllib.request
import json

BASE = "http://127.0.0.1:8000/api"

def test(url):
    try:
        r = urllib.request.urlopen(url, timeout=30)
        data = json.loads(r.read())
        return r.status, data
    except Exception as e:
        return None, str(e)

print("=" * 60)
print("  API Endpoint Tests")
print("=" * 60)

# 1. /api/mlas/
status, data = test(f"{BASE}/mlas/")
if status:
    print(f"\n[OK] GET /api/mlas/ -> {status}")
    print(f"     Count: {len(data)}")
    if data:
        print(f"     Sample: {data[0]['name']} ({data[0]['constituency']['name']})")
else:
    print(f"\n[FAIL] GET /api/mlas/ -> {data}")

# 2. /api/mlas/1/  (use first MLA id)
if status and data:
    mid = data[0]["id"]
    s2, d2 = test(f"{BASE}/mlas/{mid}/")
    if s2:
        print(f"\n[OK] GET /api/mlas/{mid}/ -> {s2}")
        print(f"     Name: {d2['name']}")
    else:
        print(f"\n[FAIL] GET /api/mlas/{mid}/ -> {d2}")

# 3. /api/constituencies/
s3, d3 = test(f"{BASE}/constituencies/")
if s3:
    print(f"\n[OK] GET /api/constituencies/ -> {s3}")
    print(f"     Count: {len(d3)}")
    if d3:
        print(f"     Sample: {d3[0]['name']}")
else:
    print(f"\n[FAIL] GET /api/constituencies/ -> {d3}")

# 4. /api/constituencies/1/
if s3 and d3:
    cid = d3[0]["id"]
    s4, d4 = test(f"{BASE}/constituencies/{cid}/")
    if s4:
        print(f"\n[OK] GET /api/constituencies/{cid}/ -> {s4}")
        print(f"     Name: {d4['name']}, District: {d4['district']}")
    else:
        print(f"\n[FAIL] GET /api/constituencies/{cid}/ -> {d4}")

print(f"\n{'=' * 60}")
print("  All API tests complete")
print(f"{'=' * 60}")
