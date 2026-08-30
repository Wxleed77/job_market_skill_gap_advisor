"""
STEP 3: Skill Extraction Pipeline

Multiple extraction strategies:
1. Keyword-based: Fast, high precision on known skills
2. spaCy NER: Entity recognition, catches contextual skills
3. LLM-based: (Optional) Most accurate but slower

Per spec §5: Populate skills_extracted from raw posting text.
"""

import re
from typing import List, Dict, Set, Tuple
import spacy
from collections import Counter

# Enhanced skill vocabulary (more comprehensive than STEP 1)
SKILL_KEYWORDS = {
    # Programming Languages
    "python": ["python", "py"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "csharp": ["c#", "csharp", "c sharp"],
    "cpp": ["c++", "cpp", "c plus plus"],
    "php": ["php"],
    "go": ["golang", "go"],
    "rust": ["rust"],
    "dart": ["dart"],
    "kotlin": ["kotlin"],
    "solidity": ["solidity"],
    "r": ["\\br\\b"],  # Single letter, use word boundary
    "scala": ["scala"],
    
    # Frontend Frameworks & Libraries
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vuejs"],
    "angular": ["angular"],
    "next.js": ["next.js", "nextjs"],
    "svelte": ["svelte"],
    "ember": ["ember"],
    
    # Backend Frameworks
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "express": ["express", "express.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "spring": ["spring", "spring boot"],
    "laravel": ["laravel"],
    "rails": ["rails", "ruby on rails"],
    
    # Databases
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb"],
    "redis": ["redis"],
    "oracle": ["oracle"],
    "elasticsearch": ["elasticsearch"],
    "dynamodb": ["dynamodb"],
    "cassandra": ["cassandra"],
    "mariadb": ["mariadb"],
    
    # Cloud & DevOps
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "cloud run", "bigquery"],
    "azure": ["azure", "microsoft azure"],
    "kubernetes": ["kubernetes", "k8s"],
    "docker": ["docker"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "jenkins": ["jenkins"],
    "github actions": ["github actions"],
    "gitlab ci": ["gitlab ci"],
    "circleci": ["circleci", "circle ci"],
    
    # ML/AI Tools
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "keras": ["keras"],
    "hugging face": ["hugging face"],
    "transformers": ["transformers"],
    "xgboost": ["xgboost"],
    
    # Data Processing
    "numpy": ["numpy"],
    "pandas": ["pandas"],
    "spacy": ["spacy"],
    "nltk": ["nltk"],
    "apache spark": ["spark", "apache spark", "pyspark"],
    "apache kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    
    # Version Control
    "git": ["git"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "bitbucket": ["bitbucket"],
    
    # APIs & Architecture
    "rest api": ["rest api", "restful"],
    "graphql": ["graphql"],
    "grpc": ["grpc"],
    "soap": ["soap"],
    
    # Databases & Query Languages
    "sql": ["sql"],
    "tsql": ["tsql", "t-sql"],
    "plsql": ["plsql", "pl/sql"],
    
    # Web Technologies
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "sass": ["sass", "scss"],
    "tailwind": ["tailwind", "tailwind css"],
    "bootstrap": ["bootstrap"],
    
    # Testing
    "selenium": ["selenium"],
    "jest": ["jest"],
    "pytest": ["pytest"],
    "testng": ["testng"],
    "mocha": ["mocha"],
    "jasmine": ["jasmine"],
    
    # Design Tools
    "figma": ["figma"],
    "adobe xd": ["adobe xd", "xd"],
    "sketch": ["sketch"],
    
    # Other Tools
    "jira": ["jira"],
    "prometheus": ["prometheus"],
    "grafana": ["grafana"],
    "elk stack": ["elk", "elasticsearch logstash kibana"],
    "redis": ["redis"],
    "celery": ["celery"],
    "web3": ["web3", "web3.js"],
    "linux": ["linux"],
    "windows": ["windows"],
    "macos": ["macos", "mac os"],
    "microservices": ["microservices", "microservice"],
    "aws lambda": ["lambda"],
    "cloud functions": ["cloud functions"],
}

class KeywordSkillExtractor:
    """Fast keyword-based skill extraction."""
    
    @staticmethod
    def extract(text: str) -> List[str]:
        """Extract skills using keyword matching."""
        text_lower = text.lower()
        found_skills = set()
        
        for skill, keywords in SKILL_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundary to avoid partial matches
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, text_lower):
                    found_skills.add(skill)
                    break
        
        return sorted(list(found_skills))


class SpacySkillExtractor:
    """
    spaCy-based skill extraction using NER.
    Identifies ORG, PRODUCT entities that are likely skills/tools.
    """
    
    SKILL_PATTERNS = {
        # Technology companies/products
        "aws": ["amazon", "aws"],
        "google cloud": ["google", "gcp"],
        "azure": ["microsoft"],
        "kubernetes": ["k8s"],
        "tensorflow": ["tensorflow"],
        "pytorch": ["pytorch"],
        "react": ["react", "facebook"],
        "angular": ["angular", "google"],
        "vue": ["vue"],
        "nodejs": ["node"],
    }
    
    def __init__(self):
        """Load spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract(self, text: str) -> List[str]:
        """Extract skills using spaCy NER + keyword patterns."""
        if self.nlp is None:
            return []
        
        doc = self.nlp(text)
        found_skills = set()
        
        # Extract from named entities (ORG, PRODUCT, GPE)
        for ent in doc.ents:
            ent_text = ent.text.lower()
            
            # Check against known patterns
            for skill_name, patterns in self.SKILL_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in ent_text:
                        found_skills.add(skill_name)
        
        # Also run keyword extraction as fallback
        keyword_skills = KeywordSkillExtractor.extract(text)
        found_skills.update(keyword_skills)
        
        return sorted(list(found_skills))


class HybridSkillExtractor:
    """
    Combines keyword-based + spaCy NER for best of both worlds.
    
    Strategy:
    1. Run keyword extraction (high precision, covers known tools)
    2. Run spaCy NER (catches contextual mentions)
    3. Union the results
    """
    
    def __init__(self):
        self.keyword_extractor = KeywordSkillExtractor()
        self.spacy_extractor = SpacySkillExtractor()
    
    def extract(self, text: str) -> List[str]:
        """Extract skills using both methods."""
        keyword_skills = set(self.keyword_extractor.extract(text))
        spacy_skills = set(self.spacy_extractor.extract(text))
        
        # Union: prefer keyword extraction, but include spaCy catches too
        all_skills = keyword_skills | spacy_skills
        
        return sorted(list(all_skills))
    
    def extract_with_metadata(self, text: str) -> Dict:
        """Extract skills and return detailed metadata."""
        keyword_skills = set(self.keyword_extractor.extract(text))
        spacy_skills = set(self.spacy_extractor.extract(text))
        all_skills = keyword_skills | spacy_skills
        
        return {
            "skills": sorted(list(all_skills)),
            "keyword_only": sorted(list(keyword_skills - spacy_skills)),
            "spacy_only": sorted(list(spacy_skills - keyword_skills)),
            "both_methods": sorted(list(keyword_skills & spacy_skills)),
            "total_unique": len(all_skills),
        }


def compare_extraction_methods(text: str) -> Dict:
    """
    Compare all extraction methods on a sample text.
    
    Returns:
        Dict with skills from each method and comparison
    """
    keyword_skills = KeywordSkillExtractor.extract(text)
    spacy_skills = SpacySkillExtractor().extract(text)
    hybrid_skills = HybridSkillExtractor().extract(text)
    
    # Find differences
    only_keyword = set(keyword_skills) - set(spacy_skills)
    only_spacy = set(spacy_skills) - set(keyword_skills)
    both = set(keyword_skills) & set(spacy_skills)
    
    return {
        "keyword_method": keyword_skills,
        "spacy_method": spacy_skills,
        "hybrid_method": hybrid_skills,
        "comparison": {
            "only_keyword": sorted(list(only_keyword)),
            "only_spacy": sorted(list(only_spacy)),
            "both_methods": sorted(list(both)),
            "accuracy": {
                "keyword_coverage": len(keyword_skills),
                "spacy_coverage": len(spacy_skills),
                "hybrid_coverage": len(hybrid_skills),
            }
        }
    }
