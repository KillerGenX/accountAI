---
title: AI Task Template
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 40 — AI Task Template

> **"An AI is only as good as the context you provide. Vague inputs yield chaotic outputs. Give the AI the rules of the game before asking it to play."**

---

# Purpose

This document provides the mandatory template that MUST be filled out by the human Product Owner (or Lead Engineer) BEFORE handing a coding task to an AI Coding Agent (e.g., Antigravity, Cursor, GitHub Copilot).

In the age of AI coding, writing the task definition *is* the programming.

---

# Instructions for Use

1. Copy the template below into a new markdown file in your local `tasks/` directory (e.g., `tasks/TASK-001-create-account-model.md`).
2. Fill out every single section. Do not skip the "Context Documents" section.
3. Open your AI IDE or CLI.
4. Issue the precise trigger prompt: `Read the task definition in tasks/TASK-001-create-account-model.md and execute it strictly according to the provided context and constraints.`

---

# The Template

```markdown
# TASK: [Ticket ID] - [Short Title of Task]

## 1. Goal
[One sentence describing exactly what needs to be accomplished. E.g., "Implement the CRUD FastAPI router for the Account entity with strict workspace isolation."]

## 2. Context Documents to Read First
> **AI INSTRUCTION:** You MUST read and understand these documents before writing any code. Do not hallucinate architectural patterns.
- [e.g., PRDs/02_account-intelligence.md]
- [e.g., 23_API_GUIDELINES.md]
- [e.g., 24_DATABASE_SCHEMA_GUIDE.md]
- [List any relevant existing codebase files to read, e.g., src/domains/account/models.py]

## 3. Detailed Requirements
- Requirement 1: [e.g., The POST endpoint must accept a JSON payload matching AccountCreateSchema.]
- Requirement 2: [e.g., The Service layer must publish an 'AccountCreated' event to NATS after the database commit.]

## 4. Strict Constraints
- Constraint 1: [e.g., Do NOT use raw SQL. Use the SQLAlchemy AsyncEngine.]
- Constraint 2: [e.g., Every endpoint MUST use the `Depends(get_current_workspace)` dependency.]
- Constraint 3: [e.g., Do not modify the existing `users` table.]

## 5. Expected Output
1. [e.g., A new file `src/domains/account/schemas.py` containing Pydantic models.]
2. [e.g., A new file `src/api/v1/accounts.py` containing the router.]
3. [e.g., Unit tests in `tests/api/test_accounts.py` mocking the database and NATS.]

## 6. Acceptance Criteria (BDD Format)
- [ ] **GIVEN** an authenticated user in workspace A **WHEN** they POST valid account data **THEN** it returns 201 Created and saves to the database.
- [ ] **GIVEN** an authenticated user in workspace A **WHEN** they GET an account belonging to workspace B **THEN** it returns 404 Not Found.

## 7. Definition of Done Checklist (Reference `44_DEFINITION_OF_DONE.md`)
- [ ] Code follows formatting standards (Black / Ruff / Prettier).
- [ ] Type hints are complete (Mypy passes).
- [ ] Unit tests are written and pass.
- [ ] No secrets or magic strings are hardcoded.
```
