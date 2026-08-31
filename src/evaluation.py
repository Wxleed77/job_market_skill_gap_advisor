from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class EvaluationCase:
    query: str
    expected_postings: List[str] = field(default_factory=list)
    expected_skills: List[str] = field(default_factory=list)
    query_type: str = "specific"
    city: Optional[str] = None
    role: Optional[str] = None


class EvaluationHarness:
    """Lightweight evaluation harness for retrieval and grounding checks."""

    def __init__(self, rag_engine):
        self.rag_engine = rag_engine

    @staticmethod
    def _retrieved_posting_ids(result: Dict[str, Any]) -> List[str]:
        ids: List[str] = []
        for chunk in result.get("retrieved_chunks", []):
            payload = chunk.get("payload", {})
            posting_id = payload.get("posting_id")
            if posting_id:
                ids.append(posting_id)
        return ids

    @staticmethod
    def _grounding_is_valid(result: Dict[str, Any], retrieved_ids: List[str]) -> bool:
        cited = set(result.get("cited_postings", []))
        if not cited:
            return False
        return cited.issubset(set(retrieved_ids))

    def evaluate_specific_query(self, case: EvaluationCase, k: int = 5) -> Dict[str, Any]:
        result = self.rag_engine.query(case.query)
        retrieved_ids = self._retrieved_posting_ids(result)
        expected = set(case.expected_postings)
        retrieved_set = set(retrieved_ids[:k])

        hits = len(expected & retrieved_set)
        precision = hits / max(len(retrieved_set), 1)
        recall = hits / max(len(expected), 1)
        grounding = self._grounding_is_valid(result, retrieved_ids)

        return {
            "query": case.query,
            "query_type": "specific",
            "expected_postings": case.expected_postings,
            "retrieved_postings": retrieved_ids[:k],
            "precision_at_k": round(precision, 3),
            "recall_at_k": round(recall, 3),
            "grounded": grounding,
            "answer_length": len(result.get("answer", "")),
        }

    def evaluate_aggregate_query(self, case: EvaluationCase) -> Dict[str, Any]:
        result = self.rag_engine.query(case.query)
        top_skills = [skill for skill, _ in result.get("top_skills", [])[:10]]
        expected = set(case.expected_skills)
        overlap = expected & set(top_skills)

        return {
            "query": case.query,
            "query_type": "aggregate",
            "expected_skills": case.expected_skills,
            "top_skills": top_skills[:10],
            "top_skill_overlap": len(overlap),
            "skill_overlap_ratio": round(len(overlap) / max(len(expected), 1), 3),
            "num_postings_analyzed": len(result.get("relevant_postings", [])),
            "answer_length": len(result.get("answer", "")),
        }

    def run(self, cases: List[EvaluationCase]) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        for case in cases:
            if case.query_type == "specific":
                results.append(self.evaluate_specific_query(case))
            else:
                results.append(self.evaluate_aggregate_query(case))

        return {
            "total_cases": len(results),
            "results": results,
        }
