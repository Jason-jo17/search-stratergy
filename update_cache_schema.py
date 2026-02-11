import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def update_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Adding 'insight' column to search_query_cache...")
    try:
        cur.execute("ALTER TABLE search_query_cache ADD COLUMN IF NOT EXISTS insight TEXT;")
        conn.commit()
        print("Column added successfully.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    update_schema()
