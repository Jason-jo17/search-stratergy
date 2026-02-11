import requests
import json
import time

BASE_URL = "http://localhost:8000/api/search"

def test_endpoint(endpoint, query, description):
    url = f"{BASE_URL}/{endpoint}"
    payload = {"query": query, "limit": 5}
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Testing {description} ({endpoint}) ---")
    
    # 1. First Call (Cache Miss)
    print("1. First Call (Expect MISS)...")
    start = time.time()
    try:
        res = requests.post(url, json=payload, headers=headers)
        dur = time.time() - start
        if res.status_code == 200:
            results = res.json().get("results", [])
            print(f"   Time: {dur:.2f}s, Results: {len(results)}")
            if results:
                print(f"   Reason: {results[0].get('match_reason', '')[:50]}...")
        else:
            print(f"   Error: {res.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")

    # 2. Second Call (Cache Hit)
    print("2. Second Call (Expect HIT)...")
    start = time.time()
    try:
        res = requests.post(url, json=payload, headers=headers)
        dur = time.time() - start
        if res.status_code == 200:
            results = res.json().get("results", [])
            print(f"   Time: {dur:.2f}s, Results: {len(results)}")
            if results:
                reason = results[0].get('match_reason', '')
                print(f"   Reason: {reason[:50]}...")
                if "[CACHE HIT]" in reason:
                    print("   SUCCESS: Cache Hit Detected!")
                else:
                    print("   FAILURE: No Cache Hit indicator.")
        else:
            print(f"   Error: {res.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")

def verify_unified_caching():
    # Clear cache first to ensure clean state
    # (Optional, but good for testing)
    
    # Test STM
    test_endpoint("stm", "Netlify", "STM Search")
    
    # Test Agentic Tool
    test_endpoint("agentic_tool", "email for john", "Agentic Tool")
    
    # Test Agentic Analysis
    test_endpoint("agentic_analysis", "find python guy", "Agentic Analysis")

if __name__ == "__main__":
    verify_unified_caching()
