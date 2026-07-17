---
title: Opportunity Management PRD
module: opportunity-management
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Core
mvp: false
domain: Opportunity
---

# Opportunity Management

> **"A pipeline without intelligence is just a list of hopes."**

---

# Why This Module Exists

An Account Manager may have 20–50 active opportunities at any given time.

Each opportunity is at a different stage.

Each has different risks, competitors, and required next actions.

Managing this manually leads to:

- Deals stalling without anyone noticing
- Wrong priorities: working on easy deals instead of important ones
- Proposals sent without understanding what competitors are doing
- Forecasts based on gut feeling instead of data

This module transforms opportunity management from a tracking exercise into an intelligent, AI-driven process.

The platform tells the AM: which deal needs attention today, why it is at risk, and what to do next.

---

# Domain Ownership

This module belongs to the **Opportunity Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Know exactly which opportunities need attention today and what to do to advance them.

**Frustration:** Today, AM has to manually review every deal to understand status. Important deals stall because there is no proactive alert.

**Success:** The platform surfaces the top 3 deals that need action today, explains why, and recommends what to do.

## Secondary User: Sales Manager

**Goal:** Understand team pipeline health and forecast accuracy.

**Access:** Read access to all team opportunities.

---

# User Stories

## Must Have (V2 — not MVP)

```
As an Account Manager,
I want to create and track opportunities linked to specific accounts,
so that I can manage my pipeline in one place.

As an Account Manager,
I want AI to score each opportunity's win probability,
so that I focus effort on deals most likely to close.

As an Account Manager,
I want to receive alerts when a deal is stalling,
so that I never lose a deal due to inaction.

As an Account Manager,
I want to see competitor intelligence for each opportunity,
so that I can prepare the right counter-strategy.

As an Account Manager,
I want AI to recommend the next best action for each deal,
so that I always know what to do next.
```

## Should Have (Future)

```
As a Sales Manager,
I want to see the full team pipeline at a glance,
so that I can identify risks and coach Account Managers proactively.

As an Account Manager,
I want to run win/loss analysis on closed deals,
so that I can improve my approach for future opportunities.

As an Account Manager,
I want to link a proposal to an opportunity,
so that the full deal history is in one place.
```

---

# User Flow

## Flow 1: Create Opportunity

```
Account Manager selects an account
        ↓
Clicks "New Opportunity"
        ↓
Fills in:
    - Opportunity name
    - Estimated value
    - Expected close date
    - Products / solutions
    - Initial stage (Prospecting / Qualification / Proposal / Negotiation)
        ↓
OpportunityCreated event published
        ↓
Opportunity Employee begins scoring
Competitor Employee begins monitoring
Next Best Action Employee prepares first recommendation
        ↓
Opportunity appears in pipeline view with initial score
```

## Flow 2: Daily Opportunity Review

```
Account Manager opens Opportunity Pipeline
        ↓
Sees opportunities sorted by: AI Priority Score
        ↓
For each high-priority opportunity:
    - AI Score displayed with justification
    - Recommended Next Action displayed
    - Risk indicators (stalling, competitor activity, close date approaching)
        ↓
AM acts on recommendation:
    Schedules meeting, updates stage, creates proposal
        ↓
AI updates score and recommendation after each action
```

## Flow 3: Deal Stall Detection

```
No activity on opportunity for X days
        ↓
Opportunity Employee detects stall
        ↓
OpportunityStallDetected event published
        ↓
Notification Employee: AM receives alert
Dashboard: "Deal Needs Attention" card appears
        ↓
AM reviews and takes action
```

---

# Functional Requirements

## Pipeline Management

- Create, update, and close opportunities
- Pipeline stages (configurable per workspace): Prospecting, Qualification, Proposal, Negotiation, Won, Lost
- Link opportunities to accounts (one account, many opportunities)
- Link products and solutions to opportunities
- Track estimated value, probability, expected close date

## AI Deal Scoring

- Score each opportunity 0–100
- Score factors: stage, activity recency, competitor threat, account intelligence quality, engagement level
- Score refreshed after every significant event
- Justification displayed with every score

## Competitor Intelligence

- Per-opportunity competitor tracking
- Competitor threat level assessment
- Counter-positioning recommendations from Knowledge Hub

## Next Best Action

- AI recommends one specific action per opportunity per day
- Action types: schedule call, send proposal, involve executive, negotiate terms
- Recommendation includes: what to do, why, how urgently

## Stall Detection

- Alert when no activity for configurable number of days
- Stage-specific thresholds (Proposal stage: 7 days without response = alert)

## Win/Loss Tracking

- Record win or loss with reason
- Every won/lost opportunity feeds the AI learning loop
- Win/loss patterns improve future scoring accuracy

---

# How AI Helps

## Digital Employees Involved

### Opportunity Employee (Sales Intelligence Department)
- Triggered by: OpportunityCreated, OpportunityStageChanged
- Calculates and refreshes deal score
- Identifies deal health risks
- Produces: Deal Score + Risk Assessment

### Competitor Employee (Sales Intelligence Department)
- Monitors competitive landscape per opportunity
- Sources competitor intelligence from Knowledge Hub
- Recommends counter-positioning

### Risk Assessment Employee (Sales Intelligence Department)
- Detects stalling deals
- Identifies close date risks
- Alerts when probability drop is significant

