import os
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from app directory if not loaded
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

import ssl

class DatabasePool:
    _instance = None
    
    @classmethod
    async def get_pool(cls):
        if cls._instance is None:
            try:
                # Create SSL context for Neon/Postgres
                ctx = ssl.create_default_context(cafile="")
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                cls._instance = await asyncpg.create_pool(DATABASE_URL, ssl=ctx)
            except Exception as e:
                print(f"Error creating asyncpg pool: {e}")
                raise e
        return cls._instance
    
    @classmethod
    async def close_pool(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

async def get_db_pool():
    """Dependency for FastAPI to get DB pool"""
    pool = await DatabasePool.get_pool()
    return pool
