---
title: Digital Workforce Console PRD
module: digital-workforce-console
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Core
mvp: true
domain: AI Platform
---

# Digital Workforce Console

> **"You cannot trust what you cannot see."**

---

# Why This Module Exists

Digital Employees work invisibly by default.

They research. They analyze. They score. They recommend.

But if an Account Manager cannot see what they are doing, cannot review their work, and cannot provide feedback — the Digital Employees are not teammates.

They are black boxes.

This module makes the Digital Workforce **visible, controllable, and trustworthy.**

It is the command center between the Account Manager and their AI workforce.

Without this module, the platform cannot fulfill the AI Constitution's principle that every AI action must be explainable and every recommendation must be reviewable.

---

# Domain Ownership

This module belongs to the **AI Platform Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Know what Digital Employees are doing, review their recommendations, and provide feedback that makes them better.

**Trust Journey:**
- Week 1: Skeptical. Reviews everything carefully.
- Month 1: Accepts recommendations more frequently as accuracy improves.
- Month 3: Trusts high-confidence recommendations without reviewing details.
- Month 6: Relies on the Digital Workforce as a core part of their workflow.

**Success:** The AM checks the Console the way they would check messages from a trusted team member — not to verify, but to act.

## Secondary User: Workspace Administrator

**Goal:** Monitor Digital Employee performance across the workspace, manage costs, and configure AI preferences.

---

# User Stories

## Must Have (MVP)

```
As an Account Manager,
I want to see a feed of all recommendations from my Digital Employees,
so that I can review and act on their work in one place.

As an Account Manager,
I want to approve or reject each recommendation with one click,
so that I can move quickly through the review queue.

As an Account Manager,
I want to provide feedback when a recommendation is wrong,
so that the Digital Employee improves over time.

As an Account Manager,
I want to see the reasoning behind every recommendation,
so that I can trust the AI's work.

As an Account Manager,
I want to see what each Digital Employee is currently working on,
so that I understand the status of background work.

As a Workspace Administrator,
I want to see the cost of AI usage per month,
so that I can manage the platform budget.
```

## Should Have (V2)

```
As an Account Manager,
I want to configure which types of recommendations require my review,
so that I can automate low-stakes decisions.

As an Account Manager,
I want to see the historical accuracy of each Digital Employee,
so that I know which employees to trust most.

As a Workspace Administrator,
I want to set cost limits per Digital Employee,
so that AI costs remain within budget.
```

---

# User Flow

## Flow 1: Daily Recommendation Review

```
Account Manager opens Digital Workforce Console
        ↓
Sees Recommendation Inbox:
    - Sorted by: urgency, then account name
    - Each item shows:
        * Which Digital Employee generated it
        * Account it relates to
        * Recommendation text (plain language)
        * Confidence score
        * Supporting evidence (sources)
        * Timestamp
        ↓
For each recommendation:
    [Approve]  → Action taken, Digital Employee receives positive signal
    [Reject]   → Recommendation dismissed, reason optionally provided
    [Feedback] → Detailed correction (e.g., "The contact has left the company")
        ↓
Feedback is stored and fed back to Digital Employee
```

## Flow 2: View Digital Employee Status

```
Account Manager opens "My Workforce" tab
        ↓
Sees each Digital Employee as a card:
    - Name and department
    - Current status: Active / Idle / Processing
    - Last completed task
    - Tasks completed today
    - Acceptance rate (last 30 days)
    - Cost this month
        ↓
Clicks on a specific employee to see:
    - Full task history
    - All recommendations (approved / rejected)
    - Performance trend
```

## Flow 3: Workspace Admin Cost Monitoring

```
Administrator opens AI Operations tab
        ↓
Sees:
    - Total AI cost this month
    - Cost per Digital Employee
    - Cost trend (daily chart)
    - Most expensive tasks
    - Recommendations for cost optimization
```

---

# Functional Requirements

## Recommendation Inbox

- Unified feed of all Digital Employee recommendations
- Sorted by: urgency → date (newest first)
- Filter by: Employee, Account, Status (pending/approved/rejected)
- Every recommendation includes: employee name, account, text, evidence, confidence score, timestamp
- Bulk approve/reject for low-confidence, low-urgency items
- Unread badge count visible in navigation

## Human Validation Levels (from AI Constitution)

As defined in `04_AI_CONSTITUTION.md`:

| Level | Type | Action Required |
|---|---|---|
| 1 | Information | No approval needed — displayed automatically |
| 2 | Recommendation | Human must approve before acting |
| 3 | Execution | Explicit authorization required before AI executes |

The Console shows Level 2 and Level 3 items.

Level 1 items appear directly in account profiles and Dashboard without Console review.

## Digital Employee Status Board

- List of all active Digital Employees in the workspace
- Per employee: status, last task, today's task count, acceptance rate, monthly cost
- Task detail view per employee

## Feedback Loop

- Structured feedback: Correct / Incorrect / Partially Correct
- Optional text reason for rejection
- Feedback stored per recommendation
- Feedback aggregated into Digital Employee performance metrics
- Feedback used to improve future recommendations (learning loop)

## AI Cost Monitoring

- Monthly cost per workspace
- Cost per Digital Employee
- Cost per task type
- Daily cost trend chart
- Alert when monthly cost exceeds configurable threshold

---

# How AI Helps

This module is the interface FOR AI, not powered by AI.

However, one Digital Employee operates here:

