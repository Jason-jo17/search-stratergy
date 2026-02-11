from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.api.utils.database import execute_query
from app.api.utils.embeddings import get_embedding
from app.api.utils.nlp import (
    tokenize_query, 
    extract_candidate_info, 
    highlight_matches, 
    calculate_keyword_score
)
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from app directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    # Hybrid params
    vector_weight: float = 0.5
    rrf_k: int = 60
    # Filter params
    skills: List[str] = []
    role: Optional[str] = None
    min_skill_score: float = 0.0
    # Pattern params
    pattern_type: Optional[str] = None
    custom_pattern: Optional[str] = None
    # Skills params
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_score: float = 0.0
    # Compare params
    strategies: List[str] = []

@router.post("/keyword")
async def search_keyword(request: SearchRequest):
    """
    Strategy 1: Keyword/Lexical Search
    NLP Approach: Tokenize query, remove stop words, LIKE matching
    Ranking: Count keyword matches
    """
    keywords = tokenize_query(request.query)
    if not keywords:
        return {"results": []}
        
    # Construct SQL query for keyword matching
    # We'll use ILIKE for each keyword
    conditions = []
    params = []
    for keyword in keywords:
        conditions.append("text ILIKE %s")
        params.append(f"%{keyword}%")
        
    where_clause = " OR ".join(conditions)
    
    sql = f"""
        SELECT id, text, metadata
        FROM student_profiles
        WHERE {where_clause}
        LIMIT %s
    """
    params.append(request.limit)
    
    results = execute_query(sql, tuple(params))
    
    # Post-processing for scoring and highlighting
    processed_results = []
    for row in results:
        score = calculate_keyword_score(row['text'], keywords)
        highlighted = highlight_matches(row['text'], keywords)
        
        # Extract info if metadata is empty or missing keys
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": score,
            "highlighted_text": highlighted,
            "matched_keywords": keywords,
            "match_reason": f"Contains keywords: {', '.join(keywords)}"
        })
        
    # Sort by score
    processed_results.sort(key=lambda x: x['score'], reverse=True)
    
    return {"results": processed_results}

