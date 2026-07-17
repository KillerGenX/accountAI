---
title: Digital Employee Template
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 13 — Digital Employee Template

> **"Every Digital Employee must have a clear identity, a clear mission, and a clear boundary."**

---

# Purpose

This document defines the **mandatory schema** for every Digital Employee in the platform.

Every Digital Employee — without exception — must be defined using this template before it can be built, deployed, or used.

This template is the **DNA** of the Digital Workforce.

If a Digital Employee does not have a complete template, it is not ready.

If a Digital Employee's template contradicts the AI Constitution (`04_AI_CONSTITUTION.md`), the template is wrong.

---

# Why This Template Exists

Without a standard schema:

- Two developers build the same employee differently
- AI agents cannot consistently understand how an employee works
- Quality cannot be measured because expectations are undefined
- The employee cannot be improved because there is no baseline

This template solves that.

Every employee, every department, every future upgrade — all follow the same structure.

---

# The Template

Below is the complete schema that every Digital Employee definition must follow.

---

## Section 1 — Identity

```yaml
id: [unique-slug]               # Example: company-research-employee
name: [Display Name]            # Example: Company Research Employee
version: 1.0.0                  # Semantic versioning: MAJOR.MINOR.PATCH
status: active | beta | deprecated
department: [Department Name]   # From 14_DEPARTMENT_BLUEPRINT.md
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
```

**Rules:**
- `id` must be unique across all employees
- `version` increments when behavior changes significantly
- `status: deprecated` employees are never called by new workflows

---

## Section 2 — Mission

```markdown
### Mission Statement

One sentence. No more.

This employee exists to [do what] so that [business outcome].

### Scope

What this employee IS responsible for:
- [Specific responsibility 1]
- [Specific responsibility 2]

What this employee is NOT responsible for:
- [Out of scope 1]
- [Out of scope 2]
```

**Rules:**
- Mission statement must be one sentence only
- Scope must include explicit "NOT responsible for" to prevent scope creep
- Mission must directly contribute to finding or winning accounts (per `12_PRODUCT_REQUIREMENTS_DOCUMENT.md`)

---

## Section 3 — Trigger

```markdown
### Trigger Type

[ ] Event-Driven     → Employee activates when a specific NATS event arrives
[ ] Scheduled        → Employee runs on a cron schedule
[ ] On-Demand        → Employee is called directly by another employee or API
[ ] Hybrid           → Multiple trigger types

### Trigger Definition

Event-Driven:
  event_name: [EventName]       # Example: AccountCreated
  nats_subject: [subject]       # Example: account.created
  filter: [optional conditions] # Example: only if workspace_id exists

Scheduled:
  cron: [cron expression]       # Example: 0 6 * * * (daily at 06:00)
  timezone: workspace_timezone

On-Demand:
  called_by: [employee_id or api_endpoint]
```

---

## Section 4 — Context Requirements

```markdown
### Required Context

This employee REQUIRES the following context to operate:

| Context Item        | Source         | Layer  | Required/Optional |
|---------------------|----------------|--------|-------------------|
| [Context name]      | [Source]       | [1/2/3]| [R/O]            |

### Context Construction

Step 1: [Describe how context is assembled]
Step 2: [What knowledge layers are queried]
Step 3: [What memory is loaded]
Step 4: [How context is compressed if too large]

### Maximum Context Size

[Specify max token budget for this employee's context window]
```

**Rules:**
- Every required context item must have an identified source
- Context must always include: workspace_id, relevant account data if applicable
- Context must never include: data from other workspaces, personal notes from other users

---

## Section 5 — Standard Operating Procedures

```markdown
### SOP List

This employee operates under the following SOPs:

| SOP ID    | SOP Name               | Trigger Condition      |
|-----------|------------------------|------------------------|
| [ID]      | [Name]                 | [When this SOP runs]   |

### [SOP Name] — Detailed Steps

**Trigger:** [What causes this SOP to activate]

**Pre-conditions:** [What must be true before SOP starts]

Step 1: [Action]
  - Input: [What is needed]
  - Output: [What is produced]
  - Error: [What happens if this fails]

Step 2: [Action]
  ...

**Post-conditions:** [What must be true when SOP completes]

**Output:** [Final deliverable of this SOP]

**Escalation:** [What happens if SOP cannot complete]
```

**Rules:**
- Every employee must have at least one SOP
- Every SOP must have explicit error handling and escalation
- SOPs cannot assume network or data availability
- SOPs must complete within the defined time SLA

---

## Section 6 — Tools

```markdown
### Available Tools

This employee has access to the following tools:

| Tool ID             | Purpose                  | Permission Level |
|---------------------|--------------------------|------------------|
| [tool_id]           | [What it does]           | [read/write/exec]|

### Tool Usage Rules

- This employee [CAN / CANNOT] make external API calls
- This employee [CAN / CANNOT] write to database
- This employee [CAN / CANNOT] publish NATS events
- This employee [CAN / CANNOT] call other Digital Employees
```

**Tool definitions are in `18_TOOL_ARCHITECTURE.md`.**

---

## Section 7 — Memory

```markdown
### Memory Types Used

| Memory Type  | Storage     | Purpose                          | TTL         |
|--------------|-------------|----------------------------------|-------------|
| Working      | Redis       | Current task context             | Task duration |
| Episodic     | PostgreSQL  | Past task results                | Permanent |
| Semantic     | pgvector    | Knowledge and research embeddings| Permanent |
| Procedural   | Codebase    | SOPs (this document)             | Until version change |

### Memory Access Pattern

Read:  [What this employee reads from memory before starting]
Write: [What this employee writes to memory after completing]
```

