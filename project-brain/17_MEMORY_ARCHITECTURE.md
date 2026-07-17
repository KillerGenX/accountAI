---
title: Memory Architecture
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 17 — Memory Architecture

> **"A Digital Employee that cannot remember is not an employee. It is a one-time tool."**

---

# Purpose

Memory is what separates a Digital Employee from a language model wrapper.

A language model has no memory between calls.

A Digital Employee accumulates knowledge over time. It remembers what it researched yesterday. It knows what the Account Manager approved last week. It gets better the longer it works.

This document defines the memory architecture that powers that continuity.

---

# Four Types of Memory

Inspired by human cognitive science and adapted for AI systems.

---

## Memory Type 1 — Working Memory

**What it is:** Temporary memory used only during a single task.

**Analogy:** A person's focus during a phone call. Exists only while the call is happening.

**Storage:** Redis (in-memory cache)

**TTL:** Task duration only — automatically expires when task completes or fails.

**What is stored:**
- Current task input and parameters
- Intermediate results between steps
- Tool call results within a single SOP execution

**Access pattern:**
```
Task starts → Load into Redis under key: task:{task_id}
Task step N → Read/write to task:{task_id}:step_N
Task ends → Delete all keys for task_id
```

**Size limit:** 10MB per task (enforced by Redis TTL and size limit)

---

## Memory Type 2 — Episodic Memory

**What it is:** Records of past task executions and their outcomes.

**Analogy:** A person's memory of specific past events. "I remember the last meeting with PT Pertamina."

**Storage:** PostgreSQL (`ai_task_log` + `ai_results` tables)

**TTL:** Permanent (no expiry — archived after 2 years)

**What is stored:**
- Task input, output, and metadata
- Confidence score per task
- Time taken and cost
- Account Manager feedback (approved/rejected/corrected)
- Employee version at time of task

**Access pattern:**
```
Before task: Query last N results for this account_id + employee_id
After task: Write result to ai_results table
After AM feedback: Update feedback field on ai_results record
```

**Schema:**
```sql
ai_results (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    employee_id     VARCHAR NOT NULL,
    employee_version VARCHAR NOT NULL,
    account_id      UUID,
    task_type       VARCHAR NOT NULL,
    input_summary   TEXT,
    output          JSONB NOT NULL,
    confidence      DECIMAL(3,2),
    sources         JSONB,
    am_feedback     VARCHAR,           -- approved, rejected, corrected
    am_feedback_note TEXT,
    processing_time_ms INTEGER,
    tokens_used     INTEGER,
    cost_usd        DECIMAL(10,6),
    created_at      TIMESTAMP
)
```

**Query pattern:** Always scoped by `workspace_id` + `account_id` + `employee_id`.

---

## Memory Type 3 — Semantic Memory

**What it is:** Embedded knowledge that enables similarity search across all past work.

**Analogy:** A person's general knowledge — not a specific memory but the ability to recognize patterns and connect ideas.

**Storage:** pgvector (vector embeddings)

**TTL:** Permanent

**What is stored:**
- Embedded company research results
- Embedded account intelligence summaries
- Embedded knowledge articles
- Embedded meeting summaries

**Access pattern:**
```
Write: After each research task, embed the result and store in pgvector
Read: Before a task, find semantically similar past results
      "Has this employee researched a company like this before?"
      Top-K nearest neighbors with cosine similarity
```

**Schema:**
```sql
semantic_memory (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    employee_id     VARCHAR,
    account_id      UUID,
    content_type    VARCHAR,           -- research, intelligence, meeting, knowledge
    content_summary TEXT,
    embedding       VECTOR(1536),      -- OpenAI ada-002 or Gemini embedding
    source_result_id UUID,             -- reference to ai_results
    created_at      TIMESTAMP
)
```

**Embedding model:** Consistent model used across all employees. Model version stored with embedding. If model changes, all embeddings must be regenerated.

---

## Memory Type 4 — Procedural Memory

**What it is:** Knowledge of how to perform tasks.

**Analogy:** A person's muscle memory — knowing how to ride a bike without thinking about it.

**Storage:** Codebase (SOPs in `15_STANDARD_OPERATING_PROCEDURES.md` + employee definitions)

**TTL:** Permanent (updated via employee version upgrade)

**What is stored:**
- Standard Operating Procedures (step-by-step task procedures)
- Decision trees and escalation policies
- System prompts (versioned with employee)

**Access pattern:**
```
Before task: Load employee SOP from employee definition (static)
During task: Follow SOP steps
After major learning: Update SOP version (manual process, requires human approval)
```

---

# Memory Access Matrix

