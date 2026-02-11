import requests
import json

def test_stm_search():
    url = "http://localhost:8000/api/search/stm"
    
    # Test queries that should match the chunks we generated
    queries = [
        "Netlify",
        "Python developer",
        "Mangaluru student"
    ]
    
    for query in queries:
        print(f"\n--- Testing Query: '{query}' ---")
        payload = {"query": query, "limit": 5}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                results = response.json().get("results", [])
                print(f"Found {len(results)} results.")
                for res in results:
                    print(f"  - ID: {res['id']}")
                    print(f"    Score: {res['score']:.4f}")
                    print(f"    Reason: {res['match_reason']}")
            else:
                try:
                    print(f"Error: {response.status_code} - {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_stm_search()
