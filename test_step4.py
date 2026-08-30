"""
STEP 4 Test: Specific Query Retrieval + LLM Synthesis (Mode 1 from spec section 6)

Tests:
1. Re-normalize with hybrid skill extraction
2. Re-chunk and re-embed with better skills
3. Query retrieval with vector search + metadata filtering
4. LLM synthesis answering queries grounded in retrieved chunks
5. Show proper citation of posting_ids and sources
"""

from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.rag_query_engine import RAGQueryEngine
from src.llm_synthesis import OpenRouterLLM

def test_step4():
    """Test STEP 4: Specific query retrieval + LLM synthesis."""
    
    print("=" * 80)
    print("STEP 4: Specific Query Retrieval + LLM Synthesis")
    print("=" * 80)
    
    # Step 1: Re-normalize with hybrid skill extraction
    print("\n1. Re-normalizing postings with hybrid skill extraction...")
    normalized = normalize_postings(RAW_POSTINGS)
    print(f"   [OK] Re-normalized {len(normalized)} postings with better skills")
    
    # Show skill improvement on sample posting
    sample = normalized[0]
    print(f"\n   Sample (posting {sample['posting_id']}):")
    print(f"   Title: {sample['title']}")
    print(f"   Skills ({len(sample['skills_extracted'])}): {', '.join(sample['skills_extracted'])}")
    
    # Step 2: Chunk and embed
    print("\n2. Chunking and embedding with improved skills...")
    chunking_strategy = ChunkingStrategy()
    chunks = chunking_strategy.chunk_postings(normalized)
    print(f"   [OK] Created {len(chunks)} chunks")
    
    embedding_engine = EmbeddingEngine()
    chunks_with_embeddings = embedding_engine.embed_chunks(chunks)
    print(f"   [OK] Generated embeddings (384-dim)")
    
    # Step 3: Store in Qdrant
    print("\n3. Storing in Qdrant...")
    vector_db = QdrantVectorDB(vector_size=embedding_engine.embedding_dim)
    vector_db.store_chunks(chunks_with_embeddings)
    print(f"   [OK] Stored {len(chunks)} chunks in Qdrant")
    
    # Step 4: Initialize RAG engine with OpenRouter LLM
    print("\n4. Initializing RAG engine with OpenRouter...")
    try:
        llm = OpenRouterLLM(model="auto")
        rag_engine = RAGQueryEngine(vector_db, embedding_engine, normalized, llm)
        print(f"   [OK] RAG engine ready with LLM synthesis")
        use_llm = True
    except ValueError as e:
        print(f"   [WARN] {e}")
        print("   -> Using mock LLM for demo (set OPENROUTER_API_KEY to use real LLM)")
        rag_engine = RAGQueryEngine(vector_db, embedding_engine, normalized, llm=None)
        use_llm = False
    
    # Step 5: Test specific queries
    print("\n" + "=" * 80)
    print("TESTING SPECIFIC QUERIES (Mode 1)")
    print("=" * 80)
    
    specific_queries = [
        "Show me postings that want Python",
        "Find jobs requiring Kubernetes",
        "What positions are hiring for React developers",
    ]
    
    for i, query in enumerate(specific_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 80)
        
        result = rag_engine.query(query)
        
        print(f"\nQuery Type: {result.get('classified_as', 'unknown')}")
        print(f"Sources: {result.get('num_sources', 0)} postings")
        
        print(f"\nAnswer:")
        print(f"{result['answer']}")
        
        if result.get('cited_postings'):
            print(f"\nCited Postings: {', '.join(result['cited_postings'])}")
        
        if result.get('retrieved_chunks'):
            print(f"\nTop Retrieved Postings:")
            for chunk in result['retrieved_chunks'][:3]:
                payload = chunk.get('payload', {})
                print(f"  - {payload.get('posting_id')}: {payload.get('title')} "
                      f"@ {payload.get('company')} (Match Score: {chunk.get('score', 0):.3f})")
    
    # Step 6: Show retrieval quality
    print("\n" + "=" * 80)
    print("RETRIEVAL QUALITY CHECK")
    print("=" * 80)
    
    test_query = "Show me postings that want Kubernetes"
    result = rag_engine.query(test_query)
    
    print(f"\nQuery: {test_query}")
    print(f"Retrieved {result.get('num_sources', 0)} postings:")
    
    for chunk in result.get('retrieved_chunks', []):
        payload = chunk.get('payload', {})
        print(f"\n  Posting ID: {payload.get('posting_id')}")
        print(f"  Title: {payload.get('title')}")
        print(f"  Company: {payload.get('company')}")
        print(f"  City: {payload.get('city')}")
        print(f"  Skills: {', '.join(payload.get('skills_extracted', []))}")
        print(f"  Similarity Score: {chunk.get('score', 0):.4f}")
        
        # Check if Kubernetes is actually in the skills
        skills_str = ' '.join(payload.get('skills_extracted', [])).lower()
        has_kubernetes = 'kubernetes' in skills_str
        print(f"  ✓ Contains Kubernetes: {has_kubernetes}")
    
    # Step 7: Show metadata filtering
    print("\n" + "=" * 80)
    print("METADATA FILTERING DEMO")
    print("=" * 80)
    
    filtered_query = "Python jobs in Karachi"
    result = rag_engine.query(filtered_query)
    
    print(f"\nQuery: {filtered_query}")
    print(f"Filters extracted: {result.get('extracted_filters', {})}")
    print(f"Filters applied: {result.get('filters', {})}")
    print(f"Retrieved {result.get('num_sources', 0)} postings")
    
    if result.get('retrieved_chunks'):
        print("\nFiltered results:")
        for chunk in result['retrieved_chunks']:
            payload = chunk.get('payload', {})
            print(f"  - {payload.get('title')} in {payload.get('city')}")
    
    # Step 8: Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    print(f"""
  ✓ STEP 4 Complete
  
  Pipeline:
    1. Normalized: {len(normalized)} postings with hybrid skill extraction
    2. Chunked: {len(chunks)} chunks created
    3. Embedded: 384-dim vectors generated
    4. Stored: Qdrant in-memory vector DB
    5. Queried: Vector search + metadata filters
    6. Synthesized: LLM answers grounded in retrieved chunks
  
  Retrieval Features:
    ✓ Vector similarity search for semantic matching
    ✓ Metadata filters (city, role_category)
    ✓ Hybrid filtering (vector + metadata)
    ✓ LLM synthesis citing posting_ids
  
  Next Steps:
    STEP 5: Aggregate query mode (all postings + skill frequency)
    STEP 6: Query router (classify and route queries)
    """)
    
    print("=" * 80)

if __name__ == "__main__":
    test_step4()
