---
title: Forecast Center PRD
module: forecast-center
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Medium
mvp: false
domain: Opportunity
---

# Forecast Center

> **"A forecast based on gut feeling is not a forecast. It is a guess."**

---

# Why This Module Exists

Revenue forecasting is one of the most important activities in enterprise sales — and one of the least accurate.

Most AMs submit forecasts based on:
- Personal optimism
- Historical patterns from memory
- Manager pressure

The result is a forecast that is wrong every quarter.

This module creates an AI-adjusted revenue forecast based on objective signals:

- Deal score trends
- Activity frequency
- Buying signal strength
- Stage velocity
- Historical win rate patterns

The Forecast Center transforms forecasting from a political exercise into a data-driven discipline.

---

# Domain Ownership

This module belongs to the **Opportunity Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Submit an accurate forecast with confidence — backed by AI analysis, not gut feeling.

## Secondary User: Sales Manager

**Goal:** See team forecast with AI-adjusted probabilities to make reliable revenue commitments.

---

# User Stories

## Must Have (V2)

```
As an Account Manager,
I want to see an AI-adjusted revenue forecast for my pipeline,
so that I understand what I am likely to close this quarter.

As an Account Manager,
I want to see which deals are most likely to close on time,
so that I can focus effort on the most impactful opportunities.

As an Account Manager,
I want to see which deals are at risk of slipping,
so that I can take action before the quarter ends.

As a Sales Manager,
I want to see the team pipeline forecast with AI adjustments,
so that I can make accurate revenue commitments to leadership.
```

---

# User Flow

## Flow 1: View Forecast

```
Account Manager opens Forecast Center
        ↓
Sees: Current Quarter Forecast Summary

    Human Forecast (AM's own probability):   IDR 5.2B
    AI-Adjusted Forecast:                    IDR 3.8B
    Difference:                              -IDR 1.4B (27% gap)
    Reason: 3 deals show stalling signals
        ↓
Sees: Deal-by-Deal Breakdown

    Each deal shows:
    - Name, Value, Stage, Close Date
    - AM Probability (human-set)
    - AI Probability (AI-calculated)
    - Risk Flags (stalling, competitor threat, close date overdue)
        ↓
AM reviews each at-risk deal
        ↓
AM updates their action plan based on AI signals
```

## Flow 2: Sales Manager View

```
Sales Manager opens Forecast Center → Team View
        ↓
Sees: Team Pipeline Summary
    - Total human forecast: IDR 25B
    - AI-adjusted forecast: IDR 18B
    - Deals at high risk: 7
        ↓
Drills down by Account Manager
        ↓
Identifies AMs with large human vs. AI gap (overforecasting)
        ↓
Schedules coaching conversation
```

---

# Functional Requirements

## Forecast Summary

- Current month and current quarter forecast
- Human forecast (sum of AM-set probability × value)
- AI-adjusted forecast (sum of AI probability × value)
- Gap analysis with top reasons for difference
- Trend vs. previous period

## Deal-Level Forecast

- Per-deal table: name, account, value, stage, close date, AM probability, AI probability
- Risk flags: stalling, competitor, close date overdue, low activity
- Color coded: green (on track), yellow (at risk), red (high risk)
- Sort by: AI probability, value, close date

## Scenario Modeling (V2+)

- Best case: if all at-risk deals close
- Committed: only high-probability deals
- Likely: AI-adjusted expected value

## Historical Accuracy

- Track AM forecast accuracy over past quarters
- Track AI forecast accuracy over past quarters
- Improve AI model with closed deals data

---

# How AI Helps

### Forecast Employee (Sales Intelligence Department)
- Triggered by: OpportunityStageChanged, DealScoreUpdated, OpportunityWon/Lost
- Calculates AI probability per deal
- Identifies forecast risk factors
- Generates: ForecastUpdated event with full breakdown

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `OpportunityCreated` | Opportunity Management | Add to forecast |
| `OpportunityStageChanged` | Opportunity Management | Recalculate forecast |
| `OpportunityWon` | Opportunity Management | Record actual outcome |
| `OpportunityLost` | Opportunity Management | Record actual outcome |
| `DealScoreUpdated` | Opportunity Management | Refresh AI probability |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `ForecastUpdated` | `forecast.updated` | period, humanForecast, aiForecast, workspaceId | Dashboard |
| `ForecastRiskDetected` | `forecast.risk_detected` | opportunityId, riskType, severity | Dashboard, Notification |

---

# API Endpoints (High Level)

```
GET    /api/v1/forecast                     → Current forecast summary
GET    /api/v1/forecast/deals               → Deal-by-deal breakdown
GET    /api/v1/forecast/team                → Team forecast (Sales Manager)
GET    /api/v1/forecast/history             → Historical forecast accuracy
GET    /api/v1/forecast/at-risk             → At-risk deals
```

---

# Data Model (High Level)

```sql
-- Forecast Snapshots (daily)
forecast_snapshots (
    id                  UUID PRIMARY KEY,
    workspace_id        UUID NOT NULL,
    user_id             UUID,           -- null for team-level
    period_type         VARCHAR,        -- month, quarter
    period_label        VARCHAR,        -- "2026-Q3"
    human_forecast      DECIMAL(15,2),
    ai_forecast         DECIMAL(15,2),
    deal_count          INTEGER,
    at_risk_count       INTEGER,
    snapshot_date       DATE,
    created_at          TIMESTAMP
)

-- Per-Deal Forecast Record
forecast_deals (
    id                  UUID PRIMARY KEY,
    snapshot_id         UUID NOT NULL,
    opportunity_id      UUID NOT NULL,
    opportunity_value   DECIMAL(15,2),
    am_probability      INTEGER,        -- 0-100, human-set
    ai_probability      INTEGER,        -- 0-100, AI-calculated
    risk_flags          JSONB,
    close_date          DATE,
    created_at          TIMESTAMP
)
```

---

# MVP Scope

## Not in MVP

This entire module is V2.

## In V2

- Current quarter forecast with AI adjustment
- Deal-by-deal breakdown with risk flags
- Basic team view for Sales Manager

## In Future

- Scenario modeling (best/committed/likely)
- Historical accuracy tracking
- Forecast submission workflow (AM → Manager approval)

---

# KPIs

| KPI | Target | Measurement |
|---|---|---|
| AI forecast accuracy vs. actual | Within 15% of actual closed | Quarterly review |
| Human vs. AI forecast gap | Decrease over time | Snapshot comparisons |
| At-risk deal action rate | > 60% | AM acts after ForecastRiskDetected |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Opportunity Management | Input | All forecast data comes from opportunities |
| Dashboard | Output | Forecast summary card in Daily Briefing (V2) |

---

# Final Note

> **"Forecasting is not about predicting the future.**
>
> **It is about understanding the present clearly enough to prepare for it."**