**Memory types defined in `17_MEMORY_ARCHITECTURE.md`.**

---

## Section 8 — Input and Output

```markdown
### Input Schema

```json
{
  "workspace_id": "UUID",
  "account_id": "UUID | null",
  "task_type": "string",
  "payload": {
    "[field]": "[type]"
  },
  "context": {
    "triggered_by": "string",
    "correlation_id": "UUID"
  }
}
```

### Output Schema

```json
{
  "employee_id": "string",
  "version": "string",
  "task_id": "UUID",
  "workspace_id": "UUID",
  "account_id": "UUID | null",
  "status": "completed | failed | partial",
  "result": {
    "[field]": "[type]"
  },
  "metadata": {
    "confidence": 0.00,
    "reasoning": "string",
    "sources": ["url1", "url2"],
    "processing_time_ms": 0,
    "tokens_used": 0,
    "cost_usd": 0.000000,
    "generated_at": "ISO8601"
  }
}
```

**Rules from `04_AI_CONSTITUTION.md`:**
- Every output MUST include: confidence score, reasoning, sources, timestamp
- Confidence below 0.4 must trigger escalation
- Outputs must always be traceable to source

---

## Section 9 — Events

```markdown
### Events Published

| Event Name         | NATS Subject         | Condition            |
|--------------------|----------------------|----------------------|
| [EventName]        | [nats.subject]       | [When published]     |

### Events Consumed

| Event Name         | NATS Subject         | Action               |
|--------------------|----------------------|----------------------|
| [EventName]        | [nats.subject]       | [What employee does] |
```

**Event naming rules from `10_EVENT_ARCHITECTURE.md`: PascalCase, past tense.**

---

## Section 10 — Performance Contract

```markdown
### SLA

| Metric                    | Target          |
|---------------------------|-----------------|
| Task completion time      | < [X] seconds   |
| Success rate              | > [X]%          |
| Confidence score average  | > [X]           |
| Cost per task             | < USD [X]       |

### Escalation Policy

If completion time > [X] seconds: [action]
If confidence < 0.4: [action]
If error rate > [X]%: [action]
```

---

## Section 11 — Evaluation

```markdown
### Quality Dimensions

| Dimension    | Measurement Method       | Minimum Acceptable |
|--------------|--------------------------|--------------------|
| Accuracy     | Human feedback rating    | > 4/5              |
| Relevance    | Acceptance rate by AM    | > 60%              |
| Timeliness   | SLA compliance           | > 99%              |
| Cost         | Cost per task            | Within budget      |

### Evaluation Cadence

- Weekly: cost and SLA metrics (automated)
- Monthly: accuracy and relevance review (human + AI)
- Quarterly: full employee performance review
```

**Full evaluation framework in `20_AI_EVALUATION.md`.**

---

## Section 12 — Version History

```markdown
### Changelog

| Version | Date       | Changes                    | Changed By |
|---------|------------|----------------------------|------------|
| 1.0.0   | YYYY-MM-DD | Initial version            | [Author]   |

### Upgrade Path

v1.0.0 → v2.0.0:
  Breaking changes: [list]
  Migration steps: [list]
  Deprecation date for v1.0.0: [date]
```

---

# Template Validation Checklist

Before a Digital Employee is considered complete, verify:

```
[ ] Identity: id, name, version, department all filled
[ ] Mission: one-sentence mission + scope boundaries defined
[ ] Trigger: trigger type and definition complete
[ ] Context: all required context items have sources
[ ] SOP: at least one complete SOP with error handling
[ ] Tools: all tools listed with permission levels
[ ] Memory: all memory types documented
[ ] Input/Output: schemas match AI Constitution requirements
[ ] Events: all published and consumed events listed
[ ] SLA: all performance targets defined
[ ] Evaluation: quality dimensions and cadence set
[ ] Version: changelog initialized
```

A Digital Employee with any unchecked item above is **not production-ready.**

---

# Example: Applying This Template

See the Digital Employees defined in the PRDs folder:

- `PRDs/account-discovery.md` — Company Research Employee, Buying Signal Employee
- `PRDs/account-intelligence.md` — Account Intelligence Employee

Each PRD's "How AI Helps" section is the summary. The full template definition for each employee lives in their dedicated employee specification file under:

```
project-brain/
└── digital-employees/
    ├── company-research-employee.md    ← Template applied here
    ├── buying-signal-employee.md
    ├── account-intelligence-employee.md
    └── ...
```

These individual employee files are created as part of Layer 4 implementation.

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `04_AI_CONSTITUTION.md` | All employees must comply with AI Constitution |
| `14_DEPARTMENT_BLUEPRINT.md` | Employees belong to departments defined here |
| `15_STANDARD_OPERATING_PROCEDURES.md` | SOPs follow the framework defined there |
| `17_MEMORY_ARCHITECTURE.md` | Memory section references types defined there |
| `18_TOOL_ARCHITECTURE.md` | Tools section references registry defined there |
| `20_AI_EVALUATION.md` | Evaluation section uses framework defined there |

---

# Final Rule

> **"If it doesn't have a template, it doesn't exist.**
>
> **If its template is incomplete, it is not ready.**
>
> **There are no exceptions."**
