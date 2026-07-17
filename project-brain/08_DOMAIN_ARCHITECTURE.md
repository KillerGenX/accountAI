---
title: Domain Architecture
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: true
---

# 🏢 Domain Architecture

> **"Technology changes. Business domains endure."**

---

# Purpose

This document defines the core business domains of the platform.

Business Domains represent the permanent language of the product.

Every feature, API, database table, event, Digital Employee, and workflow must belong to a business domain.

Technology may change.

Domains should remain stable.

---

# Domain Philosophy

The platform is built using **Domain-Driven Design (DDD).**

Domains own:

- Business Rules
- APIs
- Events
- Data
- Workflows
- Digital Employees

No feature exists outside a domain.

---

# Core Domain Map

```text
Workspace
│
├── Organization
│
├── Users
│
├── Accounts
│   ├── Contacts
│   ├── Branches
│   ├── Relationships
│   ├── Intelligence
│   ├── Documents
│   └── Timeline
│
├── Opportunities
│   ├── Pipeline
│   ├── Forecast
│   ├── Competitors
│   ├── Products
│   ├── Solutions
│   ├── Quotations
│   └── Business Case
│
├── Activities
│   ├── Calls
│   ├── Meetings
│   ├── Emails
│   ├── WhatsApp
│   ├── Tasks
│   └── Notes
│
├── Knowledge
│   ├── Product Knowledge
│   ├── Industry Knowledge
│   ├── Company Knowledge
│   ├── Sales Playbook
│   └── Documents
│
├── AI Platform
│   ├── Digital Employees
│   ├── AI Gateway
│   ├── Memory
│   ├── Prompt Library
│   ├── Evaluation
│   └── AI Tasks
│
├── Notifications
│
├── Search
│
├── Analytics
│
└── Administration
```

---

# Domain Classification

The platform contains three categories of domains.

## Core Domains

These create the product's competitive advantage.

Examples:

- Account
- Opportunity
- AI Platform
- Knowledge

These receive the highest engineering investment.

---

## Supporting Domains

Support business operations.

Examples:

- Activities
- Notifications
- Documents
- Search

These enhance the platform but are not differentiators.

---

## Generic Domains

Commodity capabilities.

Examples:

- Authentication
- Authorization
- Settings
- Audit Logs
- File Storage

Reuse existing solutions whenever possible.

---

# Domain: Workspace

The root domain.

Responsibilities:

- Organizations
- Multi-tenancy
- Workspaces
- Teams
- Roles
- Permissions

Everything belongs to a Workspace.

---

# Domain: Account

The heart of the platform.

The Account is not a CRM record.

The Account is a continuously evolving business entity.

Owns:

- Company Profile
- Industry
- Contacts
- Branches
- Relationships
- Intelligence
- Financial Insights
- News
- Documents
- Timeline

Primary Goal:

Create a **Living Account Intelligence** profile.

---

# Domain: Contact

Represents people inside an Account.

Examples:

- Decision Makers
- Influencers
- Technical Contacts
- Procurement
- Finance
- Executives

Tracks:

- Relationships
- Communication History
- Social Profiles
- Job Changes
- Responsibilities

---

# Domain: Opportunity

Represents potential business.

Owns:

- Pipeline
- Sales Stage
- Products
- Solutions
- Revenue
- Competitors
- Risks
- Forecast
- Probability

Every Opportunity belongs to exactly one Account.

---

# Domain: Activity

Captures every interaction.

Includes:

- Meetings
- Calls
- Emails
- WhatsApp
- Notes
- Follow Ups
- Tasks

Activities become organizational memory.

---

# Domain: Proposal

Owns customer-facing commercial documents.

Examples:

- Proposal
- Quotation
- Bill of Quantity
- High Level Design
- Scope of Work
- Business Case

AI assists in creating these artifacts.

---

# Domain: Knowledge

The intelligence center.

Stores:

- Product Knowledge
- Industry Knowledge
- Competitor Knowledge
- Customer Knowledge
- Best Practices
- Sales Playbooks

Every Digital Employee learns from this domain.

---

# Domain: AI Platform

Responsible for every Digital Employee.

Owns:

- AI Gateway
- Prompt Library
- Memories
- Evaluations
- AI Tasks
- AI Logs
- AI Metrics
- AI Cost Tracking

This domain never contains customer business logic.

---

# Domain: Search

Provides unified search.

Supports:

- Semantic Search
- Keyword Search
- Hybrid Search
- AI Search

Search spans all domains.

---

# Domain: Notification

Responsible for communication.

Channels include:

- Email
- In-App
- WhatsApp
- Slack
- Teams
- Push Notification

Notification never owns business logic.

---

# Domain: Analytics

Transforms operational data into insights.

Provides:

- Dashboards
- KPIs
- Pipeline Analytics
- Sales Performance
- AI Performance
- Forecast Accuracy

Analytics is read-only.

---

# Domain Relationships

```text
Workspace
│
├── Users
│
├── Accounts
│      │
│      ├── Contacts
│      ├── Activities
│      ├── Documents
│      └── Intelligence
│
├── Opportunities
│      │
│      ├── Proposal
│      ├── Forecast
│      └── Products
│
├── Knowledge
│
└── AI Platform
       │
       ├── Research Employee
       ├── Proposal Employee
       ├── Forecast Employee
       ├── Relationship Employee
       └── News Employee
```

---

# Domain Ownership Rules

Every feature belongs to exactly one domain.

Every API belongs to exactly one domain.

Every event belongs to exactly one domain.

Every database table belongs to exactly one domain.

No shared ownership.

---

# Domain Communication

Domains communicate through:

- Public APIs
- Events
- Published Contracts

Never through internal implementation.

---

# Domain Evolution

Domains may grow.

Domains should rarely split.

Domains should almost never merge.

Stability is a design goal.

---

# AI Domain Alignment

Every Digital Employee must have a home domain.

Examples:

Research Employee

→ Account

Proposal Employee

→ Proposal

Forecast Employee

→ Opportunity

Meeting Employee

→ Activity

Knowledge Employee

→ Knowledge

AI belongs to the business—not outside it.

---

# Future Domains

Reserved for future expansion.

Examples:

- Marketplace
- Partner Management
- Customer Success
- Billing
- Revenue Intelligence
- Contract Management
- Customer Health
- Renewal Management

The architecture anticipates growth.

---

# Domain Success Criteria

A successful domain:

- Has a single responsibility.
- Owns its data.
- Publishes events.
- Exposes clear APIs.
- Is independently testable.
- Can evolve without impacting unrelated domains.

---

# Final Principle

> **Business domains are the permanent language of the platform.**

> **Everything else is an implementation detail.**