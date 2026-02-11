from fastapi import APIRouter
from app.api.utils.database import execute_query

router = APIRouter()

@router.get("/schema")
def debug_schema():
    """Inspect student_profiles table schema"""
    try:
        # Schema
        schema_query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'student_profiles';
        """
        columns = execute_query(schema_query)
        
        # Row count
        count = execute_query("SELECT count(*) FROM student_profiles")
        
        # Sample row
        sample = execute_query("SELECT id, left(text, 50) as text, metadata FROM student_profiles LIMIT 1")
        
        return {
            "columns": columns,
            "count": count,
            "sample": sample
        }
    except Exception as e:
        return {"error": str(e)}
