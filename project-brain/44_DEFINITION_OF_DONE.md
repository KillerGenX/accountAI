---
title: Definition of Done
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 44 — Definition of Done

> **"Done doesn't mean 'the code compiles'. Done means it is ready for the customer to use without breaking."**

---

# Purpose

The Definition of Done (DoD) is the ultimate, non-negotiable checklist that a feature, task, or bug fix must pass before it can be considered complete and ready to merge into `main`.

AI Coding Agents generate code extremely fast. Often, that code is "90% done." If we merge 90% done code, the remaining 10% accumulates as technical debt. The human developer's primary job is to enforce this final 10% using the DoD.

---

# The Definition of Done Checklist

For a task to be marked "Done", ALL of the following MUST be true:

## 1. Code Quality & Standards
- [ ] The code is formatted according to project standards (Black/Ruff/Prettier).
- [ ] Linters and Static Analysis tools pass with NO errors or warnings.
- [ ] Strict type checking (`mypy` / `tsc`) passes with NO errors.
- [ ] The code has been self-reviewed or AI-reviewed against `42_CODE_REVIEW_CHECKLIST.md`.

## 2. Testing & Verification
- [ ] Unit tests are written, mock external dependencies correctly, and are passing.
- [ ] Code coverage for the *newly added business logic* is > 80%.
- [ ] The feature has been manually verified locally (The Happy Path + at least one Error Path).
- [ ] If an AI Prompt was modified, the Golden Dataset Evaluation Suite was run and the score did not degrade.

## 3. Architecture & Documentation
- [ ] If the database schema changed, an Alembic migration script is included, tested locally, and is reversible.
- [ ] If the API contract changed, the FastAPI Pydantic models reflect the change accurately, meaning the OpenAPI (Swagger) docs are up to date.
- [ ] If the feature introduces a major new architecture component or technology, an ADR (`46_ARCHITECTURE_DECISION_RECORD.md`) was written and approved.

## 4. Security & Performance
- [ ] Multi-tenancy (`workspace_id`) is strictly enforced on all new database queries.
- [ ] No secrets, passwords, or API keys are hardcoded in the source code or printed to the logs.
- [ ] New AI prompts follow the XML tagging strategy to prevent prompt injection vulnerabilities.
- [ ] The feature does not introduce N+1 database queries.

## 5. Product Alignment
- [ ] The feature meets ALL Acceptance Criteria defined in the original BDD-formatted task (`38_ACCEPTANCE_CRITERIA.md`).
- [ ] UI changes match the design system (Tailwind/shadcn) and are responsive (work on mobile and desktop).
