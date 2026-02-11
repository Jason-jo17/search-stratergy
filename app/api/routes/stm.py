from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from app.api.utils.stm_utils import generate_stm_chunks
from app.api.routes.search import get_embedding  # Reuse existing embedding function

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

class STMEvaluationRequest(BaseModel):
    student_id: str
    # Optional: Allow passing data directly if not in DB
    profile_data: Optional[Dict[str, Any]] = None 

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@router.post("/evaluate/{student_id}")
async def evaluate_student(student_id: str, request: STMEvaluationRequest):
    print(f"DEBUG: Received student_id: '{student_id}'")
    print(f"DEBUG: DATABASE_URL: {DATABASE_URL}")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. Collect Data
        # If profile_data is provided, use it. Otherwise, fetch from student_profiles
        student_data = request.profile_data
        
        if not student_data:
            cur.execute("SELECT metadata FROM student_profiles WHERE id = %s", (student_id,))
            row = cur.fetchone()
            if not row:
                # DEBUG: Check what IS in the DB
                cur.execute("SELECT id FROM student_profiles LIMIT 1")
                sample = cur.fetchone()
                sample_id = sample['id'] if sample else "TABLE EMPTY"
                raise HTTPException(status_code=404, detail=f"Student not found. ID: {student_id}, Sample: {sample_id}")
            student_data = row['metadata']
            # Use the data exactly as is, do not inject dummy data
            pass

        # 2. AI Processing (Gemini)
        chunks = generate_stm_chunks(student_data)

        # 3. Vectorization & Storage
        # Delete old chunks for this user
        cur.execute("DELETE FROM user_profile_chunks WHERE user_id = %s", (student_id,))
        
        # Process each chunk type
        for chunk_type, content in chunks.items():
            if not content:
                continue
            
            # Handle list content (projects, awards)
            if isinstance(content, list):
                for item in content:
                    embedding = get_embedding(item)
                    cur.execute("""
                        INSERT INTO user_profile_chunks (user_id, chunk_type, content, embedding)
                        VALUES (%s, %s, %s, %s)
                    """, (student_id, chunk_type, item, str(embedding)))
            else:
                # Handle string content (personal, skills)
                embedding = get_embedding(content)
                cur.execute("""
                    INSERT INTO user_profile_chunks (user_id, chunk_type, content, embedding)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, chunk_type, content, str(embedding)))

        conn.commit()
        return {"status": "success", "message": "STM evaluation completed", "chunks": chunks}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
