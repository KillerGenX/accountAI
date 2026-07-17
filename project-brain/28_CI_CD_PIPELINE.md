---
title: CI/CD Pipeline
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 28 — CI/CD Pipeline

> **"If it's not automated, it's broken. A human should never deploy code from their laptop to production."**

---

# Purpose

This document outlines the Continuous Integration and Continuous Deployment (CI/CD) strategy for PROJECT BRAIN. The pipeline is the gatekeeper of production. It ensures that no untested, unformatted, or insecure code ever reaches our users.

---

# 1. CI Pipeline (Continuous Integration)

The CI pipeline runs on every Pull Request (PR) targeting the `main` branch. A PR **cannot be merged** unless all CI checks pass (Status Checks required).

We use **GitHub Actions** as our CI/CD runner.

## Stage 1: Static Analysis & Linting (Fail Fast)
These checks run first because they are fast and catch 80% of silly mistakes.
- **Frontend:**
  - `npm run lint` (ESLint)
  - `npm run format:check` (Prettier)
  - `npm run type-check` (TypeScript compiler running `tsc --noEmit`)
- **Backend:**
  - `ruff check .` (Extremely fast Python linter replacing Flake8/Isort)
  - `black --check .` (Code formatter)
  - `mypy .` (Strict type checking)

## Stage 2: Security Scans
- **Dependency Audit:** Runs `npm audit` and `pip-audit` or `safety` to check for known CVEs in our dependency tree.
- **Secret Scanning:** Scans the diff for accidentally committed API keys, AWS credentials, or JWT secrets (using tools like TruffleHog or GitHub Advanced Security).

## Stage 3: Automated Testing
- **Backend Tests:** Spins up an ephemeral PostgreSQL instance via a GitHub Actions service container, then runs `pytest`.
- **Frontend Tests:** Runs Jest for component tests.

## Stage 4: Build Verification
- **Next.js Build:** Runs `npm run build` to ensure the frontend compiles successfully (catches deep React Server Component rendering errors).

---

# 2. CD Pipeline (Continuous Deployment)

The CD pipeline triggers automatically when code is pushed or merged into the `main` branch.

## Stage 1: Containerization
- The pipeline builds Docker images for three distinct services:
  1. `project-brain-frontend` (Next.js)
  2. `project-brain-api` (FastAPI)
  3. `project-brain-worker` (Temporal Worker)
- Images are tagged with the Git SHA (e.g., `sha-a1b2c3d`) and pushed to the Container Registry (AWS ECR or GCP GCR).

## Stage 2: Database Migrations
- The pipeline connects to the target environment's database (Staging or Production).
- It runs `alembic upgrade head`. 
- **Safety Gate:** If the migration fails, the pipeline aborts immediately, and the new containers are NOT deployed.

## Stage 3: Rolling Deployment
- The pipeline updates the orchestrator (Kubernetes deployment or AWS ECS task definition) with the new image tags.
- The orchestrator performs a **Rolling Update**: It spins up the new containers, waits for them to pass health checks (`/api/v1/health`), and only then drains traffic from the old containers. This ensures **Zero-Downtime Deployments**.

---

# 3. Environment Strategy

- **Local:** Developer's laptop. Spun up via `docker-compose up`.
- **Staging:** An exact replica of Production (minus the data volume). Deployed automatically on every merge to `main`. Used for final QA, product owner sign-off, and running the nightly AI Evaluation Suite.
- **Production:** The live environment. 
  - *Trigger:* Deployed by explicitly creating a GitHub Release or Tag (e.g., `v1.2.0`). This creates a manual gate for production deployments.
