import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def clear_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Clearing user_profile_chunks...")
    cur.execute("TRUNCATE TABLE user_profile_chunks;")
    
    print("Clearing search_query_cache...")
    cur.execute("TRUNCATE TABLE search_query_cache;")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database tables cleared.")

if __name__ == "__main__":
    clear_db()
