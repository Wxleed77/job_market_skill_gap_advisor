"""
STEP 4: Specific Query Retrieval + LLM Synthesis (Mode 1 from spec §6)

Two modes of operation:
1. Specific queries: "Show me postings that want LangChain" 
   -> Vector search + metadata filter -> top-k retrieval -> LLM synthesis

2. Aggregate queries: "What should I learn for AI roles in Karachi"
   -> Metadata filter for ALL matching postings -> skill frequency count -> LLM narration
"""

from typing import List, Dict, Optional, Tuple
from collections import Counter
from src.chunking_embedding import QdrantVectorDB, EmbeddingEngine
from src.llm_synthesis import OpenRouterLLM, LLMSynthesizer


class QueryClassifier:
    """Classify queries into specific vs aggregate modes."""
    
    # Keywords indicating aggregate/analytical queries
    AGGREGATE_KEYWORDS = [
        "what should i learn",
        "in demand",
        "popular skills",
        "trending",
        "for [a-z]+ roles",  # "for AI roles", "for backend roles"
        "across",
        "summary of",
        "overview of",
        "analyze",
    ]
    
    # Keywords indicating specific retrieval queries
    SPECIFIC_KEYWORDS = [
        "show me",
        "find me",
        "postings",
        "job that",
        "looking for",
        "want",
        "require",
        "hiring for",
    ]
    
    @staticmethod
    def classify(query: str) -> str:
        """
        Classify query as 'specific' or 'aggregate'.
        
        Returns:
            'specific' or 'aggregate'
        """
        query_lower = query.lower()
        
        # Check aggregate keywords first (more specific)
        for keyword in QueryClassifier.AGGREGATE_KEYWORDS:
            if keyword.replace("[a-z]+ ", "").lower() in query_lower:
                return "aggregate"
        
        # Check specific keywords
        for keyword in QueryClassifier.SPECIFIC_KEYWORDS:
            if keyword in query_lower:
                return "specific"
        
        # Default: if it sounds like a general question, aggregate
        if "?" in query:
            return "aggregate"
        
        return "specific"
    
    @staticmethod
    def extract_filters(query: str) -> Dict:
        """Extract potential city/role filters from query."""
        filters = {}
        query_lower = query.lower()
        
        # City names
        cities = ["karachi", "lahore", "islamabad", "rawalpindi", "multan", 
                 "faisalabad", "peshawar", "hyderabad"]
        for city in cities:
            if city in query_lower:
                filters["city"] = city.capitalize()
        
        # Role categories - map variations to standard names
        role_mappings = {
            "backend": ["backend"],
            "frontend": ["frontend"],
            "fullstack": ["fullstack", "full-stack", "full stack"],
            "devops": ["devops", "sre"],
            "ml": ["ml", "machine learning", "ai", "artificial intelligence"],
            "mobile": ["mobile", "react native", "flutter"],
            "data": ["data", "analytics"],
            "designer": ["designer", "design", "ux", "ui"],
            "security": ["security", "infosec"],
        }
        
        for standard_role, variations in role_mappings.items():
            for var in variations:
                if var in query_lower:
                    filters["role_category"] = standard_role
                    break
        
        return filters