@router.post("/vector")
async def search_vector(request: SearchRequest):
    """
    Strategy 2: Vector/Semantic Search
    NLP Approach: Generate embedding, Cosine Similarity
    """
    import traceback
    try:
        # Clean query to remove conversational noise ("give me someone with...")
        # This focuses the embedding on the core skills/role
        keywords = tokenize_query(request.query)
        if keywords:
            cleaned_query = " ".join(keywords)
        else:
            cleaned_query = request.query
            
        embedding = get_embedding(cleaned_query)
        if not embedding:
            return {"results": []}
        
        # pgvector cosine distance operator is <=>
        # We want similarity, so we can order by distance ASC
        # 1 - distance = similarity (roughly, for normalized vectors)
        # Changed table to student_profiles and column to embedding
        sql = """
            SELECT id, text, metadata, 1 - (embedding <=> %s) as score
            FROM student_profiles
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        
        results = execute_query(sql, (str(embedding), str(embedding), request.limit))
        
        # Extract info for display
        processed_results = []
        for row in results:
            meta = row['metadata'] or {}
            # student_profiles metadata is already rich, but we ensure fallback
            if not meta.get('name') or not meta.get('role'):
                extracted = extract_candidate_info(row['text'])
                meta.update(extracted)
                
            processed_results.append({
                "id": row['id'],
                "text": row['text'],
                "metadata": meta,
                "score": row['score'],
                "match_reason": f"High semantic similarity ({row['score']:.2f}) to '{cleaned_query}'"
            })
            
        return {"results": processed_results}
    except Exception as e:
        print(f"ERROR in search_vector: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ... (Hybrid search uses search_vector, so it inherits the fix)

# ...

@router.post("/fuzzy")
async def search_fuzzy(request: SearchRequest):
    """
    Strategy 8: Fuzzy Search (Trigram)
    Use pg_trgm for approximate matching
    """
    # Clean query to get the most significant terms
    keywords = tokenize_query(request.query)
    if not keywords:
        return {"results": []}
        
    # If query is long (natural language), use the most significant keywords joined
    if len(request.query.split()) > 3:
        search_term = " ".join(keywords)
    else:
        search_term = request.query

    # similarity() returns a value between 0 and 1
    # We filter by a threshold (default 0.1 to get some results, can be tuned)
    # OPTIMIZATION: Instead of searching the full text (which dilutes the score),
    # we search against a concatenated string of Role + Skills + Name from metadata if available.
    # This makes the document shorter and denser, improving fuzzy match scores for skills.
    sql = """
        SELECT id, text, metadata, 
               similarity(
                   COALESCE(metadata->>'role', '') || ' ' || 
                   COALESCE(metadata->>'skills_text', '') || ' ' || 
                   COALESCE(metadata->>'name', '') || ' ' || 
                   text, 
               %s) as score
        FROM student_profiles
        WHERE 
            COALESCE(metadata->>'role', '') || ' ' || 
            COALESCE(metadata->>'skills_text', '') || ' ' || 
            COALESCE(metadata->>'name', '') || ' ' || 
            text 
            %% %s
        ORDER BY score DESC
        LIMIT %s
    """
    
    results = execute_query(sql, (search_term, search_term, request.limit))
    
    processed_results = []
    for row in results:
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": row['score'],
            "match_reason": f"Fuzzy similarity ({row['score']:.2f}) to '{search_term}'"
        })
    return {"results": processed_results}

@router.post("/hybrid")
async def search_hybrid(request: SearchRequest):
    """
    Strategy 3: Hybrid Search (RRF)
    Combine vector + keyword using Reciprocal Rank Fusion
    """
    # 1. Get Vector Results
    vector_results = await search_vector(request)
    vector_results = vector_results["results"]
    
    # 2. Get Keyword Results
    keyword_results = await search_keyword(request)
    keyword_results = keyword_results["results"]
    
    # 3. RRF Fusion
    rrf_scores = {}
    
    # Process vector results
    for rank, res in enumerate(vector_results):
        doc_id = res['id']
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {"data": res, "score": 0, "reasons": []}
        rrf_scores[doc_id]["score"] += 1 / (request.rrf_k + rank + 1)
        rrf_scores[doc_id]["reasons"].append(f"Vector Rank #{rank+1}")
        
    # Process keyword results
    for rank, res in enumerate(keyword_results):
        doc_id = res['id']
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {"data": res, "score": 0, "reasons": []}
        rrf_scores[doc_id]["score"] += 1 / (request.rrf_k + rank + 1)
        rrf_scores[doc_id]["reasons"].append(f"Keyword Rank #{rank+1}")
        
    # Sort by RRF score
    final_results = sorted(rrf_scores.values(), key=lambda x: x['score'], reverse=True)
    
    # Format output
    output = []
    for item in final_results[:request.limit]:
        data = item["data"]
        data["match_reason"] = f"Hybrid Match: {', '.join(item['reasons'])}"
        output.append(data)

    return {"results": output}

@router.post("/filter")
async def search_filter(request: SearchRequest):
    """
    Strategy 4: Metadata Filtering (Simulated via Text Regex)
    Filter by extracted metadata: skills, role, location, experience
    Since metadata column might be empty, we use regex on text column.
    """
    # Build dynamic SQL query based on filters
    conditions = ["1=1"] # Default true condition
    params = []
    reasons = []
    
    if request.role:
        # Regex to match "Role: ... request.role ..."
        # Case insensitive match
        conditions.append("text ~* %s")
        params.append(f"Role:.*{request.role}")
        reasons.append(f"Role matches '{request.role}'")
        
    if request.skills:
        for skill in request.skills:
            # Regex to match "Skills: ... skill ..."
            conditions.append("text ~* %s")
            params.append(f"Skills:.*{skill}")
            reasons.append(f"Skill matches '{skill}'")
            
    where_clause = " AND ".join(conditions)
    
    sql = f"""
        SELECT id, text, metadata
        FROM student_profiles
        WHERE {where_clause}
        LIMIT %s
    """
    params.append(request.limit)
    
    results = execute_query(sql, tuple(params))
    
    # Extract info for display
    processed_results = []
    for row in results:
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": 1.0, # Default score for filter
            "match_reason": f"Filters matched: {', '.join(reasons)}"
        })
        
    return {"results": processed_results}

@router.post("/pattern")
async def search_pattern(request: SearchRequest):
    """
    Strategy 5: Pattern Matching (Regex)
    Use regex to find specific patterns
    """
    pattern = request.custom_pattern
    if not pattern and request.pattern_type:
        # Predefined patterns
        if request.pattern_type == "email":
            pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        elif request.pattern_type == "phone":
            pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
            
    if not pattern:
        return {"results": []}
        
    # Use POSIX regex operator ~ in PostgreSQL
    sql = """
        SELECT id, text, metadata
        FROM student_profiles
        WHERE text ~ %s
        LIMIT %s
    """
    
    results = execute_query(sql, (pattern, request.limit))
    
    # Extract info for display
    processed_results = []
    for row in results:
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": 1.0,
            "match_reason": f"Matches pattern: {request.pattern_type or 'Custom Regex'}"
        })
        
    return {"results": processed_results}

@router.post("/compare")
async def search_compare(request: SearchRequest):
    """
    Comparison Endpoint
    Run multiple strategies and return combined results.
    Includes Query Optimization step.
    """
    from app.api.utils.llm import analyze_query_intent
    
    try:
        results = {}
        
        # --- 1. Query Optimization ---
        # We optimize the query once and use it for relevant strategies
        print(f"DEBUG: Optimizing query: '{request.query}'")
        analysis = analyze_query_intent(request.query)
        optimized_query = analysis.get("rewritten_query", request.query)
        filters = analysis.get("filters", {})
        optimization_insight = f"Optimized: '{request.query}' -> '{optimized_query}'"
        print(f"DEBUG: {optimization_insight}")
        
        # Create a request object with the optimized query
        optimized_req = request.copy()
        optimized_req.query = optimized_query
        
        # --- 2. Execute Strategies ---
        
        if "keyword" in request.strategies:
            # Keyword search might benefit from the original query if it's specific names, 
            # but optimized query removes noise. Let's use optimized.
            res = await search_keyword(optimized_req)
            results["keyword"] = res["results"]
            
        if "vector" in request.strategies:
            res = await search_vector(optimized_req)
            results["vector"] = res["results"]
            
        if "hybrid" in request.strategies:
            res = await search_hybrid(optimized_req)
            results["hybrid"] = res["results"]

        if "fts" in request.strategies:
            res = await search_fts(optimized_req)
            results["fts"] = res["results"]

        if "fuzzy" in request.strategies:
            # Fuzzy might be better with original if it's a typo, but optimized is generally safer
            res = await search_fuzzy(optimized_req)
            results["fuzzy"] = res["results"]
            
        if "agentic" in request.strategies:
            res = await search_agentic(request) # Agentic does its own re-ranking
            results["agentic"] = res["results"]
            
        if "agentic_tool" in request.strategies:
            res = await search_agentic_tool(request) # Has its own logic
            results["agentic_tool"] = res["results"]
            
        if "agentic_analysis" in request.strategies:
            res = await search_agentic_analysis(request) # Has its own analysis
            results["agentic_analysis"] = res["results"]
            
        if "stm" in request.strategies:
            # STM benefits from optimized query for embedding
            res = await search_stm(optimized_req)
            results["stm"] = res["results"]
            
        if "bm25" in request.strategies:
            res = await search_bm25(optimized_req)
            results["bm25"] = res["results"]
            
        return {"results": results, "optimization": analysis}
        
    except Exception as e:
        import traceback
        print(f"Error in search_compare: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bm25")
async def search_bm25(request: SearchRequest):
    """
    Strategy 11: BM25 Probabilistic Search
    Best for: Exact keyword matching with smart term weighting
    """
    import traceback
    try:
        from app.api.utils.bm25 import BM25Search as BM25Searcher
        print(f"DEBUG: BM25 Request: {request}", flush=True)
        
        searcher = BM25Searcher()
        results = searcher.search(
            query=request.query,
            top_k=request.limit
        )
        return results
    except Exception as e:
        print(f"ERROR in search_bm25: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_query(request: SearchRequest):
    """
    Query Optimization Endpoint
    Analyzes the query and returns the optimized version + filters.
    """
    from app.api.utils.llm import analyze_query_intent
    
    try:
        analysis = analyze_query_intent(request.query)
        return {"optimization": analysis}
    except Exception as e:
        print(f"Error in optimize_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fts")
async def search_fts(request: SearchRequest):
    """
    Strategy 7: Full Text Search (FTS)
    Use PostgreSQL's native text search
    """
    # Clean query: remove stop words, etc.
    keywords = tokenize_query(request.query)
    if not keywords:
        return {"results": []}
        
    # Construct a more flexible TS query: "term1 | term2 | term3"
    # This allows finding documents that contain ANY of the significant terms
    ts_query_str = " | ".join(keywords)
    
    # plainto_tsquery handles simple text, websearch_to_tsquery handles operators like "quoted text" or -exclude
    # We use to_tsquery with our constructed OR string for maximum flexibility on natural language
    sql = """
        SELECT id, text, metadata,
               ts_rank(to_tsvector('english', text), to_tsquery('english', %s)) as score
        FROM student_profiles
        WHERE to_tsvector('english', text) @@ to_tsquery('english', %s)
        ORDER BY score DESC
        LIMIT %s
    """
    
    results = execute_query(sql, (ts_query_str, ts_query_str, request.limit))
    
    # Add highlighting manually or use ts_headline (optional, keeping it simple for now)
    processed_results = []
    for row in results:
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": row['score'],
            "match_reason": f"Full-text match for terms: {', '.join(keywords)}"
        })
    return {"results": processed_results}

@router.post("/fuzzy")
async def search_fuzzy(request: SearchRequest):
    """
    Strategy 8: Fuzzy Search (Trigram)
    Use pg_trgm for approximate matching
    """
    # Clean query to get the most significant terms
    # Fuzzy matching a whole sentence against a whole document usually yields low scores.
    # We'll try to match the *joined keywords* or just the raw query if it's short.
    
    keywords = tokenize_query(request.query)
    if not keywords:
        return {"results": []}
        
    # If query is long (natural language), use the most significant keywords joined
    # Otherwise use the raw query (for things like "pythn" -> "python")
    if len(request.query.split()) > 3:
        search_term = " ".join(keywords)
    else:
        search_term = request.query

    # similarity() returns a value between 0 and 1
    # We filter by a threshold (default 0.1 to get some results, can be tuned)
    sql = """
        SELECT id, text, metadata, similarity(text, %s) as score
        FROM student_profiles
        WHERE text %% %s
        ORDER BY score DESC
        LIMIT %s
    """
    
    results = execute_query(sql, (search_term, search_term, request.limit))
    
    processed_results = []
    for row in results:
        meta = row['metadata'] or {}
        if not meta.get('name') or not meta.get('role'):
            extracted = extract_candidate_info(row['text'])
            meta.update(extracted)
            
        processed_results.append({
            "id": row['id'],
            "text": row['text'],
            "metadata": meta,
            "score": row['score'],
            "match_reason": f"Fuzzy similarity ({row['score']:.2f}) to '{search_term}'"
        })
    return {"results": processed_results}

@router.post("/agentic")
async def search_agentic(request: SearchRequest):
    """
    Strategy 9: Agentic Search (LLM Re-ranking)
    1. Retrieve broad set of candidates using Hybrid Search
    2. Use Gemini Pro to analyze and re-rank
    """
    from app.api.utils.llm import analyze_and_rerank
    
    # 1. Get Broad Results (Hybrid)
    # We ask for more results than the final limit to give the LLM choices
    broad_limit = max(20, request.limit * 2)
    
    # Create a temporary request for hybrid search
    hybrid_request = request.copy()
    hybrid_request.limit = broad_limit
    
    hybrid_response = await search_hybrid(hybrid_request)
    candidates = hybrid_response["results"]
    
    if not candidates:
        return {"results": []}
        
    # 2. LLM Re-ranking
    ranked_results = analyze_and_rerank(request.query, candidates, request.limit)
    
    return {"results": ranked_results}

@router.post("/agentic_tool")
async def search_agentic_tool(request: SearchRequest):
    """
    Strategy 10: Agentic Search (Tool Use) with Semantic Caching
    1. Check Cache (Similarity > 0.95)
    2. If miss, LLM decides tool, executes, and re-ranks.
    3. Save to Cache.
    """
    from app.api.utils.llm import decide_search_tool, analyze_and_rerank
    from app.api.utils.caching import check_cache, save_to_cache
    
    # --- 1. Cache Lookup ---
    cached = check_cache(request.query)
    if cached:
        return {"results": cached["results"]}

    # --- 2. Agentic Search (Existing Logic) ---
    
    # 2.1 Decide Tool
    decision = decide_search_tool(request.query)
    tool = decision.get("tool", "vector")
    params = decision.get("parameters", {})
    reasoning = decision.get("reasoning", "Defaulting to vector search.")
    
    # 2.2 Execute Selected Tool
    candidates = []
    tool_insight = ""
    
    if tool == "keyword":
        tool_req = request.copy()
        tool_req.query = params.get("query", request.query)
        res = await search_keyword(tool_req)
        candidates = res["results"]
        tool_insight = f"Agent selected Keyword Search. Reason: {reasoning}"
        
    elif tool == "pattern":
        tool_req = request.copy()
        tool_req.pattern_type = params.get("pattern_type")
        tool_req.custom_pattern = params.get("custom_pattern")
        res = await search_pattern(tool_req)
        candidates = res["results"]
        tool_insight = f"Agent selected Pattern Search ({params.get('pattern_type')}). Reason: {reasoning}"
        
    elif tool == "filter":
        tool_req = request.copy()
        tool_req.role = params.get("role")
        tool_req.skills = params.get("skills")
        res = await search_filter(tool_req)
        candidates = res["results"]
        tool_insight = f"Agent selected Metadata Filter. Reason: {reasoning}"
        
    else: # Default to vector
        tool_req = request.copy()
        tool_req.query = params.get("query", request.query)
        res = await search_vector(tool_req)
        candidates = res["results"]
        tool_insight = f"Agent selected Vector Search. Reason: {reasoning}"
    
    if not candidates:
        return {"results": []}

    # 2.3 Re-rank results
    ranked_results = analyze_and_rerank(request.query, candidates[:20], request.limit)
    
    # Add the tool decision insight
    for res in ranked_results:
        current_reason = res.get("ai_reasoning", "")
        res["ai_reasoning"] = f"[{tool_insight}] {current_reason}"

    # --- 3. Save to Cache ---
    save_to_cache(request.query, ranked_results, tool, tool_insight)
        
    return {"results": ranked_results}

@router.post("/agentic_analysis")
async def search_agentic_analysis(request: SearchRequest):
    """
    Strategy 11: Agentic Search (Query Analysis)
    LLM analyzes query to extract filters and rewrite, then searches (Hybrid) and re-ranks.
    """
    from app.api.utils.llm import analyze_query_intent, analyze_and_rerank
    from app.api.utils.caching import check_cache, save_to_cache
    
    # --- 1. Cache Lookup ---
    cached = check_cache(request.query)
    if cached:
        return {"results": cached["results"]}
    
    # --- 2. Analyze Query ---
    analysis = analyze_query_intent(request.query)
    rewritten_query = analysis.get("rewritten_query", request.query)
    filters = analysis.get("filters", {})
    reasoning = analysis.get("reasoning", "")
    
    # 3. Execute Search (Hybrid with Filters)
    # We'll use Vector search with the rewritten query as the primary retrieval
    search_req = request.copy()
    search_req.query = rewritten_query
    
    res = await search_vector(search_req)
    candidates = res["results"]
    
    if not candidates:
        return {"results": []}
        
    # 4. Re-rank
    ranked_results = analyze_and_rerank(request.query, candidates[:20], request.limit)
    
    analysis_insight = f"Query Analysis: Rewrote '{request.query}' to '{rewritten_query}'. Reason: {reasoning}"
    
    for res in ranked_results:
        current_reason = res.get("ai_reasoning", "")
        res["ai_reasoning"] = f"[{analysis_insight}] {current_reason}"
        
    # --- 5. Save to Cache ---
    save_to_cache(request.query, ranked_results, "agentic_analysis", analysis_insight)
        
    return {"results": ranked_results}

@router.post("/stm")
async def search_stm(request: SearchRequest):
    """
    Strategy 12: STM (Short Term Memory) Search
    Simulated STM search for demonstration.
    """
    # Placeholder implementation since the original seems corrupted/missing
    # In a real scenario, this would interact with a specific STM module
    
    # For now, we'll do a vector search and add some "STM" flavor
    from app.api.utils.embeddings import get_embedding
    
    try:
        # 1. Get embedding for the query
        embedding = get_embedding(request.query)
        if not embedding:
            return {"results": []}
            
        # 2. Search (using vector search logic for now)
        sql = """
            SELECT id, text, metadata, 1 - (embedding <=> %s) as score
            FROM student_profiles
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        results = execute_query(sql, (str(embedding), str(embedding), request.limit))
        
        processed_results = []
        for row in results:
            meta = row['metadata'] or {}
            if not meta.get('name') or not meta.get('role'):
                extracted = extract_candidate_info(row['text'])
                meta.update(extracted)
                
            processed_results.append({
                "id": row['id'],
                "text": row['text'],
                "metadata": meta,
                "score": row['score'],
                "match_reason": f"STM Recall: High activation for '{request.query}'"
            })
            
        return {"results": processed_results}

    except Exception as e:
        print(f"Error in search_stm: {e}")
        raise HTTPException(status_code=500, detail=str(e))
