import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
TARGET_EMAIL = "jason@theboringpeople.in"

def check_email():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        found = False
        print(f"Searching for '{TARGET_EMAIL}' in database...\n")

        # 1. Check student_profiles
        cur.execute(f"SELECT COUNT(*) FROM student_profiles WHERE text ILIKE '%{TARGET_EMAIL}%'")
        text_count = cur.fetchone()[0]
        if text_count > 0:
            print(f"FOUND in 'student_profiles' (text column): {text_count} occurrences")
            found = True
            
        cur.execute(f"SELECT COUNT(*) FROM student_profiles WHERE metadata::text ILIKE '%{TARGET_EMAIL}%'")
        meta_count = cur.fetchone()[0]
        if meta_count > 0:
             print(f"FOUND in 'student_profiles' (metadata): {meta_count} occurrences")
             found = True

        # 2. Check n8n_vectors
        cur.execute(f"SELECT COUNT(*) FROM n8n_vectors WHERE text ILIKE '%{TARGET_EMAIL}%'")
        n8n_text_count = cur.fetchone()[0]
        if n8n_text_count > 0:
            print(f"FOUND in 'n8n_vectors' (text column): {n8n_text_count} occurrences")
            found = True

        cur.execute(f"SELECT COUNT(*) FROM n8n_vectors WHERE metadata::text ILIKE '%{TARGET_EMAIL}%'")
        n8n_meta_count = cur.fetchone()[0]
        if n8n_meta_count > 0:
             print(f"FOUND in 'n8n_vectors' (metadata): {n8n_meta_count} occurrences")
             found = True
             
        if not found:
            print("Email NOT found in any searched tables.")

        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_email()
