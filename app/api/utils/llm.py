import os
import google.generativeai as genai
import json
from typing import List, Dict, Any

# Configure Gemini API
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def analyze_and_rerank(query: str, candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Use Gemini Pro to analyze candidates and re-rank them based on the query.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare candidates text for the prompt
        candidates_text = ""
        for i, cand in enumerate(candidates):
            # Use extracted metadata if available, otherwise raw text
            meta = cand.get('metadata', {})
            info = f"ID: {cand['id']}\n"
            if meta.get('name'):
                info += f"Name: {meta['name']}\n"
            if meta.get('role'):
                info += f"Role: {meta['role']}\n"
            if meta.get('skills_text'):
                info += f"Skills: {meta['skills_text']}\n"
            else:
                info += f"Text: {cand['text'][:500]}...\n" # Truncate text to save tokens
            
            candidates_text += f"--- Candidate {i} ---\n{info}\n"

        prompt = f"""
        You are an expert HR AI Assistant. Your task is to rank the following candidates based on their relevance to the user's search query.

        User Query: "{query}"

        Candidates:
        {candidates_text}

        Instructions:
        1. Analyze the User Query to understand the required skills, role, and experience.
        2. Evaluate each candidate against these requirements.
        3. Select the top {top_k} most relevant candidates.
        4. Rank them from most relevant to least relevant.
        5. Provide a brief "reasoning" for why each candidate was selected. Focus on "key insights" - specific skills or experience that match the query.

        Output Format:
        Return a JSON object with a key "ranked_candidates" containing a list of objects.
        Each object must have:
        - "original_index": The integer index of the candidate from the provided list (0-based).
        - "reasoning": A string explaining the match (e.g., "Strong match for Python and AWS due to 5 years experience...").
        
        Example JSON:
        {{
            "ranked_candidates": [
                {{ "original_index": 2, "reasoning": "Strong match for Python and AWS..." }},
                {{ "original_index": 0, "reasoning": "Good experience but lacks..." }}
            ]
        }}
        
        Ensure the output is valid JSON. Do not include markdown formatting like ```json.
        """

        response = model.generate_content(prompt)
        
        # Clean response text (remove markdown if present)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text)
        ranked_indices = result.get("ranked_candidates", [])
        
        # Reconstruct the list
        final_results = []
        for item in ranked_indices:
            idx = item.get("original_index")
            if idx is not None and 0 <= idx < len(candidates):
                candidate = candidates[idx]
                # Add the reasoning to the candidate metadata or top level
                # We'll add it to metadata so it shows up in the UI if we modify ResultCard, 
                # or just as a separate field.
                # Let's add it to a new field 'ai_reasoning'
                candidate['ai_reasoning'] = item.get("reasoning")
                final_results.append(candidate)
                
        return final_results

    except Exception as e:
        print(f"Error in Agentic Search: {e}")
        # Fallback: return original candidates
        return candidates[:top_k]

def decide_search_tool(query: str) -> Dict[str, Any]:
    """
    Decide which search tool to use based on the query.
    Returns: {"tool": "vector"|"keyword"|"pattern"|"filter", "parameters": {...}, "reasoning": "..."}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        You are an intelligent search router. Your goal is to select the best search tool for the user's query.

        Available Tools:
        1. "vector": Best for semantic queries, describing skills, roles, or general concepts (e.g., "python developer with cloud experience").
        2. "keyword": Best for specific, exact terms or names (e.g., "John Doe", "C++").
        3. "pattern": Best for finding structured patterns like emails or phone numbers (e.g., "email for...", "phone number of...").
        4. "filter": Best when the query explicitly asks for a specific role or skill without much else (e.g., "Role: Developer", "Skills: Python").

        User Query: "{query}"

        Instructions:
        1. Analyze the query intent.
        2. Select the single best tool.
        3. Extract necessary parameters for that tool.
           - For "pattern", extract "pattern_type" ("email" or "phone") or "custom_pattern".
           - For "filter", extract "role" and "skills" (list).
           - For "vector" and "keyword", just use the query.
        4. Provide a reasoning for your choice.

        Output JSON:
        {{
            "tool": "tool_name",
            "parameters": {{ ... }},
            "reasoning": "Explanation..."
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error in decide_search_tool: {e}")
        # Fallback to vector search
        return {"tool": "vector", "parameters": {"query": query}, "reasoning": "Fallback to Vector Search due to error."}

def analyze_query_intent(query: str) -> Dict[str, Any]:
    """
    Analyze query to extract filters and rewrite for better retrieval.
    Returns: {"rewritten_query": "...", "filters": {"role": "...", "skills": [...]}, "reasoning": "..."}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        You are a query understanding engine. Your goal is to optimize the user's search query.

        User Query: "{query}"

        Instructions:
        1. Extract any specific filters (Role, Skills, Location, Experience) mentioned in the query.
        2. Rewrite the query to be more effective for a semantic search engine (remove noise, focus on key concepts).
        3. Provide a reasoning for your analysis.

        Output JSON:
        {{
            "rewritten_query": "Optimized query string",
            "filters": {{
                "role": "extracted role or null",
                "skills": ["skill1", "skill2"],
                "location": "extracted location or null"
            }},
            "reasoning": "Explanation..."
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error in analyze_query_intent: {e}")
        return {"rewritten_query": query, "filters": {}, "reasoning": "Fallback: Original query used."}