### AI Operations Monitor (AI Operations Department)
- Detects anomalies in Digital Employee performance
- Surfaces suggestions to improve AI accuracy
- Monitors for cost spikes and unusual patterns
- Produces: AI Health Report (weekly)

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `AccountScored` | Account Discovery | Add to recommendation inbox |
| `BuyingSignalDetected` | Account Discovery | Add to recommendation inbox |
| `DecisionMakerIdentified` | Account Intelligence | Add to recommendation inbox |
| `NextBestActionReady` | Opportunity Management | Add to recommendation inbox |
| `ProposalDraftReady` | Proposal Studio | Add to recommendation inbox |
| `RelationshipRiskDetected` | Account Intelligence | Add to recommendation inbox |
| `OpportunityStallDetected` | Opportunity Management | Add to recommendation inbox |
| ALL AI events | All workers | Monitor and display in status board |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `RecommendationApproved` | `recommendation.approved` | recommendationId, approvedBy, workspaceId | Source worker (learning) |
| `RecommendationRejected` | `recommendation.rejected` | recommendationId, rejectedBy, reason | Source worker (learning) |
| `FeedbackSubmitted` | `recommendation.feedback_submitted` | recommendationId, feedbackType, detail | All AI workers (learning) |
| `ExecutionAuthorized` | `recommendation.execution_authorized` | recommendationId, authorizedBy, scope | Execution worker |

---

# API Endpoints (High Level)

```
GET    /api/v1/console/inbox                → Get recommendation inbox (paginated)
GET    /api/v1/console/inbox/count          → Get unread recommendation count
POST   /api/v1/console/recommendations/:id/approve   → Approve recommendation
POST   /api/v1/console/recommendations/:id/reject    → Reject with optional reason
POST   /api/v1/console/recommendations/:id/feedback  → Detailed feedback

GET    /api/v1/console/workforce            → List all Digital Employees status
GET    /api/v1/console/workforce/:employeeId         → Get employee detail and history
GET    /api/v1/console/workforce/:employeeId/tasks   → Get employee task history

GET    /api/v1/console/costs                → AI cost summary
GET    /api/v1/console/costs/by-employee    → Cost breakdown per employee
GET    /api/v1/console/costs/trend          → Daily cost trend

GET    /api/v1/console/performance          → Overall AI performance metrics
```

---

# Data Model (High Level)

```sql
-- Recommendations
recommendations (
    id                  UUID PRIMARY KEY,
    workspace_id        UUID NOT NULL,
    account_id          UUID,
    opportunity_id      UUID,
    generated_by        VARCHAR NOT NULL,   -- Digital Employee name
    validation_level    INTEGER NOT NULL,   -- 1, 2, or 3
    recommendation_type VARCHAR,            -- score, signal, action, risk, draft
    content             TEXT NOT NULL,      -- human-readable recommendation
    evidence            JSONB,              -- sources, confidence, timestamp
    confidence_score    DECIMAL(3,2),       -- 0.00 to 1.00
    status              VARCHAR,            -- pending, approved, rejected, auto_displayed
    reviewed_by         UUID,
    reviewed_at         TIMESTAMP,
    rejection_reason    TEXT,
    created_at          TIMESTAMP,
    deleted_at          TIMESTAMP
)

-- Feedback Records
recommendation_feedback (
    id                  UUID PRIMARY KEY,
    recommendation_id   UUID NOT NULL,
    workspace_id        UUID NOT NULL,
    user_id             UUID NOT NULL,
    feedback_type       VARCHAR,            -- correct, incorrect, partially_correct
    detail              TEXT,
    created_at          TIMESTAMP
)

-- Digital Employee Registry
digital_employees (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    employee_name   VARCHAR NOT NULL,
    department      VARCHAR NOT NULL,
    description     TEXT,
    status          VARCHAR,               -- active, idle, disabled
    is_enabled      BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
)

-- AI Task Log
ai_task_log (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    employee_id     UUID NOT NULL,
    task_type       VARCHAR,
    account_id      UUID,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    duration_ms     INTEGER,
    token_used      INTEGER,
    cost_usd        DECIMAL(10,6),
    status          VARCHAR,               -- completed, failed, timeout
    error_message   TEXT
)
```

---

# MVP Scope

## In MVP

- Recommendation Inbox with full approve/reject/feedback workflow
- Digital Employee status board (basic: active/idle, last task)
- Evidence display per recommendation (source, confidence, timestamp)
- Monthly AI cost summary

## Not in MVP

- Validation level configuration (all Level 2 by default in MVP)
- Employee-level cost breakdown (workspace-level only in MVP)
- Bulk approve/reject
- Performance trend charts

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Recommendation inbox review rate | > 80% reviewed within 24h | reviewed_at tracking |
| Overall recommendation acceptance rate | > 60% | Approved / Total |
| Time to first review per new recommendation | < 4 hours | created_at vs reviewed_at |

## Trust KPIs

| KPI | Target | Measurement |
|---|---|---|
| Acceptance rate trend | Increasing month over month | Trend analysis |
| Feedback rate (when rejecting) | > 50% provide reason | feedback records |
| Level 1 auto-trust rate | Increasing over time | Level 1 recommendations not manually overridden |

## Operational KPIs

| KPI | Target | Measurement |
|---|---|---|
| Monthly AI cost per workspace | Tracked and within budget | ai_task_log |
| Failed tasks rate | < 1% | Status = failed / total |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| All AI Workers | Input | Source of all recommendations |
| Account Intelligence | Bilateral | Recommendations reference accounts |
| Opportunity Management | Bilateral | Recommendations reference opportunities |
| Dashboard | Output | Pending recommendation count shown in briefing |

---

# Anti-Goals

This module will NOT:

- Make decisions on behalf of the Account Manager
- Auto-execute Level 2 or Level 3 actions without human approval
- Store personal conversation data between AM and customers
- Expose AI performance data across workspaces

---

# Final Note

> **"Visibility builds trust.**
>
> **Trust enables adoption.**
>
> **Adoption creates value.**
>
> **This module is where trust is built."**
