# Rafi Hybrid RAG — Retrieval Engineering Upgrade

Rafi is a Canadian-first legal AI workspace designed around **source-grounded retrieval, traceable citations, and human review**.

This upgrade replaces Rafi's original deterministic keyword retriever with a production-oriented **hybrid Retrieval-Augmented Generation (RAG) architecture** using PostgreSQL, pgvector, semantic embeddings, lexical retrieval, Reciprocal Rank Fusion, retrieval telemetry, and reproducible evaluation.

The goal is not simply to make the model "sound smarter." The goal is to make retrieval **measurable, explainable, resilient, and grounded in authorized legal sources**.

---

## Architecture

```text
User legal query
        │
        ▼
Query preprocessing
        │
        ├───────────────┐
        ▼               ▼
Lexical retrieval    Query embedding
PostgreSQL FTS       OpenAI embeddings
        │               │
        │               ▼
        │          pgvector HNSW
        │          cosine similarity
        │               │
        └───────┬───────┘
                ▼
      Reciprocal Rank Fusion
                │
                ▼
      Top ranked source chunks
                │
                ▼
       Grounded generation
                │
                ▼
 Response + citations + provenance
                │
                ▼
         Human legal review
```

---

## Engineering Highlights

### Hybrid retrieval

Rafi combines two independent retrieval signals:

- **Lexical retrieval** for exact legal terminology, statute names, citations, and defined terms.
- **Semantic vector retrieval** for conceptually similar language even when the query and source use different wording.

The rankings are combined using **Reciprocal Rank Fusion (RRF)** rather than relying on a single retrieval strategy.

This is particularly useful for legal research, where both exact citation matching and semantic similarity matter.

---

### Vector search with PostgreSQL + pgvector

Corpus chunks are embedded using:

```text
text-embedding-3-small
1536 dimensions
```

Embeddings are stored directly in PostgreSQL using:

```python
Vector(1536)
```

Semantic retrieval uses cosine distance against pgvector.

The upgraded retrieval stack also supports an **HNSW approximate-nearest-neighbour index** for scalable vector search.

---

### Lexical search

The original implementation used deterministic term-frequency scoring.

The upgraded system supports PostgreSQL full-text search, allowing lexical retrieval to better handle:

- statutory terminology;
- case citations;
- legal phrases;
- exact contract language;
- named authorities.

The original keyword retriever is retained as a benchmark baseline.

---

## Legal-aware chunking

The indexing pipeline no longer relies only on arbitrary character windows.

Corpus material is divided using **section-aware and token-aware chunking**, preserving boundaries such as:

```text
Section
Article
Part
Division
Schedule
Chapter
```

Chunks are approximately:

```text
~450 tokens
~75-token overlap
```

This helps retain legal context while keeping retrieved passages small enough for precise grounding.

---

## Grounded generation

Only retrieved source material is provided to the generation layer.

Rafi's system instructions explicitly prohibit invented:

- authorities;
- quotations;
- citations;
- facts;
- deadlines;
- sources.

Retrieved authorities retain metadata including:

```text
title
citation
source URL
jurisdiction
retrieval rank
retrieval mode
chunk ID
verification metadata
```

Generated legal work remains explicitly marked as requiring professional human review.

---

## Graceful degradation

Rafi is designed to remain functional when the embedding provider is unavailable.

```text
Vector available
      ↓
Hybrid retrieval

Vector unavailable
      ↓
Lexical retrieval fallback
```

An embedding API failure therefore does not make the application unusable.

Importantly, benchmark runs use strict mode so vector failures cannot silently appear as successful vector results.

---

## Retrieval telemetry

Each retrieval request can expose engineering telemetry such as:

```text
requested_mode
used_mode
total_ms
embedding_ms
lexical_ms
vector_ms
lexical_candidates
vector_candidates
returned
fallback_reason
```

Example:

```powershell
docker compose run --rm backend python scripts/retrieval_probe.py `
  "duty of honest contractual performance" `
  --mode hybrid
```

This makes retrieval behaviour observable rather than opaque.

---

# Retrieval Evaluation

Rafi includes a labeled retrieval evaluation harness.

The benchmark evaluates the same frozen query set across four retrieval strategies:

```text
legacy_keyword
keyword
vector
hybrid
```

Metrics include:

- **HitRate@K**
- **MRR@K**
- **nDCG@K**
- **p50 retrieval latency**
- **p95 retrieval latency**
- corpus document count
- corpus chunk count
- embedded chunk count

