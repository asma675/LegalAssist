# Rafi Legal Assist

**A source-grounded legal AI workspace combining hybrid RAG, matter intelligence, evidence provenance, and human-in-the-loop review.**

Rafi is a full-stack legal-tech project built for Canadian legal workflows. Rather than operating as a general-purpose chatbot, Rafi connects legal research with the underlying **matter, documents, evidence, claims, authorities, deadlines, and review decisions**.

The project demonstrates practical engineering across **Retrieval-Augmented Generation, pgvector, PostgreSQL, FastAPI, React, multi-tenant application design, document intelligence, and grounded AI workflows**.

> **Rafi is a portfolio/development-stage legal-work platform, not a law firm and not a substitute for professional legal judgment. AI-assisted outputs are drafts requiring qualified human review.**

---

## Why I Built Rafi

General-purpose LLMs can produce useful legal text, but legal work requires more than generating an answer.

A useful legal system needs to answer questions such as:

- What document supports this factual claim?
- Which page contains the evidence?
- Are two source documents inconsistent?
- Which authority was retrieved for this legal issue?
- Is a deadline recorded in the matter, or was it inferred?
- What information is still missing?
- Which recommendations still require lawyer approval?

Rafi is designed around that problem.

### Core idea

```text
Matter
  │
  ├── Documents
  │      │
  │      └── Evidence
  │              │
  ├── Claims ────┘
  │
  ├── Legal Issues
  │      │
  │      └── Authorities
  │
  ├── Deadlines
  ├── Missing Information
  └── Recommended Actions
```

**ChatGPT gives an answer. Rafi helps operate the matter.**

---

# Hybrid Retrieval-Augmented Generation

Rafi includes a real retrieval layer rather than sending user prompts directly to an LLM.

The current pipeline combines:

```text
User query
    │
    ├───────────────┐
    ▼               ▼
Keyword retrieval   Query embedding
                    │
                    ▼
               pgvector search
               cosine similarity
    │               │
    └───────┬───────┘
            ▼
 Reciprocal Rank Fusion
            │
            ▼
 Top-ranked source chunks
            │
            ▼
  Grounded generation
            │
            ▼
 Response + citations
            │
            ▼
     Human review
```

## Retrieval stack

Rafi currently implements:

- OpenAI embeddings
- `text-embedding-3-small`
- 1536-dimensional vectors
- PostgreSQL + pgvector
- chunk-level semantic retrieval
- cosine-distance ranking
- deterministic lexical retrieval
- Reciprocal Rank Fusion
- source metadata preservation
- keyword fallback when embeddings are unavailable

The vector representation is stored using:

```python
Vector(1536)
```

Retrieved source chunks — rather than the entire corpus — are passed into the generation layer.

---

## Grounded AI Generation

Rafi's AI layer is explicitly instructed not to invent:

- legal authorities;
- citations;
- quotations;
- source facts;
- deadlines;
- supporting evidence.

When sources are retrieved, the model is instructed to cite only those supplied sources.

A typical response retains provenance such as:

```text
Authority
Citation
Source URL
Jurisdiction
Retrieved source text
Retrieval rank
Retrieval mode
Chunk ID
Verification metadata
```

This makes the generation step inspectable rather than treating the LLM as the source of truth.

---

# Matter Intelligence Graph

Rafi connects retrieved legal information to the actual matter.

The graph currently models entities including:

```text
MatterFact
Claim
EvidenceLink
LegalIssue
IssueAuthority
MatterDeadline
MissingInformation
Recommendation
MatterDigest
IntelligenceRun
DocumentPage
FirmPlaybook
```

The central workflow is:

```text
Document
   ↓
Evidence
   ↓
Claim
   ↓
Conflict / contradiction
   ↓
Legal issue
   ↓
Retrieved authority
   ↓
Review
   ↓
Action
```

---

## Evidence Provenance

Uploaded matter documents are parsed and stored with page-level text where available.

Claims can therefore link back to:

```text
Document
Page
Quoted passage
Relationship
Confidence / review state
```

The UI supports evidence click-through so reviewers can inspect the underlying source rather than relying only on an AI-generated summary.

---

## Contradiction Detection

Rafi includes deterministic logic for identifying selected factual inconsistencies.

For example, if separate source records state:

```text
Termination Letter
Effective termination date: March 3, 2026
```

and:

```text
HR Status Record
Effective termination date: March 7, 2026
```

Rafi can create a conflict claim and link both source passages rather than silently choosing one date.

This is intentional: in higher-risk workflows, deterministic source comparison can be preferable to asking an LLM to resolve ambiguity.

---

## Recorded Deadlines, Not Invented Deadlines

Matter deadlines are derived from stored:

- matter records;
- tasks;
- calendar events.

