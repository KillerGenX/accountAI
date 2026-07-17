---
title: Monorepo Structure
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: true
---

# 📦 Monorepo Structure

> **"A clean repository is the foundation of a scalable engineering organization."**

---

# Purpose

This document defines the official repository structure for the platform.

The repository is designed to support:

- AI Coding Agents
- Human Developers
- Multiple Applications
- Shared Libraries
- Independent Services
- Cloud-Native Deployment
- Long-term Scalability

Every contributor MUST follow this structure.

---

# Repository Philosophy

The repository is designed around **business capabilities**, not technologies.

We optimize for:

- Discoverability
- Maintainability
- Reusability
- Modularity
- AI Readability

A new engineer—or an AI Coding Agent—should understand where code belongs within minutes.

---

# Repository Overview

```text
project-root/

├── project-brain/
│
├── apps/
│
├── services/
│
├── packages/
│
├── infrastructure/
│
├── database/
│
├── workers/
│
├── tools/
│
├── scripts/
│
├── tests/
│
├── .github/
│
├── docker/
│
├── docs/
│
├── turbo.json
├── package.json
├── pnpm-workspace.yaml
├── README.md
└── LICENSE
```

---

# Project Brain

```
project-brain/
```

The project's single source of truth.

Contains:

- Vision
- Architecture
- ADRs
- AI Constitution
- Engineering Constitution
- Product Documentation
- Technical Decisions

No source code belongs here.

---

# Apps

```
apps/
```

Contains user-facing applications.

Example:

```text
apps/

web/

admin/

mobile/

desktop/

landing/
```

Responsibilities:

- User Interface
- Authentication
- User Experience

Apps should contain minimal business logic.

---

# Services

```
services/
```

Contains backend APIs.

Example:

```text
services/

api-gateway/

auth/

notification/

ai-gateway/
```

Every service is independently deployable.

---

# Workers

```
workers/
```

Contains Digital Employees.

Example:

```text
workers/

research-worker/

news-worker/

proposal-worker/

forecast-worker/

relationship-worker/

renewal-worker/
```

Each worker owns exactly one responsibility.

Workers communicate through NATS Events.

---

# Packages

```
packages/
```

Reusable shared libraries.

Example:

```text
packages/

ui/

types/

config/

sdk/

logger/

events/

prompts/

design-system/

shared/
```

Packages should never contain business logic.

---

# Database

```
database/
```

Contains:

```text
database/

migrations/

seeds/

schema/

views/

functions/
```

Database structure is version controlled.

---

# Infrastructure

```
infrastructure/
```

Contains Infrastructure as Code.

Example:

```text
infrastructure/

terraform/

cloudrun/

monitoring/

network/

storage/
```

Infrastructure changes are treated like code.

---

# Docker

```
docker/
```

Contains:

- Dockerfiles
- Docker Compose
- Local Development Images

---

# Tests

```
tests/
```

Project-wide testing.

Example:

```text
tests/

e2e/

integration/

performance/

fixtures/
```

---

# Tools

```
tools/
```

Internal engineering tools.

Example:

```text
tools/

generators/

cli/

codegen/

lint/

release/
```

---

# Scripts

```
scripts/
```

Automation scripts.

Examples:

- Build
- Release
- Database
- Backup
- Development

Scripts should be idempotent.

---

# GitHub

```
.github/
```

Contains:

- Workflows
- Templates
- Actions
- Issue Templates
- PR Templates

CI/CD belongs here.

---

# Dependency Rules

Dependencies flow in one direction.

```text
Apps

↓

Services

↓

Workers

↓

Packages

↓

Infrastructure
```

Lower layers never depend on higher layers.

---

# Import Rules

Allowed:

```
apps

↓

packages
```

Allowed:

```
services

↓

packages
```

Allowed:

```
workers

↓

packages
```

Not allowed:

```
packages

↓

apps
```

Not allowed:

```
packages

↓

workers
```

Shared libraries must remain independent.

---

# Business Modules

Inside each service:

```text
account/

opportunity/

proposal/

forecast/

meeting/

activity/

knowledge/
```

Never organize by:

```text
controllers/

models/

routes/

utils/
```

Organize by business domains.

---

# Naming Convention

Folders:

```
kebab-case
```

Files:

```
kebab-case.ts

kebab-case.py
```

Classes:

```
PascalCase
```

Variables:

```
camelCase
```

Constants:

```
UPPER_SNAKE_CASE
```

Database:

```
snake_case
```

---

# Module Template

Every business module follows the same structure.

```text
account/

api/

application/

domain/

infrastructure/

events/

workers/

tests/

README.md
```

The structure remains consistent across all modules.

---

# Shared Package Principles

Packages must be:

- Stateless
- Reusable
- Independently Testable
- Well Documented

Business rules never belong inside shared packages.

---

# Repository Rules

Every new folder requires a clear purpose.

No "misc".

No "helpers".

No "temp".

No "new".

No "backup".

Everything has a defined home.

---

# Growth Strategy

The repository should comfortably scale to:

- 100+ Packages
- 50+ Services
- 100+ Workers
- Millions of Lines of Code

without restructuring.

---

# AI Coding Rules

Before creating files, AI must ask:

- Does this already exist?
- Which module owns this?
- Is this reusable?
- Should this become a package?
- Does it violate dependency rules?

If uncertain,

ask before generating code.

---

# Repository Goals

A successful repository should allow any contributor to:

- Find code quickly.
- Understand ownership.
- Extend modules safely.
- Add new Digital Employees.
- Build new applications.
- Deploy independently.

without reorganizing existing code.

---

# Final Principle

> **"Repositories should grow by addition, not by reorganization."**