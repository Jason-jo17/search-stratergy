import requests
import json

def test_bm25_payload():
    url = "http://127.0.0.1:8000/api/search/bm25"
    # Replicate the frontend 'params' object potentially being passed
    # The Frontend likely sends everything in the body
    payload = {
        "query": "python",
        "limit": 10,
        "vector_weight": 0.5,
        "rrf_k": 60,
        "skills": [],
        "required_skills": ["python", "java"], # Test with list
        "preferred_skills": [],
        "min_score": 0.0,
        "strategies": ["bm25"],
        "filters": {} # Frontend might send filters
    }
    
    print(f"Sending payload to BM25: {json.dumps(payload, indent=2)}")
    try:
        resp = requests.post(url, json=payload, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error Response: {resp.text}")
        else:
            print("Success!")
            # print(resp.text[:200])
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_bm25_payload()
