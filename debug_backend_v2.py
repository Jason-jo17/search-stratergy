import asyncio
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath("d:/Downloads2/vectorprompt"))

# Load env vars
env_path = Path("d:/Downloads2/vectorprompt/app/.env")
load_dotenv(dotenv_path=env_path)

from app.api.routes.search import search_keyword, search_vector, search_agentic, search_fuzzy, SearchRequest
from app.api.utils.database import get_db_connection

async def test_search():
    print("Testing Database Connection...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM student_profiles")
            count = cur.fetchone()[0]
            print(f"Database connected. Total student profiles: {count}")
        conn.close()
    except Exception as e:
        print(f"Database Connection Failed: {e}")
        return

    req = SearchRequest(query="python developer", limit=5)

    print("\nTesting Keyword Search (student_profiles)...")
    try:
        res = await search_keyword(req)
        print(f"Keyword Results: {len(res['results'])}")
        if res['results']:
            print(f"Top result: {res['results'][0]['metadata'].get('name')}")
    except Exception as e:
        print(f"Keyword Search Failed: {e}")

    print("\nTesting Vector Search (student_profiles)...")
    try:
        res = await search_vector(req)
        print(f"Vector Results: {len(res['results'])}")
        if res['results']:
            print(f"Top result: {res['results'][0]['metadata'].get('name')}")
    except Exception as e:
        print(f"Vector Search Failed: {e}")

    print("\nTesting Fuzzy Search (student_profiles)...")
    try:
        res = await search_fuzzy(req)
        print(f"Fuzzy Results: {len(res['results'])}")
    except Exception as e:
        print(f"Fuzzy Search Failed: {e}")

    print("\nTesting Agentic Search (student_profiles)...")
    try:
        res = await search_agentic(req)
        print(f"Agentic Results: {len(res['results'])}")
    except Exception as e:
        print(f"Agentic Search Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
