# Rafi Legal Assist v3

**Rafi** is a self-hostable, Canadian-first legal-workflow MVP for small and midsize legal teams. Version 3 keeps the v2 **Matter Intelligence Graph** and adds a complete public early-access website, waitlist, demo-request funnel, founder CRM, comparison section, FAQ, mission story, privacy/terms prototype pages, and production-oriented marketing routes.

> Rafi is legal-work software, not a law firm and not a substitute for professional legal judgment. AI-assisted outputs are drafts requiring qualified human review.

## What is new in v3

- **Public Rafi website** at `/` with a premium dark-purple editorial design, original Rafi copy and product mockups.
- **Request a Demo** flow at `/request-demo`, with a high-conversion split layout inspired by best practices from enterprise legal-AI websites while using original Rafi design/copy.
- **Early-access waitlist** at `/waitlist`.
- **Founder CRM** inside the authenticated app under **Early Access**, showing saved waitlist and demo leads.
- **Startup-style product storytelling**: mission, capability cards, category comparison, FAQ, early-access positioning and transparent caveats.
- **Public privacy and terms prototype pages** at `/privacy` and `/terms`.
- Public forms persist to PostgreSQL through first-party FastAPI endpoints; no third-party form builder is required.
- Basic honeypot spam field and Pydantic input validation on public forms.
- Existing authenticated workspace moved to `/app`.
- **Matter Intelligence Graph**: Claims → Evidence → Legal Issues → Authorities.
- **Evidence click-through**: evidence nodes open the stored document page text and quoted passage.
- **Automatic contradiction detection** for conflicting dated source statements such as different termination dates.
- **Evidence-linked chronology** built from stored matter documents.
- **Issue-to-authority mapping** using Rafi's authorized / curated corpus.
- **Matter-wide missing-information checklist** by practice area.
- **Recorded deadline layer** sourced from matter, task, and calendar records rather than guessed by the model.
- **Recommended next actions** with explicit lawyer approval state.
- **Matter change digest** on the Command Center.
- **Matter brief** generated from the connected intelligence layer.
- **Firm Playbooks** for persistent institutional rules and contract review.
- **Automatic intelligence refresh** after a matter document is uploaded.
- Better API error messages and upgraded demo login: `admin@rafi.app`.

The v1 features remain: Assistant, matters, clients, Vault, research, drafting, document review, templates, contract intelligence, workflow agents, tasks, calendar integration scaffold, conflict checking, client portal scaffold, signatures API, billing scaffold, notes/messages APIs, and Canadian legal corpus import tooling.

## Quick start with Docker

### 1. Open PowerShell in the project folder

```powershell
cd "C:\path\to\rafi"
```

### 2. Create or review the environment file

The ZIP includes a safe development `.env`. To recreate it from the example:

```powershell
Copy-Item backend\.env.example backend\.env
```

Generate a development JWT secret:

```powershell
$secret = ([guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N"))
$secret
```

Paste it into `backend\.env` as `SECRET_KEY=...`.

### 3. Build and start

```powershell
docker compose up -d --build
```

Check status:

```powershell
docker compose ps -a
```

Open:

- Public website: http://localhost:8080
- Request demo: http://localhost:8080/request-demo
- Waitlist: http://localhost:8080/waitlist
- Authenticated Rafi workspace: http://localhost:8080/app
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8080/api/health

### Demo login

```text
Email: admin@rafi.app
Password: ChangeMe123!
```

Change the demo password before exposing the app to any network.

## Upgrading to Rafi v3

Rafi v3 creates the new public `waitlist_leads` and `demo_requests` tables automatically while preserving the v2 Matter Intelligence tables. Existing demo credentials remain `admin@rafi.app` / `ChangeMe123!`.

If you want the complete fresh v3 demo dataset, including the sample Patel evidence conflict, and **you do not need your current Docker demo data**, reset the local volumes once:

```powershell
docker compose down -v
docker compose up -d --build
```

**Do not use `-v` if the Docker database contains data you want to keep.**

## Environment variables

`backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://rafi:rafi@db:5432/rafi
SECRET_KEY=replace-with-a-long-random-secret
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
UPLOAD_DIR=/app/uploads
DEMO_MODE=true
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_PROFESSIONAL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/google/callback
```

