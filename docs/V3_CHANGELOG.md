# Rafi v3 Changelog

Rafi v3 adds the public acquisition and early-access layer around the v2 matter-intelligence product without removing the authenticated workspace.

## Public product website

- `/` — premium Rafi landing page in the existing dark-purple visual system.
- `/request-demo` — split-layout demo request page with product benefits and a detailed qualification form.
- `/waitlist` — early-access signup page.
- `/privacy` and `/terms` — clear prototype notices for public form and AI use.
- `/app` — authenticated legal-work workspace.

The visual system borrows only **general SaaS design patterns** (editorial typography, spacious legal-AI presentation, split conversion forms, product comparison and FAQ storytelling). Rafi uses original code, copy, colors and mockups and does not include third-party logos, screenshots or proprietary text.

## First-party lead capture

New backend tables:

- `WaitlistLead`
- `DemoRequest`

New API routes:

```text
POST /api/public/waitlist
POST /api/public/demo-request
GET  /api/growth/leads
```

Public submissions are saved directly to Rafi's PostgreSQL database. Basic server validation and an invisible honeypot field are included. Add rate limiting, CAPTCHA / Turnstile, email verification and a real privacy policy before a public launch at scale.

## Founder CRM

The authenticated sidebar now includes **Early Access**, where the founder can see:

- total waitlist signups;
- total demo requests;
- contact / organization / role / team size;
- practice-area context for demo requests.

## Existing product preserved

Version 3 keeps the existing:

- Matter Intelligence Graph;
- evidence provenance and contradiction detection;
- matters, clients, tasks and calendar;
- Assistant, Vault, Research, Drafting and Document Review;
- Contract Intelligence and Firm Playbooks;
- Agents and approval gates;
- client portal / signature scaffolding;
- Canadian corpus import tooling;
- Docker / FastAPI / React / PostgreSQL architecture.