class SpecificQueryRetrieval:
    """Handle Mode 1: Specific query retrieval."""
    
    def __init__(self, vector_db: QdrantVectorDB, embedding_engine: EmbeddingEngine):
        self.vector_db = vector_db
        self.embedding_engine = embedding_engine
    
    def retrieve(self, 
                query: str,
                city: Optional[str] = None,
                role_category: Optional[str] = None,
                k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks for a specific query.
        
        Args:
            query: User query text
            city: Optional city filter
            role_category: Optional role filter
            k: Number of results to return
            
        Returns:
            List of retrieved chunks with metadata
        """
        # Embed the query
        query_embedding = list(self.embedding_engine.model.embed([query]))[0]
        
        # Search with optional filters
        if city or role_category:
            results = self.vector_db.search_with_filter(
                query_embedding,
                city=city,
                role_category=role_category,
                k=k
            )
        else:
            results = self.vector_db.search(query_embedding, k=k)
        
        return results
    
    def retrieve_and_synthesize(self,
                               query: str,
                               llm_synthesizer: LLMSynthesizer,
                               city: Optional[str] = None,
                               role_category: Optional[str] = None,
                               k: int = 5) -> Dict:
        """
        Retrieve chunks and synthesize answer with LLM.
        
        Returns:
            Dict with answer, sources, and metadata
        """
        # Retrieve
        chunks = self.retrieve(query, city, role_category, k)
        
        if not chunks:
            return {
                "query": query,
                "query_type": "specific",
                "answer": "No relevant postings found.",
                "num_sources": 0,
                "error": "no_results"
            }
        
        # Synthesize
        result = llm_synthesizer.synthesize_specific_query(query, chunks)
        
        # Add retrieval metadata
        result["retrieved_chunks"] = chunks
        result["filters"] = {
            "city": city,
            "role_category": role_category,
        }
        
        return result


class AggregateQueryRetrieval:
    """Handle Mode 2: Aggregate query retrieval (all postings, count skills)."""
    
    def __init__(self, vector_db: QdrantVectorDB, normalized_postings: List[Dict]):
        self.vector_db = vector_db
        self.normalized_postings = normalized_postings
    
    def get_all_matching_postings(self,
                                 city: Optional[str] = None,
                                 role_category: Optional[str] = None) -> List[Dict]:
        """
        Get ALL postings matching filters (not top-k).
        This is critical for aggregate queries — we need full count, not sampling.
        
        Returns:
            List of all matching normalized postings
        """
        matching = []
        
        for posting in self.normalized_postings:
            if city and posting['city'].lower() != city.lower():
                continue
            if role_category and posting['role_category'] != role_category:
                continue
            matching.append(posting)
        
        return matching
    
    def compute_skill_frequency(self, postings: List[Dict]) -> Dict[str, int]:
        """Count skill frequency across all postings."""
        skill_counts = Counter()
        
        for posting in postings:
            skill_counts.update(posting['skills_extracted'])
        
        return dict(skill_counts)
    
    def retrieve_sample_chunks(self, postings: List[Dict], k: int = 5) -> List[Dict]:
        """Get sample chunks for context (just first few postings)."""
        chunks = []
        
        for posting in postings[:k]:
            # Create a chunk-like dict from posting
            chunk = {
                "payload": {
                    "posting_id": posting['posting_id'],
                    "title": posting['title'],
                    "company": posting['company'],
                    "city": posting['city'],
                    "role_category": posting['role_category'],
                    "skills_extracted": posting['skills_extracted'],
                    "date_posted": posting['date_posted'],
                    "source": posting['source'],
                    "content": f"{posting['title']} at {posting['company']}",
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def retrieve_and_synthesize(self,
                               query: str,
                               llm_synthesizer: LLMSynthesizer,
                               city: Optional[str] = None,
                               role_category: Optional[str] = None) -> Dict:
        """
        Retrieve ALL matching postings, count skills, and synthesize aggregate answer.
        
        Returns:
            Dict with answer, skill frequency, and metadata
        """
        # Get ALL matching postings
        postings = self.get_all_matching_postings(city, role_category)
        
        if not postings:
            return {
                "query": query,
                "query_type": "aggregate",
                "answer": f"No postings found for {role_category or 'any'} roles in {city or 'any city'}.",
                "num_postings": 0,
                "error": "no_results"
            }
        
        # Compute skill frequency
        skill_frequency = self.compute_skill_frequency(postings)
        
        # Get sample chunks for LLM context
        sample_chunks = self.retrieve_sample_chunks(postings, k=5)
        
        # Synthesize with LLM
        result = llm_synthesizer.synthesize_aggregate_query(
            query,
            skill_frequency,
            sample_chunks,
            role_category=role_category,
            city=city
        )
        
        # Add aggregate metadata
        result["num_postings_analyzed"] = len(postings)
        result["skill_frequency"] = skill_frequency
        result["filters"] = {
            "city": city,
            "role_category": role_category,
        }
        result["relevant_postings"] = postings
        
        return result


class RAGQueryEngine:
    """
    Main RAG query engine combining retrieval + synthesis.
    Handles both specific and aggregate query modes.
    """
    
    def __init__(self, 
                 vector_db: QdrantVectorDB,
                 embedding_engine: EmbeddingEngine,
                 normalized_postings: List[Dict],
                 llm: Optional[OpenRouterLLM] = None):
        """Initialize the query engine."""
        self.vector_db = vector_db
        self.embedding_engine = embedding_engine
        self.normalized_postings = normalized_postings
        
        # Initialize retrievers
        self.specific_retriever = SpecificQueryRetrieval(vector_db, embedding_engine)
        self.aggregate_retriever = AggregateQueryRetrieval(vector_db, normalized_postings)
        
        # Initialize synthesizer (works with or without LLM)
        self.llm = llm
        self.synthesizer = LLMSynthesizer(self.llm)
    
    def query(self, query_text: str) -> Dict:
        """
        Process a user query and return RAG result.
        
        Automatically:
        1. Classifies query as specific or aggregate
        2. Extracts filters (city, role)
        3. Routes to appropriate retriever
        4. Synthesizes answer with LLM
        5. Returns result with citations and metadata
        
        Args:
            query_text: User query
            
        Returns:
            Result dict with answer, sources, and metadata
        """
        # Classify query
        query_type = QueryClassifier.classify(query_text)
        
        # Extract filters
        filters = QueryClassifier.extract_filters(query_text)
        city = filters.get('city')
        role_category = filters.get('role_category')
        
        print(f"\nQuery: {query_text}")
        print(f"Type: {query_type}")
        print(f"Filters: city={city}, role={role_category}")
        
        # Route to appropriate retriever
        if query_type == "aggregate":
            result = self.aggregate_retriever.retrieve_and_synthesize(
                query_text,
                self.synthesizer,
                city=city,
                role_category=role_category
            )
        else:  # specific
            result = self.specific_retriever.retrieve_and_synthesize(
                query_text,
                self.synthesizer,
                city=city,
                role_category=role_category,
                k=5
            )
        
        # Ensure standard keys in all results
        result["query_classification"] = query_type
        result["classified_as"] = query_type
        result["extracted_filters"] = filters
        
        # For aggregate queries, add the postings list
        if query_type == "aggregate" and "relevant_postings" not in result:
            result["relevant_postings"] = self.aggregate_retriever.get_all_matching_postings(city, role_category)
        
        # For aggregate queries, add top skills
        if query_type == "aggregate" and "top_skills" not in result:
            skill_freq = self.aggregate_retriever.compute_skill_frequency(result.get("relevant_postings", []))
            result["top_skills"] = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)
        
        return result