Rafi does not ask the language model to fabricate procedural deadlines.

The system distinguishes **recorded information** from AI inference and requires professional review before reliance.

---

# Retrieval Evaluation

Rafi includes a labeled retrieval evaluation harness.

Example evaluation case:

```json
{
  "query": "What authority addresses incentive compensation during the reasonable notice period?",
  "jurisdiction": "Canada",
  "relevant_citations": ["2020 SCC 26"]
}
```

The current evaluator measures:

- **HitRate@K**
- **MRR**

This allows retrieval quality to be measured against labeled expected authorities instead of judging RAG quality only by whether an answer "looks good."

Run:

```powershell
docker compose run --rm backend python scripts/evaluate_retrieval.py
```

> Retrieval metrics are not presented as overall legal or AI accuracy. Only measured results from the evaluation set should be used in project or résumé claims.

See:

```text
backend/scripts/evaluate_retrieval.py
backend/evaluation/
RAG_UPGRADE_README.md
```

---

# Technology Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- pgvector
- JWT authentication
- OpenAI API
- pypdf
- python-docx

### Frontend

- React
- Vite
- JavaScript
- Lucide
- Recharts
- Nginx

### Infrastructure

- Docker
- Docker Compose
- PostgreSQL persistence
- container health checks
- environment-based configuration

---

# Application Capabilities

Rafi currently includes:

### AI & Research

- hybrid legal RAG
- grounded AI assistant
- Canadian authority retrieval
- source-linked research
- legal drafting assistance
- contract review
- document analysis

### Matter Intelligence

- matter graph
- claims and evidence
- issue-to-authority mapping
- evidence-linked chronology
- contradiction detection
- missing-information tracking
- deadline tracking
- recommended next actions
- matter brief generation
- matter change digest

### Legal Workflow

- matters
- clients
- document vault
- tasks
- calendar events
- conflict checking
- firm playbooks
- notes and messages
- workflow definitions
- signature API scaffold
- billing/integration scaffolds

### Product

- authenticated workspace
- public product site
- demo-request workflow
- early-access waitlist
- founder lead view
- privacy/terms prototype pages

---

# Example Legal Research Flow

A research request such as:

```text
What authority governs incentive compensation during a wrongful-dismissal notice period?
```

can follow:

```text
1. Query submitted
        ↓
2. Keyword retrieval
        +
   vector similarity search
        ↓
3. Rankings combined
        ↓
4. Relevant corpus chunks selected
        ↓
5. Retrieved authority metadata preserved
        ↓
6. Source material supplied to the LLM
        ↓
7. Grounded draft returned
        ↓
8. User can inspect citations and sources
        ↓
9. Human legal review required
```

---

# Canadian Legal Corpus

Rafi is deliberately designed around **authorized and traceable source material**.

The built-in development corpus contains editorial notes for selected Supreme Court of Canada authorities and official federal-law references.

Example authorities include:

- *Bhasin v. Hrynew*, 2014 SCC 71
- *Uber Technologies Inc. v. Heller*, 2020 SCC 16
- *Matthews v. Ocean Nutrition Canada Ltd.*, 2020 SCC 26
- *Machtinger v. HOJ Industries Ltd.*, [1992] 1 S.C.R. 986
- Canada Labour Code
- Canada Business Corporations Act
- PIPEDA

The repository does **not** claim to contain a comprehensive licensed case-law database.

Additional authorized `.txt` or `.md` material can be placed under:

```text
data/legal_corpus/
```

and imported with:

```powershell
docker compose run --rm backend python scripts/import_local_corpus.py
```

Federal Justice Laws material can be synchronized through:

```powershell
docker compose run --rm backend python scripts/sync_justice_laws.py
```

Third-party legal databases should not be bulk-copied unless licensing or authorization permits it.

---

# Quick Start

## 1. Clone the repository

```powershell
git clone https://github.com/asma675/LegalAssist.git
cd LegalAssist
```

## 2. Create the environment file

```powershell
Copy-Item backend\.env.example backend\.env
```

Generate a development JWT secret:

```powershell
$secret = ([guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N"))
$secret
```

Add the generated value to:

```env
SECRET_KEY=your-generated-secret
```

---

## 3. Start with Docker

```powershell
docker compose up -d --build
```

Verify:

```powershell
docker compose ps
```

Expected services:

```text
db          healthy
backend     healthy
frontend    running
```

Open:

```text
Public site:        http://localhost:8080
Application:        http://localhost:8080/app
API documentation:  http://localhost:8000/docs
Health endpoint:    http://localhost:8000/api/health
```

---

# Demo Account

```text
Email: admin@rafi.app
Password: ChangeMe123!
```

This credential is only for local demonstration.

Change it before exposing the application to any external network.

---

# Enable AI + Vector Retrieval

