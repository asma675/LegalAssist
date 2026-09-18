# Rafi v2 Architecture

## Runtime

```text
Browser
  │
  ▼
Nginx / React :8080
  │ /api
  ▼
FastAPI :8000
  │
  ├── PostgreSQL
  ├── tenant-scoped upload volume
  ├── authorized Canadian legal corpus
  └── optional OpenAI API
```

## Matter Intelligence Graph

```text
Matter
 ├─ Facts ───────────────► source document/page
 ├─ Claims ──supports────► Evidence
 │         └─contradicts─► Evidence
 ├─ Claims ─review_against► Legal Issues
 ├─ Legal Issues ─────────► Verified/curated Authorities
 ├─ Deadlines ◄──────────── matter/tasks/events
 ├─ Missing Information
 ├─ Recommendations
 └─ Change Digests
```

Evidence references are stored as database links to `DocumentPage` plus the extracted supporting quote. The current v2 deterministic analyzer intentionally favors traceability over opaque model-generated claims.

## Trust boundary

Every tenant-owned record includes `tenant_id`, and API queries use the authenticated user's tenant. Do not replace server-side scoping with frontend filtering.

## RAG

Current retrieval is deterministic keyword scoring over the authorized corpus. This keeps the MVP easy to inspect. A production roadmap can add embeddings/hybrid retrieval, reranking, citation validation, negative tests, and source freshness checks without changing the product-level evidence model.

## AI policy

The AI system prompt requires Rafi to avoid inventing cases, citations, quotations, facts, deadlines, or sources. When an AI key is absent, Rafi returns retrieval/demo output instead of pretending it generated a legal conclusion.
