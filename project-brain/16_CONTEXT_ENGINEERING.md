---
title: Context Engineering
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 16 — Context Engineering

> **"A language model is only as good as the context it receives. Context engineering is the most important engineering discipline in an AI-native product."**

---

# Purpose

Context Engineering is the discipline of designing, assembling, and managing the information that a Digital Employee receives before it starts working.

It is not prompt engineering.

Prompt engineering asks: *"How do I word this instruction?"*

Context engineering asks: *"What information does this employee need to do excellent work, and how do I make sure it always has exactly that information — no more, no less?"*

This document defines:
- What context is
- How context is structured
- How context is assembled for each task
- How to prevent hallucination through context design
- The Minimum Viable Context principle

---

# What Is Context?

For a Digital Employee, context is everything the AI reads before it produces output.

Context consists of multiple layers:

```
┌────────────────────────────────────────┐
│ 1. SYSTEM CONTEXT                      │
│    Who the employee is                 │
│    What its mission is                 │
│    What rules it must follow           │
├────────────────────────────────────────┤
│ 2. TASK CONTEXT                        │
│    What task it must perform           │
│    What specific inputs it received    │
│    What format the output must be      │
├────────────────────────────────────────┤
│ 3. KNOWLEDGE CONTEXT                   │
│    Relevant workspace knowledge        │
│    Relevant platform knowledge         │
│    Personal knowledge (if applicable)  │
├────────────────────────────────────────┤
│ 4. MEMORY CONTEXT                      │
│    Past results for this account       │
│    Past feedback from Account Manager  │
│    Historical patterns                 │
├────────────────────────────────────────┤
│ 5. CONSTRAINT CONTEXT                  │
│    Output format requirements          │
│    Confidence scoring rules            │
│    Escalation triggers                 │
└────────────────────────────────────────┘
```

All five layers together form the **complete context** for a Digital Employee task.

---

# The Minimum Viable Context Principle

> **Every Digital Employee must receive exactly enough context to do excellent work — never more, never less.**

Too little context → hallucination, generic output, wrong assumptions.

Too much context → the employee loses focus, performance degrades, costs increase.

The goal is precision.

## Context Budget

Every Digital Employee has a **context token budget**.

This budget is the maximum number of tokens that can be consumed by context before the employee produces output.

| Employee Type | Context Budget |
|---|---|
| Lightweight (scoring, classification) | 2,000–5,000 tokens |
| Standard (research, summarization) | 8,000–20,000 tokens |
| Complex (proposal writing, analysis) | 20,000–50,000 tokens |

When assembled context exceeds budget: apply **Context Compression** (see below).

---

# Context Layer 1 — System Context

The System Context defines the employee's identity, mission, and operating rules.

It is **static** — the same for every task this employee performs.

## Structure

```
You are the [Employee Name], part of the [Department Name] at [Company Name].

Your mission: [One-sentence mission from employee template]

You operate under the following rules:
1. Every response must include a confidence score (0.0 to 1.0)
2. Every claim must cite its source
3. If confidence is below 0.4, you must flag this explicitly
4. You never invent information — you explicitly state when information is unavailable
5. You respond in the exact output format specified in this context
6. [Employee-specific rules]

Your output will be reviewed by a human Account Manager.
Act accordingly.
```

## Rules

- System Context is versioned with the employee
- Changes to System Context require employee version increment
- System Context is never truncated regardless of context budget

---

# Context Layer 2 — Task Context

The Task Context defines what the employee must do for this specific invocation.

It is **dynamic** — different for every task.

## Structure

```
## Current Task

Task ID: [UUID]
Triggered by: [Event or schedule]
Workspace: [workspace_id]

## Input Data

[Structured input data relevant to this task]
Example for Company Research:
  Company Name: PT Pertamina
  Company URL: https://pertamina.com
  Industry Hint: Energy, Oil and Gas

## Required Output

Produce a structured JSON response matching this exact schema:
[Output schema from employee template]

## Output Requirements

- Length: [max words or tokens]
- Format: [JSON / plain text / markdown]
- Confidence: Required on every output
- Sources: Required — list all URLs consulted
```

## Rules

- Task Context must never contain data from other workspaces
- Task Context must include workspace_id for every task
- Task Context must specify exact output format

---

# Context Layer 3 — Knowledge Context

Knowledge Context provides the employee with relevant workspace and platform knowledge before it starts work.

## Retrieval Process

```
Step 1: Generate search queries from task context
    Example: Task = "research PT Pertamina"
    Queries:
      - "energy oil gas company sales approach"
      - "enterprise connectivity solutions use cases"
      - "PT Pertamina industry segment"

Step 2: Query Knowledge Hub (semantic search)
    Layer 2 (Workspace): workspace_id filter mandatory
    Layer 1 (Platform): no filter needed
    Limit: top 3 results per query

Step 3: Rank and deduplicate results

Step 4: Include top K articles in context
    K = determined by remaining context budget
    Each article: title + relevant excerpt (not full article)
```

## Context Format

```
## Relevant Knowledge

[Article 1 Title]
Source: Knowledge Hub — Layer [1/2]
Excerpt: [Most relevant 2–3 paragraphs]

[Article 2 Title]
...
```

## Rules

- Only include knowledge articles with relevance score > 0.7
- Never include Layer 3 (personal) knowledge from other users
- Include source attribution for every article
- Truncate long articles to most relevant excerpt

---

# Context Layer 4 — Memory Context

Memory Context loads relevant past results and feedback for this account or task type.

## Memory Types Loaded

