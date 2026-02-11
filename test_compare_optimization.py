import requests
import json

def test_compare_optimization():
    url = "http://localhost:8000/api/search/compare"
    # Query that benefits from optimization (e.g., vague or natural language)
    query = "find me a guy who knows python and can deploy to netlify"
    
    payload = {
        "query": query,
        "limit": 3,
        "strategies": ["vector", "stm", "agentic_tool"]
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Testing Compare Mode with Optimization ---")
    print(f"Query: '{query}'")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check Optimization
            opt = data.get("optimization", {})
            rewritten = opt.get("rewritten_query")
            print(f"\n[Optimization]")
            print(f"Rewritten Query: '{rewritten}'")
            print(f"Filters: {opt.get('filters')}")
            
            if rewritten and rewritten != query:
                print("SUCCESS: Query was optimized.")
            else:
                print("WARNING: Query was NOT optimized (or optimization returned same string).")
            
            # Check Results
            results = data.get("results", {})
            print(f"\n[Results]")
            for strategy, res_list in results.items():
                print(f"{strategy}: {len(res_list)} results")
                if res_list:
                    print(f"  Top: {res_list[0].get('text')[:50]}...")
                    
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_compare_optimization()
