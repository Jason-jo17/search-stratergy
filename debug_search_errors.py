import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/search"
STRATEGIES = ["agentic", "stm"]
QUERY = "python developer with machine learning skills"

def debug_strategy(strategy):
    url = f"{BASE_URL}/{strategy}"
    payload = {
        "query": QUERY,
        "limit": 5
    }
    
    print(f"Testing {strategy}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ {strategy} FAILED with {response.status_code}")
            try:
                print("Response JSON:", json.dumps(response.json(), indent=2))
            except:
                print("Response Text:", response.text)
        else:
            print(f"✅ {strategy} PASSED")
            # print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ {strategy} EXCEPTION: {e}")

if __name__ == "__main__":
    for s in STRATEGIES:
        debug_strategy(s)
