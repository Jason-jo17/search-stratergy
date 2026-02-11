import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_stm_chunks(student_data: dict) -> dict:
    """
    Uses Gemini to process student data into structured chunks (Personal, Skills, Projects, Awards).
    """
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are a Strict Semantic Serializer. Your job is to transform unstructured student data into structured, searchable text chunks for a vector database.
    
    Input Data:
    {json.dumps(student_data, indent=2)}

    Instructions:
    1. Analyze the input data.
       - **Personal**: Extract 'name', 'branch', 'semester', 'tenant_address' (Location). If 'tenant_address' is missing, look for 'location' or 'address'.
       - **Skills**: Iterate through the 'skills' array. Each item is an object. Extract 'tool_name' (Skill) and 'average_normalized_score' (Score). Group by 'domain_name'. Format: "Skills-[Domain]: [tool_name] ([average_normalized_score]), ..."
       - **Projects**: Look for 'portfolios' or 'projects'. If empty, return an empty list. If present, format: "Projects: [Title] (Desc: [Description] | Stack: [Tech Stack])"
       - **Awards**: Look for 'events_participated' or 'awards'. If empty, return an empty list.
    
    2. Output strictly valid JSON in the following format:
    {{
      "personal": "Candidate: [Name] | Role: [Branch] | Location: [Address] | Exp: [Semester]",
      "skills": "Skills-[Domain]: [Skill] ([Score]), ...",
      "projects": ["string", "string"],
      "awards": ["string", "string"]
    }}
    
    Do not add any markdown formatting or explanations. Just the JSON.
    """

    try:
        response = model.generate_content(prompt)
        # Clean response if it contains markdown code blocks
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        import traceback
        with open("debug_stm_utils.log", "a") as f:
            f.write(f"Error generating STM chunks: {e}\n")
            f.write(traceback.format_exc())
            f.write("\n----------------\n")
        print(f"Error generating STM chunks: {e}")
        return {
            "personal": "",
            "skills": "",
            "projects": [],
            "awards": []
        }
