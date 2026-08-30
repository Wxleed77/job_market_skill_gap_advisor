# Job-Market Skill-Gap Advisor (RAG)

A retrieval-augmented system that answers "what should I actually learn for X role in Y city" using **live job posting data**, not static blog opinions.

---

## 1. Problem Statement

Students pick skills based on outdated blog posts and hype ("learn AI!") without evidence of real, current demand. Job market data exists (Rozee.pk, LinkedIn, P@SHA surveys) but is scattered, unstructured, and stale the moment it's published. There's no tool that lets a student ask a specific, grounded question and get an answer sourced from postings from the last few weeks.

**Target user:** CS/tech students and early-career professionals in Pakistan deciding what to learn next.

---

## 2. Core Idea

Continuously scrape job postings + periodic industry reports → chunk and embed → let users query in natural language → retrieve the most relevant, recent postings → LLM synthesizes an answer **grounded in and citing actual postings**, not general knowledge.

The value isn't the LLM — it's the **freshness and grounding** of the retrieval corpus. This must be treated as a live data pipeline problem first, RAG problem second.

---

## 3. Data Sources

| Source | What it gives | Ingestion method | Refresh |
|---|---|---|---|
| Rozee.pk | Bulk of local job postings | Scraper (check ToS/robots.txt first — see §8) | Weekly |
| LinkedIn Jobs | Higher-quality, often international-facing postings | Scraper or LinkedIn API (restricted) / manual export | Weekly |
| P@SHA Skills Survey / reports | Structured, credible aggregate stats | Manual PDF ingestion on release | On publish |
| Company career pages (optional, phase 2) | Ground-truth for top employers | Targeted scraper per company | Bi-weekly |

**Note on scraping legality/ToS:** Rozee and LinkedIn both restrict scraping in their ToS. For a portfolio/demo project, either (a) scrape lightly and rate-limited for personal/academic use, (b) use publicly available RSS/job-board APIs where they exist, or (c) start with manually collected + P@SHA report data and add live scraping later. Don't let this block starting the project — build the pipeline abstraction so the scraper is swappable.

---

## 4. Architecture

```
┌─────────────────┐
│  Ingestion Layer │  Scrapers (Rozee, LinkedIn) + PDF parser (P@SHA reports)
└────────┬─────────┘
         │ raw postings/documents
         ▼
┌─────────────────┐
│ Normalization    │  Dedup, clean HTML, extract structured fields
│                  │  (title, company, city, skills, salary, date_posted)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Chunking + Embed │  Chunk per posting (not fixed-size splitting — see §5)
│                  │  Embed with metadata (city, role, date, source)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Vector DB        │  Store embeddings + metadata filters
│ (Qdrant/Chroma)  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Retrieval +      │◄─────┤ User Query        │
│ Metadata Filter  │      │ "AI roles Karachi"│
└────────┬─────────┘      └──────────────────┘
         │ top-k relevant postings
         ▼
┌─────────────────┐
│ LLM Synthesis    │  Answer grounded in retrieved postings, cites sources,
│                  │  states date range of data used
└────────┬─────────┘
         │
         ▼
     User Answer
```

---

## 5. Chunking Strategy

Job postings are **short, structured documents** — don't use generic fixed-size text splitting (this is where most RAG student projects go wrong).

- **One chunk per posting** for short postings (most Rozee listings).
- For longer postings (detailed JDs), split into: `title+summary`, `responsibilities`, `requirements/skills`, `company info` — as separate chunks sharing the same `posting_id` metadata, so retrieval can pull the most relevant section but reconstruct full context.
- **Always attach metadata**: `city`, `role_category`, `skills_extracted`, `date_posted`, `source`, `posting_id`. This lets you do **hybrid retrieval** (vector similarity + metadata filter), which matters more here than pure semantic search — "AI roles in Karachi posted in last 30 days" is a filter query, not just a similarity query.
- **Skill extraction**: run a lightweight NER/keyword extraction pass at ingestion time (spaCy or a small LLM call) to populate `skills_extracted` — this becomes your most valuable structured field and enables aggregate answers ("top 5 skills across 40 AI postings this month") without needing retrieval at all for some queries.

---

