---
title: Acceptance Criteria Standards
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 38 — Acceptance Criteria Standards

> **"Ambiguity is the enemy of automation. If you cannot define exactly what 'Done' looks like, neither the human nor the AI can build it."**

---

# Purpose

This document defines how we write Acceptance Criteria (AC) for tasks in PROJECT BRAIN. Well-written ACs serve a dual purpose: they tell the human when the feature is ready, and they provide the exact logical boundaries an AI Coding Agent needs to write the Unit Tests.

---

# 1. The BDD Format (Behavior-Driven Development)

All Acceptance Criteria MUST be written in the **GIVEN / WHEN / THEN** format. This format eliminates ambiguity and translates directly into `pytest` or `Jest` test cases.

### The Structure:
- **GIVEN:** The initial context or state of the system.
- **WHEN:** The specific action the user (or system) takes.
- **THEN:** The exact, measurable, and verifiable outcome.

---

# 2. Examples of Good vs. Bad Criteria

### Scenario 1: Fetching Account Details

**❌ Bad AC (Vague):**
- The API should return the account details.
- It should fail if the account doesn't exist.
- Users shouldn't see other people's accounts.

*(Why it's bad: An AI reading this doesn't know what HTTP status codes to return, what the JSON structure should look like, or how to check "other people's accounts".)*

**✅ Good AC (Precise):**
- **AC1 (Happy Path):** 
  - **GIVEN** an authenticated user with `workspace_id = A`
  - **WHEN** they send a `GET` request to `/api/v1/accounts/{account_id}` where the account belongs to `workspace_id = A`
  - **THEN** the system returns `200 OK` with a JSON payload matching `AccountResponseSchema`.
- **AC2 (Tenant Isolation - Crucial):**
  - **GIVEN** an authenticated user with `workspace_id = A`
  - **WHEN** they send a `GET` request to `/api/v1/accounts/{account_id}` where the account belongs to `workspace_id = B`
  - **THEN** the system MUST return `403 Forbidden` (or `404 Not Found` to prevent data enumeration).
- **AC3 (Not Found):**
  - **GIVEN** an authenticated user
  - **WHEN** they request an `account_id` that does not exist in the database or `deleted_at IS NOT NULL`
  - **THEN** the system returns `404 Not Found`.

---

# 3. AI-Specific Acceptance Criteria

When dealing with AI Generation features (e.g., generating an Account Profile), we cannot write ACs for exact string matches. We must write ACs for *structure* and *behavior*.

### Scenario 2: Generating a Company Profile

**✅ Good AI AC:**
- **AC1 (Structural Adherence):**
  - **GIVEN** a valid URL payload sent to the Temporal Worker
  - **WHEN** the LLM finishes processing the scraped text
  - **THEN** the output MUST successfully validate against the `CompanyProfileSchema` without Pydantic validation errors.
- **AC2 (Failure Handling):**
  - **GIVEN** a URL that blocks scraping (returns 403)
  - **WHEN** the web scraper tool fails
  - **THEN** the Temporal workflow MUST NOT crash; it must return a structured JSON response with `status: "error"` and `reason: "Scraping blocked"`.
- **AC3 (Hallucination Prevention - Verified via Evaluation Suite):**
  - **GIVEN** a scraped text about "Microsoft"
  - **WHEN** the LLM is asked to extract the CEO
  - **THEN** it must extract "Satya Nadella". If the text does not mention the CEO, it MUST output `null`, not guess.

---

# 4. Enforcing the Standard

If a task is handed to a developer (or an AI agent) without BDD-formatted Acceptance Criteria, the task is **rejected** and sent back to the Product Owner for clarification. 

You cannot write code for a problem you haven't defined.
