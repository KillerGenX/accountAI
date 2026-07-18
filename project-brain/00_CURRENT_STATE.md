---
title: Current Implementation State
version: 1.0.0
status: Living Document (Updated Per Phase)
owner: Engineering Lead
last_updated: 2026-07-18
ai_required: true
---

# 00 — Current Implementation State

> **AI Agent: READ THIS FIRST before doing anything.**
> This document reflects the ACTUAL state of the codebase as of `2026-07-18`.
> It is the bridge between the vision documents (01–46) and what has actually been built.
> If there is a conflict between this document and any other doc, **this document wins** for current-state facts.

---

# Phase Completion Summary

| Phase | Focus | Status | Date |
|---|---|---|---|
| Phase 1 | Monorepo + Local Infra (Docker) | ✅ COMPLETE | 2026-07-18 |
| Phase 2 | Database Models + Alembic Migrations | ✅ COMPLETE | 2026-07-18 |
| Phase 3 | Workspace & User API | ✅ COMPLETE | 2026-07-18 |
| Phase 4 | Account Intelligence Schema & CRUD API | ✅ COMPLETE | 2026-07-18 |
| Phase 5 | NATS Event Bus + Temporal AI Workers | ✅ COMPLETE | 2026-07-18 |
| Phase 6 | Next.js 14 Frontend Core UI | ✅ COMPLETE | 2026-07-18 |
| Phase 7 | Semantic Vector Search (pgvector) | ✅ COMPLETE | 2026-07-18 |
| Phase 8 | JWT Authentication + Redis Cache + RBAC | ✅ COMPLETE | 2026-07-18 |
| Phase 9 | Real AI Research (LiteLLM + Vertex AI Gemini 2.5) | ✅ COMPLETE | 2026-07-18 |
| Phase 10 | Buying Signal Employee + News Worker | ✅ COMPLETE | 2026-07-18 |
| Phase 11 | Digital Workforce Console UI (Accept/Reject) | ✅ COMPLETE | 2026-07-18 |
| Phase 12 | Knowledge Hub Layer 2 (PDF Upload + RAG) | ❌ NOT STARTED | — |

---

# Actual Repository Structure

```text
D:\Teguh\ES\Account\                   ← Monorepo Root
│
├── apps/
│   └── web/                           ← Next.js 14 Frontend (PORT 3000) ✅ ACTIVE
│       └── src/
│           ├── app/
│           │   ├── layout.tsx          ← Root layout + Sidebar shell
│           │   ├── page.tsx            ← Dashboard / Morning Brief
│           │   ├── globals.css         ← Light mode design system
│           │   ├── monitoring/
│           │   │   └── page.tsx        ← Digital Workforce Console (Reactive Inbox Tabs) ✅ ACTIVE
│           │   └── accounts/
│           │       ├── page.tsx        ← Account list + Add Account modal
│           │       └── [id]/
│           │           └── page.tsx    ← Account detail (Overview / Contacts / Notes tabs)
│           └── components/
│               └── Sidebar.tsx         ← Navigation sidebar + AI status indicators
│
├── services/
│   └── api-gateway/                   ← FastAPI Backend (PORT 8000) ✅ ACTIVE
│       └── src/
│           ├── main.py                 ← FastAPI entrypoint, CORS, router registration
│           ├── core/
│           │   ├── database.py         ← Async SQLAlchemy engine (Supabase)
│           │   ├── auth.py             ← JWT auth + Redis cache + RBAC
│           │   └── nats_client.py      ← NATS async connection wrapper
│           ├── domains/
│           │   ├── account/
│           │   │   ├── models.py       ← All account SQLAlchemy ORM models
│           │   │   ├── schemas.py      ← Pydantic request/response schemas
│           │   │   └── embeddings.py   ← Vertex AI / Mock embedding client
│           │   └── system/
│           │       ├── models.py       ← Workspace + User models
│           │       └── schemas.py      ← Workspace/user Pydantic schemas
│           └── api/
│               └── v1/
│                   ├── accounts.py     ← CRUD: accounts, contacts, notes
│                   ├── workspaces.py   ← Workspace management + user invite
│                   ├── search.py       ← Semantic vector search endpoint
│                   ├── monitoring.py   ← Manual daily scraper trigger endpoint ✅ ACTIVE
│                   └── news.py         ← News signals retrieval & status updates ✅ ACTIVE
│
├── workers/
│   ├── company-research/              ← Company Research Employee ✅ ACTIVE
│   │   └── src/
│   │       ├── worker.py              ← NATS consumer + Temporal worker entrypoint ✅ ACTIVE
│   │       ├── workflows.py           ← Workflows: CompanyResearch, DailyAccountMonitoring ✅ ACTIVE
│   │       ├── activities.py          ← Activities: research, db_update, get_active_accounts ✅ ACTIVE
│   │       ├── embeddings.py          ← Worker-side embedding client
│   │       └── register_schedule.py   ← Native Temporal Cron registration script ✅ ACTIVE
│   └── research-worker/              ← Placeholder directory (EMPTY, ignore)
│
├── database/
│   └── migrations/                    ← Alembic migration files ✅ ACTIVE
│
├── docker-compose.yml                 ← Local dev services ✅ ACTIVE
├── .env                               ← Environment variables (see section below)
├── .env.example                       ← Template for new developers
├── alembic.ini                        ← Alembic configuration
├── pnpm-workspace.yaml                ← pnpm monorepo config
├── turbo.json                         ← Turborepo pipeline config
└── project-brain/                     ← All documentation (THIS FOLDER)
```

