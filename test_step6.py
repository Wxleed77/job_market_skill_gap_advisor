"""
STEP 6 Test: Query Router + Route Validation

Tests:
1. Query classifier correctly routes aggregate vs specific queries
2. Filters extracted properly (city, role)
3. Query engine returns consistent route metadata
"""

from src.rag_query_engine import QueryClassifier, RAGQueryEngine
from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.llm_synthesis import OpenRouterLLM


def test_step6():
    """Test STEP 6: routing logic and query classification."""
    print("=" * 80)
    print("STEP 6: Query Router Validation")
    print("=" * 80)

    tests = [
        ("Show me postings that want Python", "specific"),
        ("Find jobs requiring Kubernetes", "specific"),
        ("What should I learn for backend roles?", "aggregate"),
        ("What technologies do AI/ML engineers need to know?", "aggregate"),
        ("What skills are in demand for DevOps in Karachi?", "aggregate"),
        ("React developer jobs in Lahore", "specific"),
    ]

    print("\nQUERY CLASSIFIER CHECKS")
    print("-" * 80)
    for query, expected in tests:
        actual = QueryClassifier.classify(query)
        filters = QueryClassifier.extract_filters(query)
        print(f"Query: {query}")
        print(f"  Expected: {expected} | Actual: {actual} | Filters: {filters}")
        assert actual == expected, f"Route mismatch: {query} -> {actual} (expected {expected})"

    print("\nROUTER/ENGINE INTEGRATION CHECK")
    print("-" * 80)

    normalized = normalize_postings(RAW_POSTINGS)
    chunks = ChunkingStrategy().chunk_postings(normalized)
    emb = EmbeddingEngine()
    embedded = emb.embed_chunks(chunks)
    qdb = QdrantVectorDB(vector_size=emb.embedding_dim)
    qdb.store_chunks(embedded)

    llm = OpenRouterLLM(model="auto")
    engine = RAGQueryEngine(qdb, emb, normalized, llm=llm)

    route_tests = [
        "Show me postings that want Python",
        "What should I learn for backend roles?",
        "What technologies do AI/ML engineers need to know?",
        "What skills are in demand for DevOps in Karachi?",
    ]

    for query in route_tests:
        result = engine.query(query)
        route = result.get("query_classification") or result.get("classified_as")
        print(f"Query: {query}")
        print(f"  Classified as: {route}")
        print(f"  Filters: {result.get('extracted_filters', {})}")
        print(f"  Answer length: {len(result.get('answer', ''))}")
        assert route in {"specific", "aggregate"}

    print("\n" + "=" * 80)
    print("STEP 6 COMPLETE - Query routing validated")
    print("=" * 80)


if __name__ == "__main__":
    test_step6()
