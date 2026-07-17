---
title: Tool Architecture
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 18 — Tool Architecture

> **"A Digital Employee without tools is a thinker. A Digital Employee with the right tools is a worker."**

---

# Purpose

Tools are the capabilities that Digital Employees use to interact with the world beyond their own reasoning.

Without tools, a Digital Employee can only generate text based on what it already knows.

With tools, it can:
- Search the web for current information
- Query the database for account data
- Write results to the database
- Publish events to NATS
- Call the Knowledge Hub
- Call external APIs

This document defines every tool available to Digital Employees, how they work, what permissions are required, and how failures are handled.

---

# Tool Design Principles

## 1. Least Privilege

Every Digital Employee only has access to tools it actually needs.

No employee has write access to tables it does not own.

No employee can publish events on behalf of another employee.

## 2. Explicit Over Implicit

Every tool call is logged. Every tool result is auditable.

A Digital Employee cannot use a tool silently.

## 3. Fail Safe

Every tool must handle failure gracefully.

A failed tool call must never cause a task to produce incorrect output.

A failed tool call must trigger explicit error handling (per SOP error paths).

## 4. Cost Awareness

Every tool call has a cost (latency, API credits, or both).

Tools must be called efficiently — not excessively.

---

# Tool Registry

## Category 1 — Research Tools

### T-RES-001: Web Search

**Purpose:** Search the public internet for information about companies, people, and events.

**Provider:** Google Search API / Perplexity API / Serper API

**Input:**
```json
{
  "query": "string",
  "num_results": "integer (default: 5, max: 10)",
  "date_filter": "string (optional: 'past_month', 'past_year')"
}
```

**Output:**
```json
{
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "published_date": "ISO8601 | null"
    }
  ],
  "total_results": "integer"
}
```

**Permissions:** Company Research Employee, Buying Signal Employee, Industry Research Employee, News Employee

**Rate limit:** 100 calls/hour per workspace

**Cost:** $0.001 per call (estimated)

**Failure handling:** If API unavailable → retry 3x with 10s backoff → if all fail, use cached results (Redis, 24h TTL) → if no cache, return empty results

---

### T-RES-002: Web Page Reader

**Purpose:** Read the full text content of a specific URL.

**Provider:** Internal HTTP client with HTML extraction

**Input:**
```json
{
  "url": "string",
  "max_length": "integer (default: 5000 chars)"
}
```

**Output:**
```json
{
  "url": "string",
  "title": "string",
  "content": "string",
  "fetched_at": "ISO8601"
}
```

**Permissions:** Company Research Employee, News Employee

**Rate limit:** 50 calls/hour per workspace

**Cost:** $0 (internal HTTP call)

**Failure handling:** If URL unreachable → return error with URL and reason

---

## Category 2 — Database Tools

### T-DB-001: Account Query

**Purpose:** Query account data from the database.

**Scope:** Read-only. workspace_id filter mandatory.

**Input:**
```json
{
  "workspace_id": "UUID",
  "account_id": "UUID (optional)",
  "filter": "object (optional WHERE clauses)"
}
```

**Output:** Account record(s) as JSON

**Permissions:** All employees (read access to own workspace accounts)

**Rate limit:** None (internal database call)

**Cost:** Database read cost (negligible)

---

### T-DB-002: Intelligence Write

**Purpose:** Write intelligence results to the database.

**Scope:** Write to `account_intelligence` table only. workspace_id mandatory.

**Input:**
```json
{
  "workspace_id": "UUID",
  "account_id": "UUID",
  "intel_type": "string",
  "content": "string",
  "source_url": "string",
  "confidence": "float",
  "generated_by": "string (employee_id)"
}
```

**Output:** Written record ID

**Permissions:** Account Intelligence Employee, Contact Intelligence Employee

**Rate limit:** None

---

### T-DB-003: Signal Write

**Purpose:** Write buying signals to the database.

**Scope:** Write to `buying_signals` table only.

**Input:**
```json
{
  "workspace_id": "UUID",
  "account_id": "UUID | null",
  "candidate_id": "UUID | null",
  "signal_type": "string",
  "signal_title": "string",
  "signal_summary": "string",
  "signal_date": "ISO8601",
  "source_url": "string",
  "confidence_score": "float"
}
```

**Permissions:** Buying Signal Employee

---

### T-DB-004: Result Write

**Purpose:** Write task results to Episodic Memory (`ai_results` table).

**Scope:** All employees write their own results here.

**Input:** TaskResult object (workspace_id, employee_id, output, confidence, sources, etc.)

**Permissions:** All employees (write own results only)

---

## Category 3 — Knowledge Tools

### T-KW-001: Knowledge Search

**Purpose:** Search the Knowledge Hub for relevant articles.

**Scope:** Searches Layer 1 (global) and Layer 2 (workspace) only. Layer 3 (personal) only accessible by the specific user's tasks.

**Input:**
```json
{
  "workspace_id": "UUID",
  "query": "string",
  "layers": "[1, 2]",
  "limit": "integer (default: 3, max: 10)"
}
```

**Output:**
```json
{
  "results": [
    {
      "article_id": "UUID",
      "title": "string",
      "layer": "integer",
      "relevance_score": "float",
      "excerpt": "string",
      "source": "string"
    }
  ]
}
```

