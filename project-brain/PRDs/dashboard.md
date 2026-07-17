---
title: Dashboard PRD
module: dashboard
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Core
mvp: true
domain: Account
---

# Dashboard: Daily Briefing

> **"Every morning, the Account Manager should arrive to find work already done."**

---

# Why This Module Exists

The Dashboard is the most important page in the platform.

It is the first thing an Account Manager sees every morning.

It is the proof that the Digital Workforce has been working overnight.

If the Dashboard is empty or irrelevant — the platform has failed.

If the Dashboard shows three accounts worth calling, two buying signals, and one pending proposal review — the Account Manager's day has already been structured by AI.

This module serves one purpose:

**Answer three questions in 60 seconds.**

1. What happened overnight?
2. Who should I contact today?
3. What do I need to prepare?

---

# Domain Ownership

The Dashboard is a read-only aggregation layer.

It reads from all domains but owns no data itself.

It belongs to the **Account Domain** for organizational purposes.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Start every workday knowing exactly what to focus on — without opening individual modules or searching for information.

**Morning routine:** Opens platform. Reviews Dashboard. Acts.

**Success:** The AM closes the Dashboard within 10 minutes — having approved recommendations, identified who to call, and understood today's priorities. No manual searching required.

---

# User Stories

## Must Have (MVP)

```
As an Account Manager,
I want to see new accounts discovered by AI since my last login,
so that I always have fresh leads to review.

As an Account Manager,
I want to see buying signals detected in my existing accounts,
so that I know which accounts are ready to be approached.

As an Account Manager,
I want to see pending recommendations from my Digital Employees,
so that I can approve or reject them in one place.

As an Account Manager,
I want to see which accounts have had important updates overnight,
so that I can reach out with a relevant reason.

As an Account Manager,
I want to see my top priority actions for today,
so that I can structure my day without spending time planning.
```

## Should Have (V2)

```
As an Account Manager,
I want to customize which sections appear on my Dashboard,
so that I see information most relevant to my workflow.

As an Account Manager,
I want to see my pipeline health summary,
so that I understand where my deals stand without opening the full pipeline.

As an Account Manager,
I want the Dashboard to remember my preferences,
so that the most relevant section is always first.
```

---

# User Flow

## Flow 1: Morning Routine

```
08:00 — Account Manager opens platform
              ↓
        Dashboard loads with 5 sections:

        ┌─────────────────────────────────────────┐
        │  GOOD MORNING, [NAME]                   │
        │  Your Digital Employees worked overnight │
        │  Here's what they found.                │
        └─────────────────────────────────────────┘

        Section 1: New Discoveries
        "3 new companies worth reaching out to"
            → PT Adaro Energy — Buying Signal: New CTO hired
            → PT BRI Agro — Signal: Digital transformation initiative
            → PT Teladan Prima — Signal: Expansion to 3 new provinces
            [Review All]

        Section 2: Account Updates
        "5 accounts had significant updates"
            → PT Pertamina — New procurement announcement
            → PT Astra — Q3 earnings released
            [View Updates]

        Section 3: Pending Reviews
        "4 recommendations need your review"
            → Research Complete: PT XYZ — Confidence 87%
            → Buying Signal: PT ABC — Leadership Change
            [Review Now]

        Section 4: Today's Priorities
        "Your top 3 accounts to contact today"
            1. PT Alpha — Strong signal + no contact in 14 days
            2. PT Beta — Proposal sent 7 days ago, no response
            3. PT Gamma — New budget cycle started
            [View Details]

        Section 5: Quick Stats
        "This week: 12 discoveries | 8 signals | 3 accepted accounts"
              ↓
        Account Manager acts on items in order of priority
        Total time: 10–15 minutes
        Rest of day: talking to customers
```

## Flow 2: Real-Time Updates (Intraday)

```
During the day, Digital Employees continue working
        ↓
New significant event occurs (urgent buying signal)
        ↓
Dashboard notification badge updates
        ↓
AM sees notification indicator
        ↓
Opens Dashboard → sees new priority item
        ↓
Reviews and acts
```

---

# Functional Requirements

## Section 1: New Discoveries

- Cards showing new accounts discovered overnight
- Each card: Company name, industry, discovery reason, score, primary buying signal
- CTA: Accept → opens Account Intelligence
- CTA: Reject → removes with reason
- "View All" link → opens Account Discovery module
- Shows max 5 items; remainder in Account Discovery

## Section 2: Account Updates

- List of existing accounts with significant overnight updates
- Update type displayed: news, leadership change, financial update, etc.
- Sorted by: signal strength + account priority
- CTA: View Account → opens account profile
- Shows max 5 items

## Section 3: Pending Reviews

