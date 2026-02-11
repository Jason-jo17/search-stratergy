"""
Adaptive Fusion Search Route
The ultimate multi-strategy search endpoint
"""

from fastapi import APIRouter, Body, Depends, Query
from typing import Optional, List, Dict
from app.search.strategies.adaptive_fusion_strategy import AdaptiveFusionStrategy
from app.database_async import get_db_pool
from app.ai.gemini_client import get_gemini_client

# Note: Adjusting prefix to match existing patterns if needed, but keeping /search for now
router = APIRouter(tags=["Search Strategies"])


@router.post("/adaptive-fusion")
async def search_adaptive_fusion(
    query: str = Body(..., description="Search query"),
    filters: Optional[Dict] = Body(None, description="Metadata filters"),
    parameters: Optional[Dict] = Body(None, description="Tunable search parameters"),
    top_k: int = Body(20, ge=1, le=100, description="Number of results"),
    db_pool = Depends(get_db_pool),
    gemini_client = Depends(get_gemini_client)
):
    """
    ## 🚀 ADAPTIVE FUSION SEARCH - The Ultimate Search Strategy
    
    Intelligently combines multiple ranking signals:
    - **BM25** for exact keyword precision
    - **Vector Search** for semantic understanding
    - **Skill Proficiency Boost** for quality
    - **Recency Boost** for freshness
    
    ### Request Body
```json
    {
      "query": "python fastapi machine learning",
      
      "filters": {
        "chunk_types": ["skills", "projects"],
        "branches": ["CSE", "AI/ML"],
        "min_semester": 5,
        "min_cgpa": 7.0
      },
      
      "parameters": {
        "bm25_k1": 1.5,
        "bm25_b": 0.6,
        "bm25_weight": 0.5,
        "vector_weight": 0.5,
        "skill_proficiency_boost": 0.3,
        "recency_boost": 0.1,
        "fusion_method": "weighted_sum"
      },
      
      "top_k": 20
    }
```
    
    ### Tunable Parameters (Sliders)
    
    **BM25 Configuration:**
    - `bm25_k1` (1.0-3.0): Term frequency saturation
      - 1.0-1.5 = Fast saturation (short chunks)
      - 2.0-3.0 = Slow saturation (long chunks)
      - Default: 1.5
    
    - `bm25_b` (0.0-1.0): Length normalization
      - 0.0 = No penalty
      - 0.6 = Balanced (recommended)
      - 1.0 = Full penalty
      - Default: 0.6
    
    **Fusion Weights:**
    - `bm25_weight` (0.0-1.0): Importance of BM25
      - Higher for exact skill matching
      - Default: 0.5
    
    - `vector_weight` (0.0-1.0): Importance of vector search
      - Higher for conceptual queries
      - Default: 0.5
    
    **Boosting Factors:**
    - `skill_proficiency_boost` (0.0-1.0): Boost high-skill students
      - 0.0 = No boost
      - 0.3 = Moderate boost
      - 0.5+ = Strong preference for top performers
      - Default: 0.3
    
    - `recency_boost` (0.0-1.0): Boost recent profiles
      - 0.0 = Ignore update time
      - 0.1 = Slight preference
      - 0.4+ = Strong preference for fresh profiles
      - Default: 0.1
    
    **Fusion Method:**
    - `weighted_sum`: Linear combination (default)
    - `rrf`: Reciprocal Rank Fusion
    - `multiplicative`: Both must score well
    
    ### Use Cases
    
    **Technical Skills (BM25-heavy):**
```json
    {
      "query": "react typescript graphql",
      "parameters": {
        "bm25_weight": 0.7,
        "vector_weight": 0.3
      }
    }
```
    
    **Conceptual (Vector-heavy):**
```json
    {
      "query": "innovative problem solver with leadership",
      "parameters": {
        "bm25_weight": 0.3,
        "vector_weight": 0.7
      }
    }
```
    
    **Top Performers:**
```json
    {
      "query": "machine learning",
      "parameters": {
        "skill_proficiency_boost": 0.5
      }
    }
```
    
    **Fresh Talent:**
```json
    {
      "query": "full stack developer",
      "parameters": {
        "recency_boost": 0.4
      }
    }
```
    """
    
    strategy = AdaptiveFusionStrategy(db_pool, gemini_client)
    
    results = await strategy.search(
        query=query,
        filters=filters,
        parameters=parameters,
        top_k=top_k
    )
    
    return results


