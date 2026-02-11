import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_id():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id FROM student_profiles LIMIT 1")
    row = cur.fetchone()
    print(f"Student ID: {row[0]}")
    with open("current_id.txt", "w") as f:
        f.write(str(row[0]))
    conn.close()

if __name__ == "__main__":
    get_id()
