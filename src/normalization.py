"""
Normalization function to parse raw posting text and produce structured schema.

Schema per spec §3/§5:
- posting_id: unique identifier
- title: job title
- company: company name
- city: city/location
- role_category: category of role (backend, frontend, devops, ml, etc)
- skills_extracted: list of skills (using hybrid extraction: keyword + spaCy NER)
- date_posted: ISO format date
- source: where it came from (rozee.pk, linkedin, etc)
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from src.skill_extraction import HybridSkillExtractor

# Initialize hybrid skill extractor (lazy load on first use)
_skill_extractor = None

def get_skill_extractor():
    """Lazy-load the hybrid skill extractor."""
    global _skill_extractor
    if _skill_extractor is None:
        _skill_extractor = HybridSkillExtractor()
    return _skill_extractor

# Role category mapping
ROLE_CATEGORY_KEYWORDS = {
    "backend": ["backend", "backend engineer", "python developer", "fastapi", "django", 
                "node.js", "express", "server", "api", "microservice"],
    "frontend": ["frontend", "frontend developer", "react", "angular", "vue", "next.js", "javascript"],
    "fullstack": ["full stack", "fullstack", "full-stack"],
    "devops": ["devops", "sre", "site reliability", "infrastructure", "cloud", "kubernetes", 
               "docker", "terraform", "aws"],
    "ml": ["machine learning", "ml engineer", "ai", "artificial intelligence", "nlp", "deep learning",
           "tensorflow", "pytorch", "data science"],
    "mobile": ["mobile", "flutter", "react native", "ios", "android", "app developer"],
    "qa": ["qa", "qe", "quality assurance", "automation tester", "test engineer"],
    "product": ["product manager", "pm", "product"],
    "designer": ["designer", "ux", "ui", "design", "figma"],
    "security": ["security", "cybersecurity", "penetration", "pentesting"],
    "data": ["data analyst", "data engineer", "analytics"],
}

def extract_text_from_html(html: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    # Remove HTML tags but preserve some structure
    text = re.sub(r"<[^>]+>", "\n", html)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_title(raw_html: str) -> Optional[str]:
    """Extract job title from HTML, looking for h1/h2 tags."""
    # Look for title in h1, h2, or the first <strong> tag
    patterns = [
        r"<h[12]>([^<]+)</h[12]>",
        r"<strong>([^<]{5,100})</strong>",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_html, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if title and len(title) < 150:
                return title
    
    return None

def extract_company(raw_html: str) -> Optional[str]:
    """Extract company name from HTML."""
    # Look for "Company:" pattern in the HTML
    patterns = [
        r"<strong>Company[^<]*?:</strong>\s*([^<]+?)<",
        r"Company[^<]*?:\s*([^<]+?)<",
        r"Company[^<]*?:\s*([^<]+?)(?:\n|<)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_html, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            if company and len(company) < 100:
                return company
    
    return None

def extract_city(raw_html: str) -> Optional[str]:
    """Extract city/location from HTML."""
    raw_html_lower = raw_html.lower()
    
    # Look for "Location:" or "City:" patterns
    patterns = [
        r"<strong>(?:location|city)[^<]*?:</strong>\s*([^<]+?)<",
        r"(?:location|city)[^<]*?:\s*([^<]+?)<",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_html, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            if city and city.lower() != "remote" and len(city) < 50:
                return city
    
    # Known Pakistan cities
    pakistan_cities = ["karachi", "lahore", "islamabad", "rawalpindi", "multan", 
                      "faisalabad", "peshawar", "quetta", "hyderabad"]
    
    for city in pakistan_cities:
        if city in raw_html_lower:
            return city.capitalize()
    
    return "Remote" if "remote" in raw_html_lower else None

def extract_date_posted(text: str) -> str:
    """Extract posting date."""
    # Look for date patterns
    patterns = [
        r"(?:posted|date|posted date)[:\s]*([A-Za-z]+ \d{1,2},? \d{4})",
        r"(\d{4}-\d{2}-\d{2})",
        r"([A-Za-z]+ \d{1,2}, \d{4})",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                # Try to parse various formats
                for fmt in ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%B %d %Y", "%b %d %Y"]:
                    try:
                        dt = datetime.strptime(date_str.replace(",", ""), fmt)
                        return dt.isoformat()
                    except:
                        continue
            except:
                pass
    
    # Default to today if not found
    return datetime.now().isoformat()

def extract_skills(text: str) -> List[str]:
    """Extract skills from text using hybrid method (keyword + spaCy NER)."""
    extractor = get_skill_extractor()
    return extractor.extract(text)

def infer_role_category(text: str, title: str = "") -> str:
    """Infer role category from text and title."""
    combined = (title + " " + text).lower()
    
    # Score each category
    scores = {}
    for category, keywords in ROLE_CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        scores[category] = score
    
    # Return category with highest score, default to "other"
    if scores and max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "other"

def normalize_posting(raw_posting: Dict) -> Dict:
    """
    Normalize a raw posting to the structured schema.
    
    Args:
        raw_posting: Dict with keys: source, posting_id, raw_html
        
    Returns:
        Normalized posting dict with schema: posting_id, title, company, city,
        role_category, skills_extracted, date_posted, source
    """
    raw_html = raw_posting.get("raw_html", "")
    text = extract_text_from_html(raw_html)
    
    title = extract_title(raw_html) or "Unknown Position"
    company = extract_company(raw_html) or "Unknown Company"
    city = extract_city(raw_html) or "Not Specified"
    skills = extract_skills(text)
    date_posted = extract_date_posted(text)
    role_category = infer_role_category(text, title)
    
    return {
        "posting_id": raw_posting.get("posting_id"),
        "title": title,
        "company": company,
        "city": city,
        "role_category": role_category,
        "skills_extracted": skills,
        "date_posted": date_posted,
        "source": raw_posting.get("source"),
    }

def normalize_postings(raw_postings: List[Dict]) -> List[Dict]:
    """Normalize a batch of raw postings."""
    return [normalize_posting(posting) for posting in raw_postings]
