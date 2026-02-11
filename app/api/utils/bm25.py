"""
BM25 Probabilistic Search Strategy
Standalone implementation - no dependencies on other search strategies
"""

import re
import math
from typing import List, Dict, Tuple, Any
from collections import Counter
from app.api.utils.database import execute_query, get_db_connection
from app.api.utils.nlp import extract_candidate_info
import time
from psycopg2.extras import RealDictCursor

class BM25Ranker:
    """Pure BM25 scoring logic"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.6):
        self.k1 = k1
        self.b = b
        
    def tokenize(self, text: str) -> List[str]:
        """Convert text to searchable tokens"""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        
        # Remove common stop words (expanded set)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 
            'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is',
            'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'can', 'could',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'their',
            'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her'
        }
        return [t for t in tokens if t not in stop_words and len(t) > 2]
    
    def calculate_idf(self, total_docs: int, docs_with_term: int) -> float:
        """IDF = ln[(N - n(t) + 0.5) / (n(t) + 0.5) + 1]"""
        return math.log((total_docs - docs_with_term + 0.5) / (docs_with_term + 0.5) + 1)
    
    def score_document(
        self, 
        query_terms: List[str],
        doc_content: str,
        doc_length: int,
        avg_doc_length: float,
        idf_scores: Dict[str, float]
    ) -> Tuple[float, Dict]:
        """Calculate BM25 score for one document"""
        doc_tokens = self.tokenize(doc_content)
        term_freq = Counter(doc_tokens)
        
        total_score = 0.0
        term_contributions = {}
        
        for term in query_terms:
            if term not in term_freq:
                continue
                
            tf = term_freq[term]
            idf = idf_scores.get(term, 0)
            
            # BM25 TF component with length normalization
            avg_dl = avg_doc_length if avg_doc_length > 0 else 1
            length_norm = 1 - self.b + self.b * (doc_length / avg_dl)
            
            tf_component = (tf * (self.k1 + 1)) / (tf + self.k1 * length_norm)
            
            contribution = idf * tf_component
            total_score += contribution
            term_contributions[term] = round(contribution, 2)
        
        return total_score, term_contributions


class BM25Search:
    """Database-integrated BM25 search"""
    
    def __init__(self):
        self.ranker = BM25Ranker(k1=1.5, b=0.75) # Standard b=0.75 for general text
    
    def search(
        self,
        query: str,
        chunk_types: List[str] = None,
        top_k: int = 20
    ) -> Dict:
        """
        Execute BM25 search against student_profiles
        """
        start_time = time.time()
        
        # Step 1: Tokenize query
        query_terms = self.ranker.tokenize(query)
        if not query_terms:
            return {"error": "No valid search terms", "results": []}
        
        # Use a single connection for all operations to avoid handshake overhead/timeouts
        t0 = time.time()
        conn = get_db_connection()
        print(f"DEBUG TIMING: Connection established in {time.time()-t0:.4f}s", flush=True)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                
                # Step 2: Get corpus statistics
                t1 = time.time()
                stats = self._get_corpus_stats(cur)
                print(f"DEBUG TIMING: Stats in {time.time()-t1:.4f}s", flush=True)
                
                # Step 3: Calculate IDF for each query term
                t2 = time.time()
                idf_scores = self._calculate_idf_scores(cur, query_terms, stats['total_docs'])
                print(f"DEBUG TIMING: IDF in {time.time()-t2:.4f}s", flush=True)
                
                # Step 4: Fetch candidate documents
                t3 = time.time()
                documents = self._fetch_documents(cur, query_terms)
                print(f"DEBUG TIMING: Fetch in {time.time()-t3:.4f}s (Fetched {len(documents)})", flush=True)
                
                # Step 5: Score each document
                t_score = time.time()
                scored_docs = []
                for doc in documents:
                    try:
                        content = doc.get('text') or ''
                        # OPTIMIZATION: Cap content length to avoid massive processing time
                        if len(content) > 50000:
                            content = content[:50000]
                            
                        doc_len = len(content.split())
                        
                        score, term_contribs = self.ranker.score_document(
                            query_terms,
                            content,
                            doc_len,
                            stats['avg_doc_length'],
                            idf_scores
                        )
                        
                        if score > 0:
                            # METADATA FALLBACK FIX
                            meta = doc.get('metadata') or {}
                            if not meta.get('name') or not meta.get('role'):
                                # Try parsing text as JSON first (common in this DB)
                                import json
                                try:
                                    json_content = json.loads(content)
                                    if isinstance(json_content, dict):
                                        # Map common JSON keys to metadata
                                        if not meta.get('name'): meta['name'] = json_content.get('name') or json_content.get('Name')
                                        if not meta.get('role'): meta['role'] = json_content.get('role') or json_content.get('Role') or json_content.get('job_title')
                                        if not meta.get('location'): meta['location'] = json_content.get('location') or json_content.get('Location')
                                        if not meta.get('email'): meta['email'] = json_content.get('email')
                                except:
                                    pass
                                    
                                # Fallback to regex if still missing
                                if not meta.get('name') or not meta.get('role'):
                                    extracted = extract_candidate_info(content)
                                    meta.update(extracted)

                            scored_docs.append({
                                'id': doc['id'],
                                'metadata': meta,
                                'text': content,
                                'score': score,
                                'term_contributions': term_contribs
                            })
                    except Exception as e:
                        print(f"Error scoring doc: {e}")
                        continue
                print(f"DEBUG TIMING: Scoring loop in {time.time()-t_score:.4f}s for {len(documents)} docs", flush=True)
                
                # Step 6: Sort and Format
                scored_docs.sort(key=lambda x: x['score'], reverse=True)
                results = self._format_results(scored_docs, top_k)
                
                return {
                    "strategy": "bm25",
                    "total_results": len(results),
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                    "parameters": {"k1": self.ranker.k1, "b": self.ranker.b},
                    "results": results
                }
                    
        except Exception as e:
            print(f"BM25 Error: {e}")
            raise e
        finally:
            conn.close()

    def _get_corpus_stats(self, cur) -> Dict:
        """Get total docs and average document length"""
        query = """
            SELECT 
                COUNT(*) as total_docs,
                AVG(length(text) / 6.0) as avg_doc_length
            FROM student_profiles
        """
        cur.execute(query)
        row = cur.fetchone()
        if row:
            return {
                'total_docs': row['total_docs'],
                'avg_doc_length': float(row['avg_doc_length']) if row['avg_doc_length'] else 100.0
            }
        return {'total_docs': 0, 'avg_doc_length': 100.0}
    
    def _calculate_idf_scores(self, cur, terms: List[str], total_docs: int) -> Dict[str, float]:
        """Calculate IDF for each query term"""
        idf_scores = {}
        for term in terms:
            query = "SELECT COUNT(*) as doc_freq FROM student_profiles WHERE text ILIKE %s"
            cur.execute(query, (f'%{term}%',))
            result = cur.fetchone()
            doc_freq = result['doc_freq'] if result else 0
            idf_scores[term] = self.ranker.calculate_idf(total_docs, doc_freq)
        return idf_scores
    
    def _fetch_documents(self, cur, query_terms: List[str]) -> List[Dict]:
        """Fetch documents containing at least one query term"""
        conditions = []
        params = []
        for term in query_terms:
            conditions.append("text ILIKE %s")
            params.append(f"%{term}%")
            
        where_clause = " OR ".join(conditions)
        query = f"""
            SELECT id, SUBSTRING(text, 1, 50000) as text, metadata
            FROM student_profiles
            WHERE {where_clause}
            LIMIT 200
        """
        cur.execute(query, tuple(params))
        return cur.fetchall()
    
    def _format_results(self, scored_docs: List[Dict], top_k: int) -> List[Dict]:
        """Format output for API response"""
        top_docs = scored_docs[:top_k]
        if not top_docs:
            return []
            
        max_score = top_docs[0]['score'] if top_docs else 1.0
        results = []
        
        for rank, doc in enumerate(top_docs, 1):
            normalized = doc['score'] / max_score if max_score > 0 else 0
            active_keywords = {k: v for k, v in doc['term_contributions'].items() if v > 0}
            meta = doc['metadata'] or {}
            
            # Highlight matched keywords in text
            highlighted = doc['text']
            for kw in active_keywords.keys():
                # Simple case-insensitive replacement (better to use regex but keep it fast)
                import re
                highlighted = re.sub(f'(?i)({re.escape(kw)})', r'<mark>\1</mark>', highlighted)

            results.append({
                "rank": rank,
                "id": str(doc['id']),
                "text": doc['text'], # ResultCard expects 'text'
                "highlighted_text": highlighted[:500] + "...", # ResultCard uses this if present
                "metadata": meta,    # ResultCard expects 'metadata' object with name, role, etc.
                "score": round(normalized, 4),
                "match_reason": f"Exact keyword match: {', '.join(list(active_keywords.keys())[:5])}" if active_keywords else "High keyword relevance (BM25)",
                "matched_keywords": list(active_keywords.keys()), # ResultCard uses this
                "match_details": {
                    "bm25_raw_score": doc['score'],
                    "term_contributions": active_keywords
                }
            })
            
        return results
