import requests
import json

def run_evaluation():
    try:
        with open("current_id.txt", "r") as f:
            student_id = f.read().strip()
    except:
        print("Could not read current_id.txt")
        return

    url = f"http://localhost:8000/api/stm/evaluate/{student_id}"
    payload = {"student_id": student_id}
    headers = {"Content-Type": "application/json"}
    
    print(f"Triggering evaluation for {student_id}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Evaluation successful!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    run_evaluation()