Add your API key to:

```text
backend/.env
```

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

Never commit the real `.env` file.

Build embeddings:

```powershell
docker compose run --rm backend python scripts/reindex_corpus.py
```

Verify vector readiness:

```powershell
docker compose run --rm backend python scripts/verify_rag_upgrade.py
```

A successfully indexed environment should report:

```text
chunks: >0
embedded_chunks: >0
vector_ready: True
retrieval: hybrid_vector_keyword
```

---

# Resilient Retrieval

Rafi can continue operating if the embedding service is unavailable.

```text
Embeddings available
        ↓
Hybrid semantic + lexical retrieval

Embeddings unavailable
        ↓
Deterministic keyword retrieval
```

This prevents a vector-provider failure from making the research workflow completely unavailable.

---

# Multi-Tenant Design

Authenticated application data is scoped by tenant.

For tenant-owned entities, backend queries filter records through the authenticated user's:

```text
tenant_id
```

This applies across core matter, client, document, task, evidence, and workflow operations.

Rafi currently uses JWT authentication.

The project should not yet be described as having enterprise-grade RBAC; additional role-specific policy enforcement would be required.

---

# API Examples

```text
POST /api/auth/login

GET  /api/dashboard

GET  /api/matters
POST /api/matters

GET  /api/matters/{id}/intelligence
POST /api/matters/{id}/intelligence/rebuild
POST /api/matters/{id}/brief

POST /api/documents/upload
GET  /api/documents/{id}/page/{page}

POST /api/research
POST /api/ai/chat
POST /api/contracts/review
POST /api/drafting/generate

GET  /api/playbooks
POST /api/playbooks

PATCH /api/recommendations/{id}
PATCH /api/missing-information/{id}

POST /api/public/waitlist
POST /api/public/demo-request
```

Interactive API documentation is available through FastAPI at:

```text
http://localhost:8000/docs
```

---

# Design Decisions

Several Rafi design choices are intentional.

### Deterministic logic where possible

Not every workflow needs an LLM.

Rafi uses deterministic logic for selected functions such as:

- date extraction;
- source contradiction identification;
- deadline collection;
- tenant filtering;
- workflow state.

This reduces unnecessary model dependence.

### LLMs for synthesis rather than truth

The model is primarily used to synthesize retrieved information.

The source material — not the language model — remains the basis for factual and legal review.

### Human-in-the-loop

Outputs are marked for professional review rather than automatically treated as final legal conclusions.

---

# Production Readiness

Rafi is a **portfolio-grade and development-stage MVP**, not a claim of enterprise legal-AI readiness.

Before processing real confidential or privileged client data, additional work would be required around:

- MFA / SSO;
- complete role-based access control;
- encrypted object storage;
- secrets management;
- malware scanning;
- immutable audit logs;
- database migrations;
- backup / restore testing;
- HTTPS and secure cookies;
- rate limiting;
- monitoring and alerting;
- formal privacy/security review;
- production OAuth lifecycle;
- billing/subscription lifecycle;
- retrieval and generation evaluation;
- citation validation;
- prompt-injection and document-security testing.

---

# Project Status

### Implemented

- full-stack React + FastAPI application
- PostgreSQL persistence
- Dockerized deployment
- JWT authentication
- tenant-scoped application data
- matter/document/task workflows
- document text extraction
- Matter Intelligence Graph
- evidence provenance
- contradiction detection
- legal authority retrieval
- pgvector embeddings
- hybrid RAG
- Reciprocal Rank Fusion
- source-grounded generation
- retrieval evaluation tooling
- public demo/waitlist experience

### Continuing work

- larger authorized corpus
- 100+ query held-out retrieval benchmark
- stronger lexical retrieval
- approximate-nearest-neighbour indexing
- automated test coverage
- CI/CD
- production security controls
- role-specific authorization
- broader AI quality evaluation

---

# Summary

> I built Rafi as a source-grounded legal AI system rather than a simple chatbot. The backend uses FastAPI, SQLAlchemy and PostgreSQL, while the frontend is React. For RAG, I chunk an authorized legal corpus, generate embeddings, store them in PostgreSQL with pgvector, perform semantic cosine-similarity retrieval and deterministic lexical retrieval, and combine the rankings using Reciprocal Rank Fusion. Only retrieved source material is supplied to the generation layer. I also built a Matter Intelligence Graph connecting claims, evidence, legal issues and authorities, along with source-level provenance, contradiction detection, tenant-scoped data access and human-review controls. I added a labeled retrieval evaluation framework so retrieval quality can be measured using HitRate@K and MRR rather than relying on subjective demos.

---

## Repository

**Rafi Legal Assist**

`asma675/LegalAssist`

---

## License

See [`LICENSE`](LICENSE).
