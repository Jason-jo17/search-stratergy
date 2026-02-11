import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/search"

STRATEGIES = [
    "keyword",
    "vector", 
    "hybrid",
    "fts",
    "fuzzy",
    "bm25",
    "agentic", # Might fail if no API key
    "agentic_tool", # Might fail
    "agentic_analysis" # Might fail
]

def test_strategy(strategy):
    url = f"{BASE_URL}/{strategy}"
    payload = {"query": "python", "limit": 2}
    
    print(f"\n--- Testing {strategy} ---")
    try:
        start = time.time()
        response = requests.post(url, json=payload)
        duration = time.time() - start
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.4f}s")
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("results", []))
            print(f"Results found: {count}")
            # print(json.dumps(data, indent=2)[:500] + "...")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def test_compare():
    url = f"{BASE_URL}/compare"
    payload = {
        "query": "python", 
        "limit": 2, 
        "strategies": ["bm25", "vector"]
    }
    
    print(f"\n--- Testing Compare (bm25 + vector) ---")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results keys: {list(data.get('results', {}).keys())}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    print("Starting verification of all search strategies...")
    for strat in STRATEGIES:
        test_strategy(strat)
    
    test_compare()
