import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a read query and return results as a list of dicts"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        conn.close()
