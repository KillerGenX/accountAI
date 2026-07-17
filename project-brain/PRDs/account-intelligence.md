---
title: Account Intelligence PRD
module: account-intelligence
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Core
mvp: true
domain: Account
---

# Account Intelligence

> **"An account that doesn't change is an account you don't understand."**

---

# Why This Module Exists

Traditional CRM systems store accounts as static records.

Name. Address. Phone number. Industry.

The record never changes unless someone manually updates it.

But companies are not static.

Companies hire new executives. Companies expand to new regions. Companies change technology vendors. Companies receive funding. Companies launch new products. Companies face new regulations.

This module exists to make every account **alive**.

Every account profile must continuously evolve — automatically — reflecting the real state of that company today, not the state it was in when the AM first added it.

We call this: **Living Account Intelligence.**

---

# Domain Ownership

This module belongs to the **Account Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Arrive at every customer meeting fully informed — knowing the latest news, who the real decision makers are, and what strategic initiatives are underway.

**Frustration:** Today, AM manually researches before every meeting. The information goes stale between meetings. There is no living record.

**Success:** The account profile is always up to date. The AM reads it in 2 minutes before a meeting and walks in fully prepared.

## Secondary User: Sales Manager

**Goal:** Understand the intelligence quality across all accounts in the team.

**Access:** Read access to all accounts in the workspace.

---

# User Stories

## Must Have (MVP)

```
As an Account Manager,
I want a complete company profile for every account,
so that I can understand the company without manual research.

As an Account Manager,
I want the account profile to update automatically,
so that I always have fresh intelligence without maintaining it myself.

As an Account Manager,
I want to see the key decision makers for each account,
so that I know exactly who to contact and their role in the buying process.

As an Account Manager,
I want to see recent news about each account,
so that I have a reason to reach out and a relevant conversation starter.

As an Account Manager,
I want to see the relationship history for each account,
so that I understand the full context of past interactions.
```

## Should Have (V2)

```
As an Account Manager,
I want to see the technology stack the company is currently using,
so that I can identify where my products fit.

As an Account Manager,
I want to be alerted when a key contact changes roles or leaves,
so that I can reach out to maintain the relationship.

As an Account Manager,
I want to see industry trends relevant to this account's business,
so that I can have strategic conversations beyond just product features.

As an Account Manager,
I want to add personal notes that only I can see,
so that I can record context that AI cannot capture.
```

---

# User Flow

## Flow 1: View Account Profile

```
Account Manager selects an account
        ↓
Account Profile page loads with sections:
    - Company Overview (auto-generated, auto-updated)
    - Key Contacts & Decision Makers
    - Recent News & Updates
    - Intelligence Summary (AI-generated)
    - Buying Signals
    - Relationship Timeline
    - Opportunities (linked)
    - Personal Notes
        ↓
AM reads the Intelligence Summary (AI writes this in plain language)
        ↓
AM clicks into specific sections for deeper detail
        ↓
If something is incorrect:
    AM provides correction → AI learns from feedback
```

## Flow 2: Account Created (from Discovery or Manual)

```
AccountDiscovered event received (from Account Discovery)
OR
AM manually creates account
        ↓
Account record created in database
        ↓
AccountCreated event published to NATS
        ↓
Research Employee: Deep company profiling begins (async)
News Employee: News monitoring begins (async)
Relationship Employee: Contact mapping begins (async)
        ↓
As each employee completes:
    AccountIntelligenceUpdated event published
    Profile sections update automatically
        ↓
AM opens profile → sees progressively richer data
```

---

# Functional Requirements

## Company Profile

- Legal company name and registered aliases
- Industry classification (primary and secondary)
- Company size (employee count range, revenue range)
- Founded year and company age
- Headquarters and branch locations
- Business description (AI-generated summary)
- Strategic direction and initiatives
- Completeness score (0–100%) displayed to AM

## Key Contacts and Decision Makers

- Contact name, title, department
- Seniority level (C-Level, VP, Director, Manager)
- Role in buying process (Decision Maker, Influencer, Technical Evaluator, Procurement)
- LinkedIn profile link
- Last interaction date
- Relationship strength indicator

## News and Updates Feed

- Chronological feed of company news
- AI summarizes each article in 2–3 sentences
- Source link included for traceability
- Signal type tagged (expansion, leadership, financial, technology, regulatory)
- Recency indicated (Today, This Week, This Month)