---

# Live Services & Ports

| Service | URL | Notes |
|---|---|---|
| **Next.js Frontend** | `http://localhost:3000` | `pnpm --filter web dev` |
| **FastAPI API Gateway** | `http://localhost:8000` | `services/api-gateway/.venv/Scripts/python services/api-gateway/src/main.py` |
| **FastAPI API Docs (Swagger)** | `http://localhost:8000/docs` | Auto-generated by FastAPI |
| **NATS Event Bus** | `nats://localhost:4222` | via Docker Compose |
| **NATS Monitoring Console** | `http://localhost:8222` | via Docker Compose |
| **Temporal Server** | `localhost:7233` | via Docker Compose |
| **Temporal Web UI** | `http://localhost:8080` | via Docker Compose |
| **Redis Cache** | `redis://localhost:6379` | via Docker Compose |
| **Supabase DB** | Cloud-hosted | See `DATABASE_URL` in `.env` |

---

# How to Start All Services (Quick Start)

```powershell
# Terminal 1 — Start local infra (Redis, NATS, Temporal)
docker-compose up -d

# Terminal 2 — Start FastAPI API Gateway
services/api-gateway/.venv/Scripts/python services/api-gateway/src/main.py

# Terminal 3 — Start Temporal + NATS Worker (Company Research Employee)
workers/company-research/.venv/Scripts/python workers/company-research/src/worker.py

# Terminal 4 — Start Next.js Frontend
pnpm --filter web dev
```

---

# Environment Variables Required

All variables are stored in `.env` at the repository root.

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✅ Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ Yes | Supabase public anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | Supabase service role key |
| `DATABASE_URL` | ✅ Yes | Direct PostgreSQL connection string (Supabase) |
| `REDIS_URL` | ✅ Yes | Redis URL (default: `redis://localhost:6379/0`) |
| `NATS_URL` | ✅ Yes | NATS URL (default: `nats://localhost:4222`) |
| `TEMPORAL_HOST` | ✅ Yes | Temporal gRPC host (default: `localhost:7233`) |
| `GCP_PROJECT_ID` | ✅ Yes | Google Cloud project ID for Vertex AI |
| `GCP_LOCATION` | ✅ Yes | GCP region (e.g. `us-central1`) |
| `TAVILY_API_KEY` | ⚠️ Optional | Tavily search API. Falls back to mock results if absent. |
| `RESEARCH_LLM_MODEL` | ⚠️ Optional | Default: `vertex_ai/gemini-2.5-flash` |
| `ENVIRONMENT` | ✅ Yes | Set to `development` to enable mock auth bypass |

**Google Cloud Auth:** The worker uses a service account JSON file at the root:
`arcane-splicer-465815-d9-070a13481963.json` — This path is referenced in `activities.py`.

---

# Database Schema (Tables in Supabase)

All tables live in the `public` schema in Supabase PostgreSQL 17.

