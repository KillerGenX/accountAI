---
title: AI Agent Quick Start Guide
version: 1.0.0
status: Living Document
owner: Engineering Lead
last_updated: 2026-07-18
ai_required: true
---

# 39 — AI Agent Quick Start Guide

> **You are an AI Coding Agent starting a new session on PROJECT BRAIN.**
> This document tells you everything you need to know to be productive in under 5 minutes.
> Read this before reading anything else.

---

# Step 1: Understand What This Project Is

PROJECT BRAIN is a **Digital Workforce Operating System for Enterprise Account Managers**.

In simple terms:
- An Account Manager (AM) opens this platform every morning
- AI agents ("Digital Employees") have already researched companies, found buying signals, and ranked opportunities overnight
- The AM reviews, approves, or rejects AI recommendations
- The AM leaves meetings fully prepared

See `00_VISION_AND_NORTH_STAR.md` for the full vision.

---

# Step 2: Check the Current State FIRST

> **Before writing a single line of code, read `00_CURRENT_STATE.md`.**

It tells you:
- Which phases are done (Phase 1–9 complete)
- Exactly which files exist and what they do
- Which gaps remain for the next phase
- Known issues and workarounds
- Critical rules you must follow

---

# Step 3: Start All Services

```powershell
# 1. Start local infrastructure (Redis + NATS + Temporal)
docker-compose up -d

# 2. Start FastAPI API Gateway (Port 8000)
services/api-gateway/.venv/Scripts/python services/api-gateway/src/main.py

# 3. Start Company Research Worker (NATS consumer + Temporal)
workers/company-research/.venv/Scripts/python workers/company-research/src/worker.py

# 4. Start Next.js Frontend (Port 3000)
pnpm --filter web dev
```

Verify health:
```bash
# Should return {"status": "healthy", "supabase_connected": true}
curl http://localhost:8000/health
```

---

# Step 4: Test the API (Dev Token)

In local development, use this mock token for all API calls:

```
Authorization: Bearer mock-token-teguh
```

This bypasses Supabase and returns the developer user profile directly.

Example:
```bash
# List all accounts in the workspace
curl http://localhost:8000/api/v1/accounts/ -H "Authorization: Bearer mock-token-teguh"

# Semantic search
curl "http://localhost:8000/api/v1/search/accounts?q=cloud+migration" -H "Authorization: Bearer mock-token-teguh"
```

---

# Step 5: Know the Key IDs

These IDs are seeded in the database and used throughout the system:

| Entity | ID |
|---|---|
| Default Workspace | `348ea7c6-11f3-4589-9518-e567c0958b7f` |
| Developer User (Teguh) | `5651b60c-a77f-4037-a190-f9e9a7c6eb02` |

---

# Critical Rules — Never Break These

| Rule | Why |
|---|---|
| ❌ Never change `Vector(1536)` in `account_embeddings` | Breaking embedding dimension breaks all pgvector queries |
| ❌ Never remove `mock-token-teguh` bypass from `auth.py` | It breaks local development entirely |
| ❌ Never use `gemini-1.5-flash` | It is DISABLED in this GCP project. Use `gemini-2.5-flash` |
| ❌ Never accept `workspace_id` as a request param | Always read from `current_user["workspace_id"]` for tenant isolation |
| ❌ Never call Vertex AI directly in API routes | Use `embedding_client.get_embedding()` from `domains/account/embeddings.py` |
| ❌ Never call LLM APIs directly in workers | Always go through LiteLLM in `activities.py` |
| ❌ Never modify DB schema without Alembic migration | Schema changes without migrations will break on the next `alembic upgrade head` |

---

# Where to Add New Code

| What you're adding | Where it goes |
|---|---|
| New API endpoint | `services/api-gateway/src/api/v1/<domain>.py` |
| New database model | `services/api-gateway/src/domains/<domain>/models.py` + Alembic migration |
| New Pydantic schema | `services/api-gateway/src/domains/<domain>/schemas.py` |
| New Digital Employee (worker) | `workers/<employee-name>/src/` following `company-research/` pattern |
| New frontend page | `apps/web/src/app/<page>/page.tsx` |
| New frontend component | `apps/web/src/components/<Component>.tsx` |
| New NATS event | Publish in API, subscribe in worker. Document in `10_EVENT_ARCHITECTURE.md` |

---

# Key Documents to Read for Each Task

| Task | Documents to Read |
|---|---|
| Building a new Digital Employee | `13_DIGITAL_EMPLOYEE_TEMPLATE.md`, `14_DEPARTMENT_BLUEPRINT.md`, `00_CURRENT_STATE.md` |
| Adding a new API endpoint | `23_API_GUIDELINES.md`, `26_BACKEND_GUIDELINES.md` |
| Adding a new frontend page | `25_FRONTEND_GUIDELINES.md` |
| Database schema change | `24_DATABASE_SCHEMA_GUIDE.md`, `09_DATA_ARCHITECTURE.md` |
| Understanding what to build next | `00_CURRENT_STATE.md`, `35_MVP.md`, `32_PRODUCT_ROADMAP.md` |
| Understanding AI integration | `04_AI_CONSTITUTION.md`, `11_DIGITAL_WORKFORCE_ARCHITECTURE.md` |

---

# Current Phase Status

**Completed:** Phase 1–9 (see `00_CURRENT_STATE.md` for full details)

**Active / Next Phase:** Phase 10 — Buying Signal Employee
- Goal: Build a dedicated worker that scans news daily for corporate trigger events
- Key events to detect: funding rounds, CTO/leadership changes, digital transformation signals
- Output: Records saved to `account_news` table + `buying_signals` table

See `DEVELOPMENT_LOG.md` for the detailed history of what was built.

---

# Tech Stack (Actual, Not Aspirational)

| Layer | Technology | Version |
|---|---|---|
| Frontend | Next.js | 14 |
| Backend | FastAPI + Python | 3.11+ |
| Database | PostgreSQL via Supabase | 17.6 |
| Vector DB | pgvector (same DB) | 0.8.2 |
| ORM | SQLAlchemy (async) | 2.x |
| Migrations | Alembic | latest |
| Cache | Redis | 7.x |
| Event Bus | NATS | 2.x |
| Workflow Engine | Temporal | latest |
| LLM Abstraction | LiteLLM | latest |
| LLM Provider | Google Vertex AI | — |
| LLM Model | `gemini-2.5-flash` | via `vertex_ai/` prefix |
| Embedding Model | `text-embedding-004` | 768 dims → zero-padded to 1536 |
| Monorepo | Turborepo + pnpm | latest |
| Logging | structlog (JSON) | latest |
