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
    "agentic",
    "agentic_tool",
    "agentic_analysis",
    "stm"
]

QUERY = "python developer with machine learning skills"

def verify_strategy(strategy):
    url = f"{BASE_URL}/{strategy}"
    payload = {
        "query": QUERY,
        "limit": 5
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        duration = time.time() - start_time
        
        results = data.get("results", [])
        count = len(results)
        
        status = "✅ PASS" if count > 0 else "⚠️ WARN (No results)"
        print(f"{status} | {strategy:<15} | {duration:.2f}s | {count} results")
        return True
    except Exception as e:
        print(f"❌ FAIL | {strategy:<15} | Error: {e}")
        return False

def main():
    print(f"Verifying Search Strategies on {BASE_URL}...")
    print("-" * 60)
    print(f"{'Status':<8} | {'Strategy':<15} | {'Time':<6} | {'Results'}")
    print("-" * 60)
    
    success_count = 0
    for strategy in STRATEGIES:
        if verify_strategy(strategy):
            success_count += 1
            
    print("-" * 60)
    print(f"Completed: {success_count}/{len(STRATEGIES)} strategies passed.")

if __name__ == "__main__":
    main()
