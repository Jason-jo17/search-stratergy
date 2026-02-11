import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def list_tables():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        with open("tables_report.txt", "w", encoding="utf-8") as f:
            # Get all tables in public schema
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            
            if not tables:
                f.write("No tables found in public schema.")
                return

            f.write(f"Found {len(tables)} tables:\n\n")

            for table in tables:
                table_name = table[0]
                f.write(f"=== Table: {table_name} ===\n")
                
                # Get columns for this table
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                columns = cur.fetchall()
                
                # Format nicely
                f.write(f"{'Column':<30} {'Type':<20} {'Nullable':<10}\n")
                f.write("-" * 60 + "\n")
                for col in columns:
                    f.write(f"{col[0]:<30} {col[1]:<20} {col[2]:<10}\n")
                f.write("\n\n")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
