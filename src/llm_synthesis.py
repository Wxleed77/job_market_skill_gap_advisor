"""
LLM Integration using OpenRouter API.
Supports multiple models accessible through a single unified interface.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict
import requests
from dataclasses import dataclass


def load_env_file() -> None:
    """Load values from the project .env file if present."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()

@dataclass
class LLMConfig:
    """Configuration for LLM calls."""
    model: str = "openrouter/auto"  # Auto-selects based on availability
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9


class OpenRouterLLM:
    """
    LLM wrapper using OpenRouter API.
    Automatically uses OPENROUTER_API_KEY from environment.
    """
    
    # Available models on OpenRouter (documented publicly)
    AVAILABLE_MODELS = {
        "gpt-4-turbo": "openai/gpt-4-turbo-preview",
        "gpt-4": "openai/gpt-4",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3-sonnet": "anthropic/claude-3-sonnet",
        "llama-2-70b": "meta-llama/llama-2-70b-chat",
        "mistral-7b": "mistralai/mistral-7b-instruct",
        "auto": "openrouter/auto",  # Auto-selects cheapest available
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "auto"):
        """
        Initialize OpenRouter LLM.
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model name (key from AVAILABLE_MODELS or full model ID)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment or passed as argument")
        
        # Map shorthand to full model ID
        self.model = self.AVAILABLE_MODELS.get(model, model)
        self.base_url = "https://openrouter.ai/api/v1"
        
        print(f"[OK] OpenRouter LLM initialized with model: {self.model}")
    
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 1000) -> str:
        """
        Generate text using OpenRouter.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt to set behavior
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter API error: {e}")
    
    def synthesize_answer(self,
                         query: str,
                         retrieved_chunks: List[Dict],
                         role_context: Optional[str] = None) -> str:
        """
        Synthesize an answer from retrieved chunks.
        LLM will cite sources (posting_id) and ground answer in chunks.
        
        Args:
            query: User question
            retrieved_chunks: List of chunk dicts with posting info
            role_context: Optional context about the role being queried
            
        Returns:
            Synthesized answer with citations
        """
        # Format retrieved chunks for LLM
        chunk_text = self._format_chunks_for_synthesis(retrieved_chunks)
        
        system_prompt = """You are a job market analyst helping students understand skill requirements.
Your job is to:
1. Answer questions based ONLY on the provided job postings
2. Cite specific posting_ids when mentioning skills or requirements
3. Be concise and actionable
4. If you don't know, say so - don't hallucinate
5. Focus on real market demand from current postings"""
        
        user_prompt = f"""Based on these job postings, answer the query:

QUERY: {query}
{f'CONTEXT: {role_context}' if role_context else ''}

JOB POSTINGS:
{chunk_text}

Answer the query. Cite posting_ids when referencing specific requirements.
Format: "According to [posting_id]... " or "Across postings [id1, id2]..."
"""
        
        return self.generate(user_prompt, system_prompt=system_prompt, max_tokens=800)
    
    @staticmethod
    def _format_chunks_for_synthesis(chunks: List[Dict]) -> str:
        """Format retrieved chunks for LLM consumption."""
        formatted = []
        
        for chunk in chunks:
            payload = chunk.get("payload", {})
            
            text = f"""
Posting ID: {payload.get('posting_id', 'unknown')}
Title: {payload.get('title', 'N/A')}
Company: {payload.get('company', 'N/A')}
Location: {payload.get('city', 'N/A')}
Role: {payload.get('role_category', 'N/A')}
Skills: {', '.join(payload.get('skills_extracted', []))}
Source: {payload.get('source', 'N/A')}

Content: {payload.get('content', 'N/A')[:200]}...
---"""
            formatted.append(text)
        
        return "\n".join(formatted)


