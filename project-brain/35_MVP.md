---
title: MVP Scope Definition
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
implementation_updated: 2026-07-18
---

# 35 — MVP Scope Definition

> **"Perfection is the enemy of shipment. If you are not embarrassed by the first version of your product, you've launched too late. Deliver the core value, then iterate."**

---

# Purpose

This document establishes the absolute, non-negotiable boundaries of the Minimum Viable Product (MVP) for PROJECT BRAIN. Its purpose is to act as a shield against Scope Creep. If a feature or technical requirement is not explicitly listed in this document, **it will not be built during the MVP phase.**

---

# 1. The Core MVP Value Proposition

The MVP exists to prove one single hypothesis:
**"AI can autonomously research companies, find buying signals, and present actionable intelligence to an Account Manager every morning, better and faster than they could do it manually."**

If a feature does not directly support this hypothesis, it is cut.

---

# 2. Included in MVP (Strict Boundaries)

### 2.1. Infrastructure & Security
- Next.js Frontend + FastAPI Backend + PostgreSQL (`pgvector`) + Redis.
- Basic Temporal worker setup (single queue).
- Multi-Tenancy (Workspace RLS) implemented from Day 1 (retrofitting this later is impossible).
- Basic JWT Authentication (Email/Password or simple Google OAuth).

### 2.2. Functional Modules
1. **The Daily Briefing Dashboard:** A simple, read-only view of new discoveries and signals for the day.
2. **Account Discovery (The Crawler):** AI that accepts a basic query (e.g., "Find manufacturing companies in Sumatra") and uses basic web search tools to compile a list.
3. **Account Intelligence (The Profiler):** AI that takes a specific company URL, reads their website/news, and outputs a structured Pydantic schema containing: Overview, Key Executives, Tech Stack, and Recent News.
4. **Knowledge Hub (Layer 2 Only):** Admin can upload a PDF. The system chunks it, embeds it via `pgvector`, and allows basic semantic search.
5. **Digital Workforce Console:** A simple UI table where the AM sees what the AI found and can click "Accept" or "Reject".

---

# 2.3. Implementation Status Tracker

> **Updated: 2026-07-18** — Reflects actual build status. See `00_CURRENT_STATE.md` for full details.

### Infrastructure & Security
| Item | Status | Notes |
|---|---|---|
| Next.js 14 + FastAPI + pgvector + Redis | ✅ **DONE** | All running locally |
| Temporal worker (single queue) | ✅ **DONE** | `company-research-tasks` queue |
| Multi-Tenancy (Workspace RLS via JWT) | ✅ **DONE** | Enforced in every API endpoint |
| JWT Authentication | ✅ **DONE** | Supabase + Redis session cache |

### Functional Modules
| Module | Status | Notes |
|---|---|---|
| Daily Briefing Dashboard | ⚠️ **PARTIAL** | Shows account list & metrics. Missing: buying signals section, pending AI tasks section |
| Account Discovery (Crawler) | ⚠️ **PARTIAL** | Manual entry only. Missing: auto-discover from query |
| Account Intelligence (Profiler) | ✅ **DONE** | Gemini 2.5 Flash → Indonesian summary → pgvector embedding |
| Knowledge Hub Layer 2 (PDF + RAG) | ❌ **NOT STARTED** | Phase 12 |
| Digital Workforce Console (Accept/Reject) | ❌ **NOT STARTED** | Phase 11 |

---

# 3. Excluded from MVP (Strictly V2+)

If you are asked to build these during the MVP phase, refer to `34_FEATURE_BACKLOG.md` and refuse:

- ❌ **Proposal Generation:** Too complex. Requires flawless RAG. Save for V2.
- ❌ **Pipeline / Deal Management:** We are not replacing Salesforce yet. We are just feeding data.
- ❌ **CRM Integrations:** No Salesforce or HubSpot APIs. MVP data input/output is done via CSV or manual UI entry.
- ❌ **Meeting Transcription:** No Zoom/Teams integrations.
- ❌ **User Roles & Complex Permissions:** For MVP, everyone in a Workspace is an Admin.
- ❌ **Billing & Stripe:** This is an internal tool for now. No payment gateways.
- ❌ **WebSockets / Realtime UI:** React Query polling every 3 seconds is perfectly fine for MVP.

---

# 4. Success Metrics for MVP Graduation

To graduate from MVP to V2, we must deploy this to internal/beta users and hit these specific metrics within 4 weeks of launch:

1. **Usage:** Account Managers log in > 4 days a week.
2. **Value (Time Saved):** Account Managers report saving > 5 hours per week on manual research.
3. **AI Accuracy (Trust):** The recommendation acceptance rate in the Console is > 60% (meaning the AI isn't hallucinating garbage).
4. **System Stability:** System uptime > 99%. Temporal Worker failure rate < 5%.

---

# 5. Path to MVP Graduation

**Remaining work before MVP is considered complete:**

1. ❌ Build Phase 10: Buying Signal Employee + News Employee worker
2. ❌ Build Phase 11: Digital Workforce Console (Accept/Reject UI)
3. ❌ Build Phase 12: Knowledge Hub Layer 2 (PDF upload + RAG)
4. ⚠️ Enhance Phase 6: Add buying signals section to Daily Briefing Dashboard
5. ❌ Build Phase 13: Real authentication flow (Supabase Auth login page)

See `00_CURRENT_STATE.md` for implementation details on what's been built so far.
