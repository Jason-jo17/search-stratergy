import requests
import threading
import time

def call_api(endpoint, name):
    try:
        url = f"http://127.0.0.1:8000/api/search/{endpoint}"
        print(f"[{name}] Starting request to {url}...")
        start = time.time()
        resp = requests.post(url, json={"query": "python", "limit": 2})
        duration = time.time() - start
        print(f"[{name}] Status: {resp.status_code}, Duration: {duration:.2f}s")
        if resp.status_code != 200:
            print(f"[{name}] ERROR: {resp.text}")
    except Exception as e:
        print(f"[{name}] EXCEPTION: {e}")

if __name__ == "__main__":
    print("--- Testing Concurrency: BM25 + Vector ---")
    
    t1 = threading.Thread(target=call_api, args=("bm25", "Thread-BM25"))
    t2 = threading.Thread(target=call_api, args=("vector", "Thread-Vector"))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("--- Done ---")
