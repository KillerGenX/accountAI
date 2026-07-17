---
title: Product Roadmap
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 32 — Product Roadmap

> **"A vision without a roadmap is just a hallucination. A roadmap without dates is just a wishlist."**

---

# Purpose

This document outlines the strategic phases of development for PROJECT BRAIN. It maps out how we evolve from an internal Minimum Viable Product (MVP) to a full-scale Enterprise SaaS platform.

Unlike standard Agile backlogs, this roadmap focuses on **Capability Milestones** rather than granular Jira tickets.

---

# Phase 1: The Core Intelligence (MVP)
**Estimated Timeline: Weeks 1 - 6**
**Goal:** Prove the concept internally. The Account Manager uses the platform daily and saves at least 1 hour of research time per day.

### Infrastructure (Weeks 1-2)
- Set up the Turborepo Monorepo (Next.js + FastAPI).
- Deploy PostgreSQL with `pgvector` and NATS event bus.
- Implement strictly isolated Multi-Tenancy (Workspace RLS).
- Establish the Temporal Workflow Engine.

### Capability: Account Discovery & Profiling (Weeks 3-4)
- **Company Research Employee:** AI agents that autonomously scrape public data, news, and financials given a company name.
- **Account Intelligence Module:** Display the synthesized company profile (Tech Stack, Key Execs, Recent Signals) in a modern Next.js dashboard.

### Capability: Knowledge Hub Layer 2 (Weeks 5-6)
- Ability to upload internal PDFs (e.g., past proposals, pricing guides).
- Implement basic Retrieval-Augmented Generation (RAG) so the AI can answer questions about internal capabilities.
- **Digital Workforce Console:** A unified inbox where the AM reviews and approves AI discoveries.

---

# Phase 2: Action & Pipeline
**Estimated Timeline: Weeks 7 - 12**
**Goal:** The platform transitions from a passive research tool to an active recommendation engine that tracks the sales pipeline.

### Capability: Deal Scoring & Next Best Action (Weeks 7-8)
- **Opportunity Management Module:** AI tracks active deals.
- **Scoring Employee:** AI evaluates the probability of winning a deal based on historical data and current signals.
- AI recommends the "Next Best Action" (e.g., "Schedule a technical deep-dive because their CTO just posted about cloud migration").

### Capability: Meeting & Activity Center (Weeks 9-10)
- Ingest meeting transcripts (via Zoom/Teams API).
- AI automatically extracts Action Items, Next Steps, and updates the CRM state.

### Capability: Proposal Studio Alpha (Weeks 11-12)
- Multi-agent orchestration to generate the first draft of a technical proposal by combining Account Intelligence (the client's needs) with the Knowledge Hub (our capabilities).

---

# Phase 3: Scale & Enterprise SaaS
**Estimated Timeline: Months 4 - 6**
**Goal:** Commercialize the platform. Transition from a single-tenant internal tool to a multi-tenant SaaS ready for external customers.

### Infrastructure: SaaS Readiness
- Full integration with Stripe for subscription management.
- Self-serve onboarding and workspace provisioning.
- SOC2 Compliance audits and Penetration Testing.

### Capability: Bi-Directional CRM Sync
- Deep, robust integrations with Salesforce and HubSpot.
- The AI not only reads from the CRM but can autonomously push state changes (e.g., advancing a deal stage) back to Salesforce.

### Capability: Custom Digital Employees
- Provide a No-Code builder for enterprise tenants to create their own specialized AI Agents (e.g., "Legal Contract Reviewer Agent" specific to their company's legal guidelines).

---

# Phase 4: Autonomous Revenue Operations
**Estimated Timeline: Month 7+**
**Goal:** The AI doesn't just recommend; it executes (with human-in-the-loop approval).

### Capability: Autonomous Outreach
- AI drafts hyper-personalized outbound emails based on trigger signals (e.g., a company raises funding) and queues them in Gmail/Outlook for AM approval.

### Capability: Autonomous Renewal & Expansion
- AI monitors usage metrics and contract end dates.
- It proactively generates expansion proposals (e.g., "Customer X is hitting their API limit; here is an upsell proposal for the Enterprise tier").
