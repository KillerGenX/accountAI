---
title: Release & Deployment Plan
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 36 — Release & Deployment Plan

> **"Deploying code should be boring. If deployments are stressful, your architecture or your automation is broken."**

---

# Purpose

This document outlines how we move code from the development environment to the hands of the users. It defines the release cycles, rollback strategies, and the philosophy of feature flagging.

---

# 1. The Release Cycle

We do not do "Big Bang" releases. We deploy small, incremental changes continuously.

### Continuous Deployment (CD) to Staging
- Every Pull Request merged into the `main` branch is automatically built, containerized, and deployed to the Staging environment.
- Staging always represents the absolute latest version of the code.

### Scheduled Releases to Production
- While we have the capability to deploy to Production continuously, for the MVP and V2 phases, we will batch releases twice a week (e.g., Tuesdays and Thursdays at 10:00 AM).
- **Rule:** Never deploy to Production on a Friday afternoon. If something breaks, weekend recovery is painful and expensive.

---

# 2. Deployment Strategies

### Blue/Green Deployments
We use a Blue/Green deployment model via our container orchestrator (AWS ECS/Kubernetes).
1. The new containers (Green) are spun up alongside the old containers (Blue).
2. The Load Balancer runs a health check against the Green containers (`/api/v1/health`).
3. Once Green is healthy, the Load Balancer switches 100% of the traffic to Green.
4. Blue is kept alive for 15 minutes as a fallback, then terminated.

### Database Migrations Safety
Schema changes are the most dangerous part of a release.
- All migrations must be backwards-compatible (see `24_DATABASE_SCHEMA_GUIDE.md`).
- The migration runs *before* the Blue/Green switch. Therefore, the old code (Blue) must be able to run against the new database schema without crashing.

---

# 3. Feature Flagging (LaunchDarkly / PostHog)

To decouple *Deployments* (putting code on a server) from *Releases* (exposing features to users), we use Feature Flags extensively.

1. **Incomplete Features:** If a developer merges code for the "Proposal Studio" but it is only 50% done, it must be wrapped in a feature flag (e.g., `enable-proposal-studio: false`). It can safely go to production without breaking the user experience.
2. **Canary Testing:** When a new AI model (e.g., Gemini 2.0) is released, we can use a feature flag to route only 10% of our internal users to the new model to measure cost and hallucination rates before a full rollout.
3. **Kill Switches:** If an AI prompt starts generating catastrophic errors in production, we can instantly toggle the feature flag off in the dashboard, reverting to the old logic without needing to recompile or redeploy code.

---

# 4. Rollback Strategy

If a critical bug (P0) escapes to Production:

1. **First Option: Feature Flag Toggle.** If the bug is isolated to a new feature, turn off the feature flag. Recovery time: 5 seconds.
2. **Second Option: Revert and Redeploy.** If the bug is systemic, revert the Git commit in the `main` branch and let the CI/CD pipeline push the hotfix. Recovery time: 10 minutes.
3. **Third Option: Container Rollback.** Instruct the orchestrator to instantly roll back to the previous known-good Docker image tag. Recovery time: 2 minutes.

**Rule:** NEVER attempt to roll back a database migration automatically. Database downgrades often lead to massive data loss. If a schema change caused the bug, you must "Roll Forward" by writing a new migration that fixes the issue.
