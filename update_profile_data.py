import psycopg2
import os
import json
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

SAMPLE_DATA = {
    "id": "34d6caa9-d9e9-4de9-bb5b-0eb4be3d08d4",
    "cgpa": 0,
    "name": "R S PRATHVIR",
    "email": "5d46ee75-aa1a-4160-9342-7b25dccdf9af@inpulse.in",
    "branch": "ECE",
    "skills": [
        {
            "tool_id": "0efbfa32-7499-4fa2-b44a-10abebf2fdcf",
            "tool_name": "Netlify",
            "domain_name": "Software Development",
            "category_name": "DevOps & Deployment",
            "evaluation_count": 1,
            "evaluation_types": "external_stm_scores",
            "subcategory_name": "Hosting Platforms",
            "evaluation_resources": "a338c0f4-cfc2-479d-b601-cbc57d7ef42b",
            "average_normalized_score": 6
        },
        {
            "tool_id": "5b8ab9a0-8a88-4d51-97cf-7657f3bc2700",
            "tool_name": "Python (Tkinter)",
            "domain_name": "Software Development",
            "category_name": "Programming Languages",
            "evaluation_count": 1,
            "evaluation_types": "external_stm_scores",
            "subcategory_name": "Desktop Applications",
            "evaluation_resources": "a338c0f4-cfc2-479d-b601-cbc57d7ef42b",
            "average_normalized_score": 10
        },
        {
            "tool_id": "712c6ae6-daf9-4528-90a6-0f2c2ed4bd44",
            "tool_name": "FastAPI",
            "domain_name": "Software Development",
            "category_name": "Programming Languages",
            "evaluation_count": 1,
            "evaluation_types": "external_stm_scores",
            "subcategory_name": "Backend (Server-side)",
            "evaluation_resources": "a338c0f4-cfc2-479d-b601-cbc57d7ef42b",
            "average_normalized_score": 5
        }
    ],
    "semester": "7",
    "tenant_id": "eb9d49bb-bdb9-43c0-9741-febeeca7224a",
    "thumbnail": "",
    "portfolios": [],
    "similarity": 0,
    "tenant_name": "Sahyadri College Of Engineering & Management (Autonomous)",
    "no_of_projects": 0,
    "tenant_address": "Sahyadri Campus, Mangaluru, Adyar, Karnataka 575007",
    "no_of_internships": 0,
    "events_participated": [],
    "content_for_embedding": "Candidate: R S PRATHVIR | Role: ECE | Location: Mangaluru | Exp: 7th Semester"
}

def update_profile():
    try:
        with open("current_id.txt", "r") as f:
            user_id = f.read().strip()
    except:
        print("Could not read current_id.txt")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print(f"Updating metadata for User ID: {user_id}")
    cur.execute("UPDATE student_profiles SET metadata = %s WHERE id = %s", (json.dumps(SAMPLE_DATA), user_id))
    conn.commit()
    print("Update successful.")
    conn.close()

if __name__ == "__main__":
    update_profile()
