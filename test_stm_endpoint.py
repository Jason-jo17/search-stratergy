import requests
import json

def test_endpoint():
    student_id = "a9a4d281-31c9-4018-b494-c5220a8667e5"
    url = f"http://localhost:8000/api/stm/evaluate/{student_id}"
    
    payload = {"student_id": student_id}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
