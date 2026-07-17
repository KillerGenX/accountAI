---
title: Activity and Meeting Center PRD
module: activity-meeting-center
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: High
mvp: false
domain: Activity
---

# Activity and Meeting Center

> **"Every conversation is a data point. Every meeting is an opportunity to learn."**

---

# Why This Module Exists

Every customer interaction contains valuable intelligence.

A phone call reveals a budget decision. A meeting reveals a new stakeholder. An email reveals a competitor is being evaluated. A WhatsApp message reveals urgency.

Today, this intelligence is trapped in the Account Manager's memory, personal notes, or a brief CRM log entry that says: "Meeting with customer."

This module captures every interaction, processes it with AI, and transforms it into organizational intelligence that feeds back into Account Intelligence and Opportunity Management.

Every meeting becomes smarter than the last.

Every conversation makes the next proposal better.

---

# Domain Ownership

This module belongs to the **Activity Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Log customer interactions quickly and let AI extract the intelligence — without spending 30 minutes writing meeting notes.

**Frustration:** Writing detailed meeting notes takes too long. CRM log entries are minimal because no one has time. Intelligence from meetings is lost within days.

**Success:** AM speaks 2 minutes of voice notes after a meeting. AI generates a full summary, extracts action items, identifies signals, and updates the account profile automatically.

---

# User Stories

## Must Have (V2)

```
As an Account Manager,
I want to log a meeting note with minimal effort,
so that customer interactions are always recorded without taking time away from selling.

As an Account Manager,
I want AI to generate a meeting summary automatically,
so that I don't have to write detailed notes myself.

As an Account Manager,
I want AI to extract action items from my meeting notes,
so that I never forget a follow-up commitment.

As an Account Manager,
I want to see a full interaction timeline for each account,
so that I understand the complete history before any meeting.

As an Account Manager,
I want to log a call with a short note,
so that all touchpoints are captured even for brief interactions.
```

## Should Have (Future)

```
As an Account Manager,
I want to record voice notes after a meeting and have AI transcribe them,
so that logging is as fast as speaking.

As an Account Manager,
I want AI to identify mentions of competitors, budget signals, or timeline changes in my notes,
so that important intelligence is automatically flagged.

As an Account Manager,
I want upcoming meetings to be auto-populated from my calendar,
so that I don't need to manually create meeting records.
```

---

# User Flow

## Flow 1: Log Meeting Note

```
Account Manager finishes a customer meeting
        ↓
Opens Activity Center or Account Profile → Timeline tab
        ↓
Clicks "Log Meeting"
        ↓
Fills in:
    - Account linked (auto-suggested based on recent activity)
    - Meeting date and duration
    - Participants (contacts from account)
    - Raw notes (free text — bullet points, rough language, okay)
        ↓
Submits
        ↓
MeetingCompleted event published
        ↓
Meeting Employee processes note:
    - Generates structured summary
    - Extracts action items with owners and due dates
    - Identifies signals: competitor mentions, budget signals, stakeholder changes
    - Suggests: next recommended action
        ↓
MeetingNoteCreated event published
        ↓
Account profile timeline updates automatically
        ↓
AM sees: clean summary, action items, and AI insight cards
```

## Flow 2: View Account Timeline

```
Account Manager prepares for a meeting
        ↓
Opens Account Profile → Timeline
        ↓
Sees chronological history:
    - All meetings (summarized by AI)
    - All calls logged
    - All emails noted
    - All proposals sent
    - Buying signals detected
    - Account intelligence updates
        ↓
AM reads last 3 interactions in 2 minutes
        ↓
Walks into meeting fully prepared
```

## Flow 3: Task Management

```
AI extracts action item from meeting:
"Follow up with HLD draft by Friday"
        ↓
ActionItemExtracted event published
        ↓
Task created automatically:
    - Title: "Send HLD draft to PT XYZ"
    - Due: Friday
    - Linked to: Meeting record, Account, Contact
        ↓
Task appears in AM's task list
        ↓
AM completes task → marks done
        ↓
Account timeline updated: "HLD draft sent"
```

---

# Functional Requirements

## Activity Types

The module supports:

- Meeting (in-person or virtual)
- Phone Call
- Email (manually logged)
- Task / Follow-up
- Note (freeform observation)

## Meeting Log

- Link to account and contacts
- Date, duration, location/platform
- Participants from account contacts
- Raw notes field (free text)
- AI-generated summary (separate from raw notes)
- AI-extracted action items
- AI-identified signals

## AI Meeting Processing

- Generate structured summary in 3–5 bullet points
- Extract action items with: description, assigned to, due date
- Identify signal mentions: competitor, budget, decision maker change, timeline, project
- Suggest: recommended next action

## Timeline View

- Chronological feed of all activities per account
- Mixed types: meetings, calls, emails, signals, intelligence updates, proposal events
- Filter by: activity type, date range
- Expandable: click to read full summary

## Task Management (Basic)

- Task created from action item extraction
- Or manually created
- Fields: title, account, contact, due date, notes
- Status: open, in progress, completed
- Overdue tasks highlighted

## Relationship Intelligence

- Last contact date per account (visible in account profile header)
- No-contact alert: accounts with no activity in configurable days
- This feeds the Relationship Risk Detection event

