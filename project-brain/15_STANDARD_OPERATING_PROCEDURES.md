---
title: Standard Operating Procedures Framework
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 15 — Standard Operating Procedures

> **"A Digital Employee without an SOP is not an employee. It is a language model with ambition."**

---

# Purpose

Standard Operating Procedures (SOPs) define the exact, step-by-step instructions that govern how each Digital Employee performs their work.

SOPs transform general AI capability into reliable, predictable, auditable work.

An SOP is the difference between an AI that *tries* to do something and an AI that *knows* exactly what to do, in what order, under what conditions, and what to do when something goes wrong.

---

# What an SOP Is

An SOP answers four questions:

1. **When does this procedure start?** (Trigger)
2. **What exactly happens, step by step?** (Procedure)
3. **What is produced at the end?** (Output)
4. **What happens if something goes wrong?** (Error Handling)

---

# What an SOP Is Not

An SOP is not:

- A prompt template (prompts are implementation details inside an SOP step)
- A vague description ("research the company thoroughly")
- An optional guide ("you may want to consider...")

An SOP is a **binding operational contract** for a Digital Employee.

---

# SOP Structure

Every SOP follows this mandatory structure:

```
SOP-[DEPT]-[NUMBER]-[SHORT-NAME]

Example: SOP-RES-001-COMPANY-RESEARCH
```

---

## SOP Template

```markdown
## [SOP ID]: [SOP Name]

**Employee:** [Digital Employee Name]
**Department:** [Department Name]
**Version:** 1.0.0
**Last Updated:** YYYY-MM-DD

---

### Trigger

[What event or condition causes this SOP to activate]

Trigger Type: [ ] Event | [ ] Scheduled | [ ] On-Demand

If Event:
  Event: [EventName]
  Subject: [nats.subject]

If Scheduled:
  Schedule: [cron expression]
  Timezone: workspace_timezone

---

### Pre-Conditions

Before this SOP begins, the following MUST be true:
- [ ] [Pre-condition 1]
- [ ] [Pre-condition 2]

If any pre-condition is not met: [action — abort / wait / escalate]

---

### Input

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| workspace_id | UUID   | Yes      | Tenant identifier |
| [field]      | [type] | [Y/N]    | [Description] |

---

### Steps

**Step 1: [Step Name]**
- Action: [Exact action to perform]
- Tool used: [Tool ID or "none"]
- Input: [What data is needed]
- Output: [What data is produced]
- Validation: [How to verify the step succeeded]
- On error: [What to do if step fails]
- Time limit: [Maximum time for this step]

**Step 2: [Step Name]**
[same structure]

---

### Decision Points

If [condition]:
  → Take [path A]
Else if [condition]:
  → Take [path B]
Else:
  → [Default path]

---

### Output

| Field           | Type   | Description |
|-----------------|--------|-------------|
| [output_field]  | [type] | [What it contains] |

Confidence scoring:
- High confidence (> 0.8): [proceed normally]
- Medium confidence (0.4–0.8): [add uncertainty note]
- Low confidence (< 0.4): [escalate to human review]

---

### Post-Conditions

After this SOP completes:
- [ ] [What must be true]
- [ ] [Event published]
- [ ] [Memory updated]

---

### Error Handling

| Error Type          | Response                          |
|---------------------|-----------------------------------|
| Data not found      | [action]                          |
| API timeout         | [retry policy: max 3, backoff 30s]|
| Low confidence      | [escalate to Digital Workforce Console] |
| Critical failure    | [abort + publish FailedEvent + alert] |

---

### SLA

| Metric        | Target    |
|---------------|-----------|
| Completion    | < [X]s    |
| Success rate  | > [X]%    |

---

### Change Log

| Version | Date       | Change         |
|---------|------------|----------------|
| 1.0.0   | YYYY-MM-DD | Initial        |
```

---

# SOP Registry

All SOPs must be registered here.

## Research Department SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-RES-001 | Company Research | Company Research Employee | ✅ |
| SOP-RES-002 | News Monitoring | News Employee | ✅ |
| SOP-RES-003 | Industry Analysis | Industry Research Employee | V2 |

## Sales Intelligence SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-SI-001 | Buying Signal Detection | Buying Signal Employee | ✅ |
| SOP-SI-002 | Account Scoring | Account Scoring Employee | ✅ |
| SOP-SI-003 | Competitor Analysis | Competitor Employee | V2 |
| SOP-SI-004 | Next Best Action | Next Best Action Employee | V2 |
| SOP-SI-005 | Deal Risk Assessment | Risk Assessment Employee | V2 |

## Customer Intelligence SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-CI-001 | Account Profile Build | Account Intelligence Employee | ✅ |
| SOP-CI-002 | Contact Mapping | Contact Intelligence Employee | ✅ |
| SOP-CI-003 | Meeting Processing | Meeting Employee | V2 |
| SOP-CI-004 | Relationship Monitoring | Relationship Employee | V2 |

