import psycopg2
import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Loaded DATABASE_URL: {DATABASE_URL}") # Debug print

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Creating user_profile_chunks table...")
    
    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profile_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL, -- references student_profiles(id) if strictly enforced, but we might want flexibility
            chunk_type VARCHAR(50) NOT NULL,
            content TEXT,
            embedding VECTOR(768),
            search_vector TSVECTOR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, chunk_type)
        );
    """)

    # Create index for vector search
    print("Creating vector index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_profile_chunks_embedding 
        ON user_profile_chunks 
        USING hnsw (embedding vector_cosine_ops);
    """)

    # Create index for full-text search
    print("Creating FTS index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_profile_chunks_search_vector 
        ON user_profile_chunks 
        USING GIN (search_vector);
    """)
    
    # Trigger to update search_vector on insert/update
    print("Creating FTS update trigger...")
    cur.execute("""
        CREATE OR REPLACE FUNCTION user_profile_chunks_tsvector_trigger() 
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', coalesce(NEW.content, ''));
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS tsvectorupdate ON user_profile_chunks;
        
        CREATE TRIGGER tsvectorupdate 
        BEFORE INSERT OR UPDATE ON user_profile_chunks 
        FOR EACH ROW EXECUTE FUNCTION user_profile_chunks_tsvector_trigger();
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
