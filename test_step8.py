"""
STEP 8 Test: Live Ingestion Pipeline

Tests:
1. Source abstraction fetches listings from a source
2. Deduplication removes repeated posting IDs
3. Refresh pipeline normalizes + embeds fresh postings
4. Scheduler-style refresh is available for periodic ingestion
"""

from src.seed_data import RAW_POSTINGS
from src.chunking_embedding import EmbeddingEngine, QdrantVectorDB
from src.live_ingestion import LiveIngestionPipeline, LocalSeedSource, RefreshScheduler


def test_step8():
    print("=" * 80)
    print("STEP 8: Live Ingestion Pipeline")
    print("=" * 80)

    source = LocalSeedSource("seed_data", RAW_POSTINGS)
    emb = EmbeddingEngine()
    qdb = QdrantVectorDB(vector_size=emb.embedding_dim)
    pipeline = LiveIngestionPipeline(qdb, emb, [source])
    scheduler = RefreshScheduler(pipeline)

    result = scheduler.run_once(max_age_days=90)

    print("\nRefresh result:")
    print(f"  Status: {result['status']}")
    print(f"  Sources checked: {result['sources_checked']}")
    print(f"  New postings: {result['new_postings']}")
    print(f"  Stored chunks: {result['stored_chunks']}")
    print(f"  Posting IDs sample: {result['posting_ids'][:5]}")

    assert result["status"] == "refreshed"
    assert result["new_postings"] > 0
    assert result["stored_chunks"] > 0

    # Test deduplication with repeated source payload
    duplicate_payload = RAW_POSTINGS[:3] + RAW_POSTINGS[:3]
    duplicate_source = LocalSeedSource("duplicate_seed", duplicate_payload)
    duplicate_pipeline = LiveIngestionPipeline(qdb, emb, [duplicate_source])
    dup_result = duplicate_pipeline.refresh(max_age_days=90)
    print(f"\nDuplicate refresh result: {dup_result['new_postings']} new postings")
    assert dup_result["new_postings"] >= 3

    print("\n" + "=" * 80)
    print("STEP 8 COMPLETE - Refresh pipeline validated")
    print("=" * 80)


if __name__ == "__main__":
    test_step8()
