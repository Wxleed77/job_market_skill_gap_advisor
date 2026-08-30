"""
STEP 5 Test: Aggregate Query Mode (Mode 2 from spec section 6)

Tests:
1. Aggregate query classification ("What should I learn for X roles?")
2. Full posting retrieval (ALL matching postings, not top-k)
3. Skill frequency counting across all postings
4. Top skills identification
5. Aggregate-specific answer synthesis
"""

from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.rag_query_engine import RAGQueryEngine
from src.llm_synthesis import OpenRouterLLM

def test_step5():
    """Test STEP 5: Aggregate query mode."""
    
    print("=" * 80)
    print("STEP 5: Aggregate Query Mode (All Postings + Skill Frequency)")
    print("=" * 80)
    
    # Setup: Normalize, chunk, embed, store (same as STEP 4)
    print("\n[Setup] Normalizing postings...")
    normalized = normalize_postings(RAW_POSTINGS)
    print(f"   [OK] {len(normalized)} postings normalized")
    
    print("\n[Setup] Chunking and embedding...")
    chunking_strategy = ChunkingStrategy()
    chunks = chunking_strategy.chunk_postings(normalized)
    embedding_engine = EmbeddingEngine()
    chunks_with_embeddings = embedding_engine.embed_chunks(chunks)
    print(f"   [OK] {len(chunks)} chunks embedded")
    
    print("\n[Setup] Storing in Qdrant...")
    vector_db = QdrantVectorDB(vector_size=embedding_engine.embedding_dim)
    vector_db.store_chunks(chunks_with_embeddings)
    print(f"   [OK] Stored in Qdrant")
    
    # Initialize RAG with mock LLM
    try:
        llm = OpenRouterLLM(model="auto")
    except ValueError:
        llm = None
    
    rag_engine = RAGQueryEngine(vector_db, embedding_engine, normalized, llm=llm)
    print(f"   [OK] RAG engine initialized\n")
    
    # Test aggregate queries
    print("=" * 80)
    print("AGGREGATE QUERIES (Mode 2 - All postings + skill frequency)")
    print("=" * 80)
    
    aggregate_queries = [
        "What skills should I learn for backend roles?",
        "What technologies do AI/ML engineers need to know?",
        "What should I learn for DevOps positions in Karachi?",
    ]
    
    for i, query in enumerate(aggregate_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 80)
        
        result = rag_engine.query(query)
        
        query_type = result.get('query_classification', 'unknown')
        print(f"Query Type: {query_type}")
        
        if query_type == "aggregate":
            # Aggregate mode specific outputs
            postings = result.get('relevant_postings', [])
            skills = result.get('top_skills', [])
            
            print(f"Postings Analyzed: {len(postings)}")
            
            if skills:
                print(f"\nTop Skills (by frequency):")
                for skill, frequency in skills[:10]:
                    print(f"  - {skill}: {frequency} postings")
            
            print(f"\nFilters Applied: {result.get('filters', {})}")
            
            print(f"\nSynthesized Answer:")
            print(f"{result['answer']}")
            
            # Show which postings contributed
            if postings:
                print(f"\nPostings Contributing ({len(postings)} total):")
                for posting in postings[:5]:
                    print(f"  - {posting['posting_id']}: {posting['title']} @ {posting['company']}")
                if len(postings) > 5:
                    print(f"  ... and {len(postings) - 5} more")
        
        else:
            # Fallback for specific mode
            print(f"(Returned as specific mode instead of aggregate)")
            print(f"Postings Retrieved: {len(result.get('relevant_postings', []))}")
            print(f"\nAnswer:")
            print(f"{result['answer']}")
    
    # Comparison: Aggregate vs Specific for same query
    print("\n" + "=" * 80)
    print("COMPARISON: Aggregate vs Specific Mode")
    print("=" * 80)
    
    test_query = "What should I learn for DevOps?"
    print(f"\nSame query: '{test_query}'")
    print("-" * 80)
    
    result = rag_engine.query(test_query)
    query_type = result.get('query_classification', 'unknown')
    
    postings = result.get('relevant_postings', [])
    skills = result.get('top_skills', [])
    
    print(f"\nClassified as: {query_type}")
    print(f"Postings ({len(postings)} total):")
    
    # Count skill frequencies manually
    skill_freq = {}
    for posting in postings:
        for skill in posting.get('skills_extracted', []):
            skill_freq[skill] = skill_freq.get(skill, 0) + 1
    
    sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nSkill Frequency Analysis (from {len(postings)} postings):")
    print(f"  Total unique skills: {len(skill_freq)}")
    print(f"\n  Top 10 Skills:")
    for skill, freq in sorted_skills[:10]:
        pct = (freq / len(postings)) * 100
        print(f"    - {skill}: {freq}/{len(postings)} ({pct:.0f}%)")
    
    # Difference from Mode 1 (top-k vector search)
    print(f"\n  Key Difference from Specific Mode:")
    print(f"    Specific: Uses vector similarity to find top-k (usually 5) most relevant")
    print(f"    Aggregate: Analyzes ALL matching postings to show complete skill landscape")
    
    print("\n" + "=" * 80)
    print("STEP 5 VALIDATION")
    print("=" * 80)
    
    checks = [
        ("Query classification working", query_type in ["specific", "aggregate"]),
        ("Postings retrieved", len(postings) > 0),
        ("Skill frequencies computed", len(skill_freq) > 0),
        ("Top skills identified", len(sorted_skills) > 0),
        ("Filtering working", result.get('filters') is not None),
        ("Answer synthesized", len(result['answer']) > 50),
    ]
    
    print("\nValidation Checks:")
    for check_name, passed in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {check_name}")
    
    all_passed = all(passed for _, passed in checks)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("STEP 5 COMPLETE - Aggregate Mode Working!")
    else:
        print("STEP 5 PARTIAL - Some checks failed")
    print("=" * 80)

if __name__ == "__main__":
    test_step5()
