---
title: Code Review Checklist
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 42 — Code Review Checklist

> **"Code review is about catching structural flaws, security holes, and logic errors. Let the CI pipeline handle the formatting."**

---

# Purpose

This document provides the definitive checklist for reviewing code in PROJECT BRAIN. Whether the review is performed by a human Lead Engineer or an AI Coding Agent acting as a reviewer, this checklist must be satisfied before any Pull Request is merged into `main`.

---

# 1. Architecture & Design Boundaries

- [ ] **Layer Integrity:** Does this code belong in the layer where it is placed? (e.g., No HTTP `Request` objects in the Service layer. No raw SQL in the API Router).
- [ ] **Event Publishing:** If a state changes, is an event published to NATS? If so, is it published *after* the database transaction commits (to avoid ghost events)?
- [ ] **Blocking the Event Loop:** Are there any synchronous blocking calls (like `time.sleep()`, `requests.get()`, or heavy CPU operations) inside an `async def` function? (These must be offloaded to Temporal or `asyncio.to_thread()`).
- [ ] **AI Context Windows:** If this code passes data to an LLM, is the payload size bounded? (E.g., Are we accidentally sending a 10MB PDF string without chunking it first?)

# 2. Security & Privacy (Mission Critical)

- [ ] **Tenant Isolation (RLS):** Is `workspace_id` explicitly extracted from the authenticated user context and passed into the database query for EVERY read and write operation?
- [ ] **Prompt Injection Mitigation:** If user-generated text is passed into an LLM prompt, is it safely enclosed within XML tags (e.g., `<untrusted_input>`) and accompanied by a system warning to ignore instructions within the tags?
- [ ] **Secrets Management:** Are there any hardcoded API keys, JWT secrets, or database passwords in the code? (They must use `os.environ` or a secrets manager).
- [ ] **Data Serialization:** Does the API endpoint return a Pydantic schema (e.g., `response_model=AccountResponseSchema`) to strip out sensitive fields (like password hashes) before sending JSON to the client?

# 3. Database & Performance

- [ ] **N+1 Query Problem:** If a query fetches a list of Accounts, and the code later loops through them to print the Workspace Name, did the query use SQLAlchemy's `joinedload` or `selectinload` to prevent triggering hundreds of separate queries?
- [ ] **Soft Deletes:** Does the query explicitly filter `WHERE deleted_at IS NULL`, or does the base repository handle it automatically?
- [ ] **Missing Indexes:** If a new column is added that will be frequently searched or used as a foreign key, is an index included in the Alembic migration?

# 4. Maintainability & Code Quality

- [ ] **The Bouncer Pattern:** Does the function return early on errors/invalid states, avoiding deeply nested `if/else` blocks?
- [ ] **Type Safety:** Are type hints complete? (Will `mypy` pass?) Does the frontend code avoid using `any`?
- [ ] **Error Swallowing:** Are there any `except Exception: pass` blocks? (Errors must be logged or handled).
- [ ] **Magic Values:** Are magic strings/numbers extracted into Enums or Constants?

# 5. Testing & Observability

- [ ] **Test Coverage:** Does this change include adequate unit tests for the "Happy Path" and at least one "Error Path"?
- [ ] **Mocking:** Do the unit tests mock external dependencies (Database, NATS, LLM APIs)?
- [ ] **Observability:** If this is a complex AI workflow, is the `trace_id` properly propagated? Are errors logged using the JSON structured logger with the appropriate severity level?
