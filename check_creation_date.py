import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def check_dates():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print(f"{'Source':<30} {'Earliest Date Found':<30}")
        print("-" * 60)

        # 1. Check student_profiles metadata (ingested_at)
        try:
            cur.execute("SELECT MIN(metadata->>'ingested_at') FROM student_profiles")
            min_ingested = cur.fetchone()[0]
            print(f"{'student_profiles (ingested_at)':<30} {str(min_ingested):<30}")
        except Exception as e:
            print(f"{'student_profiles':<30} Error: {e}")

        # 2. Check n8n_vectors (created_at is not standard, check metadata)
        try:
            cur.execute("SELECT MIN(metadata->>'ingested_at') FROM n8n_vectors")
            min_n8n = cur.fetchone()[0]
            print(f"{'n8n_vectors (ingested_at)':<30} {str(min_n8n):<30}")
        except Exception as e:
             print(f"{'n8n_vectors':<30} Error: {e}")
             
        # 3. Check search_query_cache (created_at)
        try:
            cur.execute("SELECT MIN(created_at) FROM search_query_cache")
            min_cache = cur.fetchone()[0]
            print(f"{'search_query_cache (created_at)':<30} {str(min_cache):<30}")
        except Exception as e:
             print(f"{'search_query_cache':<30} Error: {e}")

        # 4. Check user_profile_chunks (created_at)
        try:
            cur.execute("SELECT MIN(created_at) FROM user_profile_chunks")
            min_chunks = cur.fetchone()[0]
            print(f"{'user_profile_chunks (created_at)':<30} {str(min_chunks):<30}")
        except Exception as e:
             print(f"{'user_profile_chunks':<30} Error: {e}")

        conn.close()
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    check_dates()