| Employee Type | Working | Episodic | Semantic | Procedural |
|---|---|---|---|---|
| Company Research Employee | Redis | Read+Write | Read+Write | Read |
| Buying Signal Employee | Redis | Read+Write | Read | Read |
| Account Intelligence Employee | Redis | Read+Write | Read+Write | Read |
| Contact Intelligence Employee | Redis | Read+Write | Read | Read |
| Knowledge Indexing Employee | Redis | Write | Write | Read |
| Dashboard Priority Employee | Redis | Read | None | Read |
| Scoring Employee | Redis | Read+Write | None | Read |
| Meeting Employee | Redis | Write | Write | Read |
| Proposal Employee | Redis | Read+Write | Read | Read |

---

# Memory Lifecycle

## Creation

```
Task executes → Result produced
        ↓
Working Memory: Written during task, deleted at end
Episodic Memory: Written after task completes (async)
Semantic Memory: Embedding generated, written after task (async, lower priority)
Procedural Memory: Written only when SOP is updated (human action)
```

## Retrieval

```
Task begins → Context Assembly starts (per 16_CONTEXT_ENGINEERING.md)
        ↓
Episodic Memory: Query last 3 results for this account + employee
Semantic Memory: Query top 2 similar past results
Procedural Memory: Load current SOP (always)
Working Memory: Initialize empty for this task
```

## Learning Loop

```
Task result displayed to AM
        ↓
AM approves/rejects/provides feedback
        ↓
FeedbackSubmitted event published
        ↓
Episodic Memory updated: am_feedback field set
        ↓
Future context assembly: negative feedback included
Employee improves because it "remembers" what AM rejected
```

## Expiry and Archival

| Memory Type | Expiry Policy |
|---|---|
| Working | Immediate on task completion |
| Episodic | Archive after 2 years (move to cold storage) |
| Semantic | Regenerate if embedding model changes |
| Procedural | Never expires — versioned permanently |

---

# Workspace Memory Isolation

**All memory is workspace-scoped. No exceptions.**

Every query to Episodic or Semantic memory MUST include `workspace_id` as a mandatory filter.

This is enforced at:
1. The repository layer in code (SQL WHERE workspace_id = ?)
2. The vector search layer (metadata filter on workspace_id)
3. Not just in prompts — in the code itself

A Digital Employee working in Workspace A can never access, read, or be influenced by memory from Workspace B.

---

# Memory Privacy Rules

Per `04_AI_CONSTITUTION.md` and PDPA compliance:

- Personal Notes (Layer 3 Knowledge Hub) are **never** stored in Semantic Memory
- Account Manager feedback is stored in Episodic Memory but never used to train global models
- All memory is stored in tenant's own data partition
- Memory can be deleted per user request (right to erasure)

---

# Memory Implementation Guide

## Working Memory (Redis)

```python
# Key pattern
key = f"task:{task_id}:working"
step_key = f"task:{task_id}:step:{step_number}"

# Set with TTL
redis.setex(key, ttl_seconds=3600, value=json.dumps(data))

# Cleanup on task end
redis.delete(f"task:{task_id}:*")
```

## Episodic Memory (PostgreSQL)

```python
# Write after task
def save_episodic_result(result: TaskResult):
    db.execute(
        "INSERT INTO ai_results (workspace_id, employee_id, account_id, ...) VALUES (...)",
        result.to_dict()
    )

# Read before task
def get_past_results(workspace_id: UUID, account_id: UUID, employee_id: str, limit: int = 3):
    return db.query(
        "SELECT * FROM ai_results WHERE workspace_id = ? AND account_id = ? AND employee_id = ? ORDER BY created_at DESC LIMIT ?",
        workspace_id, account_id, employee_id, limit
    )
```

## Semantic Memory (pgvector)

```python
# Write embedding
def store_embedding(workspace_id: UUID, content: str, account_id: UUID, employee_id: str):
    embedding = embed(content)  # Call embedding model
    db.execute(
        "INSERT INTO semantic_memory (workspace_id, employee_id, account_id, embedding, ...) VALUES (...)",
        workspace_id, employee_id, account_id, embedding
    )

# Query similar
def find_similar(workspace_id: UUID, query: str, limit: int = 2):
    query_embedding = embed(query)
    return db.query(
        "SELECT * FROM semantic_memory WHERE workspace_id = ? ORDER BY embedding <=> ? LIMIT ?",
        workspace_id, query_embedding, limit
    )
```

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `09_DATA_ARCHITECTURE.md` | Defines storage systems used here (PostgreSQL, Redis, pgvector) |
| `16_CONTEXT_ENGINEERING.md` | Memory Context layer is built from this architecture |
| `13_DIGITAL_EMPLOYEE_TEMPLATE.md` | Section 7 (Memory) references types defined here |
| `04_AI_CONSTITUTION.md` | Memory privacy and isolation rules must comply |

---

# Final Principle

> **"Memory is what makes an employee, an employee.**
>
> **Without memory, every task starts from zero.**
>
> **With memory, every task builds on everything that came before."**
