---
title: Observability
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 30 — Observability

> **"If you can't see it, you can't fix it. If you can't measure it, you can't improve it. In an AI platform, a silent failure is worse than a crash."**

---

# Purpose

This document outlines how we monitor the health, performance, and behavior of PROJECT BRAIN in production. Given the non-deterministic nature of AI and the complexity of Event-Driven Architectures, observability is not optional—it is a core engineering requirement.

---

# 1. The Three Pillars of Observability

We implement the standard three pillars of observability across the entire stack.

### 1.1. Structured Logging
Plain text logs are useless for automated alerting. All logs in production MUST be output as JSON.
- **Library:** Use `structlog` in Python and a compatible JSON logger in Node.js/Next.js.
- **Mandatory Fields:** Every single log entry must include:
  - `timestamp` (ISO 8601 UTC)
  - `level` (INFO, WARN, ERROR, CRITICAL)
  - `trace_id` (Crucial for stitching requests)
  - `workspace_id` (If the operation is tenant-scoped)
  - `event` (A strict string, e.g., `llm_call_started`, `db_query_failed`)

```json
{
  "timestamp": "2026-07-17T12:05:32Z",
  "level": "INFO",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "workspace_id": "ws-12345",
  "event": "llm_call_completed",
  "model": "gemini-1.5-pro",
  "tokens_used": 1450,
  "duration_ms": 3200
}
```

### 1.2. Metrics
We track standard RED (Rate, Errors, Duration) metrics for APIs, plus AI-specific business metrics.
- **Tools:** Prometheus/Grafana or Datadog.
- **AI Specific Metrics to Track:**
  - `llm.token_usage.total` (Counter, tagged by model and workspace)
  - `llm.request.duration` (Histogram, tagged by model)
  - `worker.task.success_rate` (Gauge, tagged by Digital Employee type)
  - `tool.call.failure_rate` (Counter, tagged by tool name, e.g., `web_search`)

### 1.3. Distributed Tracing (OpenTelemetry)
Because a single user action (e.g., "Create Opportunity") might trigger an API request, a database write, an event publish to NATS, and a background AI Temporal worker, tracing is mandatory to understand the flow.
- We use **OpenTelemetry (OTel)** instrumentation.
- Every incoming HTTP request gets a unique `trace_id`.
- This `trace_id` is passed into the NATS event payload and into the Temporal Workflow context. This allows us to view a single waterfall chart showing exactly how much time was spent in the API, the DB, the message queue, and the AI LLM call.

---

# 2. Alerting Rules

Alerts must be actionable. We do not trigger pager alerts for single `404 Not Found` errors. We alert on systemic degradation.

### PagerDuty / Critical Alerts (Wake up the engineer):
- API Error Rate (`5xx`) > 5% over 5 minutes.
- Temporal Worker Queue Depth > 500 (Workers are failing to process tasks).
- Database CPU > 90% for 10 minutes.
- LLM API Error Rate > 20% (Indicates OpenAI/Gemini is down, requires manual failover).

### Slack / Warning Alerts (Investigate during business hours):
- Average LLM Latency increases by 50%.
- AI Evaluation Suite (Golden Dataset) score drops below 0.85.
- Elevated 429 (Rate Limit) errors from external APIs (e.g., Web Search tool).

---

# 3. AI-Specific Observability (Tracing Thoughts)

Debugging an AI is different from debugging code. You need to see its "thoughts."
- For every task, the full reasoning trace (`<thinking>` block from `19_REASONING_STRATEGY.md`) and the exact prompt sent to the LLM must be saved to the database (`ai_results.reasoning_trace`).
- When a user reports a "dumb" AI output, the engineer must be able to query the exact prompt, context, and reasoning trace that produced that output to understand if the failure was due to bad context, a bad prompt, or an LLM hallucination.
