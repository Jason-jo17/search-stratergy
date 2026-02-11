import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_cache():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("--- Inspecting search_query_cache ---")
        cur.execute("SELECT id, query_text, strategy_used, created_at FROM search_query_cache ORDER BY created_at DESC")
        rows = cur.fetchall()
        
        if not rows:
            print("Table is empty.")
        else:
            print(f"Found {len(rows)} cached queries:")
            for row in rows:
                print(f"ID: {row[0]}")
                print(f"Query: {row[1]}")
                print(f"Strategy: {row[2]}")
                print(f"Created At: {row[3]}")
                print("-" * 20)
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_cache()
