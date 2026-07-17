---
title: Account Discovery PRD
module: account-discovery
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Core
mvp: true
domain: Account
---

# Account Discovery

> **"The best opportunity is the one you find before your competitor does."**

---

# Why This Module Exists

Getting new accounts is the hardest challenge in enterprise sales.

Most Account Managers rely on:

- Personal networks
- Referrals
- Cold lists with no context
- Luck and timing

This module changes that.

Account Discovery replaces luck with a systematic, AI-powered process for identifying high-potential companies at exactly the right moment.

The Account Manager no longer asks: *"Who should I call today?"*

The platform already has the answer.

---

# Domain Ownership

This module belongs to the **Account Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

All data created by this module is owned by the Account Domain.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Find new companies worth pursuing without spending hours on manual research.

**Frustration:** Today, finding the right account requires luck, cold lists, or relying on network referrals. There is no system.

**Success:** Every morning, the AM sees a prioritized list of companies worth contacting — discovered, researched, and scored overnight by Digital Employees.

## Secondary User: Sales Manager

**Goal:** Understand which new accounts the team is targeting and why.

**Access:** Read-only view of team discovery pipeline.

---

# User Stories

## Must Have (MVP)

```
As an Account Manager,
I want to see new high-potential companies discovered by AI every morning,
so that I always have qualified leads without manual prospecting.

As an Account Manager,
I want each discovered company to come with a research summary,
so that I understand why it was surfaced before deciding to pursue it.

As an Account Manager,
I want to see buying signals for each discovered company,
so that I know the right reason and timing to reach out.

As an Account Manager,
I want to approve or reject each discovered account,
so that I control what enters my active account pipeline.

As an Account Manager,
I want to configure what types of companies I am interested in,
so that the AI discovers accounts relevant to my territory.
```

## Should Have (V2)

```
As an Account Manager,
I want to search for a specific company and add it manually,
so that I can combine AI discovery with my own leads.

As an Account Manager,
I want to see which accounts my competitors might be targeting,
so that I can prioritize faster where timing matters.

As a Sales Manager,
I want to see team-wide discovery performance,
so that I can coach Account Managers on their prospecting strategy.
```

---

# User Flow

## Flow 1: Daily Discovery Review

```
Account Manager opens Dashboard
        ↓
Sees "New Discoveries" section (prepared overnight by AI)
        ↓
Clicks a discovered company
        ↓
Reads: Company Summary, Why Discovered, Buying Signals, Score
        ↓
Decision:
    [Accept] → Moves to Account Intelligence for deeper profiling
    [Reject] → Removed from discovery queue, AI learns preference
    [Defer]  → Stays in queue for tomorrow's review
        ↓
If Accepted:
    Account is created in Account Intelligence
    Research Employee begins deep profiling
    Buying Signal Employee begins monitoring
```

## Flow 2: Configure Discovery Criteria

```
Account Manager goes to Discovery Settings
        ↓
Defines:
    - Target industries
    - Company size range (employees, revenue)
    - Geographic area
    - Technology keywords (signals of digital transformation)
    - Exclusion list (already customers, blacklisted)
        ↓
AI uses these criteria for all future discovery runs
        ↓
Criteria can be updated at any time
```

---

# Functional Requirements

## Discovery Engine

- Discover new companies daily based on configured criteria
- Each discovery includes: company name, industry, estimated size, discovery reason
- Discovery runs automatically overnight (scheduled workflow)
- Discovery results appear in Dashboard every morning

## Buying Signal Detection

- Monitor discovered companies for trigger events
- Signal types:
  - Leadership change (new CTO, CIO, IT Director)
  - Company expansion (new office, new region)
  - Funding announcement
  - Digital transformation initiative (news, press release)
  - Technology change (migration, new vendor announcement)
  - Hiring surge in IT roles
  - Regulatory compliance deadline approaching
- Each signal includes: type, description, date, source, confidence score

## Account Scoring

- Score each discovered company on a scale of 0–100
- Score factors:
  - Signal strength and recency
  - Company size vs. territory fit
  - Industry match to AM's expertise
  - Buying signal type relevance
- Score displayed with explanation

## Territory Configuration

- AM can define discovery criteria per territory
- Criteria: industry, size, geography, keywords, exclusions
- Criteria are stored per workspace and per user

## Discovery Queue Management

- Accept → creates account in Account Intelligence
- Reject → removed, reasoning stored for AI learning
- Defer → remains in queue
- Queue is paginated and sortable

---

# How AI Helps

## Digital Employees Involved

### Company Research Employee (Research Department)
- Runs when a discovery candidate is identified
- Performs initial company research
- Extracts: industry, size, strategic initiatives, technology landscape
- Produces: Company Research Summary

### Buying Signal Employee (Customer Intelligence Department)
- Monitors companies continuously for trigger events
- Sources: news APIs, company websites, LinkedIn signals, industry publications
- Produces: Buying Signal Report with confidence score

### Account Scoring Employee (Sales Intelligence Department)
- Combines research and signals to produce a single score
- Explains scoring rationale in human-readable format
- Produces: Account Score + Justification

## AI Workflow

