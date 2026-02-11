import requests
import json
import time

def test_caching():
    url = "http://localhost:8000/api/search/agentic_tool"
    query = "Find me a python developer"
    payload = {"query": query, "limit": 5}
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Test 1: First Query (Should be MISS) ---")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            print(f"Time: {duration:.2f}s")
            print(f"Results: {len(results)}")
            if results:
                print(f"Reason: {results[0].get('ai_reasoning', '')[:100]}...")
                print(f"Match Reason: {results[0].get('match_reason', '')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

    print(f"\n--- Test 2: Second Query (Should be HIT) ---")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            print(f"Time: {duration:.2f}s")
            print(f"Results: {len(results)}")
            if results:
                print(f"Reason: {results[0].get('ai_reasoning', '')[:100]}...")
                print(f"Match Reason: {results[0].get('match_reason', '')}")
                
                # Check for cache indicator
                if "[CACHE HIT]" in results[0].get('match_reason', ''):
                    print("SUCCESS: Cache Hit Detected!")
                else:
                    print("FAILURE: No Cache Hit indicator found.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_caching()
