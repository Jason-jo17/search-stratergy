import requests
import json

def test_endpoint():
    url = "http://127.0.0.1:8000/api/search/compare"
    payload = {
        "query": "python",
        "strategies": ["keyword", "vector"],
        "limit": 5
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_endpoint()
