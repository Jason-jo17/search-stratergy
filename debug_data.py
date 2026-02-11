import psycopg2
from app.api.routes.search import get_db_connection

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM student_profiles WHERE text ILIKE '%python%'")
    print(f"Python matches: {cur.fetchone()}")
    cur.execute("SELECT COUNT(*) FROM student_profiles")
    print(f"Total profiles: {cur.fetchone()}")
    conn.close()
except Exception as e:
    print(e)
