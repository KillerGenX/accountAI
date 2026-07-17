---
title: Deployment Guide
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 29 — Deployment Guide

> **"A system is only as good as its ability to run in production under stress. Architecture diagrams don't serve customers; running infrastructure does."**

---

# Purpose

This document outlines how PROJECT BRAIN is deployed, scaled, and managed in a production environment. It defines the target cloud infrastructure and the strict rules around environment variables and secrets management.

---

# 1. Target Infrastructure (Cloud Native)

We aim for a managed, scalable, containerized infrastructure. The preferred target cloud is AWS, with GCP as an acceptable alternative. We avoid raw VMs (EC2) in favor of managed orchestration to reduce DevOps overhead.

### 1.1. Application Compute
- **Frontend (Next.js):** Deployed to Vercel (preferred for optimal Next.js edge caching and image optimization) or AWS ECS (Fargate).
- **Backend API (FastAPI):** Containerized. Deployed to AWS ECS (Fargate). Configured with Application Auto Scaling based on CPU utilization (target 70%) or Request Count.
- **AI Workers (Temporal Workers):** Containerized. Deployed to AWS ECS. 
  - *Scaling Rule:* Workers must NOT be scaled based on CPU. They must be scaled based on the Temporal Task Queue depth. If 100 AI tasks are queued, we spin up more workers, even if current CPU is low.

### 1.2. State & Storage (The Stateful Layer)
- **Database (PostgreSQL + pgvector):** Managed service (AWS RDS for PostgreSQL). Multi-AZ enabled for high availability. Automated backups with a 30-day retention period.
- **Cache & Ephemeral State (Redis):** AWS ElastiCache for Redis (Cluster mode disabled for simplicity unless scaling dictates otherwise).
- **Object Storage:** AWS S3 for storing uploaded PDFs, user avatars, and generated reports.

### 1.3. Orchestration & Messaging
- **Workflow Engine (Temporal):** Temporal Cloud (SaaS) is the strongly preferred option to avoid the massive overhead of managing a self-hosted Cassandra/Elasticsearch cluster required by Temporal.
- **Event Bus (NATS):** Synadia Cloud (managed NATS JetStream) or a self-hosted lightweight 3-node cluster on AWS Fargate.

---

# 2. Configuration & Secrets Management (12-Factor App)

Strict separation between codebase and configuration is mandatory. 
**No credentials, API keys, or environment-specific configuration may ever be committed to the Git repository.**

### 2.1. Environment Variables
All configuration is injected into containers via environment variables.
- `ENVIRONMENT` (local, staging, production)
- `DATABASE_URL` (Connection string)
- `REDIS_URL`
- `NATS_URL`
- `TEMPORAL_HOST`

### 2.2. Secrets Manager
Highly sensitive data must be injected via a Secret Manager (AWS Secrets Manager or HashiCorp Vault), not just plain text environment variables in the CI/CD pipeline.
- `LLM_API_KEY_GEMINI`
- `LLM_API_KEY_OPENAI`
- `JWT_SECRET_KEY` (Used to sign/verify authentication tokens)
- `DATABASE_PASSWORD`

---

# 3. Network Security (VPC)

- **Public Subnet:** Only Load Balancers (ALB) and NAT Gateways live here.
- **Private Subnet:** The Backend API, Temporal Workers, and Redis cluster live here. They have no direct inbound internet access.
- **Isolated Data Subnet:** The RDS PostgreSQL database lives here. It only accepts connections from the Backend API and Worker security groups.

---

# 4. Disaster Recovery (DR)

- **RPO (Recovery Point Objective):** 5 minutes. (Achieved via AWS RDS Continuous Backups/WAL archiving).
- **RTO (Recovery Time Objective):** 1 hour.
- **Infrastructure as Code (IaC):** The entire infrastructure MUST be defined using Terraform or AWS CDK. In the event of a total region failure, we should be able to spin up the entire cluster in a new region by running a single command and restoring the database snapshot.