## Intelligence Summary

- AI-generated narrative of current account status
- Written in plain language for the Account Manager
- Includes: key developments, recommended actions, potential risks
- Updated after every significant new information event
- Timestamp and confidence score displayed

## Relationship Timeline

- Chronological log of all interactions: meetings, calls, emails, tasks
- AI-summarized interaction notes
- Action items from past meetings
- Last contact date prominently displayed

## Personal Notes

- Free-text notes visible only to the AM who wrote them
- Stored in Layer 3 of Knowledge Hub (Personal Knowledge)
- Never used to train global AI models

---

# How AI Helps

## Digital Employees Involved

### Account Intelligence Employee (Customer Intelligence Department)
- Triggered by: AccountCreated, AccountUpdated
- Builds and maintains the Company Overview section
- Generates and refreshes Intelligence Summary
- Updates completeness score

### Contact Intelligence Employee (Customer Intelligence Department)
- Maps decision makers and contacts from public sources
- Updates contact seniority and role classifications
- Detects contact role changes (job change signals)

### News Employee (Research Department)
- Monitors news sources continuously for account mentions
- Summarizes articles in 2–3 sentences
- Tags signal type per article

### Industry Research Employee (Research Department)
- Provides industry context relevant to the account
- Updates when significant industry events occur

### Relationship Employee (Customer Intelligence Department)
- Analyzes interaction history to score relationship strength
- Identifies relationship risks (no contact in 90+ days)

## AI Memory

Account Intelligence is the primary consumer of **Long-Term Memory (pgvector)** as defined in `09_DATA_ARCHITECTURE.md`.

Every company research result is embedded and stored for semantic search and future retrieval.

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `AccountDiscovered` | Account Discovery | Trigger initial profile build |
| `DiscoveryAccepted` | Account Discovery | Create account record |
| `MeetingCompleted` | Activity Center | Update relationship timeline |
| `CallLogged` | Activity Center | Update relationship timeline |
| `FeedbackSubmitted` | Digital Workforce Console | Improve AI accuracy |
| `ProposalSubmitted` | Proposal Studio | Update account timeline |
| `OpportunityCreated` | Opportunity Management | Link opportunity to account |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `AccountCreated` | `account.created` | accountId, companyName, workspaceId | All workers |
| `AccountIntelligenceUpdated` | `account.intelligence_updated` | accountId, updateType, workspaceId | Dashboard, Opportunity Management |
| `ContactAdded` | `contact.added` | contactId, accountId, role, workspaceId | Relationship Worker |
| `DecisionMakerIdentified` | `contact.decision_maker_identified` | contactId, accountId, workspaceId | Dashboard, Sales Intelligence |
| `BuyingSignalUpdated` | `account.buying_signal_updated` | accountId, signalType, workspaceId | Dashboard, Opportunity |
| `AccountProfileEnriched` | `account.profile_enriched` | accountId, completenessScore, workspaceId | Dashboard |
| `RelationshipRiskDetected` | `account.relationship_risk_detected` | accountId, riskType, lastContactDate | Dashboard, Notification |

---

# API Endpoints (High Level)

```
GET    /api/v1/accounts                     → List accounts (paginated, filterable)
POST   /api/v1/accounts                     → Create account manually
GET    /api/v1/accounts/:id                 → Get full account profile
PUT    /api/v1/accounts/:id                 → Update account metadata
DELETE /api/v1/accounts/:id                 → Soft delete account

GET    /api/v1/accounts/:id/intelligence    → Get AI intelligence summary
GET    /api/v1/accounts/:id/news            → Get account news feed
GET    /api/v1/accounts/:id/contacts        → Get contacts and decision makers
POST   /api/v1/accounts/:id/contacts        → Add contact manually
GET    /api/v1/accounts/:id/timeline        → Get relationship timeline
POST   /api/v1/accounts/:id/notes           → Add personal note
GET    /api/v1/accounts/:id/notes           → Get personal notes (own only)
POST   /api/v1/accounts/:id/refresh         → Trigger manual intelligence refresh
GET    /api/v1/accounts/:id/completeness    → Get completeness score breakdown
```

---

# Data Model (High Level)

