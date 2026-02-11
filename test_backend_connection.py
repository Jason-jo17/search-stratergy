import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def check_health():
    print(f"Checking {BASE_URL}/ ...")
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Root status: {r.status_code}")
        print(f"Root content: {r.text}")
    except Exception as e:
        print(f"Root request failed: {e}")
        return False
    return True

def check_options():
    print(f"\nChecking CORS (OPTIONS) on {BASE_URL}/api/search/adaptive-fusion ...")
    try:
        r = requests.options(
            f"{BASE_URL}/api/search/adaptive-fusion",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        print(f"OPTIONS status: {r.status_code}")
        print(f"Headers: {r.headers}")
    except Exception as e:
        print(f"OPTIONS request failed: {e}")

def check_post():
    print(f"\nChecking POST {BASE_URL}/api/search/adaptive-fusion ...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/search/adaptive-fusion",
            json={"query": "test", "top_k": 1}
        )
        print(f"POST status: {r.status_code}")
        if r.status_code != 200:
            print(f"Error content: {r.text}")
        else:
            print("POST success")
    except Exception as e:
        print(f"POST request failed: {e}")

if __name__ == "__main__":
    if check_health():
        check_options()
        check_post()
    else:
        print("\nBackend seems DOWN.")
