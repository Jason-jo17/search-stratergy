# Search Strategies Documentation

This document outlines the search strategies implemented in the application, their underlying logic, and the code associated with them.

## Data Source
All search strategies now query the **`student_profiles`** table in the PostgreSQL database. This table contains:
- `id`: Unique identifier.
- `text`: Full text content of the profile (for lexical/fuzzy search).
- `metadata`: Structured JSON data (Name, Role, Skills, etc.).
- `embedding`: Vector embedding of the profile (generated using Gemini `text-embedding-004`).

## Match Insights
All search strategies now return a **`match_reason`** field. This provides transparency into *why* a specific result was chosen.

---

## 1. Keyword Search (Lexical)
**Description:** Traditional keyword matching. It tokenizes the user's query (removing conversational stop words like "give me") and finds documents containing those keywords using case-insensitive matching (`ILIKE`).
**Ranking:** Results are ranked by the number of keyword matches.
**Example Insight:**
> "Contains keywords: python, ecommerce"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/keyword")
async def search_keyword(request: SearchRequest):
    keywords = tokenize_query(request.query)
    # ...
    
    # SQL Construction
    conditions = []
    for keyword in keywords:
        conditions.append("text ILIKE %s")
    where_clause = " OR ".join(conditions)
    
    sql = f"""
        SELECT id, text, metadata
        FROM student_profiles
        WHERE {where_clause}
        LIMIT %s
    """
    # ...
    # Insight: f"Contains keywords: {', '.join(keywords)}"
```

## 2. Vector Search (Semantic)
**Description:** Uses AI embeddings to find results that are *semantically* similar to the query.
**Optimization:** Conversational noise (e.g., "give me someone with") is stripped out before embedding, ensuring the vector focuses on the core skills/role.
**Model:** Google Gemini `text-embedding-004`.
**Database:** `pgvector` extension for cosine similarity (`<=>` operator).
**Example Insight:**
> "High semantic similarity (0.89) to 'python ecommerce'"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/vector")
async def search_vector(request: SearchRequest):
    # Clean query to remove conversational noise
    keywords = tokenize_query(request.query)
    cleaned_query = " ".join(keywords) if keywords else request.query
    
    embedding = get_embedding(cleaned_query)
    
    # 1 - distance = similarity
    sql = """
        SELECT id, text, metadata, 1 - (embedding <=> %s) as score
        FROM student_profiles
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    # ...
    # Insight: f"High semantic similarity ({row['score']:.2f}) to '{cleaned_query}'"
```

## 3. Hybrid Search (RRF)
**Description:** Combines the strengths of Keyword and Vector search using **Reciprocal Rank Fusion (RRF)**.
**Example Insight:**
> "Hybrid Match: Vector Rank #1, Keyword Rank #3"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/hybrid")
async def search_hybrid(request: SearchRequest):
    # 1. Get Vector Results
    vector_results = await search_vector(request)
    
    # 2. Get Keyword Results
    keyword_results = await search_keyword(request)
    
    # 3. RRF Fusion
    rrf_scores = {}
    # ... (calculate scores based on rank in both lists)
    
    # Insight: f"Hybrid Match: Vector Rank #1, Keyword Rank #3"
    return {"results": ...}
```

## 4. Metadata Filter
**Description:** Filters results based on specific criteria like Role or Skills using regex on the `text` column.
**Example Insight:**
> "Filters matched: Role matches 'developer', Skill matches 'python'"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/filter")
async def search_filter(request: SearchRequest):
    conditions = ["1=1"]
    if request.role:
        conditions.append("text ~* %s") # Regex match for Role
    if request.skills:
        # ... (Regex match for Skills)
        
    sql = f"""
        SELECT id, text, metadata
        FROM student_profiles
        WHERE {where_clause}
        LIMIT %s
    """
    # ...
    # Insight: f"Filters matched: Role matches 'developer'"
```

## 5. Pattern Matching (Regex)
**Description:** Finds specific patterns in the text (Email, Phone) using PostgreSQL's POSIX regex operator (`~`).
**Example Insight:**
> "Matches pattern: email"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/pattern")
async def search_pattern(request: SearchRequest):
    # ... (define pattern based on type)
    
    sql = """
        SELECT id, text, metadata
        FROM student_profiles
        WHERE text ~ %s
        LIMIT %s
    """
    # ...
    # Insight: f"Matches pattern: email"
