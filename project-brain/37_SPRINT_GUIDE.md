---
title: Sprint & Agile Guide
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 37 — Sprint & Agile Guide (AI-Augmented)

> **"Agile was designed for humans writing code linearly. In an era where AI writes 80% of the boilerplate in seconds, our sprint methodology must evolve from 'Velocity of Writing' to 'Velocity of Verification'."**

---

# Purpose

This document outlines how we structure our development cycles (Sprints) in PROJECT BRAIN. Because we heavily utilize AI Coding Agents (like Antigravity, Cursor, and Codex), traditional Agile estimation techniques (like Story Points based on human typing speed) are obsolete.

---

# 1. The 1-Week Sprint Cycle

Because AI dramatically accelerates development, a standard 2-week sprint is too long. We operate on strict 1-week cycles.

### Monday: Planning & Context Gathering
- **The human's job:** Write incredibly detailed AI Task Templates (`40_AI_TASK_TEMPLATE.md`) for the week's goals.
- Ensure the Master PRD, Architecture documents, and Database Schema guides are perfectly up to date. If the context is wrong, the AI will generate wrong code very quickly.

### Tuesday - Thursday: The Generation & Verification Loop
- **The AI's job:** Generate the code (Models, Routers, Services, Tests) based on the Task Templates.
- **The human's job:** Act as the Senior Reviewer. You do not type boilerplate; you review architecture, security boundaries, and edge cases. You execute the tests.
- This is an iterative loop: Generate -> Review -> Tweak Prompt -> Regenerate -> Commit.

### Friday: Deployment & Evaluation
- Deploy the week's work to Staging.
- Run the AI Evaluation Suite (Golden Dataset) to ensure the new features did not degrade the LLM's performance on existing tasks.
- Cut the release to Production (or schedule for Monday morning).

---

# 2. Rethinking Estimation (Story Points)

Traditional story points estimate complexity based on human effort. AI-Augmented points estimate complexity based on **Context Depth and Risk**.

- **1 Point (Trivial):** A task the AI can solve in one zero-shot prompt with 99% accuracy (e.g., adding a new CRUD endpoint for a simple table).
- **3 Points (Moderate):** Requires providing the AI with 3-4 files of context. The human will likely need to tweak the output to fix minor logical errors (e.g., writing a new Temporal Worker that calls a third-party API).
- **5 Points (Complex/Risky):** Tasks involving heavy architectural changes, deep multi-tenant security, or complex LLM Prompt Engineering. The human will spend significant time verifying the AI's output.
- **8+ Points (Epic):** Must be broken down. The context window required to solve this would overwhelm the AI, leading to hallucination and spaghetti code.

---

# 3. The Definition of Ready (DoR)

A task cannot enter the sprint (and cannot be handed to an AI agent) unless it meets the Definition of Ready:

1. **Acceptance Criteria are mathematically clear:** (See `38_ACCEPTANCE_CRITERIA.md`). "Make the UI look good" is not ready.
2. **Context is mapped:** The task explicitly lists which existing files/documents the AI needs to read before coding.
3. **Architecture is decided:** If the task introduces a new technology, the ADR (`46_ARCHITECTURE_DECISION_RECORD.md`) must already be approved.

---

# 4. The Role of the "Human in the Loop"

As an engineer on this project, your job title shifts from *Software Developer* to *Software Editor & Architect*.

1. **Do not fight the AI:** If the AI generates code that works and passes the standards, accept it, even if it's not exactly how you would have typed it.
2. **Protect the Boundaries:** The AI does not inherently understand our business domain or the importance of `workspace_id`. You are the guardian of Tenant Security and System Architecture.
3. **Write Tests First:** The best way to guide an AI is to write the `pytest` test yourself, then ask the AI to write the implementation that makes your test pass.
