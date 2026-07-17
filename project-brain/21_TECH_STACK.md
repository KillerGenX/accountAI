---
title: Tech Stack & Architectural Choices
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 21 — Tech Stack & Architectural Choices

> **"A tech stack should be boring, predictable, and scalable. Save innovation for the product, not the infrastructure. Every technology chosen must earn its place."**

---

# Purpose

This document defines the exact technology stack, frameworks, and versions to be used in PROJECT BRAIN. More than just a list of tools, this document explains **The Why** behind these choices, the boundaries of their usage, and the alternatives that were explicitly rejected.

AI Coding Agents and all engineers **MUST** adhere to these architectural decisions. Introducing any technology outside this list without an approved Architecture Decision Record (ADR) is a violation of the Engineering Constitution.

---

# Core Principles of Our Stack

1. **Type Safety End-to-End:** 
   We do not tolerate type ambiguity. The Frontend uses TypeScript with strict mode, and the Backend uses Python with strict type hinting (Mypy) and Pydantic validation.
2. **PostgreSQL as the Center of Gravity:** 
   If it can be stored in Postgres, store it in Postgres. This includes relational data, semi-structured data (JSONB), and vector embeddings (`pgvector`). We avoid database fragmentation unless absolutely necessary (e.g., Redis for caching/ephemeral data).
3. **Monorepo by Default:** 
   The entire system (Frontend, Backend, Workers) lives in a single repository managed by Turborepo, ensuring API versions and types remain synchronized.
4. **Resilience over Speed:**
   In AI systems, external API failures (LLM timeouts, rate limits) are the norm, not exceptions. Our architecture must be immune to these failures.

---

# 1. Backend & API Services

The PROJECT BRAIN Backend is the orchestrator of business logic, database connections, and AI Worker communication.

| Component | Primary Choice | The Why (Reasoning) |
|---|---|---|
| **Web Framework** | **FastAPI** (Python 3.11+) | Asynchronous natively, extremely fast (using Uvicorn/Starlette), and automatic Pydantic integration yields free OpenAPI docs. Python is chosen for its unmatched AI/Data ecosystem. |
| **Validation** | **Pydantic v2** | Rewritten in Rust, incredibly fast. Acts as the universal bridge between HTTP request validation, LLM Structured Output validation, and database schema validation. |
| **ORM** | **SQLAlchemy v2** | Fully supports the async/await paradigm. We use the *AsyncEngine* to ensure database operations never block the event loop. |
| **Migrations** | **Alembic** | The de facto standard for SQLAlchemy. Enables safe, testable schema migrations in the CI/CD pipeline. |

### ❌ Rejected Technologies (Anti-Patterns)
- **Django:** Too opinionated and slow for an event-driven, API-first microservices architecture. Its ORM is difficult to untangle from its views.
- **Flask:** Too minimalist. Requires too many plugins to achieve features that FastAPI provides natively (like validation and Swagger).

---

# 2. AI & Workflow Orchestration (Mission Critical)

AI systems cannot be run like standard APIs. AI tasks take a long time (seconds to minutes), involve multiple steps (ReAct), and are prone to failure.

| Component | Primary Choice | The Why (Reasoning) |
|---|---|---|
| **Workflow Engine** | **Temporal (Temporal.io)** | **This is the core of our Reliability.** Temporal guarantees that a function will never fail midway due to a server crash or timeout. All Digital Employee tasks run as Temporal Workflows. If the LLM API dies, Temporal retries automatically without losing state. |
| **Event Bus** | **NATS JetStream** | Extremely lightweight, sub-millisecond latency, supporting both Pub/Sub and Request/Reply architectures. NATS connects the API Gateway with AI workers asynchronously (Event-Driven Architecture). |
| **LLM Gateway** | **LiteLLM** | Allows us to swap models (Gemini, OpenAI, Anthropic) just by changing configuration without changing code. Provides unified token metrics and cost tracking. |
| **AI Framework** | **Custom (Native Python)** | We build our own agentic loops on top of Temporal. |