| Table | Purpose |
|---|---|
| `workspaces` | Tenant organizations (RLS boundary) |
| `users` | Account Managers within a workspace |
| `accounts` | Core company records (targets for AM) |
| `contacts` | Decision makers mapped to accounts |
| `account_intelligence` | AI-generated intelligence records per account |
| `account_news` | News feed items per account (table exists, worker not yet built) |
| `account_notes` | Private AM notes (Knowledge Layer 3) |
| `account_embeddings` | pgvector 1536-dim embeddings for semantic search |

**Critical:** The `account_embeddings` table uses `Vector(1536)`. Google Vertex AI `text-embedding-004` returns 768 dimensions — these are **zero-padded to 1536** in `embeddings.py` to match the schema. Do NOT change the vector dimension without a new Alembic migration.

---

# Authentication System

| Mode | Token | Behavior |
|---|---|---|
| **Development (local)** | `mock-token-teguh` | Bypasses Supabase, returns hardcoded user `am_teguh@company.com` |
| **Production** | Real Supabase JWT | Verified via `GET {SUPABASE_URL}/auth/v1/user` |

The mock user profile:
```json
{
  "id": "5651b60c-a77f-4037-a190-f9e9a7c6eb02",
  "email": "am_teguh@company.com",
  "workspace_id": "348ea7c6-11f3-4589-9518-e567c0958b7f",
  "role": "account_manager"
}
```

The default workspace ID hardcoded in the frontend:
`DEFAULT_WORKSPACE_ID = "348ea7c6-11f3-4589-9518-e567c0958b7f"`

---

# AI / LLM Configuration

| Component | Library | Provider | Model | Notes |
|---|---|---|---|---|
| **Company Research** | LiteLLM | Google Vertex AI | `vertex_ai/gemini-2.5-flash` | Default — `gemini-1.5-flash` is DISABLED in this GCP project |
| **Account Embedding** | Custom HTTP | Google Vertex AI | `text-embedding-004` | Returns 768 dims, zero-padded to 1536 |
| **Search Embedding** | Same as above | Google Vertex AI | `text-embedding-004` | Used at query time for pgvector cosine distance |
| **Tavily Search** | httpx | Tavily API | N/A | Falls back to mock if `TAVILY_API_KEY` not set |

---

# What the Company Research Employee Does (End-to-End Flow)

```
1. AM creates account via UI form
           ↓
2. FastAPI POST /api/v1/accounts/ → saves to DB, publishes NATS event "account.created"
           ↓
3. Worker (worker.py) receives NATS event → starts Temporal CompanyResearchWorkflow
           ↓
4. Temporal executes activities in sequence:
   a. research_company_profile()     → Tavily search + Gemini 2.5 → Indonesian summary
   b. update_account_in_db()         → saves business_summary, completeness_score += 30
   c. detect_buying_signals()        → scans summary for trigger keywords
   d. save_buying_signals_to_db()    → saves signal records (if detected)
           ↓
5. Frontend auto-refreshes → shows AI summary in Account Detail "Overview" tab
```

---

# API Endpoints Reference

## Workspaces
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/workspaces/` | Public | Create a new workspace |
| GET | `/api/v1/workspaces/{id}` | JWT | Get workspace profile |
| POST | `/api/v1/workspaces/{id}/users` | JWT (admin) | Invite user to workspace |

## Accounts
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/accounts/` | JWT (admin/am) | Create account + auto-embed |
| GET | `/api/v1/accounts/` | JWT | List workspace accounts |
| GET | `/api/v1/accounts/{id}` | JWT | Get account details |
| GET | `/api/v1/accounts/{id}/contacts` | JWT | List account contacts |
| POST | `/api/v1/accounts/{id}/contacts` | JWT (admin/am) | Add contact + auto-embed |
| GET | `/api/v1/accounts/{id}/notes` | JWT | List private AM notes |
| POST | `/api/v1/accounts/{id}/notes` | JWT | Add private note + auto-embed |

## Search
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/search/accounts?q={query}` | JWT | Semantic vector search via pgvector |

## News Signals
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/news/` | JWT | List scoped news discoveries with status filtering |
| PUT | `/api/v1/news/{id}/status` | JWT | Update news alert verification status |