| Memory Type | What Is Loaded | Storage |
|---|---|---|
| Episodic | Past research results for this account | PostgreSQL |
| Semantic | Embeddings of past account intelligence | pgvector |
| Feedback | AM's past approval/rejection patterns for this employee | PostgreSQL |

## Retrieval Process

```
Step 1: Query episodic memory
    SELECT last 3 task results for this account_id AND this employee_id
    Include: result summary, confidence, AM feedback

Step 2: Query semantic memory
    Find similar past results via vector similarity
    Limit: top 2 results

Step 3: Load feedback patterns
    What has AM accepted or rejected from this employee recently?
    Limit: last 10 feedback records

Step 4: Format as context
```

## Context Format

```
## Relevant Past Work

Past Research (2025-06-15, Confidence: 0.82):
  [Summary of previous research result]
  AM Feedback: Approved / Note: "Contact name was incorrect"

Similar Account Research (2025-07-01):
  [Summary of research for a similar company]
```

## Rules

- Memory context is workspace-scoped (never loads from other workspaces)
- Memory context is account-scoped (only loads memory for relevant account)
- Negative feedback must always be included (so employee learns from mistakes)
- Memory context is optional — if no relevant memory exists, skip this layer

---

# Context Layer 5 — Constraint Context

Constraint Context defines explicit rules, format requirements, and escalation triggers.

## Structure

```
## Output Constraints

Confidence Scoring:
  - Score your overall confidence from 0.0 to 1.0
  - If confidence < 0.4: prepend output with [LOW CONFIDENCE]
  - If confidence < 0.4: this response will require mandatory human review

Source Requirements:
  - Every factual claim must cite its source URL
  - If no source is available, state: "Source not found — manual verification recommended"
  - Do not invent sources

Escalation Triggers:
  - If you cannot complete this task: output {"status": "failed", "reason": "[explain why]"}
  - Do not attempt to produce partial output for critical fields
  - [Employee-specific escalation rules]

Output Format:
  [Exact JSON schema or structured format the employee must follow]
```

---

# Context Assembly Pipeline

For every task, context is assembled in this order:

```
1. Load System Context (static, from employee definition)
        ↓
2. Build Task Context (from incoming event/request data)
        ↓
3. Query Knowledge Context (semantic search against Knowledge Hub)
        ↓
4. Load Memory Context (query past results and feedback)
        ↓
5. Add Constraint Context (static, from employee definition)
        ↓
6. Measure total token count
        ↓
7. If over budget: apply Context Compression
        ↓
8. Final assembled context → LLM call
```

---

# Context Compression

When assembled context exceeds the employee's token budget:

## Compression Strategies (applied in order)

**Strategy 1: Truncate Memory Context**
Reduce to last 1 episodic result only.

**Strategy 2: Reduce Knowledge Context**
Reduce from top 3 to top 1 knowledge article.

**Strategy 3: Summarize Knowledge Articles**
Further compress knowledge excerpts.

**Strategy 4: Truncate Task Input**
If input data is long (e.g., long company description), truncate to first 1000 tokens.

**Never truncate:**
- System Context
- Constraint Context
- Core task parameters (workspace_id, account_id, task type)

---

# Anti-Hallucination by Design

Context Engineering is the primary defense against hallucination.

## Rules

**Rule 1: Ground every fact in provided context.**
The System Context must instruct the employee: "Only state facts that appear in the context or are retrieved from provided tools. Never infer or guess."

**Rule 2: Make unavailability explicit.**
When information is not available, the employee must state: "Not found in available sources." Not guess.

**Rule 3: Confidence gates human exposure.**
Outputs below 0.4 confidence do not display to the Account Manager without explicit escalation. They go to Digital Workforce Console for review.

**Rule 4: Sources are mandatory.**
If an employee cannot cite a source for a claim, it must not make that claim.

**Rule 5: Workspace isolation in context.**
No context assembly process ever loads data from a different workspace_id. This is enforced in the context assembly code, not just in the prompt.

---

# Context Templates by Employee Type

## Template: Research Employee

```
Budget: 15,000 tokens
System Context: 1,000 tokens (static)
Task Context: 500 tokens
Knowledge Context: 3,000 tokens (top 3 articles)
Memory Context: 2,000 tokens (past 2 results + feedback)
Constraint Context: 500 tokens
Remaining for LLM reasoning: ~8,000 tokens
```

## Template: Scoring Employee

```
Budget: 5,000 tokens
System Context: 800 tokens (static)
Task Context: 1,000 tokens (account data + signals)
Knowledge Context: 1,000 tokens (scoring criteria)
Memory Context: 500 tokens (past scores + feedback)
Constraint Context: 300 tokens
Remaining for LLM reasoning: ~1,400 tokens
```

## Template: Proposal Employee

```
Budget: 40,000 tokens
System Context: 1,500 tokens (static)
Task Context: 3,000 tokens (account + opportunity data)
Knowledge Context: 15,000 tokens (product catalog, templates)
Memory Context: 3,000 tokens (past proposals + feedback)
Constraint Context: 1,000 tokens
Remaining for LLM reasoning: ~16,500 tokens
```

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `13_DIGITAL_EMPLOYEE_TEMPLATE.md` | Section 4 (Context Requirements) uses this framework |
| `17_MEMORY_ARCHITECTURE.md` | Memory Context layer sources from here |
| `knowledge-hub PRD` | Knowledge Context queries this |
| `04_AI_CONSTITUTION.md` | Constraint Context enforces AI Constitution rules |

---

# Final Principle

> **"You cannot write a better prompt than the one that has the right context.**
>
> **Context Engineering is not about writing prompts.**
>
> **It is about making sure the AI never has to guess."**
