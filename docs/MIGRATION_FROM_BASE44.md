# Migration from Base44

This codebase does not import `@base44/sdk`, use Base44 entities, Base44 auth, Base44 functions, Base44 file storage, or Base44 connectors.

| Former dependency | Rafi replacement |
|---|---|
| `base44.auth` | JWT auth in `backend/app/auth.py` |
| `base44.entities.*` | SQLAlchemy/PostgreSQL models |
| `UploadFile` integration | FastAPI upload endpoint + tenant file volume |
| `InvokeLLM` | server-side AI adapter in `backend/app/ai.py` |
| `checkUsage` | billing/status API scaffold; add metered usage table before commercial launch |
| Base44 Stripe function | direct Stripe Checkout endpoint |
| Base44 Google Calendar connector | Google OAuth connection endpoint scaffold |
| Base44 client-side entity filtering | mandatory server-side tenant filter |

The old Base44 project is not required at runtime.