**Permissions:** All employees

**Rate limit:** None (internal pgvector query)

---

## Category 4 — Event Tools

### T-EVT-001: Event Publisher

**Purpose:** Publish NATS events on behalf of a Digital Employee.

**Scope:** Each employee can only publish events listed in its template's "Events Published" section.

**Input:**
```json
{
  "subject": "string (nats subject)",
  "event_type": "string (PascalCase event name)",
  "payload": "object",
  "workspace_id": "UUID",
  "correlation_id": "UUID"
}
```

**Output:** Publish acknowledgement

**Permissions:** Restricted per employee (whitelist of allowed subjects per employee)

**Failure handling:** Retry 3x with 5s backoff → if all fail, log critical error → alert via monitoring

---

## Category 5 — Memory Tools

### T-MEM-001: Semantic Memory Write

**Purpose:** Store embeddings in pgvector for future similarity search.

**Input:**
```json
{
  "workspace_id": "UUID",
  "account_id": "UUID | null",
  "employee_id": "string",
  "content": "string",
  "content_type": "string"
}
```

**Permissions:** Company Research Employee, Account Intelligence Employee, Meeting Employee, Knowledge Indexing Employee

---

### T-MEM-002: Semantic Memory Search

**Purpose:** Find similar past results via vector similarity.

**Input:**
```json
{
  "workspace_id": "UUID",
  "query": "string",
  "content_type": "string (optional filter)",
  "limit": "integer (default: 2)"
}
```

**Permissions:** All employees

---

## Category 6 — LLM Tools

### T-LLM-001: LLM Completion

**Purpose:** Call the configured LLM to generate structured or free-text output.

**Provider:** Configured via AI Gateway (per `06_SYSTEM_ARCHITECTURE.md`)

**Input:**
```json
{
  "messages": "[{role, content}]",
  "model": "string (default: workspace configured model)",
  "temperature": "float (default: 0.3 for factual, 0.7 for creative)",
  "max_tokens": "integer",
  "response_format": "json_object | text"
}
```

**Output:** LLM response + token usage metadata

**Cost:** Varies by model. Tracked per call in `ai_task_log`.

**Permissions:** All employees (via AI Gateway only — no direct LLM calls allowed)

**Model options:**
| Use Case | Model | Reason |
|---|---|---|
| Research and factual extraction | Gemini 1.5 Pro / GPT-4o | High accuracy |
| Summarization and scoring | Gemini 1.5 Flash / GPT-4o Mini | Cost efficient |
| Proposal writing | Gemini 1.5 Pro | Longer context window |
| Embeddings | text-embedding-3-small | Cost efficient, good quality |

---

# Tool Permission Matrix

| Tool | Research Employee | Buying Signal | Account Intelligence | Contact Intelligence | Knowledge Indexing | Dashboard Priority | Proposal Employee |
|---|---|---|---|---|---|---|---|
| T-RES-001 Web Search | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| T-RES-002 Web Reader | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| T-DB-001 Account Query | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| T-DB-002 Intelligence Write | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| T-DB-003 Signal Write | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| T-DB-004 Result Write | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| T-KW-001 Knowledge Search | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| T-EVT-001 Event Publisher | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| T-MEM-001 Semantic Write | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| T-MEM-002 Semantic Search | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| T-LLM-001 LLM Completion | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

# Tool Registration Process

When adding a new tool:

1. Assign tool ID: T-[CATEGORY]-[NUMBER]
2. Define input and output schemas
3. Define which employees have permission
4. Implement with full error handling
5. Add to this registry
6. Add rate limiting and cost tracking
7. Test with each permitted employee

---

# Tool Failure Handling Standard

All tools must implement:

```python
class ToolResult:
    success: bool
    data: dict | None
    error: str | None
    error_type: str | None  # timeout, rate_limit, not_found, server_error
    retry_recommended: bool
    cost_usd: float

async def call_tool(tool_id: str, input: dict) -> ToolResult:
    try:
        result = await execute_tool(tool_id, input)
        log_tool_call(tool_id, input, result)
        return ToolResult(success=True, data=result, cost_usd=calculate_cost(tool_id, result))
    except TimeoutError:
        return ToolResult(success=False, error="Timeout", error_type="timeout", retry_recommended=True)
    except RateLimitError:
        return ToolResult(success=False, error="Rate limited", error_type="rate_limit", retry_recommended=True)
    except Exception as e:
        log_error(tool_id, e)
        return ToolResult(success=False, error=str(e), error_type="server_error", retry_recommended=False)
```

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `13_DIGITAL_EMPLOYEE_TEMPLATE.md` | Section 6 (Tools) lists tools per employee |
| `15_STANDARD_OPERATING_PROCEDURES.md` | Each SOP step specifies which tool is used |
| `06_SYSTEM_ARCHITECTURE.md` | AI Gateway handles LLM routing |
| `04_AI_CONSTITUTION.md` | All tool calls must be auditable and traceable |

---

# Final Principle

> **"Tools are not features.**
>
> **Tools are the hands of a Digital Employee.**
>
> **Give them the right tools, with the right permissions,**
>
> **and they will do excellent work."**
