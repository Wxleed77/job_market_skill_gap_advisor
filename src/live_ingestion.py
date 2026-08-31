from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Any

from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.normalization import normalize_postings


@dataclass
class IngestionSource:
    """A fetcher abstraction for job-posting sources."""
    name: str
    fetch: Callable[[], List[Dict[str, Any]]]
    freshness_days: int = 30


class LocalSeedSource(IngestionSource):
    """Simple source that returns a local seed payload; useful for demos and tests."""

    def __init__(self, name: str, postings: List[Dict[str, Any]], freshness_days: int = 30):
        super().__init__(name=name, fetch=lambda: postings, freshness_days=freshness_days)


class LiveIngestionPipeline:
    """Pipeline for fetching fresh postings, deduplicating, normalizing, and refreshing vector index."""

    def __init__(self, vector_db: QdrantVectorDB, embedding_engine: EmbeddingEngine, sources: Optional[List[IngestionSource]] = None):
        self.vector_db = vector_db
        self.embedding_engine = embedding_engine
        self.sources = sources or []
        self.chunking_strategy = ChunkingStrategy()
        self._seen_posting_ids: set[str] = set()

    def _collect_raw_postings(self) -> List[Dict[str, Any]]:
        raw_postings: List[Dict[str, Any]] = []
        for source in self.sources:
            try:
                fetched = source.fetch() or []
                raw_postings.extend(fetched)
            except Exception as exc:  # pragma: no cover - defensive,
                print(f"[WARN] Source {source.name} failed: {exc}")
        return raw_postings

    @staticmethod
    def _deduplicate(raw_postings: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: set[str] = set()
        deduped: List[Dict[str, Any]] = []
        for posting in raw_postings:
            posting_id = posting.get("posting_id")
            if posting_id and posting_id in seen:
                continue
            seen.add(posting_id)
            deduped.append(posting)
        return deduped

    def _filter_recent(self, postings: List[Dict[str, Any]], max_age_days: int = 90) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow()
        recent: List[Dict[str, Any]] = []

        for posting in postings:
            posted = posting.get("date_posted")
            if not posted:
                recent.append(posting)
                continue

            try:
                parsed = datetime.fromisoformat(str(posted))
            except ValueError:
                recent.append(posting)
                continue

            if (cutoff - parsed).days <= max_age_days:
                recent.append(posting)

        return recent

    def refresh(self, sources: Optional[List[IngestionSource]] = None, max_age_days: int = 90) -> Dict[str, Any]:
        """Fetch new feed, normalize, dedupe, and refresh the vector index."""
        source_list = sources or self.sources
        if not source_list:
            return {
                "new_postings": 0,
                "stored_chunks": 0,
                "sources_checked": 0,
                "status": "no_sources",
            }

        raw = self._collect_raw_postings()
        deduped = self._deduplicate(raw)
        recent = self._filter_recent(deduped, max_age_days=max_age_days)

        if not recent:
            return {
                "new_postings": 0,
                "stored_chunks": 0,
                "sources_checked": len(source_list),
                "status": "no_recent_postings",
            }

        normalized = normalize_postings(recent)
        chunks = self.chunking_strategy.chunk_postings(normalized)
        chunks_with_embeddings = self.embedding_engine.embed_chunks(chunks)
        self.vector_db.store_chunks(chunks_with_embeddings)

        self._seen_posting_ids.update({posting["posting_id"] for posting in normalized if "posting_id" in posting})

        return {
            "new_postings": len(normalized),
            "stored_chunks": len(chunks_with_embeddings),
            "sources_checked": len(source_list),
            "status": "refreshed",
            "posting_ids": [posting["posting_id"] for posting in normalized],
        }


class RefreshScheduler:
    """Minimal scheduler abstraction. In a real deployment this would be a cron or GitHub Action job."""

    def __init__(self, pipeline: LiveIngestionPipeline):
        self.pipeline = pipeline

    def run_once(self, max_age_days: int = 90) -> Dict[str, Any]:
        return self.pipeline.refresh(max_age_days=max_age_days)

    def run_daily(self, max_age_days: int = 90) -> Dict[str, Any]:
        return self.pipeline.refresh(max_age_days=max_age_days)