```sql
-- Core Account Record
accounts (
    id                  UUID PRIMARY KEY,
    workspace_id        UUID NOT NULL,
    company_name        VARCHAR NOT NULL,
    company_url         VARCHAR,
    industry            VARCHAR,
    sub_industry        VARCHAR,
    company_size        VARCHAR,          -- small/mid/large/enterprise
    employee_count_min  INTEGER,
    employee_count_max  INTEGER,
    headquarters        VARCHAR,
    founded_year        INTEGER,
    business_summary    TEXT,             -- AI-generated
    completeness_score  INTEGER,          -- 0-100
    status              VARCHAR,          -- active, inactive, archived
    assigned_to         UUID,             -- account manager user id
    source              VARCHAR,          -- discovery, manual
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP,
    deleted_at          TIMESTAMP         -- soft delete
)

-- Contacts / Decision Makers
contacts (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    full_name       VARCHAR NOT NULL,
    title           VARCHAR,
    department      VARCHAR,
    seniority       VARCHAR,              -- c_level, vp, director, manager, individual
    buying_role     VARCHAR,             -- decision_maker, influencer, evaluator, procurement
    linkedin_url    VARCHAR,
    email           VARCHAR,
    phone           VARCHAR,
    is_primary      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- Intelligence Records
account_intelligence (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    intel_type      VARCHAR,             -- summary, news, industry, technology, financial
    content         TEXT,               -- AI-generated content
    source_url      VARCHAR,
    confidence      DECIMAL(3,2),
    generated_by    VARCHAR,            -- which Digital Employee
    valid_until     TIMESTAMP,          -- when this intel expires
    created_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- News Feed
account_news (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    headline        VARCHAR,
    summary         TEXT,               -- AI-summarized
    source_url      VARCHAR,
    published_at    TIMESTAMP,
    signal_type     VARCHAR,
    created_at      TIMESTAMP
)

-- Personal Notes (Layer 3 Knowledge)
account_notes (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    user_id         UUID NOT NULL,      -- private to this user
    content         TEXT,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)
```

**AI Memory (pgvector):**

```
account_embeddings (
    id              UUID,
    account_id      UUID,
    content_type    VARCHAR,            -- summary, news, contact
    embedding       VECTOR(1536),       -- for semantic search
    source_record_id UUID,
    created_at      TIMESTAMP
)
```

---

# MVP Scope

## In MVP

- Company profile with AI-generated summary
- Key contacts display (up to 10 per account)
- News feed (last 30 days)
- Intelligence summary (AI-generated, refreshed daily)
- Relationship timeline (activities and meetings)
- Completeness score
- Personal notes
- Manual account creation
- Trigger manual refresh

## Not in MVP

- Technology stack detection
- Financial intelligence (revenue estimates)
- Org chart visualization
- Contact job-change alerts
- Industry trend overlay
- LinkedIn integration
- CRM import/sync

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Account intelligence completeness score | > 80% average | Completeness score field |
| Accounts with decision maker identified | > 70% | contacts with decision_maker role |
| Time saved per meeting preparation | > 1 hour | User feedback survey |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Intelligence accuracy (human rating) | > 4/5 | FeedbackSubmitted events |
| News relevance score (human rating) | > 3.5/5 | Per-article feedback |
| Profile freshness (updated within 7 days) | > 90% | Updated_at tracking |

## Operational KPIs

| KPI | Target | Measurement |
|---|---|---|
| Profile build time after account creation | < 10 minutes | Workflow latency |
| Daily intelligence refresh completion | > 99% | Temporal metrics |
| Cost per account intelligence update | Tracked | AI Gateway cost |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Discovery | Input | Source of new accounts |
| Knowledge Hub | Input | Research Employee uses workspace knowledge |
| Activity Center | Input | Meetings and calls update timeline |
| Opportunity Management | Bilateral | Opportunities linked to accounts |
| Digital Workforce Console | Output | AM reviews AI work here |
| Dashboard | Output | Account updates appear in Daily Briefing |

---

# Anti-Goals

This module will NOT:

- Replace the AM's personal relationship knowledge with generic AI summaries
- Store or process customer's confidential business data without consent
- Provide legally verified company information (e.g., financial statements)
- Guarantee the accuracy of third-party data sources
- Share account intelligence across workspaces

---

# Final Note

> **"A company is not a static record.**
>
> **It is a living entity that changes every day.**
>
> **This module makes sure the platform knows that."**
