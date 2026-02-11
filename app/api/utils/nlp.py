import re
from typing import List, Dict

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'this', 'that', 'these', 'those', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
    'give', 'me', 'someone', 'need', 'want', 'looking', 'for', 'find', 'search', 'get', 'show', 'list'
}

def tokenize_query(query: str) -> List[str]:
    """Remove stop words, extract meaningful keywords"""
    # Convert to lowercase and remove punctuation
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    tokens = clean_query.split()
    # Remove stop words
    keywords = [token for token in tokens if token not in STOP_WORDS]
    return keywords

def extract_candidate_info(text: str) -> Dict[str, str]:
    """Use regex to extract structured data from profile text"""
    info = {}
    
    # Extract Name
    name_match = re.search(r'Candidate:\s*([^|]+)', text)
    if name_match:
        info['name'] = name_match.group(1).strip()
        
    # Extract Role
    role_match = re.search(r'Role:\s*([^|]+)', text)
    if role_match:
        info['role'] = role_match.group(1).strip()
        
    # Extract Location
    loc_match = re.search(r'Location:\s*([^|]+)', text)
    if loc_match:
        info['location'] = loc_match.group(1).strip()
        
    # Extract Experience
    exp_match = re.search(r'Exp:\s*(.+?)(?=\n|$)', text)
    if exp_match:
        info['experience'] = exp_match.group(1).strip()
        
    # Extract Skills
    skills_match = re.search(r'Skills:\s*(.+?)(?=\n|$)', text)
    if skills_match:
        info['skills_text'] = skills_match.group(1).strip()
        # Try to parse individual skills if they are comma separated
        # Format: Skill (Domain: ... | Score), Skill 2 ...
        # This is complex to parse perfectly with regex, but we can try a simple split
        
    # Extract Projects
    projects_match = re.search(r'Projects:\s*(.+?)(?=\n|$)', text)
    if projects_match:
        info['projects_text'] = projects_match.group(1).strip()
        
    # Extract Awards
    awards_match = re.search(r'Awards:\s*(.+?)(?=\n|$)', text)
    if awards_match:
        info['awards_text'] = awards_match.group(1).strip()
        
    return info

def highlight_matches(text: str, keywords: List[str]) -> str:
    """Add HTML highlighting to matched terms"""
    if not keywords:
        return text
        
    highlighted_text = text
    for keyword in keywords:
        if len(keyword) < 2: continue # Skip very short keywords
        # Case-insensitive replacement with preserving original case
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(lambda m: f'<mark class="bg-yellow-200">{m.group(0)}</mark>', highlighted_text)
        
    return highlighted_text

def calculate_keyword_score(text: str, keywords: List[str]) -> float:
    """Score based on keyword frequency"""
    if not keywords:
        return 0.0
        
    text_lower = text.lower()
    score = 0.0
    
    for keyword in keywords:
        count = text_lower.count(keyword.lower())
        score += count
        
    return score
