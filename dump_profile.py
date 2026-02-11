import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def dump_profile():
    try:
        with open("current_id.txt", "r") as f:
            user_id = f.read().strip()
    except:
        print("Could not read current_id.txt")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT metadata FROM student_profiles WHERE id = %s", (user_id,))
    row = cur.fetchone()
    if row:
        print(json.dumps(row[0], indent=2))
    else:
        print("User not found")
    conn.close()

if __name__ == "__main__":
    dump_profile()