### Next Best Action Employee (Sales Intelligence Department)
- Produces one recommended action per opportunity per day
- Prioritizes actions across all opportunities for the AM
- Learns from which actions the AM actually takes

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `AccountIntelligenceUpdated` | Account Intelligence | Update deal context |
| `BuyingSignalDetected` | Account Discovery | Update opportunity score |
| `MeetingCompleted` | Activity Center | Reset stall timer, update score |
| `ProposalSubmitted` | Proposal Studio | Advance deal stage |
| `RecommendationApproved` | Digital Workforce Console | Learn what AM accepts |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `OpportunityCreated` | `opportunity.created` | opportunityId, accountId, value, stage | Scoring, Competitor, Forecast |
| `OpportunityStageChanged` | `opportunity.stage_changed` | opportunityId, fromStage, toStage | Forecast, Dashboard |
| `OpportunityWon` | `opportunity.won` | opportunityId, value, accountId | Forecast, Knowledge (learning) |
| `OpportunityLost` | `opportunity.lost` | opportunityId, value, lostReason | Forecast, Knowledge (learning) |
| `DealScoreUpdated` | `opportunity.score_updated` | opportunityId, score, justification | Dashboard |
| `OpportunityStallDetected` | `opportunity.stall_detected` | opportunityId, daysSinceActivity | Notification, Dashboard |
| `NextBestActionReady` | `opportunity.next_action_ready` | opportunityId, action, urgency | Dashboard |

---

# API Endpoints (High Level)

```
GET    /api/v1/opportunities                → List opportunities (filterable by stage, account, AM)
POST   /api/v1/opportunities                → Create opportunity
GET    /api/v1/opportunities/:id            → Get opportunity detail
PUT    /api/v1/opportunities/:id            → Update opportunity
DELETE /api/v1/opportunities/:id            → Soft delete (close)

PUT    /api/v1/opportunities/:id/stage      → Change pipeline stage
POST   /api/v1/opportunities/:id/won        → Mark as won
POST   /api/v1/opportunities/:id/lost       → Mark as lost with reason

GET    /api/v1/opportunities/:id/score      → Get AI score and justification
GET    /api/v1/opportunities/:id/next-action → Get recommended next action
GET    /api/v1/opportunities/:id/competitors → Get competitor intelligence
GET    /api/v1/opportunities/:id/timeline   → Get opportunity activity timeline

GET    /api/v1/pipeline                     → Pipeline summary view (all stages)
GET    /api/v1/pipeline/at-risk             → Stalling deals
```

---

# Data Model (High Level)

```sql
-- Opportunities
opportunities (
    id                  UUID PRIMARY KEY,
    workspace_id        UUID NOT NULL,
    account_id          UUID NOT NULL,
    assigned_to         UUID NOT NULL,      -- Account Manager
    name                VARCHAR NOT NULL,
    description         TEXT,
    estimated_value     DECIMAL(15,2),
    currency            VARCHAR(3),
    stage               VARCHAR NOT NULL,   -- prospecting, qualification, proposal, negotiation, won, lost
    probability         INTEGER,            -- 0-100 (human-set)
    ai_score            INTEGER,            -- 0-100 (AI-set)
    ai_score_justification TEXT,
    expected_close_date DATE,
    won_at              TIMESTAMP,
    lost_at             TIMESTAMP,
    lost_reason         TEXT,
    last_activity_at    TIMESTAMP,
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP,
    deleted_at          TIMESTAMP
)

-- Opportunity Products
opportunity_products (
    id              UUID PRIMARY KEY,
    opportunity_id  UUID NOT NULL,
    product_name    VARCHAR,
    quantity        INTEGER,
    unit_price      DECIMAL(15,2),
    total_price     DECIMAL(15,2),
    notes           TEXT
)

-- Competitors per Opportunity
opportunity_competitors (
    id                  UUID PRIMARY KEY,
    opportunity_id      UUID NOT NULL,
    competitor_name     VARCHAR NOT NULL,
    threat_level        VARCHAR,            -- low, medium, high, critical
    counter_strategy    TEXT,              -- AI-generated
    last_updated        TIMESTAMP
)

-- Next Best Actions
opportunity_actions (
    id              UUID PRIMARY KEY,
    opportunity_id  UUID NOT NULL,
    action_type     VARCHAR,               -- call, meeting, proposal, negotiation
    action_detail   TEXT,
    urgency         VARCHAR,               -- low, medium, high, critical
    generated_by    VARCHAR,               -- Digital Employee name
    accepted        BOOLEAN,
    created_at      TIMESTAMP,
    acted_at        TIMESTAMP
)
```

---

# MVP Scope

## Not in MVP

This entire module is V2.

In MVP, Account Managers can manually note opportunities as free text within an account's timeline.

Full pipeline management and AI scoring is delivered in V2.

## In V2

- Full opportunity pipeline with stages
- AI deal scoring
- Competitor intelligence
- Next Best Action
- Stall detection
- Win/Loss tracking

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Win rate for AI high-scored deals | > industry average | Won / Total high-score deals |
| Deals stalling for more than 14 days | Decrease over time | StallDetected events |
| Next Best Action acceptance rate | > 50% | acted_at filled in |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Deal score accuracy (predicted vs. actual outcome) | > 65% | Post-close analysis |
| Stall detection precision | > 80% | Feedback from AM |
| Competitor intelligence relevance | > 3.5/5 | AM feedback rating |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Intelligence | Input | Account context enriches deal scoring |
| Knowledge Hub | Input | Competitor intelligence, product knowledge |
| Proposal Studio | Bilateral | Proposals linked to opportunities |
| Forecast Center | Output | Opportunities feed revenue forecast |
| Activity Center | Input | Activities update opportunity timeline |
| Dashboard | Output | Priority deals surface in Daily Briefing |

---

# Anti-Goals

This module will NOT:

- Replace human judgment on deal strategy
- Guarantee AI-scored deals will close
- Automate proposal sending without AM approval
- Track opportunities across different workspaces

---

# Final Note

> **"The AM who knows which deal to work on today**
>
> **will always outperform the AM who is working hardest."**
