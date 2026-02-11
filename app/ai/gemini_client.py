import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from app directory if not loaded
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment")

    async def embed_content(self, model: str, content: str, task_type: str = "retrieval_query"):
        """
        Generate embedding for content.
        Note: The google-generativeai library is currently synchronous for embeddings.
        We wrap it or just call it directly since it's an HTTP call.
        For true async, we'd use aiohttp, but strictly wrapping is fine for this scope.
        """
        try:
            result = genai.embed_content(
                model=model,
                content=content,
                task_type=task_type,
                output_dimensionality=768
            )
            return result
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise e

async def get_gemini_client():
    """Dependency for FastAPI"""
    return GeminiClient()
