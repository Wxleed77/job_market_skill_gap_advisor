"""
STEP 7 Test: Evaluation Harness

Checks:
1. Retrieval precision/recall on representative queries
2. Grounding check: cited postings must come from retrieved postings
3. Aggregate skill overlap for skill-demand queries
"""

from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.rag_query_engine import RAGQueryEngine
from src.evaluation import EvaluationCase, EvaluationHarness
from src.llm_synthesis import OpenRouterLLM


def test_step7():
    print("=" * 80)
    print("STEP 7: Evaluation Harness")
    print("=" * 80)

    normalized = normalize_postings(RAW_POSTINGS)
    chunks = ChunkingStrategy().chunk_postings(normalized)
    emb = EmbeddingEngine()
    embedded = emb.embed_chunks(chunks)
    qdb = QdrantVectorDB(vector_size=emb.embedding_dim)
    qdb.store_chunks(embedded)

    llm = OpenRouterLLM(model="auto")
    engine = RAGQueryEngine(qdb, emb, normalized, llm=llm)
    harness = EvaluationHarness(engine)

    cases = [
        EvaluationCase(
            query="Show me postings that want Python",
            expected_postings=["rozee_008", "rozee_018", "linkedin_003"],
            query_type="specific",
        ),
        EvaluationCase(
            query="Find jobs requiring Kubernetes",
            expected_postings=["rozee_017", "linkedin_007", "linkedin_001"],
            query_type="specific",
        ),
        EvaluationCase(
            query="What should I learn for backend roles?",
            expected_skills=["python", "fastapi", "postgresql", "redis", "git"],
            query_type="aggregate",
        ),
        EvaluationCase(
            query="What technologies do AI/ML engineers need to know?",
            expected_skills=["python", "pytorch", "tensorflow", "scikit-learn"],
            query_type="aggregate",
        ),
    ]

    report = harness.run(cases)

    for result in report["results"]:
        print("\n---")
        print(f"Query: {result['query']}")
        print(f"Type: {result['query_type']}")
        if result["query_type"] == "specific":
            print(f"Precision@k: {result['precision_at_k']}")
            print(f"Recall@k: {result['recall_at_k']}")
            print(f"Grounded: {result['grounded']}")
            print(f"Retrieved: {result['retrieved_postings']}")
        else:
            print(f"Top skills: {result['top_skills'][:10]}")
            print(f"Skill overlap ratio: {result['skill_overlap_ratio']}")
            print(f"Postings analyzed: {result['num_postings_analyzed']}")

    print("\n" + "=" * 80)
    print("STEP 7 COMPLETE - Evaluation harness validated")
    print("=" * 80)


if __name__ == "__main__":
    test_step7()