---

# How AI Helps

### Meeting Employee (Customer Intelligence Department)
- Triggered by: MeetingCompleted event
- Processes raw meeting notes
- Generates: structured summary, action items, signal tags, next action recommendation
- Produces: MeetingNoteCreated event with enriched data

### Relationship Employee (Customer Intelligence Department)
- Monitors: last contact date per account
- Detects: accounts approaching relationship risk threshold
- Produces: RelationshipRiskDetected event for Dashboard alert

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `ProposalSubmitted` | Proposal Studio | Add to account timeline automatically |
| `OpportunityCreated` | Opportunity Management | Add to account timeline |
| `OpportunityStageChanged` | Opportunity Management | Add to account timeline |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `MeetingCompleted` | `meeting.completed` | meetingId, accountId, participantIds | Account Intelligence, Opportunity, Meeting Worker |
| `MeetingNoteCreated` | `meeting.note_created` | meetingId, summary, actionItems, signals | Account Intelligence, Dashboard |
| `ActionItemExtracted` | `activity.action_item_extracted` | taskId, meetingId, description, dueDate | Task system |
| `CallLogged` | `activity.call_logged` | activityId, accountId, duration | Account Intelligence |
| `SignalMentionedInMeeting` | `meeting.signal_mentioned` | meetingId, signalType, description | Account Intelligence, Opportunity |
| `RelationshipRiskDetected` | `account.relationship_risk_detected` | accountId, daysSinceContact, riskLevel | Dashboard, Notification |

---

# API Endpoints (High Level)

```
# Activities
GET    /api/v1/activities                   → List activities (by account, type, date)
POST   /api/v1/activities/meeting           → Log meeting with notes
POST   /api/v1/activities/call              → Log call
POST   /api/v1/activities/note              → Add freeform note

GET    /api/v1/activities/:id               → Get activity detail
PUT    /api/v1/activities/:id               → Update activity
DELETE /api/v1/activities/:id               → Soft delete

GET    /api/v1/activities/:id/summary       → Get AI-generated meeting summary
GET    /api/v1/activities/:id/action-items  → Get extracted action items

# Account Timeline
GET    /api/v1/accounts/:id/timeline        → Full chronological timeline for account

# Tasks
GET    /api/v1/tasks                        → List open tasks for AM
POST   /api/v1/tasks                        → Create task manually
PUT    /api/v1/tasks/:id                    → Update task
POST   /api/v1/tasks/:id/complete           → Mark task as done
```

---

# Data Model (High Level)

```sql
-- Activities
activities (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    opportunity_id  UUID,
    user_id         UUID NOT NULL,
    activity_type   VARCHAR NOT NULL,    -- meeting, call, email, note, task
    title           VARCHAR,
    raw_notes       TEXT,               -- what AM typed
    ai_summary      TEXT,               -- AI-generated structured summary
    ai_signals      JSONB,              -- competitor, budget, timeline mentions
    next_action     TEXT,               -- AI-suggested next step
    meeting_date    TIMESTAMP,
    duration_min    INTEGER,
    location        VARCHAR,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- Activity Participants
activity_participants (
    id              UUID PRIMARY KEY,
    activity_id     UUID NOT NULL,
    contact_id      UUID NOT NULL,
    role            VARCHAR            -- host, attendee, no_show
)

-- Action Items / Tasks
tasks (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID,
    opportunity_id  UUID,
    activity_id     UUID,              -- source meeting (if extracted)
    assigned_to     UUID NOT NULL,
    title           VARCHAR NOT NULL,
    description     TEXT,
    due_date        DATE,
    status          VARCHAR,           -- open, in_progress, completed, cancelled
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)
```

---

# MVP Scope

## Not in MVP

This entire module is V2.

In MVP, Account Managers can add personal notes inside Account Intelligence (Layer 3 Knowledge Hub).

Full activity tracking and AI meeting processing is V2.

## In V2

- Meeting log with AI summary and action item extraction
- Call logging
- Account timeline view
- Task management (basic)
- Relationship risk detection

## In Future

- Voice note recording and transcription
- Calendar integration (auto-populate upcoming meetings)
- Email thread context capture
- WhatsApp integration

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Meeting logging rate | > 80% of customer meetings | Meetings logged / estimated meetings |
| Action items completed on time | > 70% | Task completion rate |
| Accounts with no contact alert reduction | Decrease over time | RelationshipRiskDetected events |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Meeting summary quality (AM rating) | > 4/5 | Post-summary rating |
| Action item extraction accuracy | > 80% relevant | AM edit rate |
| Signal detection accuracy | > 70% | AM confirmation rate |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Intelligence | Output | Meeting content enriches account profile |
| Opportunity Management | Bilateral | Activities linked to opportunities |
| Dashboard | Output | Relationship risk alerts appear in Daily Briefing |
| Digital Workforce Console | Output | Meeting summaries are Level 1 (auto-displayed) |

---

# Anti-Goals

This module will NOT:

- Record customer conversations without explicit consent
- Store confidential customer information shared in meetings beyond what AM logs
- Replace CRM meeting logging (it extends it)
- Automatically email customers based on action items

---

# Final Note

> **"Every meeting is an investment.**
>
> **This module makes sure the return on that investment never gets lost."**
