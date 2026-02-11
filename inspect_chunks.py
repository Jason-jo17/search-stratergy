import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_chunks():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Get the user ID we used for testing
    try:
        with open("current_id.txt", "r") as f:
            user_id = f.read().strip()
    except:
        print("Could not read current_id.txt")
        return

    print(f"Inspecting chunks for User ID: {user_id}")
    
    cur.execute("SELECT chunk_type, content FROM user_profile_chunks WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()
    
    if not rows:
        print("No chunks found for this user.")
    else:
        for row in rows:
            print(f"[{row[0]}] {row[1][:100]}...") # Print first 100 chars

    conn.close()

if __name__ == "__main__":
    inspect_chunks()
