import requests
import json

strategies = ['keyword', 'vector', 'hybrid', 'fts', 'fuzzy', 'agentic', 'agentic_tool', 'agentic_analysis', 'stm', 'bm25']
base_url = "http://127.0.0.1:8000/api/search"

print("--- Testing /optimize ---")
try:
    r = requests.post(f"{base_url}/optimize", json={"query": "python"})
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
except Exception as e:
    print(e)

print("\n--- Testing Strategies ---")
for s in strategies:
    print(f"Testing {s}...")
    try:
        r = requests.post(f"{base_url}/{s}", json={"query": "python", "limit": 5})
        if r.status_code != 200:
            print(f"❌ {s} FAILED: {r.status_code}")
            print(r.text[:200])
        else:
            try:
                js = r.json()
                print(f"✅ {s} OK")
            except:
                print(f"❌ {s} returned invalid JSON")
                print(r.text[:200])
    except Exception as e:
        print(f"❌ {s} Exception: {e}")