## Knowledge SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-KW-001 | Knowledge Indexing | Knowledge Indexing Employee | ✅ |
| SOP-KW-002 | Knowledge Gap Detection | Documentation Employee | V2 |

## Proposal SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-PR-001 | Full Proposal Generation | Proposal Employee | V2 |
| SOP-PR-002 | Executive Summary | Executive Summary Employee | V2 |
| SOP-PR-003 | BoQ Generation | BoQ Employee | V2 |
| SOP-PR-004 | Business Case | Business Case Employee | V2 |

## AI Operations SOPs

| SOP ID | SOP Name | Employee | MVP |
|---|---|---|---|
| SOP-OPS-001 | Dashboard Priority Aggregation | Dashboard Priority Employee | ✅ |
| SOP-OPS-002 | AI Health Monitoring | AI Operations Monitor | V2 |

---

# MVP SOP: SOP-RES-001 — Company Research

This is the most important SOP in MVP.

---

## SOP-RES-001: Company Research

**Employee:** Company Research Employee
**Department:** Research Department
**Version:** 1.0.0

---

### Trigger

**Type:** Event-Driven

**Event:** `DiscoveryAccepted` or `AccountCreated`
**Subject:** `account.discovery_accepted` | `account.created`

---

### Pre-Conditions

- Account record exists in database
- workspace_id is valid
- Company name or URL is available
- Knowledge Hub Layer 2 is accessible

---

### Input

| Field | Type | Required |
|---|---|---|
| workspace_id | UUID | Yes |
| account_id | UUID | Yes |
| company_name | String | Yes |
| company_url | String | Optional |
| industry_hint | String | Optional |

---

### Steps

**Step 1: Retrieve Workspace Knowledge Context**
- Action: Query Knowledge Hub for workspace's industry focus and product categories
- Tool: `knowledge_hub.search`
- Input: workspace_id, query="target industries and ideal customer profile"
- Output: Relevant knowledge articles (max 3)
- Time limit: 5 seconds
- On error: Continue without workspace context (log warning)

**Step 2: Research Company via Web**
- Action: Search for company information from public sources
- Tool: `web_search`
- Input: company_name + company_url (if available)
- Queries to run (in parallel):
  - "[company_name] company overview business description"
  - "[company_name] industry revenue employees locations"
  - "[company_name] leadership executives management team"
  - "[company_name] recent news announcements 2024 2025"
  - "[company_name] technology digital transformation IT"
- Output: Raw search results per query
- Time limit: 30 seconds
- On error: If all queries fail → abort with ResearchFailed event

**Step 3: Extract Structured Information**
- Action: Parse raw results into structured fields
- Tool: LLM (Gemini/GPT-4o) with structured output
- Extract:
  - Company description (2–3 sentences)
  - Industry (primary and secondary)
  - Company size (employees, revenue estimate)
  - Headquarters and locations
  - Key executives (name, title)
  - Strategic initiatives (top 3)
  - Technology mentions (systems, vendors, platforms)
  - Recent significant events (top 3)
- Validation: All required fields must be populated or marked "not found"
- Time limit: 20 seconds
- On error: Retry once, then proceed with partial data

**Step 4: Generate Intelligence Summary**
- Action: Write AI-generated summary for Account Manager
- Tool: LLM
- Input: Structured information from Step 3
- Output: 150–200 word plain-language summary
- Format: Why this company is interesting, what they are doing, recommended approach
- Time limit: 15 seconds
- On error: Skip summary (display raw structured data)

**Step 5: Calculate Completeness Score**
- Action: Score how complete the profile is
- Formula: (fields_populated / total_required_fields) × 100
- Required fields: description, industry, size, headquarters, at least 1 executive
- Output: Integer 0–100
- Time limit: 1 second

**Step 6: Persist Results**
- Action: Write to database
- Tool: `database.write`
- Records to write:
  - Update `accounts` table: industry, size, description, completeness_score
  - Insert into `account_intelligence`: all intelligence records with source URLs
  - Insert into `contacts`: discovered executives
  - Insert into `account_news`: recent events
- Time limit: 10 seconds
- On error: Retry 3 times → publish ResearchFailed

**Step 7: Publish Completion Event**
- Action: Publish NATS event
- Event: `ResearchCompleted`
- Subject: `research.completed`
- Payload: { accountId, workspaceId, completenessScore, executivesFound, hasStrategicInitiatives }
- Time limit: 2 seconds

---

### Decision Points

If completeness_score < 40:
  → Add note: "Limited public information available"
  → Still publish ResearchCompleted (let AM decide)

If company not found after all searches:
  → Publish ResearchFailed with reason "company_not_found"
  → Display placeholder profile with manual fill prompt

---

### Output

