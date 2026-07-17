---
title: Settings and Administration PRD
module: settings-administration
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: Required
mvp: true
domain: Administration
---

# Settings and Administration

> **"A platform that cannot be configured cannot be trusted."**

---

# Why This Module Exists

Every workspace is different.

A telco enterprise team has different products, different pricing, and different playbooks than an IT systems integrator.

Every Account Manager has different territory boundaries and different discovery preferences.

The Settings module makes the platform configurable per workspace and per user — without requiring code changes.

It also provides the workspace foundation that every other module depends on: workspace creation, user management, and the initial configuration that determines how Digital Employees behave.

---

# Domain Ownership

This module belongs to the **Administration Domain** (generic domain) as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Workspace Administrator

**Goal:** Set up and maintain the workspace so that Digital Employees work correctly and Account Managers can be productive from day one.

## Secondary User: Enterprise Account Manager

**Goal:** Configure personal preferences: territory, notification preferences, and display settings.

---

# User Stories

## Must Have (MVP)

```
As a Workspace Administrator,
I want to create a workspace with my company information,
so that my team can start using the platform.

As a Workspace Administrator,
I want to invite Account Managers to the workspace,
so that my team can access the platform.

As a Workspace Administrator,
I want to configure roles and permissions,
so that each user has the right level of access.

As an Account Manager,
I want to configure my discovery territory,
so that AI discovers accounts relevant to my area.

As a Workspace Administrator,
I want to see AI usage and cost summary,
so that I can monitor platform costs.

As a Workspace Administrator,
I want to configure which Digital Employees are active,
so that I control which AI capabilities are running.
```

## Should Have (V2)

```
As a Workspace Administrator,
I want to configure Knowledge Hub categories,
so that the knowledge base structure matches our organization.

As a Workspace Administrator,
I want to set alert thresholds for AI costs,
so that I receive a notification before costs exceed budget.

As an Account Manager,
I want to configure notification preferences,
so that I control which alerts I receive and how.
```

---

# Functional Requirements

## Workspace Setup

- Workspace name and company information
- Industry and geographic focus
- Timezone configuration (affects Dashboard refresh schedule)
- Logo upload (used in exported proposals)
- Default currency

## User Management

- Invite users by email
- Roles:
  - **Administrator:** Full access. Manages workspace, users, knowledge.
  - **Account Manager:** Full access to own accounts. Cannot manage workspace settings.
  - **Sales Manager:** Read access to team data. Cannot edit other AMs' accounts.
- Pending invitations management
- Deactivate / remove users

## Digital Employee Configuration

- List of all available Digital Employees
- Enable / disable per employee
- Configuration per employee: sensitivity thresholds, cost limits
- SLA configuration: when overnight jobs must complete

## Territory Configuration (per Account Manager)

- Target industries (multi-select)
- Geographic focus (region, city, province)
- Company size range
- Discovery keywords
- Account exclusion list
- Accessible to AM in personal settings

## Notification Settings (per user)

- Email notifications: on/off per event type
- In-app notifications: on/off per event type
- Event types: new discovery, buying signal, stall alert, recommendation ready

## AI Cost Settings

- Monthly budget alert threshold
- Cost alert recipient
- Current month usage dashboard (read-only summary)

## Workspace Data

- Data retention policies (future)
- Export workspace data (future)

---

# How AI Helps

No Digital Employees operate within this module.

Settings is a human-operated configuration module.

One exception: the **WorkspaceConfigured** event triggers all Digital Employees to refresh their configuration.

---

# Events

## Subscribes To

None.

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `WorkspaceConfigured` | `workspace.configured` | workspaceId, changedFields | All Digital Employees |
| `UserAdded` | `workspace.user_added` | userId, role, workspaceId | Access control, Notification |
| `UserDeactivated` | `workspace.user_deactivated` | userId, workspaceId | Access control |
| `DiscoveryCriteriaUpdated` | `discovery.criteria_updated` | userId, criteria, workspaceId | Account Discovery Worker |
| `EmployeeConfigured` | `workforce.employee_configured` | employeeId, config, workspaceId | Specific Digital Employee |

---

# API Endpoints (High Level)

