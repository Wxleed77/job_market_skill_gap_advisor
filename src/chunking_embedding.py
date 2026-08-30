"""
STEP 2: Chunking Strategy + Embedding + Qdrant Storage

Chunking strategy per spec §5:
- For short postings: one chunk per posting
- For longer postings: split into title+summary, responsibilities, requirements/skills
- All chunks share the same posting_id in metadata
- Always attach metadata: city, role_category, skills_extracted, date_posted, source, posting_id
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

@dataclass
class Chunk:
    """Represents a single chunk of a job posting."""
    chunk_id: str
    posting_id: str
    content: str
    chunk_type: str  # "full", "title_summary", "responsibilities", "requirements"
    # Metadata
    title: str
    company: str
    city: str
    role_category: str
    skills_extracted: List[str]
    date_posted: str
    source: str

class ChunkingStrategy:
    """Implements chunking strategy from spec §5."""
    
    MIN_LENGTH_FOR_SPLIT = 300  # If content is shorter than this, keep as single chunk
    
    @staticmethod
    def chunk_postings(postings: List[Dict]) -> List[Chunk]:
        """
        Chunk normalized postings according to strategy.
        
        Args:
            postings: List of normalized posting dicts
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        for posting in postings:
            # Reconstruct posting text from normalized data
            posting_text = f"""
Title: {posting['title']}
Company: {posting['company']}
Location: {posting['city']}
Role Category: {posting['role_category']}
Skills: {', '.join(posting['skills_extracted'])}

Description: (would be in raw posting)
            """.strip()
            
            # For now, treat all as short postings (one chunk per posting)
            # In a real scenario, you'd parse the raw_html to check length
            chunk_id = str(uuid.uuid4())
            
            chunk = Chunk(
                chunk_id=chunk_id,
                posting_id=posting['posting_id'],
                content=posting_text,
                chunk_type="full",
                title=posting['title'],
                company=posting['company'],
                city=posting['city'],
                role_category=posting['role_category'],
                skills_extracted=posting['skills_extracted'],
                date_posted=posting['date_posted'],
                source=posting['source'],
            )
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def chunk_longer_posting(title: str, summary: str, responsibilities: str, 
                             requirements: str, posting_id: str, metadata: Dict) -> List[Chunk]:
        """
        Split a longer posting into multiple chunks.
        (Placeholder for when we have longer postings with separate sections)
        """
        chunks = []
        
        # Chunk 1: Title + Summary
        if title or summary:
            chunk_id = str(uuid.uuid4())
            chunks.append(Chunk(
                chunk_id=chunk_id,
                posting_id=posting_id,
                content=f"{title}\n\n{summary}",
                chunk_type="title_summary",
                **metadata
            ))
        
        # Chunk 2: Responsibilities
        if responsibilities:
            chunk_id = str(uuid.uuid4())
            chunks.append(Chunk(
                chunk_id=chunk_id,
                posting_id=posting_id,
                content=f"Responsibilities:\n{responsibilities}",
                chunk_type="responsibilities",
                **metadata
            ))
        
        # Chunk 3: Requirements/Skills
        if requirements:
            chunk_id = str(uuid.uuid4())
            chunks.append(Chunk(
                chunk_id=chunk_id,
                posting_id=posting_id,
                content=f"Requirements:\n{requirements}",
                chunk_type="requirements",
                **metadata
            ))
        
        return chunks


class EmbeddingEngine:
    """Manages embedding generation using FastEmbed."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """Initialize embedding model."""
        print(f"Loading embedding model: {model_name}")
        self.model = TextEmbedding(model_name=model_name)
        self.embedding_dim = 384  # BGE-small produces 384-dim embeddings
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[Tuple[Chunk, List[float]]]:
        """
        Embed a batch of chunks.
        
        Returns:
            List of (chunk, embedding_vector) tuples
        """
        # Extract content to embed
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = list(self.model.embed(texts))
        
        # Pair chunks with embeddings
        return list(zip(chunks, embeddings))


class QdrantVectorDB:
    """Manages Qdrant vector database for job postings."""
    
    def __init__(self, collection_name: str = "job_postings", vector_size: int = 384):
        """
        Initialize Qdrant client (using in-memory storage for this demo).
        """
        # Use in-memory Qdrant for STEP 2 demo
        self.client = QdrantClient(":memory:")
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Create collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created Qdrant collection: {collection_name}")
    
    def store_chunks(self, chunks_with_embeddings: List[Tuple[Chunk, List[float]]]) -> int:
        """
        Store chunks with embeddings and metadata in Qdrant.
        
        Returns:
            Number of chunks stored
        """
        points = []
        
        for idx, (chunk, embedding) in enumerate(chunks_with_embeddings):
            # Metadata payload
            payload = {
                "chunk_id": chunk.chunk_id,
                "posting_id": chunk.posting_id,
                "content": chunk.content,
                "chunk_type": chunk.chunk_type,
                "title": chunk.title,
                "company": chunk.company,
                "city": chunk.city,
                "role_category": chunk.role_category,
                "skills_extracted": chunk.skills_extracted,
                "date_posted": chunk.date_posted,
                "source": chunk.source,
            }
            
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload=payload,
            )
            points.append(point)
        
        # Upload points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        
        print(f"Stored {len(points)} chunks in Qdrant")
        return len(points)
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search for similar chunks using query_points.
        
        Returns:
            List of results with score and metadata
        """
        from qdrant_client.models import PointIdsList
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=k,
        )
        
        return [
            {
                "score": result.score if hasattr(result, 'score') else 0,
                "payload": result.payload if hasattr(result, 'payload') else {},
            }
            for result in results.points
        ]
    
    def search_with_filter(self, query_embedding: List[float], 
                          city: str = None, role_category: str = None, k: int = 5) -> List[Dict]:
        """
        Search with metadata filters (hybrid retrieval).
        
        Args:
            query_embedding: Query vector
            city: Filter by city (optional)
            role_category: Filter by role category (optional)
            k: Number of results
            
        Returns:
            Filtered search results
        """
        # For simplicity, do vector search then filter in Python
        # (A real implementation would use Qdrant's filter syntax)
        all_results = self.search(query_embedding, k=k*2)  # Get more to filter
        
        filtered = []
        for result in all_results:
            payload = result['payload']
            if city and payload['city'].lower() != city.lower():
                continue
            if role_category and payload['role_category'] != role_category:
                continue
            filtered.append(result)
            if len(filtered) >= k:
                break
        
        return filtered
    
    def get_all_chunks_for_posting(self, posting_id: str) -> List[Dict]:
        """Retrieve all chunks for a specific posting_id."""
        # Use scroll to get all points
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
        )
        
        return [
            {"id": point.id, "payload": point.payload}
            for point in points
            if point.payload.get('posting_id') == posting_id
        ]
