import asyncio
import os
from app.database_async import get_db_pool
from app.search.strategies.adaptive_fusion_strategy import AdaptiveFusionStrategy

async def check_db():
    print("Connecting to DB...")
    pool = await get_db_pool()
    
    # Check tables
    print("\n--- Checking Tables ---")
    tables = await pool.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    for t in tables:
        name = t['table_name']
        try:
            count = await pool.fetchval(f"SELECT COUNT(*) FROM {name}")
            print(f"Table '{name}': {count} rows")
        except Exception as e:
            print(f"Table '{name}': Error {e}")

    # Check 'user_profile_chunks' specifically
    print("\n--- Checking user_profile_chunks content ---")
    try:
        sample = await pool.fetch("SELECT chunk_type, content FROM user_profile_chunks LIMIT 3")
        for s in sample:
            print(f"Type: {s['chunk_type']}, Content: {s['content'][:50]}...")
    except Exception as e:
        print(f"Error reading chunks: {e}")

async def test_search():
    print("\n--- Testing Search 'python' ---")
    pool = await get_db_pool()
    # Mock Gemini (pass None) - verify if vector search failure causes empty results
    # Strategy handles None gemini client by skipping vector search
    strategy = AdaptiveFusionStrategy(pool, None) 
    
    try:
        results = await strategy.search("python", parameters={"bm25_weight": 1.0, "vector_weight": 0.0})
        print(f"Search Results (BM25 only): {results['total_results']}")
        for r in results['results'][:3]:
             print(f" - {r['student']['name']}: {r['scores']['final_score']}")
    except Exception as e:
         print(f"Search Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
    asyncio.run(test_search())
