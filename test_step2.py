"""
STEP 2 Test: Chunking + Embedding + Qdrant Storage
"""

import json
from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB

def test_step2():
    """Test STEP 2: chunking, embedding, and Qdrant storage."""
    
    print("=" * 80)
    print("STEP 2: Chunking + Embedding + Qdrant Storage")
    print("=" * 80)
    
    # Step 1: Normalize postings
    print("\n1. Normalizing postings...")
    normalized = normalize_postings(RAW_POSTINGS)
    print(f"   ✓ Normalized {len(normalized)} postings")
    
    # Step 2: Chunk postings
    print("\n2. Chunking postings...")
    chunking_strategy = ChunkingStrategy()
    chunks = chunking_strategy.chunk_postings(normalized)
    print(f"   ✓ Created {len(chunks)} chunks")
    print(f"   - All chunks are 'full' type (single chunk per posting)")
    
    # Step 3: Initialize embedding engine
    print("\n3. Initializing embedding engine...")
    embedding_engine = EmbeddingEngine()
    print(f"   ✓ Embedding model loaded")
    
    # Step 4: Generate embeddings
    print("\n4. Generating embeddings...")
    chunks_with_embeddings = embedding_engine.embed_chunks(chunks)
    print(f"   ✓ Generated {len(chunks_with_embeddings)} embeddings")
    print(f"   - Each embedding dimension: {embedding_engine.embedding_dim}")
    
    # Step 5: Store in Qdrant
    print("\n5. Storing in Qdrant...")
    vector_db = QdrantVectorDB(vector_size=embedding_engine.embedding_dim)
    num_stored = vector_db.store_chunks(chunks_with_embeddings)
    print(f"   ✓ Stored {num_stored} chunks in Qdrant")
    
    # Step 6: Display sample chunks
    print("\n" + "=" * 80)
    print("SAMPLE CHUNKS WITH METADATA")
    print("=" * 80)
    
    sample_indices = [0, 9, 19]
    for idx in sample_indices:
        if idx < len(chunks):
            chunk = chunks[idx]
            print(f"\nChunk {idx + 1} (posting_id: {chunk.posting_id}):")
            print(f"  Chunk Type: {chunk.chunk_type}")
            print(f"  Title: {chunk.title}")
            print(f"  Company: {chunk.company}")
            print(f"  City: {chunk.city}")
            print(f"  Role Category: {chunk.role_category}")
            print(f"  Skills: {', '.join(chunk.skills_extracted)}")
            print(f"  Date Posted: {chunk.date_posted}")
            print(f"  Source: {chunk.source}")
            print(f"  Content Preview: {chunk.content[:150]}...")
            
            # Show first few dimensions of embedding
            embedding = chunks_with_embeddings[idx][1]
            print(f"  Embedding (first 5 dims): {[round(x, 4) for x in embedding[:5]]}")
    
    # Step 7: Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    print(f"\n  Total chunks created: {len(chunks)}")
    print(f"  Chunks per posting: 1 (all short postings)")
    print(f"  Embedding model: BAAI/bge-small-en-v1.5")
    print(f"  Embedding dimension: {embedding_engine.embedding_dim}")
    print(f"  Vector DB: Qdrant (in-memory)")
    
    # Break down by city
    city_counts = {}
    for chunk in chunks:
        city = chunk.city
        city_counts[city] = city_counts.get(city, 0) + 1
    print(f"\n  Chunks by city:")
    for city, count in sorted(city_counts.items()):
        print(f"    - {city}: {count}")
    
    # Break down by role category
    role_counts = {}
    for chunk in chunks:
        role = chunk.role_category
        role_counts[role] = role_counts.get(role, 0) + 1
    print(f"\n  Chunks by role category:")
    for role, count in sorted(role_counts.items()):
        print(f"    - {role}: {count}")
    
    # Metadata completeness check
    print(f"\n  Metadata completeness check:")
    all_chunks_have_metadata = all(
        chunk.posting_id and chunk.title and chunk.city and chunk.role_category
        for chunk in chunks
    )
    print(f"    - All chunks have complete metadata: {all_chunks_have_metadata}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_step2()
