import requests
import json

def test_optimize_endpoint():
    url = "http://localhost:8000/api/search/optimize"
    query = "find me a guy who knows python and can deploy to netlify"
    
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Testing Optimize Endpoint ---")
    print(f"Query: '{query}'")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            opt = data.get("optimization", {})
            
            print(f"\n[Optimization Result]")
            print(f"Rewritten Query: '{opt.get('rewritten_query')}'")
            print(f"Filters: {opt.get('filters')}")
            print(f"Reasoning: {opt.get('reasoning')}")
            
            if opt.get("rewritten_query"):
                print("SUCCESS: Endpoint returned optimization data.")
            else:
                print("WARNING: Endpoint returned empty optimization data.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_optimize_endpoint()
