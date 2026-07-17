---
title: System Modules Index
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 33 — System Modules Index

> **"A complex system that works is invariably found to have evolved from a simple system that worked. Isolate features into strict domains."**

---

# Purpose

This document serves as the master index of all functional modules within PROJECT BRAIN. By defining strict module boundaries, we prevent monolithic spaghetti code. Each module should theoretically be capable of being extracted into its own microservice if required.

---

# 1. Core Platform Modules (Foundation)

These modules must exist before any AI logic can function.

### 1.1. Identity & Access Management (IAM)
- **Domain:** User authentication, JWT issuance, Workspace (Tenant) provisioning.
- **Key Entities:** User, Workspace, Role, Session.
- **Responsibilities:** Enforces Row-Level Security (RLS) contexts and handles invitations/RBAC.

### 1.2. The Digital Workforce Console (The Brain Center)
- **Domain:** The primary UI where humans and AI interact.
- **Key Entities:** Task, AI Message, Human Feedback, Approval Workflow.
- **Responsibilities:** Acts as the "Inbox" where Account Managers review AI-generated reports and click "Approve", "Reject", or "Regenerate".

### 1.3. Knowledge Hub (The Memory)
- **Domain:** Ingestion and retrieval of internal unstructured data.
- **Key Entities:** Document, Vector Chunk, Tag.
- **Responsibilities:** Parses PDFs/Word docs, generates embeddings (`pgvector`), and exposes a semantic search API for the AI Workers.

---

# 2. Sales Intelligence Modules (The Business Value)

These modules define the actual domain of Enterprise Sales.

### 2.1. Account Discovery & Intelligence
- **Domain:** Finding and profiling companies.
- **Key Entities:** Account, Contact, Tech Stack, Signal (e.g., funding rounds, executive changes).
- **Responsibilities:** Triggers background web scrapers, queries LinkedIn/Crunchbase APIs, and synthesizes 50 pages of raw data into a 2-page executive summary.

### 2.2. Opportunity Management (Pipeline)
- **Domain:** Tracking deals through the sales funnel.
- **Key Entities:** Opportunity, Deal Stage, Win Probability Score.
- **Responsibilities:** Replaces traditional CRM views with an AI-augmented pipeline that flags deals "At Risk" based on sentiment analysis of recent emails.

### 2.3. Meeting & Activity Intelligence
- **Domain:** Processing human interactions.
- **Key Entities:** Meeting Transcript, Email Thread, Action Item.
- **Responsibilities:** Parses Zoom/Teams transcripts, extracts commitments made by the Account Manager, and auto-generates follow-up emails.

### 2.4. Proposal Studio (Generative Output)
- **Domain:** Creating tangible artifacts for clients.
- **Key Entities:** Proposal Template, Generated Draft.
- **Responsibilities:** Uses multi-agent orchestration (one agent writes the technical architecture, another writes the pricing, a third reviews for compliance) to output a complete `.docx` or `.pdf` proposal.

---

# Architecture Rule: Cross-Module Communication

Modules must NOT perform SQL `JOIN`s directly into the tables of another module if they are conceptually separated domains. 

- **Good:** The `Proposal Studio` queries the `Account Intelligence` API service internally to fetch the account profile before generating a document.
- **Bad:** The `Proposal Studio` repository writes a raw SQL query that joins `proposals` with `account_signals` and `user_sessions`. 

This strict separation guarantees that when the `Account Intelligence` database schema inevitably changes, it doesn't break the `Proposal Studio`.
