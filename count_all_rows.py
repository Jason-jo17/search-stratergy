import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def count_rows():
    tables = [
        "student_profiles",
        "n8n_vectors",
        "search_query_cache",
        "user_profile_chunks"
    ]
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        counts = {}
        print(f"{'Table Name':<30} {'Row Count':<10}")
        print("-" * 40)
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                counts[table] = count
                print(f"{table:<30} {count:<10}")
            except Exception as e:
                print(f"{table:<30} Error: {e}")
                conn.rollback() # Rollback in case of error to proceed to next
        
        print("-" * 40)
        
        # Find max
        if counts:
            max_table = max(counts, key=counts.get)
            print(f"\nLargest Table: {max_table} ({counts[max_table]} rows)")
            
        conn.close()
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    count_rows()
