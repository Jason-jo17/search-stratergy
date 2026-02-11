import os
import google.generativeai as genai
from typing import List

# Configure Gemini API
# It's better to configure this at app startup, but for now we'll do it here or assume env var is set
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using Gemini API"""
    try:
        # Use the text-embedding-004 model as requested
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []
