import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def list_models():
    try:
        with open("available_models.txt", "w") as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
                    print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
