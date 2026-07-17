---
title: Engineering Constitution
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: true
---

# ⚖️ Engineering Constitution

> **"Architecture is a long-term investment. Every line of code must protect it."**

---

# Purpose

This Constitution defines the engineering principles, architectural standards, development workflow, and quality requirements for the project.

Every human developer and every AI Coding Agent **MUST** follow this document before writing, reviewing, or modifying any code.

The objective is simple:

> Build software that remains maintainable, scalable, observable, and extensible for the next ten years.

---

# Engineering Mission

We are not optimizing for speed.

We are optimizing for **compounding engineering quality**.

Every sprint should leave the project better than before.

Every commit should increase long-term maintainability.

Every architectural decision should reduce future complexity.

---

# Engineering Philosophy

We believe:

- Software is a long-term asset.
- Architecture is more valuable than implementation.
- Readability is more valuable than cleverness.
- Consistency is more valuable than individual preference.
- Automation is more valuable than manual work.
- Documentation is part of the product.
- Testing is part of development.
- Observability is a first-class feature.
- AI accelerates engineering but never replaces engineering discipline.

---

# Engineering Principles

## 1. Foundation First

Never build features before the foundation exists.

The order is always:

Foundation

↓

Platform

↓

Modules

↓

Features

↓

Optimization

Never reverse this order.

---

## 2. Modular Architecture

Every capability must exist as an independent module.

Modules own:

- APIs
- Business Logic
- Database Access
- Events
- Workers

Modules never expose internal implementation details.

---

## 3. Domain-Driven Design

The project structure follows business domains.

Never organize code by technology.

❌ Bad

```
controllers/
models/
routes/
redis/
```

✅ Good

```
account/
opportunity/
proposal/
research/
forecast/
```

Business domains should remain stable even if technologies change.

---

## 4. Event-Driven Communication

Modules never communicate through direct dependencies whenever asynchronous communication is appropriate.

All long-running processes communicate through NATS Events.

Example:

Account Created

↓

Research Employee

↓

News Employee

↓

Industry Employee

↓

Relationship Employee

↓

Opportunity Employee

Every service remains loosely coupled.

---

## 5. AI Is a First-Class Citizen

Artificial Intelligence is part of the architecture.

Not an external plugin.

Every AI capability should be designed as a Digital Employee with:

- Responsibilities
- Memory
- Knowledge
- KPIs
- Events
- Evaluation Metrics

---

## 6. Workflow Reliability

Long-running AI workflows must use Temporal.

Never rely on chained API calls for critical workflows.

Workflows should be resumable, retryable, and observable.

---

## 7. AI Gateway

The application never communicates directly with an LLM.

All requests pass through the AI Gateway.

Responsibilities include:

- Provider Routing
- Prompt Versioning
- Cost Tracking
- Rate Limiting
- Retry Logic
- Logging
- Model Selection

---

## 8. Technology Independence

Business logic must never depend on infrastructure.

Infrastructure can change.

Business rules should not.

---

## 9. Build for Replacement

Every component should be replaceable.

Examples:

Gemini

↓

Claude

↓

OpenAI

↓

Open Source

No architectural changes required.

---

# Code Principles

Every piece of code should be:

- Simple
- Readable
- Testable
- Observable
- Documented
- Reusable

Never optimize for cleverness.

Optimize for clarity.

---

# Documentation First

No implementation starts without documentation.

Every module requires:

- Overview
- Responsibilities
- Public APIs
- Events
- Dependencies
- Data Model

Documentation evolves together with code.

---

# Testing Constitution

No feature is complete without testing.

Testing pyramid:

- Unit Test
- Integration Test
- End-to-End Test
- AI Prompt Regression Test
- Load Test

Every Pull Request must pass all required tests.

---

# Observability Constitution

Everything must be observable.

Every service exposes:

- Metrics
- Structured Logs
- Distributed Traces
- Health Checks
- Error Reports

We never debug by guessing.

We debug using evidence.

---

# Security Constitution

Security is never optional.

Every release includes:

- Dependency Scanning
- Secret Scanning
- Container Scanning
- Static Analysis

No secrets inside source code.

Never commit API Keys.

---

# CI/CD Constitution

Every Pull Request automatically triggers:

- Lint
- Formatting
- Tests
- Security Scan
- Build
- AI Review

Deployment only happens after all quality gates pass.

---

# AI Coding Constitution

Every AI Coding Agent MUST:

Read Project Brain first.

Understand the architecture before generating code.

Follow Coding Standards.

Update documentation.

Create tests.

Never invent APIs.

Never assume business rules.

Always ask for clarification if information is missing.

Architecture is more important than generating code quickly.

---

# Pull Request Rules

Every Pull Request must answer:

Why is this change needed?

What business problem does it solve?

Which modules are affected?

Which tests were added?

Which documentation was updated?

What architectural decisions were made?

---

# Definition of Ready

A task is ready only if:

- Requirements are clear
- Acceptance Criteria exist
- Dependencies are identified
- Architecture is understood
- Test strategy exists

---

# Definition of Done

A task is complete only if:

✅ Code Compiles

✅ Tests Pass

✅ Documentation Updated

✅ AI Review Passed

✅ Security Scan Passed

✅ Lint Passed

✅ Monitoring Added

✅ Logging Added

✅ Metrics Added

✅ Pull Request Approved

---

# Architectural Decision Records (ADR)

Every significant technical decision must produce an ADR.

Examples:

- Why FastAPI?
- Why NATS?
- Why Temporal?
- Why PostgreSQL?
- Why Event-Driven?

Future engineers should understand not only what was chosen,

but why it was chosen.

---

# Engineering Quality Gates

Code cannot be merged if:

❌ Tests fail

❌ Documentation missing

❌ Security scan fails

❌ Architecture violation detected

❌ AI review fails

❌ Lint fails

❌ Required approvals missing

---

# Engineering Workflow

```
Vision

↓

Architecture

↓

Sprint Planning

↓

Task

↓

AI Coding

↓

Human Review

↓

Testing

↓

Security Scan

↓

Documentation

↓

Merge

↓

Deployment

↓

Monitoring

↓

Feedback

↓

Continuous Improvement
```

---

# Engineering Values

We value:

Architecture over speed.

Quality over quantity.

Consistency over creativity.

Evidence over assumptions.

Automation over repetition.

Documentation over memory.

Systems over heroes.

---

# The Golden Rule

> **Every line of code should make the project easier to extend tomorrow than it was yesterday.**

If it does not,

it should not be merged.

---

# Final Commitment

Every contributor commits to protecting:

- The Vision
- The Architecture
- The Code Quality
- The Engineering Standards
- The Future Maintainability of the Platform

---

> **We do not build software for today.**

> **We build foundations that will continue creating software for the next decade.**