```
Overnight Scheduled Trigger
        ↓
Buying Signal Employee: Scan for signals
        ↓
New signal found → AccountDiscovered event
        ↓
Company Research Employee: Research company
        ↓
ResearchCompleted event
        ↓
Account Scoring Employee: Calculate score
        ↓
AccountScored event
        ↓
Dashboard: New discovery appears
```

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `ResearchCompleted` | Research Worker | Trigger scoring after research |
| `FeedbackSubmitted` | Digital Workforce Console | Learn from AM rejection/approval |
| `WorkspaceConfigured` | Settings | Update discovery criteria |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `AccountDiscovered` | `account.discovered` | companyName, source, reason, workspaceId | Research Worker, Buying Signal Worker, Dashboard |
| `AccountScored` | `account.scored` | accountId, score, justification, workspaceId | Dashboard, Notification Worker |
| `BuyingSignalDetected` | `buying_signal.detected` | accountId, signalType, description, confidence, source | Dashboard, Account Intelligence |
| `DiscoveryAccepted` | `account.discovery_accepted` | accountId, acceptedBy, workspaceId | Account Intelligence (triggers deep profile) |
| `DiscoveryRejected` | `account.discovery_rejected` | candidateId, rejectedBy, reason, workspaceId | AI Learning Loop |

---

# API Endpoints (High Level)

```
GET    /api/v1/discovery                    → List discovery queue (paginated)
GET    /api/v1/discovery/:id                → Get single discovery detail
POST   /api/v1/discovery/:id/accept         → Accept discovery → create account
POST   /api/v1/discovery/:id/reject         → Reject with optional reason
POST   /api/v1/discovery/:id/defer          → Defer to tomorrow

GET    /api/v1/discovery/criteria           → Get current territory criteria
PUT    /api/v1/discovery/criteria           → Update territory criteria

GET    /api/v1/buying-signals               → List signals (by account or global)
GET    /api/v1/buying-signals/:id           → Get signal detail

GET    /api/v1/discovery/history            → Past accepted/rejected discoveries
```

All endpoints require workspace-scoped authentication.

All responses include: source, confidence score, timestamp (per `04_AI_CONSTITUTION.md`).

---

# Data Model (High Level)

```sql
-- Discovery Candidates
discovery_candidates (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,        -- tenant isolation
    company_name    VARCHAR NOT NULL,
    company_url     VARCHAR,
    industry        VARCHAR,
    company_size    VARCHAR,
    location        VARCHAR,
    discovery_source VARCHAR,             -- signal type that triggered discovery
    discovery_reason TEXT,               -- human-readable explanation
    score           INTEGER,             -- 0-100
    score_justification TEXT,
    status          VARCHAR,             -- pending, accepted, rejected, deferred
    rejected_reason TEXT,
    created_at      TIMESTAMP,
    reviewed_at     TIMESTAMP,
    reviewed_by     UUID,
    deleted_at      TIMESTAMP            -- soft delete
)

-- Buying Signals
buying_signals (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID,                -- null if not yet accepted
    candidate_id    UUID,               -- reference to discovery_candidates
    signal_type     VARCHAR,            -- leadership_change, expansion, funding, etc.
    signal_title    VARCHAR,
    signal_summary  TEXT,
    signal_date     TIMESTAMP,
    source_url      VARCHAR,
    confidence_score DECIMAL(3,2),      -- 0.00 to 1.00
    created_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- Discovery Criteria (per user per workspace)
discovery_criteria (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    user_id         UUID NOT NULL,
    industries      JSONB,              -- array of industry tags
    min_employees   INTEGER,
    max_employees   INTEGER,
    geographies     JSONB,              -- array of location strings
    keywords        JSONB,              -- technology and business keywords
    exclusions      JSONB,              -- company names or domains to exclude
    updated_at      TIMESTAMP
)
```

Storage: **PostgreSQL** as defined in `09_DATA_ARCHITECTURE.md`.

---

# MVP Scope

## In MVP

- Daily discovery queue with AI-generated company summaries
- Buying signal detection (top 5 signal types)
- Account scoring with explanation
- Accept / Reject / Defer workflow
- Basic territory criteria configuration
- Integration with Account Intelligence (accepted → creates account)
- Dashboard card showing new discoveries

## Not in MVP

- Manual company search and add
- Competitor intelligence per candidate
- Team-wide discovery analytics
- Discovery from CRM import
- External data provider integrations (LinkedIn, Crunchbase API)
- Mobile notifications

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| New accounts discovered per week per AM | > 5 | Count of AccountDiscovered events |
| Discovery acceptance rate | > 40% | Accepted / Total reviewed |
| Accepted accounts that generate opportunity | > 30% | Opportunity created within 90 days |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Buying signal accuracy | > 70% accepted by AM | FeedbackSubmitted events |
| Research summary quality score | > 4/5 | AM feedback rating |
| Discovery scoring relevance | > 60% accepted | Acceptance rate |
| Overnight workflow completion rate | > 99% | Temporal workflow metrics |

## Operational KPIs

| KPI | Target | Measurement |
|---|---|---|
| Discovery results available by | 08:00 every morning | Workflow SLA |
| Research completion time per company | < 5 minutes | Latency metric |
| Cost per company researched | Tracked | AI Gateway cost tracking |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Intelligence | Output | Accepted discoveries become accounts |
| Knowledge Hub | Input | Research Employee uses workspace knowledge for context |
| Digital Workforce Console | Bilateral | AM reviews recommendations here |
| Dashboard | Output | Discoveries appear in Daily Briefing |
| Settings | Input | Territory criteria configured here |

---

# Anti-Goals

This module will NOT:

- Replace the Account Manager's judgment on which accounts to pursue
- Guarantee that every discovered account will become a customer
- Provide legal or financial due diligence on discovered companies
- Connect to or sync with external CRM systems (MVP)
- Show competitor's discovery data across workspaces

---

# Final Note

> **This module exists because finding the right account at the right time should not depend on luck.**
>
> **It should depend on intelligence.**
