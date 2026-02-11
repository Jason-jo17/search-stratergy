import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from collections import Counter

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_metadata_owners():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Scanning metadata for user-identifiable keys (e.g., 'user', 'email', 'owner')...\n")
        
        # Fetch all metadata keys first to see what we have
        cur.execute("""
            SELECT DISTINCT jsonb_object_keys(metadata) 
            FROM student_profiles
        """)
        keys = cur.fetchall()
        print(f"Found Metadata Keys: {[k[0] for k in keys]}")
        
        # If 'email' or 'user' exists in keys, inspect values
        interesting_keys = ['email', 'user', 'uploaded_by', 'creator', 'source']
        found_keys = [k[0] for k in keys if k[0] in interesting_keys]
        
        if found_keys:
            for key in found_keys:
                print(f"\nAnalyzing values for key: '{key}'")
                cur.execute(f"SELECT metadata->>'{key}', COUNT(*) FROM student_profiles GROUP BY metadata->>'{key}' LIMIT 10")
                values = cur.fetchall()
                for v in values:
                    print(f"  - {v[0]}: {v[1]} records")
        else:
             print("\nNo obvious owner/user keys found in metadata.")
             
        # Check if there is an email inside the 'text' JSON blob (heuristic)
        print("\nChecking for common emails in 'text' content (limit 5 samples)...")
        cur.execute("SELECT text FROM student_profiles LIMIT 5")
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            try:
                data = json.loads(row[0])
                if 'email' in data:
                    print(f"  Record {i+1} email: {data['email']}")
            except:
                pass

        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_metadata_owners()