```

## 6. Full Text Search (FTS)
**Description:** Uses PostgreSQL's built-in `tsvector` and `tsquery`.
**Optimization:** Uses `OR` logic (`|`) for keywords, allowing it to handle natural language queries by finding documents containing *any* of the significant terms.
**Example Insight:**
> "Full-text match for terms: python, ecommerce"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/fts")
async def search_fts(request: SearchRequest):
    keywords = tokenize_query(request.query)
    ts_query_str = " | ".join(keywords)
    
    sql = """
        SELECT id, text, metadata,
               ts_rank(to_tsvector('english', text), to_tsquery('english', %s)) as score
        FROM student_profiles
        WHERE to_tsvector('english', text) @@ to_tsquery('english', %s)
        ORDER BY score DESC
        LIMIT %s
    """
    # ...
    # Insight: f"Full-text match for terms: python, java"
```

## 7. Fuzzy Search (Trigram)
**Description:** Matches text based on character similarity (trigrams).
**Optimization:** Searches against a **concatenated string** of `Role + Skills + Name + Text`. This increases the density of important keywords, improving matches for specific skills in long documents.
**Database:** `pg_trgm` extension.
**Example Insight:**
> "Fuzzy similarity (0.45) to 'pythn'"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/fuzzy")
async def search_fuzzy(request: SearchRequest):
    # ... (clean query)
    
    # Concatenate metadata fields for denser search target
    sql = """
        SELECT id, text, metadata, similarity(
            COALESCE(metadata->>'role', '') || ' ' || 
            COALESCE(metadata->>'skills_text', '') || ' ' || 
            text, %s) as score
        FROM student_profiles
        WHERE ... %% %s
        ORDER BY score DESC
        LIMIT %s
    """
    # ...
    # Insight: f"Fuzzy similarity (0.45) to 'python'"
```

## 8. Agentic Search (LLM Re-ranking)
**Description:** The most advanced strategy.
1.  **Retrieval:** Uses **Hybrid Search** to get a broad set of candidates.
2.  **Reasoning:** Sends the query and candidates to **Google Gemini Pro**.
3.  **Re-ranking:** The LLM analyzes each candidate and assigns a relevance score.
**Example Insight:**
> "Strong match for Python and AWS due to 5 years experience in cloud infrastructure."

**Code (`app/api/routes/search.py` & `app/api/utils/llm.py`):**
```python
@router.post("/agentic")
async def search_agentic(request: SearchRequest):
    # 1. Get Broad Results (Hybrid)
    hybrid_response = await search_hybrid(hybrid_request)
    
    # 2. LLM Re-ranking
    ranked_results = analyze_and_rerank(request.query, candidates, request.limit)
    return {"results": ranked_results}
```
```python
# app/api/utils/llm.py
def analyze_and_rerank(query, candidates, top_k):
    # ...
    prompt = f"""
    ...
    5. Provide a brief "reasoning" for why each candidate was selected. Focus on "key insights".
    ...
    """
    # ...
```

## 9. Agentic Search (Tool Use)
**Description:** The AI acts as a router. It analyzes the query to decide which underlying search tool (Vector, Keyword, Pattern, Filter) is best, executes it, and then re-ranks the results.
**Example Insight:**
> "[Agent selected Pattern Search (email). Reason: User is asking for contact info.] Matches pattern: email"

**Code (`app/api/routes/search.py`):**
```python
@router.post("/agentic_tool")
async def search_agentic_tool(request: SearchRequest):
    # 1. Decide Tool
    decision = decide_search_tool(request.query)
    # ... execute tool ...
    # 3. Re-rank
    ranked_results = analyze_and_rerank(...)
```

## 10. Agentic Search (Query Analysis)
**Description:** The AI analyzes the query first to extract structured filters (Role, Skills) and rewrite the query for better retrieval. It then executes a search (typically Vector) with the optimized query and re-ranks.
**Example Insight:**
> "[Query Analysis: Rewrote 'find python guy' to 'Python Developer'. Reason: Extracted role and skill.] Strong match for Python..."

**Code (`app/api/routes/search.py`):**
```python
@router.post("/agentic_analysis")
async def search_agentic_analysis(request: SearchRequest):
    # 1. Analyze Query
    analysis = analyze_query_intent(request.query)
    # ... execute search with rewritten query ...
    # 3. Re-rank
    ranked_results = analyze_and_rerank(...)