- Count and preview of unreviewed recommendations from Digital Workforce Console
- Sorted by: urgency first
- CTA: Review Now → opens Digital Workforce Console
- Badge count always visible in navigation
- Shows max 5 items

## Section 4: Today's Priorities

- AI-generated list of top 3 accounts the AM should contact today
- Each item includes: Account name, reason (why today), recommended action
- Reason is specific: not "this account is important" but "no contact in 14 days + new budget cycle announcement"
- CTA: View Account

## Section 5: Quick Stats

- This week summary: Discoveries / Signals / Accepted Accounts / Meetings Logged
- Simple numeric display, no charts in MVP

## Performance

- Dashboard must load in under 2 seconds
- Data is pre-computed and cached in Redis
- Real-time badge counts use server-sent events (SSE)

---

# How AI Builds the Dashboard

The Dashboard does not call AI in real-time.

The Dashboard **reads pre-computed results** from all other modules.

```
Overnight:
    Account Discovery Worker → stores discoveries
    Account Intelligence Worker → stores intelligence updates
    Buying Signal Worker → stores signals
    Opportunity Worker → stores deal priorities

Morning:
    Dashboard Priority Engine → aggregates all outputs
    → Selects top 5 from each section
    → Calculates "Today's Priorities" from all signals
    → Stores final Dashboard snapshot in Redis cache

Account Manager opens Dashboard:
    → Reads from Redis cache (< 200ms)
    → Live recommendation count from database
```

### Dashboard Priority Employee

This is a lightweight orchestration worker that:
- Runs daily at 06:00 workspace timezone
- Reads from all domain outputs
- Produces the day's prioritized Dashboard content
- Stores result in Redis for fast retrieval

---

# Events

## Subscribes To (for badge updates)

| Event | Purpose |
|---|---|
| `AccountDiscovered` | Increment new discovery count |
| `AccountScored` | Update discovery section |
| `BuyingSignalDetected` | Update account updates section |
| `RecommendationApproved` | Decrement pending review count |
| `RecommendationRejected` | Decrement pending review count |
| `AccountIntelligenceUpdated` | Update account updates section |

## Publishes

None.

The Dashboard is a read-only aggregation view. It publishes no events.

---

# API Endpoints (High Level)

```
GET    /api/v1/dashboard                    → Full Dashboard payload (cached)
GET    /api/v1/dashboard/discoveries        → New discoveries section
GET    /api/v1/dashboard/updates            → Account updates section
GET    /api/v1/dashboard/pending-count      → Pending recommendation count (live)
GET    /api/v1/dashboard/priorities         → Today's priorities section
GET    /api/v1/dashboard/stats              → Weekly stats section

POST   /api/v1/dashboard/refresh            → Force refresh (bypasses cache)
```

---

# Data Model (High Level)

The Dashboard owns no permanent data.

It reads from:
- `discovery_candidates` table (Account Discovery)
- `account_intelligence` table (Account Intelligence)
- `buying_signals` table (Account Discovery)
- `recommendations` table (Digital Workforce Console)

Cache model:

```
Redis Keys:

dashboard:{workspaceId}:{userId}:snapshot  → Full pre-computed Dashboard JSON
dashboard:{workspaceId}:{userId}:pending_count → Integer count
TTL: 6 hours (refreshed by overnight worker at 06:00)
```

---

# MVP Scope

## In MVP

- All 5 sections above
- Pre-computed overnight cache
- Real-time pending recommendation count badge
- Dismiss/accept quick actions on discovery cards

## Not in MVP

- Pipeline health section
- Customizable section order
- Historical Dashboard archive ("What did my Dashboard look like last Monday?")
- Mobile-optimized layout (comes with mobile app in V3)
- Notification center (V2)

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Daily Dashboard open rate | > 80% of active users | Session tracking |
| Actions taken from Dashboard per session | > 2 | Click tracking |
| Time to act after opening Dashboard | < 15 minutes | Session duration |

## Quality KPIs

| KPI | Target | Measurement |
|---|---|---|
| Today's Priority acceptance rate | > 60% | AM acts on recommended account |
| Dashboard load time | < 2 seconds | API response time |
| Overnight refresh completion | By 06:00 every day | Temporal workflow SLA |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Discovery | Input | New discoveries section |
| Account Intelligence | Input | Account updates section |
| Digital Workforce Console | Input | Pending review count and section |
| Opportunity Management | Input | Today's priorities (V2) |
| All AI Workers | Input | All events contribute to Dashboard content |

---

# Anti-Goals

This module will NOT:

- Store its own data (it reads from other modules)
- Make decisions or recommendations itself
- Show data from other workspaces
- Replace the deeper functionality of each individual module
- Be the only entry point to the platform (each module is accessible directly)

---

# Final Note

> **"The Dashboard is not a feature.**
>
> **It is the promise of the platform fulfilled every morning."**
