import requests
import json

def test_payload():
    url = "http://127.0.0.1:8000/api/search/vector"
    # Replicate the frontend 'params' object potentially being passed
    payload = {
        "query": "python",
        "limit": 10,
        "vector_weight": 0.5,
        "rrf_k": 60,
        "skills": [],
        "required_skills": [],
        "preferred_skills": [],
        "min_score": 0.0,
        "strategies": ["vector"] # Frontend might be sending this even in single mode?
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    try:
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}...")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_payload()
