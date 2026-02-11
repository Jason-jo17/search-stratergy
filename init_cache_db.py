import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Creating search_query_cache table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS search_query_cache (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            query_text TEXT NOT NULL,
            embedding VECTOR(768),
            strategy_used TEXT,
            results JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create an HNSW index for fast vector search
    print("Creating vector index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_cache_embedding 
        ON search_query_cache USING hnsw (embedding vector_cosine_ops);
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