@router.get("/adaptive-fusion/presets")
async def get_fusion_presets():
    """
    Get pre-configured parameter sets for common scenarios
    """
    return {
        "presets": {
            "technical_skills_exact": {
                "name": "Technical Skills (Exact Match)",
                "description": "Best for specific technology stacks (e.g., 'React TypeScript GraphQL')",
                "use_when": "You need exact technical skill matching",
                "parameters": {
                    "bm25_k1": 2.0,
                    "bm25_b": 0.5,
                    "bm25_weight": 0.75,
                    "vector_weight": 0.25,
                    "skill_proficiency_boost": 0.3,
                    "recency_boost": 0.05,
                    "fusion_method": "weighted_sum"
                }
            },
            
            "conceptual_semantic": {
                "name": "Conceptual Understanding",
                "description": "Best for soft skills and concepts (e.g., 'innovative team leader')",
                "use_when": "You need semantic understanding of qualities",
                "parameters": {
                    "bm25_k1": 1.2,
                    "bm25_b": 0.75,
                    "bm25_weight": 0.25,
                    "vector_weight": 0.75,
                    "skill_proficiency_boost": 0.2,
                    "recency_boost": 0.1,
                    "fusion_method": "weighted_sum"
                }
            },
            
            "balanced_hybrid": {
                "name": "Balanced Hybrid",
                "description": "Equal weight to lexical and semantic matching",
                "use_when": "Mixed queries with both technical and soft skills",
                "parameters": {
                    "bm25_k1": 1.5,
                    "bm25_b": 0.6,
                    "bm25_weight": 0.5,
                    "vector_weight": 0.5,
                    "skill_proficiency_boost": 0.3,
                    "recency_boost": 0.1,
                    "fusion_method": "weighted_sum"
                }
            },
            
            "top_performers": {
                "name": "Top Performers",
                "description": "Heavily weight students with high skill proficiency",
                "use_when": "You want the absolute best candidates",
                "parameters": {
                    "bm25_k1": 1.5,
                    "bm25_b": 0.6,
                    "bm25_weight": 0.4,
                    "vector_weight": 0.6,
                    "skill_proficiency_boost": 0.6,
                    "recency_boost": 0.05,
                    "fusion_method": "multiplicative"
                }
            },
            
            "fresh_talent": {
                "name": "Fresh Talent",
                "description": "Prioritize recently updated profiles",
                "use_when": "You want active, engaged students",
                "parameters": {
                    "bm25_k1": 1.5,
                    "bm25_b": 0.6,
                    "bm25_weight": 0.5,
                    "vector_weight": 0.5,
                    "skill_proficiency_boost": 0.2,
                    "recency_boost": 0.5,
                    "fusion_method": "weighted_sum"
                }
            },
            
            "strict_requirements": {
                "name": "Strict Requirements",
                "description": "Both BM25 and Vector must score well (multiplicative fusion)",
                "use_when": "Candidates must meet both exact and conceptual criteria",
                "parameters": {
                    "bm25_k1": 1.5,
                    "bm25_b": 0.6,
                    "bm25_weight": 0.5,
                    "vector_weight": 0.5,
                    "skill_proficiency_boost": 0.3,
                    "recency_boost": 0.1,
                    "fusion_method": "multiplicative"
                }
            }
        },
        
        "parameter_guide": {
            "bm25_k1": {
                "range": "[1.0, 3.0]",
                "low_values": "1.0-1.5: Fast saturation, good for short chunks (skills)",
                "high_values": "2.0-3.0: Slow saturation, good for long chunks (projects)"
            },
            "bm25_b": {
                "range": "[0.0, 1.0]",
                "low_values": "0.0-0.3: Minimal length penalty",
                "high_values": "0.7-1.0: Strong length penalty"
            },
            "weights": {
                "note": "bm25_weight + vector_weight will be normalized to sum to 1.0",
                "bm25_heavy": "0.7+ for exact keyword matching",
                "vector_heavy": "0.7+ for semantic understanding",
                "balanced": "0.5/0.5 for mixed queries"
            },
            "boosts": {
                "skill_proficiency_boost": "0.0-1.0, adds to final score based on avg skill rating",
                "recency_boost": "0.0-1.0, adds to final score based on profile freshness"
            }
        }
    }


@router.get("/adaptive-fusion/examples")
async def get_fusion_examples():
    """
    Get example queries with recommended parameters
    """
    return {
        "examples": [
            {
                "scenario": "Find Python + FastAPI + PostgreSQL developers",
                "query": "python fastapi postgresql",
                "recommended_preset": "technical_skills_exact",
                "custom_parameters": {
                    "bm25_k1": 2.0,
                    "bm25_b": 0.5,
                    "bm25_weight": 0.75,
                    "vector_weight": 0.25
                },
                "explanation": "High BM25 weight for exact tech stack, slower saturation for detailed mentions"
            },
            {
                "scenario": "Find innovative entrepreneurs with technical skills",
                "query": "innovative entrepreneur startup technical background",
                "recommended_preset": "conceptual_semantic",
                "custom_parameters": {
                    "bm25_weight": 0.3,
                    "vector_weight": 0.7,
                    "skill_proficiency_boost": 0.3
                },
                "explanation": "High vector weight for concepts like 'innovative' and 'entrepreneur'"
            },
            {
                "scenario": "Find senior ML engineers (exact skills + high performance)",
                "query": "machine learning tensorflow pytorch deep learning",
                "recommended_preset": "top_performers",
                "custom_parameters": {
                    "bm25_weight": 0.5,
                    "vector_weight": 0.5,
                    "skill_proficiency_boost": 0.6,
                    "fusion_method": "multiplicative"
                },
                "explanation": "Balanced search + strong skill boost + multiplicative ensures both tech and quality"
            },
            {
                "scenario": "Find recently active full-stack developers",
                "query": "full stack developer react node mongodb",
                "recommended_preset": "fresh_talent",
                "custom_parameters": {
                    "recency_boost": 0.5
                },
                "explanation": "High recency boost prioritizes active, engaged students"
            }
        ]
    }
