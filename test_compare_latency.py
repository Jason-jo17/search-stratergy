import requests
import time
import json

def test_compare_and_latency():
    # Test 1: BM25 Latency
    url_bm25 = "http://127.0.0.1:8000/api/search/bm25"
    start = time.time()
    try:
        r = requests.post(url_bm25, json={"query": "python", "limit": 5}, timeout=60)
        dur = time.time() - start
        print(f"BM25 Latency: {dur:.2f}s")
        if r.status_code == 200:
            res = r.json()['results']
            print(f"BM25 Results: {len(res)}")
            if len(res) > 0:
                print(f"Top 1 Match Reason: {res[0].get('match_reason')}")
        else:
            print(f"BM25 Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"BM25 Exception: {e}")

    # Test 2: Compare Mode
    url_compare = "http://127.0.0.1:8000/api/search/compare"
    payload = {
        "query": "python",
        "strategies": ["bm25", "vector"],
        "limit": 5
    }
    start = time.time()
    try:
        r = requests.post(url_compare, json=payload, timeout=60)
        dur = time.time() - start
        print(f"Compare Latency: {dur:.2f}s")
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", {})
            print(f"Compare Strategies Returned: {list(results.keys())}")
            print(f"BM25 in Compare: {len(results.get('bm25', []))} results")
        else:
            print(f"Compare Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Compare Exception: {e}")

if __name__ == "__main__":
    test_compare_and_latency()