```

# Search Engine Flow - STM Evaluation Worker

## Overview

The STM (Skills, Tools, Mindset) Evaluation Worker is a background job that processes student data to create vectorized profile chunks for semantic search. It aggregates data from multiple sources, structures it using AI, and stores it as embeddings in the database.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Job Trigger                                                  │
│    - River Queue Worker receives StmEvaluationsArgs            │
│    - Contains: student_id                                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Transaction Setup                                            │
│    - RunInBackground creates pgx.Tx transaction                │
│    - Calls ProcessStudentData with GORM DB                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Cleanup Old Data                                             │
│    - DELETE FROM stm_evaluations WHERE user_id = $1            │
│    - Removes previous evaluation records                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Collect STM Evaluations                                      │
│    ├─ CollectFromExternalStmScores()                           │
│    │  └─ Inserts from external_stm_scores table                │
│    │     - Maps to mind_set, skill_set, or tool_set            │
│    │                                                             │
│    └─ CollectFromRubricEvaluations()                            │
│       └─ Inserts from rubric_evaluations table                  │
│          - Calculates weighted scores                            │
│          - Maps to mind_set, skill_set, or tool_set             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Build Profile Data Aggregation                               │
│    ├─ Get user profile (recruitment_service.GetProfile)        │
│    │  └─ Converts to JSON string                                │
│    │                                                             │
│    ├─ Get user projects                                         │
│    │  ├─ Projects created by user                               │
│    │  └─ Projects where user is team member                     │
│    │  └─ For each project: GetProjectByID()                     │
│    │     └─ Includes steps, attachments, problem statements      │
│    │                                                             │
│    ├─ Get GitHub repositories                                   │
│    │  └─ github_module.GetGithubRepoInsights()                  │
│    │     └─ Adds repository insights to llm_input                │
│    │                                                             │
│    └─ Get Awards (Credly badges)                                │
│       ├─ For Credly badges:                                     │
│       │  ├─ Extract badge_id from HTML embed                    │
│       │  ├─ Fetch badge details from credly.com                 │
│       │  └─ Extract og:title and og:description                 │
│       └─ For other awards: use title                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. AI Processing (Gemini)                                       │
│    - Input: Aggregated JSON string (llm_input)                  │
│    - System Instruction: Strict Semantic Serializer              │
│      └─ Formats data into structured chunks:                   │
│         • Personal: Candidate info, role, location, exp         │
│         • Skills: Grouped by domain with scores                 │
│         • Projects: Name, description, stack, features          │
│         • Awards: Title, issuer, description                     │
│    - Output: JSON with structured chunks                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Vectorization & Storage                                      │
│    For each chunk type (personal, skills, projects, awards):    │
│    ├─ Convert text to vector embedding (Gemini)                 │
│    ├─ Create UserProfileChunk object                            │
│    │  └─ Fields: user_id, chunk_type, content, embedding        │
│    └─ Upsert to database                                        │
│       └─ ON CONFLICT (user_id, chunk_type)                      │
│          DO UPDATE SET content, embedding                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Cleanup & Commit                                             │
│    - DELETE FROM vectorise_profiles WHERE student_id = $1      │
│    - Commit transaction                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### Data Sources

1. **Profile Data**: User profile information from recruitment service
2. **Projects**: User-created projects and team projects
3. **GitHub Repositories**: Repository insights and metadata
4. **Awards**: Credly badges and other awards
5. **STM Evaluations**: External scores and rubric evaluations

### AI Processing

- **Model**: Google Gemini
- **Purpose**: Transform unstructured JSON into structured, searchable text chunks
- **Output Format**:
  - Personal: Single line with candidate info
  - Skills: Domain-grouped skills with scores
  - Projects: Array of project descriptions
  - Awards: Array of award descriptions

### Vector Storage

- **Table**: `user_profile_chunks`
- **Embedding Dimension**: 768 (Gemini embedding size for search)
- **Unique Constraint**: (user_id, chunk_type)
- **Update Strategy**: Upsert (INSERT ... ON CONFLICT UPDATE)
- **Search Vector**: `search_vector` column (tsvector type) for full-text search
  - Contains indexed text from chunk content
  - Enables PostgreSQL full-text search with ranking
  - Used alongside vector embeddings for hybrid search

### Transaction Management

- **Transaction Type**: pgx.Tx (PostgreSQL native)
- **Scope**: Entire ProcessStudentData function
- **Commit**: On successful completion
- **Rollback**: On any error

## Data Flow Example

```
Input:
{
  "profile": { "name": "John", "branch": "CS", ... },
  "projects": [{ "title": "E-commerce", ... }],
  "github_repos": [{ "insights": "..." }],
  "awards": [{ "title": "AWS Certified", ... }]
}

↓ AI Processing ↓

Output:
{
  "personal": "Candidate: John | Role: CS | Location: ...",
  "skills": "Skills-Backend: Python (8), Go (7), ...",
  "projects": [
    "Projects: E-commerce (Desc: ... | Stack: React, Node | Feat: ...)"
  ],
  "awards": [
    "Awards: AWS Certified (Issuer: AWS | Desc: ...)"
  ]
}

↓ Vectorization ↓