### AI

Rafi works without an OpenAI key in deterministic demo mode. It will build the Matter Intelligence Graph and retrieve corpus sources without generating unsupported legal conclusions.

To enable source-grounded narrative drafting, set:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-mini
```

Then restart the backend:

```powershell
docker compose restart backend
```

Never commit a real key to Git.

## Canadian legal corpus

The built-in seed contains editorial notes for real Supreme Court of Canada authorities and a small set of official federal-law references. These are deliberately notes and metadata, not copied case-law databases.

To import the Department of Justice Canada consolidated federal Acts and regulations through the included importer:

```powershell
docker compose run --rm backend python scripts/sync_justice_laws.py
```

The importer is designed to fail if it cannot build the intended large corpus instead of pretending a large import succeeded.

For your own licensed or authorized `.txt` / `.md` materials, place them under:

```text
data/legal_corpus/
```

then run:

```powershell
docker compose run --rm backend python scripts/import_local_corpus.py
```

Do not bulk-copy CanLII or another database unless your licence or authorization allows it.

## Matter Intelligence architecture

The v2 backend introduces these entities:

- `MatterFact`
- `Claim`
- `EvidenceLink`
- `LegalIssue`
- `IssueAuthority`
- `MatterDeadline`
- `MissingInformation`
- `Recommendation`
- `MatterDigest`
- `IntelligenceRun`
- `DocumentPage`
- `FirmPlaybook`

When a matter is refreshed, Rafi:

1. reads tenant-scoped matter documents;
2. extracts source-linked dated facts;
3. builds reviewable claims;
4. detects conflicting dates for the same event where the text supports that comparison;
5. links claims to exact document/page text;
6. creates practice-area issue prompts;
7. retrieves possible Canadian authorities from the corpus;
8. derives deadlines from stored matter/task/event records;
9. identifies information that counsel should confirm;
10. proposes next actions; and
11. writes a matter-change digest.

The system **does not treat model output as a verified legal conclusion**. Authority relevance and legal significance remain review tasks for counsel.

## Useful v3 endpoints

```text
POST /api/public/waitlist
POST /api/public/demo-request
GET  /api/growth/leads
GET  /api/matters/{id}/intelligence
POST /api/matters/{id}/intelligence/rebuild
POST /api/matters/{id}/brief
GET  /api/documents/{document_id}/page/{page_number}
GET  /api/playbooks
POST /api/playbooks
PATCH /api/recommendations/{id}
PATCH /api/missing-information/{id}
```

## Docker services

- `db`: PostgreSQL 16
- `backend`: FastAPI / SQLAlchemy on port `8000`
- `frontend`: React/Vite built into Nginx on port `8080`

## Production checklist before real client data

Rafi v3 is a **production-oriented MVP**, not a claim of enterprise readiness. Before using privileged or confidential client data in production, complete at least:

- MFA / SSO and secure user lifecycle management;
- separate scoped client-portal authentication;
- encrypted object storage and key management;
- malware scanning and file-type validation;
- immutable audit logging;
- Alembic migrations and tested backup / restore;
- secrets management rather than `.env` files on servers;
- HTTPS, secure cookies / hardened token handling, rate limiting and monitoring;
- encrypted Google OAuth token persistence and completed callback/sync lifecycle;
- complete Stripe webhook/subscription state handling;
- legal/privacy/security review for your deployment and jurisdiction;
- evaluation suites for citation accuracy, extraction accuracy, contradiction false positives, and retrieval quality.

## Public website design note

The public website takes **high-level layout inspiration** from strong contemporary SaaS patterns: large editorial legal-AI demo pages, focused request-demo funnels, startup mission storytelling, comparison tables and FAQs. All Rafi copy, colors, product mockups, components and assets in this repository are original; the project does not copy Harvey or Gravity logos, images, customer marks or proprietary page text.

## Positioning

**ChatGPT gives an AI answer. Rafi helps operate the legal matter.**

Rafi's intended differentiation is the connected workflow around AI: matter context, evidence provenance, Canadian research, firm playbooks, review controls, deadlines, client work, and repeatable agents.
