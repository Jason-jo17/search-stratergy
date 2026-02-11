import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath("d:/Downloads2/vectorprompt"))

# Load env vars
load_dotenv("d:/Downloads2/vectorprompt/app/.env")

from app.api.routes.search import search_keyword, search_vector, search_agentic, SearchRequest
from app.api.utils.database import get_db_connection

async def test_search():
    print("Testing Database Connection...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM n8n_vectors")
            count = cur.fetchone()[0]
            print(f"Database connected. Total records: {count}")
        conn.close()
    except Exception as e:
        print(f"Database Connection Failed: {e}")
        return

    req = SearchRequest(query="python developer", limit=5)

    print("\nTesting Keyword Search...")
    try:
        res = await search_keyword(req)
        print(f"Keyword Results: {len(res['results'])}")
    except Exception as e:
        print(f"Keyword Search Failed: {e}")

    print("\nTesting Vector Search...")
    try:
        res = await search_vector(req)
        print(f"Vector Results: {len(res['results'])}")
    except Exception as e:
        print(f"Vector Search Failed: {e}")

    print("\nTesting Agentic Search...")
    try:
        res = await search_agentic(req)
        print(f"Agentic Results: {len(res['results'])}")
    except Exception as e:
        print(f"Agentic Search Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
