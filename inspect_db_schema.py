from app.api.utils.database import execute_query
import json
from dotenv import load_dotenv
import os

load_dotenv(r"d:\Downloads2\vectorprompt\.env")

def inspect_schema():
    print("--- Inspecting student_profiles Schema ---")
    try:
        # Check columns
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'student_profiles';
        """
        columns = execute_query(query)
        print(json.dumps(columns, indent=2))
        
        # Check 1 row
        print("\n--- Inspecting 1 Row ---")
        row_query = "SELECT id, left(text, 50) as text_preview, metadata FROM student_profiles LIMIT 1"
        rows = execute_query(row_query)
        print(json.dumps(rows, indent=2, default=str))

        # Check total count
        print("\n--- Total Count ---")
        count = execute_query("SELECT count(*) FROM student_profiles")
        print(count)
        
    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    inspect_schema()