| Field | Type | Description |
|---|---|---|
| company_summary | String | AI-generated 150-200 word summary |
| industry | String | Primary industry classification |
| company_size | String | small/mid/large/enterprise |
| executives | Array | Name, title, per executive |
| strategic_initiatives | Array | Top 3 initiatives |
| tech_landscape | Array | Technology mentions |
| recent_events | Array | Top 3 recent events |
| completeness_score | Integer | 0-100 |
| confidence | Float | 0.0-1.0 |
| sources | Array | Source URLs used |

---

### Post-Conditions

- Account record is updated in database
- `ResearchCompleted` event is published
- Account Intelligence Employee is triggered (via event)
- Account Scoring Employee is triggered (via event)

---

### Error Handling

| Error | Response |
|---|---|
| Web search timeout | Retry once, then proceed with partial data |
| LLM timeout | Retry once with shorter prompt |
| Database write failure | Retry 3x with exponential backoff |
| All steps fail | Publish `ResearchFailed`, alert via Console |

---

### SLA

| Metric | Target |
|---|---|
| Total completion time | < 2 minutes |
| Success rate | > 95% |
| Completeness score average | > 60% |

---

# MVP SOP: SOP-SI-001 — Buying Signal Detection

---

## SOP-SI-001: Buying Signal Detection

**Employee:** Buying Signal Employee
**Department:** Sales Intelligence Department
**Version:** 1.0.0

---

### Trigger

**Type:** Scheduled + Event-Driven

**Scheduled:** Daily at 03:00 workspace timezone (runs overnight)
**Event:** `AccountCreated` (immediate scan for new accounts)

---

### Pre-Conditions

- At least one active account exists in workspace
- News sources are accessible
- Discovery criteria are configured for workspace

---

### Steps

**Step 1: Load Active Accounts**
- Action: Query all active accounts in workspace
- Tool: `database.query`
- Filter: status = 'active', deleted_at IS NULL
- Output: List of account IDs and company names

**Step 2: For Each Account — Scan for Signals**
(Run in parallel, max 50 concurrent)

  **Step 2a: Leadership Change Detection**
  - Search: "[company_name] new CTO CIO CEO VP Director appointed 2025"
  - Signal: Any leadership change in IT/tech/digital roles
  - Confidence: 0.85 if press release found, 0.6 if inferred from LinkedIn

  **Step 2b: Expansion Detection**
  - Search: "[company_name] expansion new office new region 2025"
  - Signal: Geographic or operational expansion
  - Confidence: 0.8 if official announcement, 0.5 if rumor/report

  **Step 2c: Digital Transformation Detection**
  - Search: "[company_name] digital transformation technology investment IT project"
  - Signal: Active digital initiative
  - Confidence: 0.7 if project confirmed, 0.5 if planned

  **Step 2d: Funding/Investment Detection**
  - Search: "[company_name] funding investment capital raised 2025"
  - Signal: New budget available
  - Confidence: 0.9 if press release, 0.6 if reported

  **Step 2e: Regulatory Compliance Detection**
  - Search: "[company_name] [relevant regulation] compliance deadline"
  - Signal: Regulatory pressure creating urgent need
  - Confidence: 0.8 if deadline confirmed

**Step 3: Score Each Detected Signal**
- Score formula: signal_type_weight × recency_weight × source_quality_weight
- Weights:
  - Leadership change: 0.9
  - Funding: 0.85
  - Expansion: 0.8
  - Digital transformation: 0.75
  - Regulatory: 0.85
- Recency: Signal from last 30 days = 1.0, 31-60 days = 0.7, 61-90 days = 0.4

**Step 4: Filter Actionable Signals**
- Threshold: Only signals with score > 0.5 are stored
- Deduplication: Do not re-publish signals already stored within last 14 days

**Step 5: Persist and Publish**
- Write signals to `buying_signals` table
- Publish `BuyingSignalDetected` event per signal
- Update Dashboard snapshot (via Dashboard Priority Employee next run)

---

### SLA

| Metric | Target |
|---|---|
| Completion time (100 accounts) | < 10 minutes |
| False positive rate | < 30% (AM rejects) |
| Signal coverage | > 80% of accounts scanned daily |

---

# SOP Governance

## Creating New SOPs

1. Copy the SOP Template above
2. Fill all sections completely
3. Register in the SOP Registry in this document
4. Update the employee's `13_DIGITAL_EMPLOYEE_TEMPLATE.md` definition
5. Write unit tests for each step
6. Get approval from Founder before activation

## Updating Existing SOPs

1. Increment version number (MAJOR for breaking changes, MINOR for enhancements)
2. Document changes in changelog
3. Test in staging before production
4. If MAJOR version: migrate any in-flight tasks to new version gracefully

## Deprecating SOPs

1. Set status to `deprecated`
2. Set end-of-life date (minimum 30 days notice)
3. Ensure no active workflows depend on it
4. Archive (do not delete — SOPs are historical records)

---

# Final Principle

> **"An SOP is a promise.**
>
> **A promise that the Digital Employee will do the right thing,**
>
> **in the right order, every time, without being asked twice."**