```
# Workspace
GET    /api/v1/workspace                    → Get workspace settings
PUT    /api/v1/workspace                    → Update workspace settings
POST   /api/v1/workspace/logo               → Upload workspace logo

# Users
GET    /api/v1/workspace/users              → List workspace users
POST   /api/v1/workspace/users/invite       → Invite user by email
PUT    /api/v1/workspace/users/:id/role     → Change user role
DELETE /api/v1/workspace/users/:id          → Deactivate user

GET    /api/v1/workspace/invitations        → List pending invitations
DELETE /api/v1/workspace/invitations/:id    → Cancel invitation

# Digital Employees
GET    /api/v1/workspace/employees          → List Digital Employees with config
PUT    /api/v1/workspace/employees/:id      → Update employee config
POST   /api/v1/workspace/employees/:id/enable  → Enable employee
POST   /api/v1/workspace/employees/:id/disable → Disable employee

# Personal Settings (Account Manager)
GET    /api/v1/me/settings                  → Get personal settings
PUT    /api/v1/me/settings                  → Update personal settings
GET    /api/v1/me/territory                 → Get territory criteria
PUT    /api/v1/me/territory                 → Update territory criteria
GET    /api/v1/me/notifications             → Get notification preferences
PUT    /api/v1/me/notifications             → Update notification preferences

# Cost
GET    /api/v1/workspace/costs              → Monthly AI cost summary
```

---

# Data Model (High Level)

```sql
-- Workspaces
workspaces (
    id              UUID PRIMARY KEY,
    name            VARCHAR NOT NULL,
    company_name    VARCHAR,
    industry        VARCHAR,
    timezone        VARCHAR NOT NULL DEFAULT 'Asia/Jakarta',
    currency        VARCHAR(3) DEFAULT 'IDR',
    logo_url        VARCHAR,
    status          VARCHAR DEFAULT 'active',
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
)

-- Users
users (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    email           VARCHAR NOT NULL,
    full_name       VARCHAR,
    role            VARCHAR NOT NULL,  -- administrator, account_manager, sales_manager
    status          VARCHAR,           -- active, inactive, pending
    invited_by      UUID,
    invited_at      TIMESTAMP,
    joined_at       TIMESTAMP,
    last_login_at   TIMESTAMP,
    created_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- User Personal Settings
user_settings (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL UNIQUE,
    workspace_id    UUID NOT NULL,
    notification_preferences  JSONB,
    display_preferences       JSONB,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
)

-- Digital Employee Configuration
employee_configs (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    employee_name   VARCHAR NOT NULL,
    is_enabled      BOOLEAN DEFAULT TRUE,
    config          JSONB,             -- employee-specific settings
    cost_limit_usd  DECIMAL(10,2),
    updated_at      TIMESTAMP
)
```

---

# MVP Scope

## In MVP

- Workspace creation and basic configuration
- User invite and role management (Administrator, Account Manager)
- Territory configuration per Account Manager
- Digital Employee enable/disable
- Basic AI cost summary view

## Not in MVP

- Sales Manager role (V2 — requires team visibility features)
- Custom notification preferences (all notifications on by default in MVP)
- Cost alert thresholds
- Data retention policies
- Workspace data export

---

# KPIs

| KPI | Target | Measurement |
|---|---|---|
| Time to workspace setup completion | < 30 minutes | Created_at → first account created |
| Users invited within first week | > 1 additional user | UserAdded events |
| Territory configured per AM | 100% before first discovery run | discovery_criteria filled |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| All modules | Foundational | Workspace and user identity underlies everything |
| Account Discovery | Output | Territory criteria flows to discovery |
| Knowledge Hub | Output | Admin manages knowledge from here |
| Digital Workforce Console | Output | Employee config available here |

---

# Security Notes

Per `03_ENGINEERING_CONSTITUTION.md` and Security Constitution:

- Workspace isolation is enforced at database level (row-level security)
- All API endpoints validate workspace membership before returning data
- Role-based access control is enforced in API layer
- No cross-workspace data access under any circumstances
- Invitation tokens expire after 7 days

---

# Anti-Goals

This module will NOT:

- Allow self-registration without an invitation
- Allow data export that crosses workspace boundaries
- Store passwords (authentication handled by dedicated auth service)
- Allow Administrator to read Account Manager's personal notes

---

# Final Note

> **"Configuration is not a feature.**
>
> **It is the foundation that makes every other feature work."**
