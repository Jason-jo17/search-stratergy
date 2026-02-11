import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def verify_student_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        with open("verification_report.txt", "w", encoding="utf-8") as f:
            f.write("=== Student Data Verification Report ===\n\n")
            
            # 1. Count total records
            cur.execute("SELECT COUNT(*) FROM student_profiles")
            count = cur.fetchone()[0]
            f.write(f"Total Student Profiles: {count}\n\n")
            
            if count == 0:
                f.write("No records found.\n")
                return

            # 2. Fetch sample records (limit 5)
            f.write("=== Sample Records (First 5) ===\n\n")
            cur.execute("SELECT id, text, metadata FROM student_profiles LIMIT 5")
            rows = cur.fetchall()
            
            for i, row in enumerate(rows):
                record_id = row[0]
                text_content = row[1]
                metadata = row[2]
                
                f.write(f"--- Record {i+1} ---\n")
                f.write(f"ID: {record_id}\n")
                
                # Check for project-related keys in metadata
                f.write("Metadata Analysis:\n")
                if isinstance(metadata, dict):
                    has_projects = any(k.lower() in ['project', 'projects', 'title'] for k in metadata.keys())
                    f.write(f"  - Contains Project Info? {'YES' if has_projects else 'NO'}\n")
                    f.write(f"  - Keys: {', '.join(metadata.keys())}\n")
                    f.write(f"  - Full Metadata: {json.dumps(metadata, indent=2)}\n")
                else:
                    f.write(f"  - Raw Metadata: {metadata}\n")
                
                # Text preview
                preview = text_content[:200].replace('\n', ' ') + "..." if text_content else "None"
                f.write(f"Text Content (First 200 chars): {preview}\n\n")

        print("Verification report generated: verification_report.txt")
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_student_data()
