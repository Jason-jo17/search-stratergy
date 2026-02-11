import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, payload):
    print(f"\n{'='*20} TESTING: {name} {'='*20}")
    url = f"{BASE_URL}/search/adaptive-fusion"
    
    try:
        start = time.time()
        response = requests.post(url, json=payload)
        duration = time.time() - start
        
        print(f"Status: {response.status_code}")
        print(f"Time: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Results: {data.get('total_results')}")
            print(f"Execution Time (Server): {data.get('execution_time_ms')}ms")
            
            results = data.get("results", [])
            if results:
                print(f"\nTop Result:")
                top = results[0]
                print(f"  Student: {top['student']['name']} ({top['student']['branch']})")
                print(f"  Score: {top['scores']['final_score']}")
                print(f"  Match Insight: {top['match_insight']}")
            else:
                print("\nNo results found.")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    # Wait for server to start
    print("Waiting for server...")
    time.sleep(5)
    
    # 1. Basic Fusion
    test_endpoint("Basic Fusion", {
        "query": "python developer",
        "top_k": 3
    })

    # 2. BM25 Heavy
    test_endpoint("BM25 Heavy (Exact Skills)", {
        "query": "react typescript",
        "parameters": {
            "bm25_weight": 0.8,
            "vector_weight": 0.2
        },
        "top_k": 3
    })

    # 3. Vector Heavy
    test_endpoint("Vector Heavy (Concepts)", {
        "query": "innovative leader",
        "parameters": {
            "bm25_weight": 0.2,
            "vector_weight": 0.8
        },
        "top_k": 3
    })

    # 4. Filters
    test_endpoint("With Filters", {
        "query": "python",
        "filters": {
            "branches": ["CSE"],
            "min_cgpa": 8.0
        },
        "top_k": 3
    })
    
    # 5. Presets
    print(f"\n{'='*20} TESTING: Presets Endpoint {'='*20}")
    try:
        resp = requests.get(f"{BASE_URL}/search/adaptive-fusion/presets")
        if resp.status_code == 200:
            print("Presets fetched successfully.")
            print("Keys:", list(resp.json()['presets'].keys()))
        else:
            print(f"Error fetching presets: {resp.status_code}")
    except Exception as e:
        print(f"Presets request failed: {e}")

if __name__ == "__main__":
    main()
