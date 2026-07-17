---
title: Feature Backlog & Prioritization
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 34 — Feature Backlog & Prioritization

> **"Strategy is deciding what not to do. A backlog is a graveyard of good ideas that aren't important enough right now."**

---

# Purpose

This document captures features that are valuable but out of scope for the immediate sprint or MVP. It prevents scope creep while ensuring good ideas are not lost. Features here are ranked by Business Value vs. Implementation Effort.

---

# Prioritization Matrix (RICE Framework)

We use a simplified RICE (Reach, Impact, Confidence, Effort) model to prioritize features.
- **Impact (1-5):** How much does this move the needle for the Account Manager?
- **Effort (1-5):** How many weeks of engineering time? (5 = >1 month).

---

# 1. High Priority (Candidates for V2 / Next Sprint)

| Feature Name | Impact | Effort | Description |
|---|---|---|---|
| **HubSpot / Salesforce Bi-directional Sync** | 5 | 4 | Pull existing accounts from CRM, and push AI-generated insights back into the CRM's custom fields. |
| **Email Thread Sentiment Analysis** | 4 | 2 | Ingest raw email threads and flag "Risk of Churn" or "Ready to Buy" on the dashboard. |
| **Competitor Battlecard Generator** | 4 | 3 | Given a competitor name, AI scrapes their current pricing/features and generates a PDF battlecard for the AM. |

---

# 2. Medium Priority (Nice to Have)

| Feature Name | Impact | Effort | Description |
|---|---|---|---|
| **Voice Note Ingestion** | 3 | 2 | AM records a 2-minute voice note on WhatsApp after a meeting; system transcribes, structures, and updates the deal state. |
| **Automated Org Chart Builder** | 3 | 3 | AI infers the reporting structure of a target company based on LinkedIn data and draws a visual Org Chart. |
| **Dark Mode / Theming** | 2 | 1 | Complete the Tailwind configuration for a seamless dark mode experience. |

---

# 3. Low Priority (Icebox / Deferred)

*Do not build these until Phase 4 or unless a massive enterprise customer demands them.*

| Feature Name | Impact | Effort | Description |
|---|---|---|---|
| **Fully Autonomous Outreach** | 2 | 5 | AI actually sends emails on behalf of the AM without approval. (Too much brand risk right now). |
| **Custom LLM Fine-Tuning** | 2 | 5 | Training our own open-source models (Llama 3) on internal data instead of using RAG. (Too expensive, RAG is sufficient for now). |
| **Mobile App (iOS/Android)** | 1 | 4 | Building a native mobile app. (Responsive web via Tailwind is perfectly fine for the MVP). |

---

# How to use this Backlog

When an AI Agent or Developer thinks of a "cool feature" while building the MVP (e.g., "Oh, we should add WebSocket chat so users can talk to the AI!"), **STOP**. 

Do not implement it. Add it to this backlog document under "Medium Priority", and return to building the strict MVP defined in `35_MVP.md`.