Stored in user_profile_chunks:
- user_id: "uuid"
- chunk_type: "personal" | "skills" | "projects" | "awards"
- content: "formatted text"
- embedding: vector(768) - for vector similarity search
- search_vector: tsvector - for full-text search (indexed content)
```

## Error Handling

- All database operations return errors immediately
- Transaction rollback on any error
- Vector generation failures are caught and skipped (for projects/awards)
- HTTP request failures for Credly badges fall back to award title

## Search Flow

After profile chunks are stored, the search process works as follows:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Search Query Processing                                      │
│    - User submits search query (e.g., "backend developer")     │
│    - Query is enhanced with AI to extract requirements         │
│    - Query is converted to vector embedding (768 dimensions)   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Dual Search Strategy                                         │
│    ├─ Vector Similarity Search                                  │
│    │  └─ Query: SELECT user_id FROM user_skill_vectors         │
│    │     WHERE content_embedding IS NOT NULL                    │
│    │     ORDER BY 1 - (content_embedding <=> ?::vector) DESC   │
│    │     LIMIT ?                                                │
│    │     └─ Uses cosine distance for semantic matching         │
│    │                                                             │
│    └─ Full-Text Search (FTS)                                   │
│       └─ Query: SELECT user_id FROM user_skill_vectors         │
│          WHERE search_vector @@ plainto_tsquery('english', ?)   │
│          ORDER BY ts_rank_cd(search_vector, query, 32) DESC      │
│          LIMIT ?                                                │
│          └─ Uses PostgreSQL tsvector for keyword matching      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Result Combination                                            │
│    - Merge user_ids from both searches (union, no duplicates)   │
│    - Fetch full profile data for matched users                 │
│    - Initial limit: requested_limit × 3 (for ranking)         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Multi-Factor Ranking  (ignore this part )                                                           │
│    Each profile receives a weighted score from 6 factors:      │
│    ├─ Tool Vector Score (55%):                                  │
│    │  └─ Weighted average of skill scores × tool relevance    │
│    │                                                             │
│    ├─ Tool Overlap / Jaccard (25%):                             │
│    │  └─ Intersection/Union of required vs candidate tools    │
│    │  └─ +10% bonus if candidate has ALL required tools        │
│    │                                                             │
│    ├─ Vector Similarity (10%):                                   │
│    │  └─ Semantic match score from vector search               │
│    │                                                             │
│    ├─ Experience Score (4%):                                     │
│    │  └─ Projects and internships count comparison             │
│    │                                                             │
│    ├─ Mindset Score (3%):                                       │
│    │  └─ Sum of normalized scores from "Mind Set" domain        │
│    │                                                             │
│    └─ Skill Set Score (3%):                                     │
│       └─ Sum of normalized scores from "Skill Set" domain      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Final Score Calculation                                      │
│    Final Score = (Tool Vector × 0.55) + (Tool Overlap × 0.25) + │
│                  (Vector Similarity × 0.10) + (Experience × 0.04)│
│                  + (Mindset × 0.03) + (Skill Set × 0.03)        │
│    └─ Clamped to 0-1 range, then × 100 for percentage          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Top 30 Selection                                             │
│    - Sort profiles by Match Percentage (descending)            │
│    - Limit to top 30 profiles (or requested limit)             │
│    - Return ranked results with match percentages               │
└─────────────────────────────────────────────────────────────────┘
```

### Search Vector Details

**Full-Text Search (FTS):**

- Uses PostgreSQL `tsvector` type stored in `search_vector` column
- Query matching: `search_vector @@ plainto_tsquery('english', query)`
- Ranking: `ts_rank_cd(search_vector, query, 32)` - covers density ranking
- Matches keywords and phrases in chunk content

**Vector Similarity Search:**

- Uses `content_embedding` column (vector type, 768 dimensions)
- Similarity calculation: `1 - (embedding <=> query_vector)`
- `<=>` operator is cosine distance (0 = identical, 1 = orthogonal)
- Captures semantic meaning beyond exact keyword matches

**Chunk Matching:**

- Each chunk type (personal, skills, projects, awards) is stored separately
- Search matches against aggregated user profile data
- Multiple chunks per user are combined for comprehensive matching

### Score Combination Example

```
User Profile A:
- Vector similarity: 0.85 (from vector search)
- FTS rank: 0.72 (from full-text search)
- Tool Vector Score: 0.90 (has relevant skills)
- Tool Overlap: 0.80 (has 4 of 5 required tools)
- Experience: 0.75 (meets project/internship requirements)
- Mindset: 0.65
- Skill Set: 0.70

Final Score = (0.90 × 0.55) + (0.80 × 0.25) + (0.85 × 0.10) +
              (0.75 × 0.04) + (0.65 × 0.03) + (0.70 × 0.03)
            = 0.495 + 0.20 + 0.085 + 0.03 + 0.0195 + 0.021
            = 0.8505
            = 85.05% match
```

## Performance Considerations

- Batch processing of chunks
- Vector generation happens sequentially (API rate limits)
- Database upserts use ON CONFLICT for efficiency
- Transaction ensures atomicity of all operations
- Vector search uses IVFFlat index for fast similarity queries
- FTS uses GIN index on search_vector for fast text matching
- Initial search returns 3× limit candidates, then ranks to final limit
