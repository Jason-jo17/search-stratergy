import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load env vars explicitly
env_path = Path("d:/Downloads2/vectorprompt/app/.env")
load_dotenv(dotenv_path=env_path)

def inspect_db():
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        
        with open("d:/Downloads2/vectorprompt/db_inspection.txt", "w") as f:
            # Check for duplicates in student_profiles (by text or metadata->>name)
            f.write("--- Duplicate Check (student_profiles) ---\n")
            cur.execute("""
                SELECT text, COUNT(*) 
                FROM student_profiles 
                GROUP BY text 
                HAVING COUNT(*) > 1 
                LIMIT 20
            """)
            dups = cur.fetchall()
            if dups:
                f.write(f"Found {len(dups)} duplicate text entries in student_profiles:\n")
                for d in dups:
                    f.write(f"Count: {d[1]}, Text: {d[0][:50]}...\n")
            else:
                f.write("No text duplicates found in student_profiles.\n")
                
            # Check by name in metadata
            f.write("\n--- Duplicate Check (Name in Metadata) ---\n")
            cur.execute("""
                SELECT metadata->>'name', COUNT(*) 
                FROM student_profiles 
                GROUP BY metadata->>'name' 
                HAVING COUNT(*) > 1 
                LIMIT 20
            """)
            name_dups = cur.fetchall()
            if name_dups:
                 f.write(f"Found {len(name_dups)} duplicate names:\n")
                 for d in name_dups:
                     f.write(f"Count: {d[1]}, Name: {d[0]}\n")
            else:
                 f.write("No name duplicates found.\n")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