## 6. Retrieval Strategy

Two query modes, because "what skills are in demand" is fundamentally different from "find me a posting":

1. **Aggregate/analytical queries** ("what should I learn for AI roles in Karachi") → don't just do top-k similarity retrieval. Pull *all* postings matching the metadata filter (role category + city + recency window), then aggregate `skills_extracted` frequency, and pass the aggregate + a sample of postings to the LLM for synthesis. Pure vector search alone will give a shallow answer.
2. **Specific queries** ("show me postings that want LangChain") → standard vector + metadata filter, return top-k.

Route between the two with a simple query classifier (a small LLM call or rule-based check for phrases like "what should I learn" vs "show me jobs with").

---

## 7. Freshness & Re-embedding

- Weekly scrape → normalize → embed new postings only (don't re-embed the whole corpus each time).
- Expire/archive postings older than ~60-90 days from the "active" index (job demand data goes stale fast) but keep them in a `historical` index for trend queries ("has AI demand grown since Q1").
- Store `date_posted` and always surface it in answers — the tool should say "based on 34 postings from the last 30 days," so users can judge data freshness themselves.

---

## 8. Practical/Legal Considerations

- Scraping Rozee/LinkedIn at scale violates their ToS — for a real product this needs either partnership/API access or a different sourcing strategy. For a **portfolio project**, keep scrape volume low, rate-limit heavily, cache aggressively, and lead with this as a known limitation/future-work item rather than ignoring it — reviewers/interviewers respect that awareness.
- Consider starting with a **static seed dataset** (manually collected postings + P@SHA reports) to prove the RAG pipeline works, then layer in live scraping as a stretch goal.

---

## 9. Evaluation

This is the part most student RAG projects skip — and it's what separates a demo from a real project.

- **Retrieval quality**: hand-label ~30 test queries with which postings *should* be retrieved; measure precision/recall @ k.
- **Answer grounding**: check that every skill/claim in the LLM's answer traces back to a retrieved posting (no hallucinated skills) — spot-check manually, or use an LLM-as-judge pass.
- **Freshness check**: verify answers correctly reflect the date range of underlying data and don't silently use stale postings.
- **Aggregate accuracy**: for "top skills" queries, manually verify the frequency count against the raw postings.

---

## 10. Tech Stack (suggested)

| Layer | Tool |
|---|---|
| Scraping | Python (`requests`/`playwright` for JS-heavy pages) |
| PDF parsing (P@SHA reports) | `pymupdf` / `unstructured` |
| Skill extraction | spaCy NER or small LLM call (batched) |
| Embeddings | OpenAI `text-embedding-3-small` or local (`bge-small`) for cost control |
| Vector DB | Qdrant or Chroma (both support metadata filtering) |
| Orchestration | LangChain / LlamaIndex, or hand-rolled (recommended once you understand the pieces — less magic to debug) |
| Backend | FastAPI |
| Frontend | Simple React/Next.js chat UI with filter chips (city, role) |
| Scheduling | Cron job / GitHub Actions for weekly scrape+embed |

---

## 11. Build Plan (Incremental)

1. **Seed dataset**: manually collect ~100-200 postings (Rozee + P@SHA data), build normalization + skill-extraction pipeline.
2. **Core RAG loop**: embed, store in Qdrant, basic retrieval + LLM synthesis for specific queries.
3. **Aggregate query mode**: add the metadata-filter + frequency-count path for "what should I learn" style queries.
4. **Evaluation harness**: build the 30-query test set, measure retrieval precision before doing anything fancier.
5. **Live ingestion**: add scheduled scraping (rate-limited), dedup, weekly re-embed of new postings only.
6. **Frontend polish**: filter chips, source citations shown to user, "data freshness" indicator.

Stop and test after each step — this matches how you've said you like to work (incremental, not speculative).

---

## 12. What Makes This Non-Generic

- Aggregate analytical retrieval (not just top-k chat-with-docs).
- Metadata-first hybrid retrieval (city/role/date filters, not pure semantic search).
- Explicit freshness/date-grounding in every answer.
- A real evaluation harness instead of "looks good when I tried it."
- Honest handling of the scraping ToS problem instead of ignoring it.