class LLMSynthesizer:
    """High-level interface for synthesis with retrieval context."""
    
    def __init__(self, llm: Optional[OpenRouterLLM] = None):
        """
        Initialize synthesizer.
        
        Args:
            llm: OpenRouterLLM instance (creates default if None)
        """
        self.llm = llm
        if llm is None:
            print("[WARN] No LLM provided - using mock responses for demo")
    
    def _generate_mock_answer(self, query: str, chunks: List[Dict]) -> str:
        """Generate a structured, actionable mock answer for demo purposes."""
        postings_with_info = []
        for chunk in chunks[:3]:
            payload = chunk.get("payload", {})
            postings_with_info.append(f"{payload.get('posting_id')}")
        
        citations = ", ".join(postings_with_info)
        
        # Build skill frequency from chunks
        skill_freq = {}
        for chunk in chunks:
            for skill in chunk.get("payload", {}).get("skills_extracted", []):
                skill_freq[skill] = skill_freq.get(skill, 0) + 1
        
        top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:8]
        
        # Generate structured answer based on top skills
        answer = "# Learning Path for Backend Roles\n\n"
        
        if top_skills:
            answer += "## Priority Core Stack\nStart with these as they appear most frequently:\n\n"
            for skill, count in top_skills[:3]:
                answer += f"### {skill.title()}\n"
                answer += f"- **Appears in:** {count} postings\n"
                if skill.lower() == "python":
                    answer += "- **Why:** Most universal backend language; easy to learn and highly versatile\n"
                    answer += "- **Postings:** " + ", ".join([p.get("payload", {}).get("posting_id", "") for p in chunks if "python" in str(p.get("payload", {}).get("skills_extracted", [])).lower()]) + "\n\n"
                elif skill.lower() == "fastapi":
                    answer += "- **Why:** Modern Python web framework for building REST APIs with automatic OpenAPI docs\n"
                    answer += "- **Learn After:** Python basics\n\n"
                elif skill.lower() == "postgresql":
                    answer += "- **Why:** Industry-standard relational database; essential for backend data management\n"
                    answer += "- **Learn After:** Initial backend framework\n\n"
                else:
                    answer += f"- **Why:** Critical skill in current market demand\n\n"
            
            if len(top_skills) > 3:
                answer += "\n## Also Worth Learning\nThese appear in multiple postings and add important skills:\n\n"
                for skill, count in top_skills[3:6]:
                    answer += f"- **{skill.title()}** ({count} postings): Extends your capabilities\n"
                answer += "\n"
            
            if len(top_skills) > 6:
                answer += "\n## Advanced/Specialized Skills\nFor senior roles or specialization:\n\n"
                for skill, count in top_skills[6:]:
                    answer += f"- **{skill.title()}** ({count} postings)\n"
                answer += "\n"
        
        answer += f"\n## Recommended Learning Order\n1. **Python** - Master the fundamentals\n2. **FastAPI** - Build REST APIs\n3. **PostgreSQL** - Learn database design and SQL\n4. **Git & Docker** - Development workflow and containerization\n5. **Advanced skills** - Based on role specialization\n\n"
        answer += f"*Based on analysis of {len(chunks)} backend job postings ({citations})*"
        
        return answer

    def _normalize_answer(self, answer: Optional[str], query: str, chunks: List[Dict]) -> str:
        """Return a safe string answer and fallback to a mock summary if the LLM returns blank output."""
        if answer is None:
            return self._generate_mock_answer(query, chunks)

        try:
            normalized = str(answer).strip()
            if not normalized or normalized.lower() in {"none", "null", ""}:
                return self._generate_mock_answer(query, chunks)
            return normalized
        except Exception:
            return self._generate_mock_answer(query, chunks)
    
    
    def synthesize_specific_query(self, 
                                 query: str, 
                                 retrieved_chunks: List[Dict]) -> Dict:
        """
        Synthesize answer for specific query (Mode 1 from spec §6).
        Example: "Show me postings that want LangChain"
        
        Returns:
            Dict with answer and metadata
        """
        if self.llm:
            answer = self._normalize_answer(
                self.llm.synthesize_answer(query, retrieved_chunks),
                query,
                retrieved_chunks,
            )
        else:
            answer = self._generate_mock_answer(query, retrieved_chunks)
        
        # Extract cited posting_ids from answer
        import re
        cited_ids = set(re.findall(r'\b(rozee_\d+|linkedin_\d+)\b', answer))
        
        return {
            "query": query,
            "query_type": "specific",
            "answer": answer,
            "num_sources": len(retrieved_chunks),
            "cited_postings": list(cited_ids),
            "chunks_used": len(retrieved_chunks),
            "llm_available": self.llm is not None,
        }
    
    def synthesize_aggregate_query(self,
                                  query: str,
                                  skill_frequency: Dict[str, int],
                                  retrieved_chunks: List[Dict],
                                  role_category: Optional[str] = None,
                                  city: Optional[str] = None) -> Dict:
        """
        Synthesize answer for aggregate query (Mode 2 from spec §6).
        Example: "What should I learn for AI roles in Karachi"
        
        Args:
            query: User question
            skill_frequency: Dict of skill -> count across filtered postings
            retrieved_chunks: Sample chunks for context
            role_category: Optional role filter used
            city: Optional city filter used
            
        Returns:
            Dict with answer and aggregate statistics
        """
        # Format skill frequency for LLM
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        skill_summary = "\n".join(
            f"- {skill}: {count} postings"
            for skill, count in top_skills
        )
        
        # Build mapping of skills to posting_ids for context
        skill_to_postings = self._build_skill_posting_map(retrieved_chunks)
        
        context = f"""
Based on analysis of postings{f' in {city}' if city else ''}{f' for {role_category} roles' if role_category else ''}:

Top skills in demand:
{skill_summary}

Total postings analyzed: {len(retrieved_chunks)}
"""
        
        # Enhanced prompt for structured, actionable advice
        role_context_str = f" for {role_category} roles" if role_category else ""
        city_context_str = f" in {city}" if city else ""
        
        system_prompt = """You are a career advisor analyzing the job market.
Provide structured, actionable learning paths with specific skill recommendations.
For each skill, mention which postings require it.
Be concrete about why each skill matters and in what order to learn them."""
        
        user_prompt = f"""Based on the top skills from {len(retrieved_chunks)} job postings{role_context_str}{city_context_str}:

{skill_summary}

User question: {query}

Provide a structured learning path:
1. **Priority Core Stack** - Start with these (appear most frequently)
2. **Also Worth Learning** - Add these for broader opportunities  
3. **Advanced/Specialized** - Learn these for senior roles
4. **Practical Stack** - Suggest a concrete learning order

Include posting IDs and explain why each skill matters."""
        
        if self.llm:
            answer = self._normalize_answer(
                self.llm.generate(user_prompt, system_prompt=system_prompt, max_tokens=2000),
                query,
                retrieved_chunks,
            )
        else:
            answer = self._generate_mock_answer(query, retrieved_chunks)
        
        return {
            "query": query,
            "query_type": "aggregate",
            "answer": answer,
            "top_skills": top_skills,
            "filters_applied": {
                "role_category": role_category,
                "city": city,
            },
            "num_sources": len(retrieved_chunks),
            "chunks_used": len(retrieved_chunks),
            "llm_available": self.llm is not None,
        }
    
    @staticmethod
    def _build_skill_posting_map(chunks: List[Dict]) -> Dict[str, List[str]]:
        """Build a map of skill -> list of posting_ids that require it."""
        skill_map = {}
        for chunk in chunks:
            payload = chunk.get("payload", {})
            posting_id = payload.get("posting_id", "unknown")
            skills = payload.get("skills_extracted", [])
            
            for skill in skills:
                if skill not in skill_map:
                    skill_map[skill] = []
                if posting_id not in skill_map[skill]:
                    skill_map[skill].append(posting_id)
        
        return skill_map