---

# Implementation Gaps (What Still Needs to Be Built)

These are gaps vs the MVP scope defined in `35_MVP.md`:

| Gap | Priority | Phase | Impact |
|---|---|---|---|
| **Account Scoring Employee** (AI 0-100 scoring) | 🟡 Medium | Phase 11 | No prioritization for which accounts to target |
| **Knowledge Hub Layer 2** (PDF upload + RAG) | 🟡 Medium | Phase 12 | AM cannot upload internal docs (pricing, proposals) |
| **Search UI in frontend** | 🟡 Medium | Phase 10 | Semantic search API works but no search bar in UI |
| **Real Auth flow** (Supabase Auth UI / login page) | 🟡 Medium | Phase 13 | Frontend still uses hardcoded mock token |

---

# Known Issues & Workarounds

| Issue | Workaround |
|---|---|
| `gemini-1.5-flash` disabled in this GCP project | Use `vertex_ai/gemini-2.5-flash` (already set as default) |
| Google Vertex AI `text-embedding-004` returns 768 dims | Zero-padded to 1536 in `embeddings.py`. Do NOT change schema. |
| NATS connection fails if Docker Compose not running | Run `docker-compose up -d` first before starting any service |
| Frontend uses hardcoded `mock-token-teguh` | For real auth, user must be in `users` table with matching Supabase UUID |
| `research-worker/` directory in workers/ is empty | Ignore this folder — it's an artifact, use `company-research/` only |

---

# Rules for AI Agents Working on This Codebase

1. **Never change vector dimension** in `account_embeddings` without an Alembic migration. Current: `Vector(1536)`.
2. **Never remove the `mock-token-teguh` bypass** in `auth.py` — it's critical for local development.
3. **Always use `workspace_id` from the authenticated user** (from `current_user["workspace_id"]`). Never accept workspace_id as a query param — this enforces tenant isolation.
4. **New Digital Employees** go in `workers/<employee-name>/` following the same pattern as `company-research/`.
5. **Database changes** always require a new Alembic migration. Never modify the schema directly.
6. **All embeddings** must go through `embedding_client.get_embedding()` — never call Vertex AI directly from API routes.
7. **LiteLLM** is the only approved LLM abstraction layer. Do not import `google.generativeai` or `openai` directly in workers.

---

# Verification Test Results (as of Phase 10)

| Component | Test | Status |
|---|---|---|
| Supabase DB Connection | `SELECT 1` via SQLAlchemy | ✅ PASS |
| pgvector Extension | `CREATE EXTENSION vector` | ✅ PASS |
| Alembic Migrations | `alembic upgrade head` | ✅ PASS |
| Workspace CRUD API | POST + GET workspace | ✅ PASS |
| Account CRUD API | POST + GET account | ✅ PASS |
| Contact API | POST contact + embedding | ✅ PASS |
| Private Notes API | POST + GET notes | ✅ PASS |
| NATS Event Bus | Publish `account.created` | ✅ PASS |
| Temporal Workflow | `CompanyResearchWorkflow` E2E | ✅ PASS |
| AI DB Enrichment | `business_summary` saved to DB | ✅ PASS |
| Next.js Frontend | Renders at `localhost:3000` | ✅ PASS |
| UI Account Creation | Form → API → DB | ✅ PASS |
| UI AI Overview | Completeness 45% + summary visible | ✅ PASS |
| Vertex AI Embedding | `text-embedding-004` → 768→1536 dims | ✅ PASS |
| Semantic Vector Search | pgvector cosine similarity | ✅ PASS |
| JWT Authentication | Supabase token + Redis cache | ✅ PASS |
| Redis Session Cache | Cache hit < 2ms | ✅ PASS |
| Real AI Research | `gemini-2.5-flash` → Indonesian profile | ✅ PASS |
| Scheduled Daily Scraper | Temporal schedule + Daily Monitoring | ✅ PASS |
| Manual Scraper Trigger | API POST → NATS → Temporal | ✅ PASS |
| Workforce Console UI | Inbox console retrieves pending, approved, and rejected alerts correctly | ✅ PASS |
| Verification Actions | Approving/rejecting updates status in DB and animates card away | ✅ PASS |
