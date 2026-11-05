# Rafi Vector + Hybrid RAG Upgrade

This upgrade converts the existing deterministic keyword RAG into a portfolio-grade hybrid RAG pipeline while preserving keyword fallback.

## What changed

- PostgreSQL image changed to `pgvector/pgvector:pg16`
- `CorpusChunk` table with 1536-dimensional pgvector embeddings
- chunking + embedding indexer
- semantic retrieval using cosine distance
- keyword + vector Reciprocal Rank Fusion
- retrieved chunk text passed to the grounded generation layer
- health endpoint reports corpus/chunk/vector readiness
- retrieval evaluation script with HitRate@K and MRR
- keyword fallback if embeddings are unavailable

## Important

Do not claim a page count, embedding count, or retrieval improvement percentage until the scripts below produce those actual numbers.

## Start

From the repository root:

```powershell
docker compose down
docker compose up -d --build
docker compose ps
```

Do **not** use `docker compose down -v` if you want to keep the existing database volume.

## Configure embeddings

In `backend/.env`:

```env
OPENAI_API_KEY=your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

Never commit `backend/.env`.

## Build the vector index

Test on a smaller batch first:

```powershell
docker compose run --rm backend python scripts/reindex_corpus.py --limit 100
docker compose run --rm backend python scripts/verify_rag_upgrade.py
```

A vector-ready result should show:

```text
chunks: >0
embedded_chunks: >0
vector_ready: True
retrieval: hybrid_vector_keyword
```

Then index the full authorized corpus:

```powershell
docker compose run --rm backend python scripts/reindex_corpus.py
```

## Evaluate retrieval

Copy the example file:

```powershell
Copy-Item backend\evaluation\retrieval_queries.example.json backend\evaluation\retrieval_queries.json
```

Replace the example cases with a larger set of real labeled questions and expected citations, then run:

```powershell
docker compose run --rm backend python scripts/evaluate_retrieval.py
```

Use only the measured HitRate@5 / MRR numbers in interviews and on your resume.

## Interview explanation

> Rafi uses hybrid RAG. I chunk the authorized legal corpus, generate embeddings, store them in PostgreSQL with pgvector, retrieve semantically similar chunks, combine semantic and keyword rankings with Reciprocal Rank Fusion, and pass only retrieved source text into the generation layer. The response preserves source metadata and requires human review. I also added a labeled retrieval evaluation harness so I can measure HitRate@5 and MRR instead of claiming unverified accuracy.

## If the embedding API is unavailable

Rafi automatically falls back to deterministic keyword retrieval. That preserves app availability, but `vector_ready` will remain false until embeddings are actually created.