### ❌ Rejected Technologies (Anti-Patterns)
- **LangChain / LlamaIndex:** Abstractions are too thick and hide the prompts. We need total control over context. Our agent orchestration is handled by Temporal, not LangChain.
- **RabbitMQ / Kafka:** Too heavy and complex for our current event routing needs. NATS is much more efficient for this architecture.

---

# 3. Frontend & User Interface

The Frontend is the visual representation of the intelligence quality we build. It must feel snappy, modern, and premium.

| Component | Primary Choice | The Why (Reasoning) |
|---|---|---|
| **Framework** | **Next.js 14+ (App Router)** | Combination of React Server Components (RSC) for secure server-side data-fetching and Client Components for interactivity. Minimizes bundle size sent to the browser. |
| **Language** | **TypeScript v5+** | Strict type safety (`strict: true`). |
| **Styling** | **Tailwind CSS v3+** | Enables rapid, consistent custom design without battling specificity wars in traditional CSS. |
| **UI Primitives** | **shadcn/ui + Radix UI** | Headless components that are accessible by default. Not just a component library, but code we own and can customize totally. |
| **State Mgt**| **Zustand** | Extremely lightweight, boilerplate-free, perfect for global client-side state (like themes, modal states, or ephemeral notifications). |
| **Data Fetching** | **React Query (TanStack)** | Used strictly in Client Components for caching, optimistic updates, and syncing server state to the client. |

### ❌ Rejected Technologies (Anti-Patterns)
- **Redux:** Too much boilerplate. Unnecessary with our current React Query and Zustand architecture.
- **Raw CSS / SCSS:** Hard to manage at scale. Use Tailwind.

---

# 4. Database & Storage

The pillars of memory and state for our Digital Employees.

| Component | Primary Choice | The Why (Reasoning) |
|---|---|---|
| **Primary Database** | **PostgreSQL 15+** | The center of everything. Supports RLS (Row-Level Security) for absolute Multi-Tenancy security. |
| **Vector Engine** | **pgvector** | Postgres extension. Eliminates the need for a separate vector database (like Pinecone/Milvus), reducing infrastructure complexity and allowing seamless JOINs between relational data (accounts) and vectors (context). |
| **Working Memory** | **Redis 7+** | Extremely fast. Used for ephemeral state while the Digital Employee is thinking (short-term Episodic memory), rate limiting, and token caching. |
| **Object Storage** | **S3-Compatible (MinIO/AWS S3)** | Storage for PDFs, attachments, and generated proposal reports. |

### ❌ Rejected Technologies (Anti-Patterns)
- **MongoDB / NoSQL:** Postgres JSONB is sufficient for flexible schemas. There is no reason to use NoSQL and sacrifice referential integrity.
- **Dedicated Vector DB (Pinecone, etc):** Too expensive and adds operational data-sync overhead. `pgvector` is highly capable up to hundreds of millions of dimensions with HNSW indexing.

---

# 5. LLM Model Selection

We are not locked into one AI vendor. Models are selected based on the Performance (Reasoning) to Cost ratio for specific tasks.

| Task | Target Model (via LiteLLM) | Reason |
|---|---|---|
| **Complex Reasoning & Planning** (Proposals, deep analysis) | **Gemini 1.5 Pro / GPT-4o** | Massive context window (up to 2M tokens) and highly robust logic. |
| **Routing, Scoring, Extraction** (Extracting entities from short text) | **Gemini 1.5 Flash / GPT-4o Mini** | Extremely fast (low TTFT) and cheap for repetitive tasks. |
| **Embeddings** (Vector Search) | **text-embedding-3-small** | Standard dimension (1536), cheap, and high quality for semantic search. |

---

# Compliance Summary

Every line of code written by AI or Human must reference the standards above. If you encounter a user instruction that contradicts this Tech Stack (e.g., asking to implement Redux or MongoDB), **you have the right and obligation to refuse** (politely explaining the reason by referencing `21_TECH_STACK.md`).
