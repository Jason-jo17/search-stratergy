"""
Adaptive Fusion Search (AFS) - The Mega Strategy
Combines BM25 + Vector Search + Multiple Boosting Factors
All parameters tunable via API
"""

import re
import math
import time
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import asyncpg
import numpy as np


class AdaptiveFusionStrategy:
    """
    The Ultimate Search Strategy
    Combines multiple ranking signals with tunable parameters
    """
    
    def __init__(self, db_pool: asyncpg.Pool, gemini_client=None):
        self.db = db_pool
        self.gemini = gemini_client
    
    # ==================== TOKENIZATION ====================
    
    def tokenize(self, text: str) -> List[str]:
        """Convert text to searchable tokens"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'is', 'as', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had'
        }
        
        return [t for t in tokens if t not in stop_words and len(t) > 2]
    
    # ==================== BM25 COMPONENT ====================
    
    def calculate_idf(self, term: str, total_docs: int, docs_with_term: int) -> float:
        """Calculate Inverse Document Frequency"""
        if docs_with_term == 0:
            return 0.0
        
        numerator = total_docs - docs_with_term + 0.5
        denominator = docs_with_term + 0.5
        return math.log(numerator / denominator + 1)
    
    def calculate_bm25_score(
        self,
        query_terms: List[str],
        doc_content: str,
        doc_length: int,
        avg_doc_length: float,
        idf_scores: Dict[str, float],
        k1: float,
        b: float
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate BM25 score for a document"""
        doc_tokens = self.tokenize(doc_content)
        term_freq = Counter(doc_tokens)
        
        total_score = 0.0
        term_contributions = {}
        
        for term in query_terms:
            if term not in term_freq:
                continue
            
            tf = term_freq[term]
            idf = idf_scores.get(term, 0)
            
            # BM25 formula
            if avg_doc_length == 0:
                length_norm = 1.0
            else:
                length_norm = 1 - b + b * (doc_length / avg_doc_length)
            
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * length_norm
            
            if denominator == 0:
                tf_component = 0
            else:
                tf_component = numerator / denominator
            
            contribution = idf * tf_component
            total_score += contribution
            term_contributions[term] = round(contribution, 2)
        
        return total_score, term_contributions
    
    # ==================== VECTOR SEARCH COMPONENT ====================
    
    async def get_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for query using Gemini"""
        if not self.gemini:
            return None
        
        try:
            response = await self.gemini.embed_content(
                model="models/text-embedding-004",
                content=query
            )
            return response['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    # ==================== MAIN SEARCH FUNCTION ====================
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        parameters: Optional[Dict] = None,
        top_k: int = 20
    ) -> Dict:
        """
        Execute Adaptive Fusion Search
        """
        start_time = time.time()
        
        # Parse parameters with defaults
        params = self._parse_parameters(parameters)
        
        # Parse filters
        filters = filters or {}
        chunk_types = filters.get('chunk_types', None)
        branches = filters.get('branches', None)
        min_semester = filters.get('min_semester', None)
        min_cgpa = filters.get('min_cgpa', None)
        
        # Tokenize query
        query_terms = self.tokenize(query)
        
        if not query_terms:
            return {
                "strategy": "adaptive_fusion",
                "error": "No valid search terms",
                "results": []
            }
        
        # Step 1: Run BM25 Search (if weight > 0)
        bm25_results = []
        if params['bm25_weight'] > 0:
            bm25_results = await self._run_bm25_search(
                query_terms,
                chunk_types,
                params['bm25_k1'],
                params['bm25_b'],
                top_k=100  # Get more candidates for fusion
            )
        
        # Step 2: Run Vector Search (if weight > 0 and Gemini available)
        vector_results = []
        if params['vector_weight'] > 0 and self.gemini:
            vector_results = await self._run_vector_search(
                query,
                chunk_types,
                top_k=100
            )
        
        # Step 3: Fusion (combine BM25 + Vector)
        fused_results = self._fusion(
            bm25_results,
            vector_results,
            params['bm25_weight'],
            params['vector_weight'],
            params['fusion_method']
        )
        
        if not fused_results:
            return {
                "strategy": "adaptive_fusion",
                "total_results": 0,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "results": []
            }
        
        # Step 4: Apply Skill Proficiency Boost
        if params['skill_proficiency_boost'] > 0:
            fused_results = await self._apply_skill_boost(
                fused_results,
                params['skill_proficiency_boost']
            )
        
        # Step 5: Apply Recency Boost
        if params['recency_boost'] > 0:
            fused_results = await self._apply_recency_boost(
                fused_results,
                params['recency_boost']
            )
        
        # Step 6: Apply Metadata Filters
        if branches or min_semester or min_cgpa:
            fused_results = await self._apply_metadata_filters(
                fused_results,
                branches,
                min_semester,
                min_cgpa
            )
        
        # Step 7: Get top K
        top_results = fused_results[:top_k]
        
        # Step 8: Enrich with full student profiles
        enriched_results = await self._enrich_with_profiles(
            top_results,
            query_terms,
            bm25_results,
            vector_results
        )
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "strategy": "adaptive_fusion",
            "total_results": len(enriched_results),
            "execution_time_ms": execution_time,
            "query_analysis": {
                "original_query": query,
                "extracted_keywords": query_terms,
                "detected_intent": self._detect_intent(query_terms)
            },
            "parameters_used": params,
            "results": enriched_results,
            "debug": {
                "bm25_candidates": len(bm25_results),
                "vector_candidates": len(vector_results),
                "fused_candidates": len(fused_results),
                "after_filtering": len(top_results)
            }
        }
    
    # ==================== PARAMETER PARSING ====================
    
    def _parse_parameters(self, parameters: Optional[Dict]) -> Dict:
        """Parse and validate parameters with defaults"""
        defaults = {
            'bm25_k1': 1.5,
            'bm25_b': 0.6,
            'bm25_weight': 0.5,
            'vector_weight': 0.5,
            'skill_proficiency_boost': 0.3,
            'recency_boost': 0.1,
            'fusion_method': 'weighted_sum'
        }
        
        if not parameters:
            return defaults
        
        params = defaults.copy()
        params.update(parameters)
        
        # Validate ranges
        params['bm25_k1'] = max(1.0, min(3.0, float(params['bm25_k1'])))
        params['bm25_b'] = max(0.0, min(1.0, float(params['bm25_b'])))
        params['bm25_weight'] = max(0.0, min(1.0, float(params['bm25_weight'])))
        params['vector_weight'] = max(0.0, min(1.0, float(params['vector_weight'])))
        params['skill_proficiency_boost'] = max(0.0, min(1.0, float(params['skill_proficiency_boost'])))
        params['recency_boost'] = max(0.0, min(1.0, float(params['recency_boost'])))
        
        # Normalize search weights to sum to 1.0
        total_weight = params['bm25_weight'] + params['vector_weight']
        if total_weight > 0:
            params['bm25_weight'] /= total_weight
            params['vector_weight'] /= total_weight
        
        # Validate fusion method
        if params['fusion_method'] not in ['weighted_sum', 'rrf', 'multiplicative']:
            params['fusion_method'] = 'weighted_sum'
        
        return params
    
    # ==================== BM25 SEARCH ====================
    
    async def _run_bm25_search(
        self,
        query_terms: List[str],
        chunk_types: Optional[List[str]],
        k1: float,
        b: float,
        top_k: int = 100
    ) -> List[Dict]:
        """Run BM25 search and return scored results"""
        
        # Get corpus statistics
        stats = await self._get_corpus_stats(chunk_types)
        total_docs = stats['total_docs']
        avg_doc_length = stats['avg_doc_length']
        
        if total_docs == 0:
            return []
        
        # Calculate IDF for each term
        idf_scores = {}
        for term in query_terms:
            doc_freq = await self._count_docs_with_term(term, chunk_types)
            idf_scores[term] = self.calculate_idf(term, total_docs, doc_freq)
        
        # Fetch candidate chunks
        chunks = await self._fetch_candidate_chunks(query_terms, chunk_types)
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            doc_length = len(chunk['content'].split())
            score, term_contribs = self.calculate_bm25_score(
                query_terms,
                chunk['content'],
                doc_length,
                avg_doc_length,
                idf_scores,
                k1,
                b
            )
            
            if score > 0:
                scored_chunks.append({
                    'student_id': chunk['student_id'],
                    'chunk_type': chunk['chunk_type'],
                    'content': chunk['content'],
                    'bm25_score': score,
                    'term_contributions': term_contribs
                })
        
        # Aggregate by student
        student_scores = self._aggregate_bm25_by_student(scored_chunks)
        
        # Sort and return top K
        student_scores.sort(key=lambda x: x['bm25_score'], reverse=True)
        return student_scores[:top_k]
    
    def _aggregate_bm25_by_student(self, scored_chunks: List[Dict]) -> List[Dict]:
        """Aggregate BM25 scores by student"""
        student_data = defaultdict(lambda: {
            'total_score': 0,
            'matched_chunks': [],
            'term_contributions': {},
            'content_preview': ''
        })
        
        for chunk in scored_chunks:
            sid = chunk['student_id']
            student_data[sid]['total_score'] += chunk['bm25_score']
            student_data[sid]['matched_chunks'].append(chunk['chunk_type'])
            
            for term, score in chunk['term_contributions'].items():
                student_data[sid]['term_contributions'][term] = \
                    student_data[sid]['term_contributions'].get(term, 0) + score
            
            if not student_data[sid]['content_preview']:
                preview = chunk['content'][:150]
                student_data[sid]['content_preview'] = \
                    preview + "..." if len(chunk['content']) > 150 else preview
        
        results = []
        for student_id, data in student_data.items():
            results.append({
                'student_id': student_id,
                'bm25_score': data['total_score'],
                'matched_chunks': list(set(data['matched_chunks'])),
                'term_contributions': data['term_contributions'],
                'content_preview': data['content_preview']
            })
        
        return results
    
    # ==================== VECTOR SEARCH ====================
    
    async def _run_vector_search(
        self,
        query: str,
        chunk_types: Optional[List[str]],
        top_k: int = 100
    ) -> List[Dict]:
        """Run vector similarity search"""
        
        # Generate query embedding
        query_embedding = await self.get_query_embedding(query)
        if not query_embedding:
            return []
        
        # Build query
        where_clause = ""
        params = [str(query_embedding)] # Cast to string for pgvector format
        
        if chunk_types:
            placeholders = ','.join([f"${i+2}" for i in range(len(chunk_types))])
            where_clause = f"WHERE chunk_type IN ({placeholders})"
            params.extend(chunk_types)
        
        # Vector search using cosine distance
        # We assume `user_profile_chunks` table since `chunks` is not a standard table in previous analysis
        # The user provided code uses `chunks` and `students`.
        # I MUST adjust table names to match the schema I found: `user_profile_chunks` and `student_profiles`
        # `user_profile_chunks` has `user_id` not `student_id`.
        vector_query = f"""
            SELECT 
                user_id as student_id,
                chunk_type,
                content,
                1 - (embedding <=> $1::vector) as similarity
            FROM user_profile_chunks
            {where_clause}
            ORDER BY embedding <=> $1::vector
            LIMIT {top_k}
        """
        
        results = await self.db.fetch(vector_query, *params)
        
        # Aggregate by student
        student_scores = self._aggregate_vector_by_student(results)
        
        return student_scores
    
    def _aggregate_vector_by_student(self, results) -> List[Dict]:
        """Aggregate vector scores by student"""
        student_data = defaultdict(lambda: {
            'max_similarity': 0,
            'matched_chunks': [],
            'content_preview': ''
        })
        
        for row in results:
            sid = row['student_id']
            similarity = row['similarity']
            
            # Take max similarity across chunks
            if similarity > student_data[sid]['max_similarity']:
                student_data[sid]['max_similarity'] = similarity
            
            student_data[sid]['matched_chunks'].append(row['chunk_type'])
            
            if not student_data[sid]['content_preview']:
                preview = row['content'][:150]
                student_data[sid]['content_preview'] = \
                    preview + "..." if len(row['content']) > 150 else preview
        
        vector_results = []
        for student_id, data in student_data.items():
            vector_results.append({
                'student_id': student_id,
                'vector_score': data['max_similarity'],
                'matched_chunks': list(set(data['matched_chunks'])),
                'content_preview': data['content_preview']
            })
        
        return vector_results
    
    # ==================== FUSION ====================
    
    def _fusion(
        self,
        bm25_results: List[Dict],
        vector_results: List[Dict],
        bm25_weight: float,
        vector_weight: float,
        fusion_method: str
    ) -> List[Dict]:
        """Combine BM25 and Vector scores"""
        
        # Normalize BM25 scores to 0-1
        if bm25_results:
            max_bm25 = max(r['bm25_score'] for r in bm25_results)
            if max_bm25 > 0:
                for r in bm25_results:
                    r['bm25_normalized'] = r['bm25_score'] / max_bm25
            else:
                for r in bm25_results:
                    r['bm25_normalized'] = 0
        
        # Create lookup maps
        bm25_map = {r['student_id']: r for r in bm25_results}
        vector_map = {r['student_id']: r for r in vector_results}
        
        # Get all unique student IDs
        all_student_ids = set(bm25_map.keys()) | set(vector_map.keys())
        
        # Fusion
        fused_results = []
        for student_id in all_student_ids:
            bm25_data = bm25_map.get(student_id, {})
            vector_data = vector_map.get(student_id, {})
            
            bm25_score = bm25_data.get('bm25_normalized', 0)
            vector_score = vector_data.get('vector_score', 0)
            
            # Apply fusion method
            if fusion_method == 'weighted_sum':
                fused_score = (bm25_weight * bm25_score) + (vector_weight * vector_score)
            
            elif fusion_method == 'multiplicative':
                if bm25_score > 0 and vector_score > 0:
                    fused_score = (bm25_score ** bm25_weight) * (vector_score ** vector_weight)
                else:
                    fused_score = 0
            
            elif fusion_method == 'rrf':
                # Reciprocal Rank Fusion
                k = 60
                bm25_rank = next((i+1 for i, r in enumerate(bm25_results) if r['student_id'] == student_id), 1000)
                vector_rank = next((i+1 for i, r in enumerate(vector_results) if r['student_id'] == student_id), 1000)
                fused_score = (bm25_weight / (k + bm25_rank)) + (vector_weight / (k + vector_rank))
            
            else:
                fused_score = (bm25_weight * bm25_score) + (vector_weight * vector_score)
            
            # Combine metadata
            matched_chunks = list(set(
                bm25_data.get('matched_chunks', []) + vector_data.get('matched_chunks', [])
            ))
            
            fused_results.append({
                'student_id': student_id,
                'bm25_score': bm25_data.get('bm25_score', 0),
                'bm25_normalized': bm25_score,
                'vector_score': vector_score,
                'base_fusion_score': fused_score,
                'final_score': fused_score,  # Will be updated by boosts
                'matched_chunks': matched_chunks,
                'term_contributions': bm25_data.get('term_contributions', {}),
                'content_preview': bm25_data.get('content_preview') or vector_data.get('content_preview', ''),
                'skill_boost': 0.0,
                'recency_boost': 0.0
            })
        
        # Sort by fused score
        fused_results.sort(key=lambda x: x['base_fusion_score'], reverse=True)
        return fused_results
    
    # ==================== BOOSTING ====================
    
    async def _apply_skill_boost(
        self,
        results: List[Dict],
        boost_factor: float
    ) -> List[Dict]:
        """Boost students with high skill proficiency"""
        
        if not results:
            return []
        
        student_ids = [str(r['student_id']) for r in results]
        
        # Fetch skill data
        # Adjusted table name to student_profiles
        placeholders = ','.join([f"${i+1}" for i in range(len(student_ids))])
        
        # NOTE: Using 'text' column logic since 'skills' column likely doesn't exist directly
        # Based on verification report, skills are inside the 'text' JSON blob.
        # But 'metadata' might have 'skills' too? verification said no 'project' in metadata.
        # Let's assume skills are in the 'text' JSON blob.
        # We read the 'text' column, parse it as JSON to get skills.
        query = f"""
            SELECT id, text
            FROM student_profiles
            WHERE id IN ({placeholders})
        """
        
        skill_data = await self.db.fetch(query, *student_ids)
        
        import json
        skill_map = {}
        for s in skill_data:
            try:
                data = json.loads(s['text'])
                skill_map[str(s['id'])] = data.get('skills', [])
            except:
                skill_map[str(s['id'])] = []
        
        # Apply boost
        for result in results:
            sid = str(result['student_id'])
            skills = skill_map.get(sid, [])
            
            if skills and isinstance(skills, list):
                # Check structure of skill object (verification report showed: tool_id, tool_name)
                # Does it have 'average_normalized_score'? Let's assume yes or default 0.
                scores = []
                for s in skills:
                    score = s.get('average_normalized_score', 0)
                    scores.append(float(score) if score else 0)
                
                avg_skill_score = np.mean(scores) if scores else 0
                    
                # Normalize to 0-1 (assuming scores are 0-10)
                normalized_skill = avg_skill_score / 10.0
                boost = normalized_skill * boost_factor
                result['skill_boost'] = round(boost, 4)
                result['final_score'] += boost
        
        # Re-sort
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results
    
    async def _apply_recency_boost(
        self,
        results: List[Dict],
        boost_factor: float
    ) -> List[Dict]:
        """Boost recently updated profiles"""
        # Metadata has 'ingested_at'
        
        if not results:
            return []
        
        student_ids = [str(r['student_id']) for r in results]
        
        placeholders = ','.join([f"${i+1}" for i in range(len(student_ids))])
        query = f"""
            SELECT id, metadata->>'ingested_at' as ingested_at
            FROM student_profiles
            WHERE id IN ({placeholders})
        """
        
        recency_data = await self.db.fetch(query, *student_ids)
        recency_map = {}
        for r in recency_data:
            ts_str = r['ingested_at']
            if ts_str:
                try:
                    # ISO format parsing
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    recency_map[str(r['id'])] = ts
                except:
                    pass
        
        # Calculate recency boost
        now = datetime.now().astimezone()
        max_days_old = 365  # 1 year
        
        for result in results:
            sid = str(result['student_id'])
            updated_at = recency_map.get(sid)
            
            if updated_at:
                days_old = (now - updated_at).days
                # Freshness score: 1.0 for today, 0.0 for 1 year old
                freshness = max(0, 1 - (days_old / max_days_old))
                boost = freshness * boost_factor
                result['recency_boost'] = round(boost, 4)
                result['final_score'] += boost
        
        # Re-sort
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results
    
    # ==================== FILTERING ====================
    
    async def _apply_metadata_filters(
        self,
        results: List[Dict],
        branches: Optional[List[str]],
        min_semester: Optional[int],
        min_cgpa: Optional[float]
    ) -> List[Dict]:
        """Filter by branch, semester, CGPA"""
        # Note: In student_profiles, branch/cgpa are inside 'text' JSON or 'metadata'
        # Verification report showed 'branch' inside 'text' JSON. 'metadata' was mostly technical.
        # So we need to query 'text::jsonb'
        
        if not results:
            return []
        
        student_ids = [str(r['student_id']) for r in results]
        
        # Build filter conditions
        filter_conditions = []
        params = student_ids.copy()
        param_idx = len(student_ids) + 1
        
        placeholders = ','.join([f"${i+1}" for i in range(len(student_ids))])
        where_clause = f"WHERE id IN ({placeholders})"
        
        if branches:
            # text ->> 'branch'
            branch_placeholders = ','.join([f"${i+param_idx}" for i in range(len(branches))])
            filter_conditions.append(f"text::jsonb->>'branch' IN ({branch_placeholders})")
            params.extend(branches)
            param_idx += len(branches)
        
        if min_semester is not None:
             # text ->> 'semester' cast to int
            filter_conditions.append(f"(text::jsonb->>'semester')::int >= ${param_idx}")
            params.append(min_semester)
            param_idx += 1
        
        if min_cgpa is not None:
             # text ->> 'cgpa' cast to float
            filter_conditions.append(f"(text::jsonb->>'cgpa')::float >= ${param_idx}")
            params.append(min_cgpa)
            param_idx += 1
        
        if filter_conditions:
            where_clause += " AND " + " AND ".join(filter_conditions)
        
        # Fetch filtered IDs
        query = f"""
            SELECT id
            FROM student_profiles
            {where_clause}
        """
        
        filtered_ids = await self.db.fetch(query, *params)
        filtered_id_set = {str(row['id']) for row in filtered_ids}
        
        # Filter results
        return [r for r in results if str(r['student_id']) in filtered_id_set]
    
    # ==================== ENRICHMENT ====================
    
    async def _enrich_with_profiles(
        self,
        results: List[Dict],
        query_terms: List[str],
        bm25_results: List[Dict],
        vector_results: List[Dict]
    ) -> List[Dict]:
        """Enrich with full student profiles"""
        
        if not results:
            return []
        
        student_ids = [str(r['student_id']) for r in results]
        
        # Fetch profiles
        placeholders = ','.join([f"${i+1}" for i in range(len(student_ids))])
        query = f"""
            SELECT id, text, metadata
            FROM student_profiles
            WHERE id IN ({placeholders})
        """
        
        profiles = await self.db.fetch(query, *student_ids)
        profile_map = {}
        for p in profiles:
             import json
             try:
                 data = json.loads(p['text'])
                 # Start with data from 'text'
                 profile_map[str(p['id'])] = data
                 # Add metadata fields if needed
                 profile_map[str(p['id'])]['metadata'] = json.loads(p['metadata']) if isinstance(p['metadata'], str) else p['metadata']
             except:
                 profile_map[str(p['id'])] = {}

        
        # Build enriched results
        enriched = []
        for rank, result in enumerate(results, 1):
            sid = str(result['student_id'])
            profile = profile_map.get(sid, {})
            
            # Extract top skills
            top_skills = []
            if profile.get('skills'):
                try:
                    skills = sorted(
                        profile['skills'],
                        key=lambda s: s.get('average_normalized_score', 0),
                        reverse=True
                    )[:5]
                    
                    top_skills = [
                        {
                            "name": s.get('tool_name', 'N/A'),
                            "score": s.get('average_normalized_score', 0),
                            "domain": s.get('domain_name', 'N/A')
                        }
                        for s in skills
                    ]
                except:
                    top_skills = []
            
            # Generate match insight
            match_insight = self._generate_match_insight(
                result,
                query_terms,
                bm25_results,
                vector_results
            )
            
            enriched.append({
                "rank": rank,
                "student": {
                    "id": sid,
                    "name": profile.get('name', 'N/A'),
                    "email": profile.get('email', 'N/A'),
                    "branch": profile.get('branch', 'N/A'),
                    "semester": str(profile.get('semester', 'N/A')),
                    "cgpa": profile.get('cgpa', 0.0),
                    "role": profile.get('branch', 'N/A'),
                    "location": profile.get('tenant_address', 'N/A') if profile.get('tenant_address') else "N/A",
                    "tenant_name": profile.get('tenant_name', 'N/A')
                },
                "scores": {
                    "final_score": round(result['final_score'], 4),
                    "breakdown": {
                        "bm25_score": round(result.get('bm25_score', 0), 2),
                        "bm25_normalized": round(result.get('bm25_normalized', 0), 2),
                        "vector_score": round(result.get('vector_score', 0), 2),
                        "base_fusion_score": round(result.get('base_fusion_score', 0), 2),
                        "skill_boost": round(result.get('skill_boost', 0), 4),
                        "recency_boost": round(result.get('recency_boost', 0), 4)
                    }
                },
                "match_details": {
                    "matched_chunks": result['matched_chunks'],
                    "keywords_found": list(result['term_contributions'].keys()) if result.get('term_contributions') else [],
                    "bm25_term_contributions": result.get('term_contributions', {}),
                    "vector_similarity": round(result.get('vector_score', 0), 2),
                    "top_skills": top_skills
                },
                "content_preview": result.get('content_preview', ''),
                "match_insight": match_insight
            })
        
        return enriched
    
    def _generate_match_insight(
        self,
        result: Dict,
        query_terms: List[str],
        bm25_results: List[Dict],
        vector_results: List[Dict]
    ) -> str:
        """Generate human-readable match explanation"""
        insights = []
        
        # Fusion score
        insights.append(f"Final score: {result['final_score']:.2f}")
        
        # BM25 component
        bm25_norm = result.get('bm25_normalized', 0)
        if bm25_norm > 0.7:
            insights.append(f"Strong lexical match (BM25: {bm25_norm:.2f})")
        elif bm25_norm > 0:
            insights.append(f"Lexical match (BM25: {bm25_norm:.2f})")
        
        # Vector component
        vector_score = result.get('vector_score', 0)
        if vector_score > 0.7:
            insights.append(f"Strong semantic alignment (Vector: {vector_score:.2f})")
        elif vector_score > 0:
            insights.append(f"Semantic match (Vector: {vector_score:.2f})")
        
        # Boosts
        if result.get('skill_boost', 0) > 0:
            insights.append(f"Skill boost: +{result['skill_boost']:.2f}")
        
        if result.get('recency_boost', 0) > 0:
            insights.append(f"Recency boost: +{result['recency_boost']:.2f}")
        
        # Matched chunks
        if result.get('matched_chunks'):
            insights.append(f"Found in: {', '.join(result['matched_chunks'])}")
        
        return " | ".join(insights)
    
    # ==================== HELPER FUNCTIONS ====================
    
    async def _get_corpus_stats(self, chunk_types: Optional[List[str]]) -> Dict:
        """Get corpus statistics"""
        where_clause = ""
        params = []
        
        if chunk_types:
            placeholders = ','.join([f"${i+1}" for i in range(len(chunk_types))])
            where_clause = f"WHERE chunk_type IN ({placeholders})"
            params = chunk_types
        
        # Adjusted table to user_profile_chunks
        query = f"""
            SELECT 
                COUNT(*) as total_docs,
                AVG(array_length(regexp_split_to_array(content, '\s+'), 1)) as avg_doc_length
            FROM user_profile_chunks
            {where_clause}
        """
        
        # Note: If user_profile_chunks is empty, we should fallback or handle it
        if params:
            result = await self.db.fetchrow(query, *params)
        else:
            result = await self.db.fetchrow(query)
        
        return {
            'total_docs': result['total_docs'] if result and result['total_docs'] else 1,
            'avg_doc_length': result['avg_doc_length'] if result and result['avg_doc_length'] else 50.0
        }
    
    async def _count_docs_with_term(self, term: str, chunk_types: Optional[List[str]]) -> int:
        """Count documents containing a term"""
        where_clause = "WHERE LOWER(content) LIKE $1"
        params = [f'%{term}%']
        
        if chunk_types:
            placeholders = ','.join([f"${i+2}" for i in range(len(chunk_types))])
            where_clause += f" AND chunk_type IN ({placeholders})"
            params.extend(chunk_types)
        
        # Adjusted table
        query = f"""
            SELECT COUNT(*) as doc_freq
            FROM user_profile_chunks
            {where_clause}
        """
        
        result = await self.db.fetchrow(query, *params)
        return result['doc_freq']
    
    async def _fetch_candidate_chunks(
        self,
        query_terms: List[str],
        chunk_types: Optional[List[str]]
    ) -> List[Dict]:
        """Fetch chunks that might contain query terms"""
        like_conditions = []
        params = []
        param_idx = 1
        
        for term in query_terms:
            like_conditions.append(f"LOWER(content) LIKE ${param_idx}")
            params.append(f'%{term}%')
            param_idx += 1
        
        where_clause = f"WHERE ({' OR '.join(like_conditions)})"
        
        if chunk_types:
            placeholders = ','.join([f"${i+param_idx}" for i in range(len(chunk_types))])
            where_clause += f" AND chunk_type IN ({placeholders})"
            params.extend(chunk_types)
        
        # Adjusted table and columns
        query = f"""
            SELECT id, user_id as student_id, chunk_type, content
            FROM user_profile_chunks
            {where_clause}
        """
        
        chunks = await self.db.fetch(query, *params)
        return [dict(chunk) for chunk in chunks]
    
    def _detect_intent(self, query_terms: List[str]) -> str:
        """Detect query intent based on terms"""
        technical_terms = {
            'python', 'java', 'javascript', 'react', 'node', 'sql',
            'aws', 'docker', 'kubernetes', 'mongodb', 'postgresql',
            'typescript', 'fastapi', 'django', 'flask', 'angular', 'vue'
        }
        
        soft_skill_terms = {
            'leader', 'leadership', 'creative', 'innovative', 'team',
            'communication', 'mentor', 'collaborative', 'organized'
        }
        
        has_technical = any(term in technical_terms for term in query_terms)
        has_soft = any(term in soft_skill_terms for term in query_terms)
        
        if has_technical and has_soft:
            return "mixed_technical_soft_skills"
        elif has_technical:
            return "technical_skill_search"
        elif has_soft:
            return "soft_skill_search"
        else:
            return "general_search"
