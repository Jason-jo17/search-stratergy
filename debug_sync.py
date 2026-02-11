import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    print("Connecting to DB (Sync)...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("\n--- Tables ---")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cur.fetchall()
        for t in tables:
            print(f"- {t[0]}")
            
            # Count
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
                print(f"  Count: {cur.fetchone()[0]}")
            except:
                print("  Count: Error")
                conn.rollback()

        # Check for 'chunks' or 'user_profile_chunks'
        target_table = None
        for t in tables:
            if 'chunk' in t[0]:
                target_table = t[0]
                break
        
        if target_table:
            print(f"\n--- Content of {target_table} ---")
            cur.execute(f"SELECT chunk_type, content FROM {target_table} LIMIT 3")
            rows = cur.fetchall()
            for r in rows:
                print(f"[{r[0]}] {r[1][:50]}...")
            
            # Check for 'python'
            print(f"\n--- Search 'python' in {target_table} ---")
            cur.execute(f"SELECT COUNT(*) FROM {target_table} WHERE LOWER(content) LIKE '%python%'")
            print(f"Matches: {cur.fetchone()[0]}")
            
        else:
            print("\nWARNING: No chunk table found!")
            
        conn.close()
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
