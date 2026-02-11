import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.api.utils.embeddings import get_embedding
from app.api.routes.search import get_db_connection

def check_cache(query: str, threshold: float = 0.95):
    """
    Checks the search_query_cache for a semantically similar query.
    Returns: {"results": [...], "insight": "..."} or None
    """
    print(f"DEBUG: Checking cache for query: '{query}'")
    try:
        embedding = get_embedding(query)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT results, insight, 1 - (embedding <=> %s) as similarity
            FROM search_query_cache
            WHERE 1 - (embedding <=> %s) > %s
            ORDER BY similarity DESC
            LIMIT 1
        """, (str(embedding), str(embedding), threshold))
        
        cached_row = cur.fetchone()
        cur.close()
        conn.close()
        
        if cached_row:
            print(f"DEBUG: Cache HIT! Similarity: {cached_row['similarity']:.4f}")
            results = cached_row['results']
            insight = cached_row.get('insight', '')
            
            # Add cache indicator
            for res in results:
                res['match_reason'] = f"[CACHE HIT] {res.get('match_reason', '')}"
                
            return {"results": results, "insight": insight}
            
        print("DEBUG: Cache MISS.")
        return None
        
    except Exception as e:
        print(f"Cache lookup failed: {e}")
        return None

def save_to_cache(query: str, results: list, strategy: str, insight: str = ""):
    """
    Saves the query, results, and insight to the search_query_cache.
    """
    try:
        embedding = get_embedding(query)
        conn = get_db_connection()
        cur = conn.cursor()
        print("DEBUG: Saving results to cache...")
        
        cur.execute("""
            INSERT INTO search_query_cache (query_text, embedding, strategy_used, results, insight)
            VALUES (%s, %s, %s, %s, %s)
        """, (query, str(embedding), strategy, json.dumps(results), insight))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to save to cache: {e}")