A publishable benchmark requires at least **100 labeled held-out queries**.

This prevents small hand-selected examples from being presented as meaningful retrieval performance.

Run:

```powershell
docker compose run --rm backend python scripts/evaluate_retrieval.py
```

Results are written to:

```text
EVALUATION_RESULTS.md
backend/evaluation/results/latest.json
```

For development smoke testing only:

```powershell
docker compose run --rm backend python scripts/evaluate_retrieval.py --allow-small
```

---

## Evaluation integrity

Rafi intentionally separates:

```text
retrieval quality
```

from:

```text
answer quality
```

A retrieval HitRate@5 of 90%, for example, means the expected authority appeared in the top five retrieved results.

It does **not** mean the AI is "90% legally accurate."

Only measured benchmark results should be used in interviews, project descriptions, or résumé claims.

---

# Reliability and Testing

The project includes automated backend tests covering:

- API health;
- JWT authentication;
- tenant isolation;
- source-grounded research;
- human-review flags;
- lexical retrieval;
- retrieval telemetry;
- legal-aware token chunking.

GitHub Actions runs the backend test suite against a PostgreSQL + pgvector service and also verifies that the React frontend builds successfully.

This provides automated validation on every push and pull request.

---

# Running the RAG Pipeline

## 1. Start the application

```powershell
docker compose down
docker compose up -d --build
docker compose ps
```

Do not use:

```powershell
docker compose down -v
```

unless you intentionally want to delete the PostgreSQL volume.

---

## 2. Configure embeddings

Create:

```text
backend/.env
```

and configure:

```env
OPENAI_API_KEY=your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

Never commit `backend/.env`.

---

## 3. Build the vector index

Start with a limited corpus:

```powershell
docker compose run --rm backend python scripts/reindex_corpus.py --limit 100
```

Verify:

```powershell
docker compose run --rm backend python scripts/verify_rag_upgrade.py
```

A vector-ready environment should report:

```text
chunks: >0
embedded_chunks: >0
vector_ready: True
retrieval: hybrid_vector_keyword
```

Then index the complete authorized corpus:

```powershell
docker compose run --rm backend python scripts/reindex_corpus.py
```

---

# Corpus Principles

Rafi is designed to operate on **authorized legal material**.

The repository includes curated metadata and editorial summaries for selected Canadian authorities and tooling for importing permitted legal sources.

It does not claim to contain a comprehensive commercial case-law database.

Do not bulk-copy or redistribute third-party legal databases unless the applicable licence permits it.

---

# Why Hybrid Retrieval?

Pure semantic search can miss exact legal language.

Pure lexical search can miss conceptually related authorities.

Legal research frequently needs both.

For example:

```text
Query:
"Can an employee recover incentive compensation during the notice period?"
```

A lexical system may heavily depend on exact words such as:

```text
bonus
incentive
notice
```

while semantic retrieval can identify authority discussing the same legal concept using different wording.

RRF allows both signals to contribute to the final ranking.

---

# Interview Summary

A concise technical explanation of the project:

> I upgraded Rafi from deterministic keyword retrieval to a hybrid RAG architecture. Legal documents are section-aware and token-aware chunked, embedded with OpenAI embeddings, and stored in PostgreSQL using pgvector. At query time I run PostgreSQL full-text retrieval and semantic cosine-similarity retrieval, then combine the rankings using Reciprocal Rank Fusion. The retrieved source chunks are passed into a constrained generation layer that preserves citation metadata and requires human review. I also built retrieval telemetry, automated tests, CI, and a held-out evaluation harness measuring HitRate@K, MRR, nDCG, and latency so retrieval quality can be demonstrated with evidence rather than subjective examples.

---

# What This Project Demonstrates

Rafi is intended to demonstrate practical engineering across:

- Retrieval-Augmented Generation
- vector databases
- PostgreSQL / pgvector
- semantic search
- information retrieval evaluation
- ranking fusion
- FastAPI
- SQLAlchemy
- React
- Docker
- CI/CD
- multi-tenant application design
- source provenance
- AI reliability controls
- legal-domain human-in-the-loop workflows

The emphasis is not simply on calling an LLM API.

The engineering focus is on building a system where AI output can be connected back to the **documents, evidence, authorities, and retrieval decisions that produced it**.

---

## Current project status

Rafi is a portfolio and development-stage system, not a claim of production legal-AI readiness.

Before handling real privileged or confidential client information in production, additional work would be required around security, identity, auditability, encrypted storage, migrations, monitoring, data governance, and formal legal/AI evaluation.
