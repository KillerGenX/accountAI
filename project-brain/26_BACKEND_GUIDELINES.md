---
title: Backend Guidelines
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 26 — Backend Guidelines

> **"The backend is the brain of the platform. Keep it organized, fast, and secure. A messy backend leads to a fragile AI."**

---

# Purpose

This document outlines the architectural patterns and strict best practices for the FastAPI backend application in PROJECT BRAIN. It defines how we structure code, separate concerns, and handle the complex orchestration of databases, events, and AI workers.

---

# 1. Architecture: Domain-Driven Structure

We organize code by **Domain (Feature Area)**, not by technical layer. This keeps related logic grouped together, making the codebase easier to navigate and split into microservices later if necessary.

```text
/backend
  /src
    /api              # API routers (The Presentation Layer)
      /v1
        /accounts.py
        /opportunities.py
    /core             # Core configs, security auth, DB engine setup
    /domains          # Business logic grouped by domain
      /account
        models.py     # SQLAlchemy models
        schemas.py    # Pydantic validation schemas
        service.py    # Business logic (The Domain Layer)
        repository.py # Database interactions (The Data Layer)
      /opportunity
        ...
    /workers          # Temporal worker activities & workflows
    /events           # NATS event publishers & subscribers
```

---

# 2. The Three-Layer Architecture

Strict separation of concerns is mandatory. Code in one layer must not leak responsibilities into another.

### Layer 1: API Router (Presentation)
- **Responsibility:** Handle HTTP requests/responses, extract JWT tokens, enforce authorization, and validate incoming JSON payloads via Pydantic.
- **Rule:** ZERO business logic. The router should immediately pass the validated data to the Service layer and return the result.

### Layer 2: Service Layer (Domain)
- **Responsibility:** The heart of the application. Enforces business rules, calculates scores, coordinates multiple repositories, and triggers background workers.
- **Rule:** Must not know about HTTP requests (no FastAPI `Request` objects). Must not contain raw SQL.

### Layer 3: Repository Layer (Data)
- **Responsibility:** Execute SQLAlchemy queries against the database.
- **Rule:** Must not contain business logic. Just pure CRUD operations returning SQLAlchemy model instances.

---

# 3. Dependency Injection

FastAPI's `Depends` system must be used extensively to decouple components and make them testable.

- **Database Sessions:** Inject `AsyncSession` via `Depends(get_db)`. Do not create sessions globally.
- **Current User / Workspace:** Inject `workspace_id` via `Depends(get_current_workspace)`.
- **Services:** Inject service classes if they require specific configuration, rather than instantiating them directly in the router.

```python
@router.post("/")
async def create_opportunity(
    payload: OpportunityCreateSchema,
    db: AsyncSession = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace)
):
    # The router just routes. The service does the work.
    return await opp_service.create(db, workspace.id, payload)
```

---

# 4. Background Tasks vs Temporal Workflows

In an AI application, distinguishing between simple background tasks and complex workflows is critical.

### FastAPI BackgroundTasks
- **When to use:** ONLY for fire-and-forget tasks that take **less than 5 seconds** and are safe to lose if the server crashes (e.g., sending an internal Slack notification, recording a quick telemetry metric).
- **Why:** BackgroundTasks run in the same memory space as the web server. If the server restarts, the task is lost forever.

### Temporal Workflows
- **When to use:** For ALL AI tasks, long-running processes, multi-step operations (ReAct loops), and anything involving external API calls that might rate-limit (LLMs).
- **Why:** Temporal provides durable execution. If an AI worker crashes midway through analyzing a company, Temporal remembers exactly which step it was on and resumes it automatically on another worker node.

---

# 5. Event Publishing (NATS)

PROJECT BRAIN relies heavily on an Event-Driven Architecture (see `10_EVENT_ARCHITECTURE.md`).

**The Golden Rule of Event Publishing:**
Events must ONLY be published to NATS *after* the database transaction has successfully committed. 
- If you publish an `AccountCreated` event, but the database transaction rolls back due to a constraint violation, downstream AI workers will trigger, try to read the account from the database, fail to find it, and crash.
- Use the **Outbox Pattern** or hook into SQLAlchemy's `after_commit` event hook to guarantee atomic event publishing.

---

# 6. Error Handling

- Use custom exception classes derived from a base `AppException`.
- Map specific `AppException` types to standard HTTP status codes using FastAPI's exception handlers.
- **Logging:** Any exception resulting in a `500 Internal Server Error` must log the full stack trace and the `trace_id` for observability. Client errors (`400`, `401`, `404`) should be logged at the `INFO` or `WARNING` level, without polluting the error logs with user typos.
