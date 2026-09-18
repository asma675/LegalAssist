# Rafi v2 Changelog

## Core differentiation

Rafi v2 moves from a collection of legal-AI tools to a connected matter-intelligence model.

### Added

- Matter Intelligence Graph UI and API
- Claims & Evidence tab with support/contradiction relationships
- evidence drawer with page-level source text
- source-linked chronology
- issue/authority mapping view
- missing-information workflow
- recommended-action approval workflow
- deadline provenance view
- matter digest feed on Command Center
- matter brief generation
- Firm Playbooks
- auto-rebuild after document upload
- demo evidence showing a conflicting termination-date record
- 15 curated SCC case notes plus selected official federal-law references
- local backend port `8000` in Docker for API docs and OAuth development

### Fixed

- demo login uses `admin@rafi.app` instead of the invalid special-use `.local` email
- v1 demo database email is upgraded automatically
- `bcrypt==4.0.1` is pinned for Passlib compatibility
- API validation errors render as readable messages instead of `[object Object]`

### Important limitations

- authority mappings are retrieval candidates and require counsel review;
- contradiction detection in v2 focuses on traceable date conflicts and is not a general truth engine;
- the client portal, e-signature provider integration, Google Calendar lifecycle, and Stripe lifecycle remain scaffolds requiring production hardening;
- Rafi does not include or claim a bulk CanLII licence.
