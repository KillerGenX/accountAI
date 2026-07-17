---
title: Proposal Studio PRD
module: proposal-studio
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: High
mvp: false
domain: Opportunity
---

# Proposal Studio

> **"A proposal that takes days to prepare will always lose to one prepared in hours."**

---

# Why This Module Exists

Preparing a commercial proposal is one of the most time-consuming tasks in enterprise sales.

A complete proposal package typically includes:

- Company-specific cover letter
- Executive Summary
- Solution Overview
- High Level Design (HLD)
- Bill of Quantity (BoQ)
- Pricing
- Business Case
- Terms and Conditions
- Timeline

Today, an Account Manager and Solutions Engineer spend 2–5 days preparing this manually.

They search for the right product information. They build the BoQ from scratch. They write the executive summary from memory. They create the business case with spreadsheets.

This module changes that.

The Proposal Studio, powered by Digital Employees, generates a complete proposal draft in minutes — using account intelligence, opportunity context, and workspace knowledge.

The Account Manager reviews and refines.

The Digital Workforce prepared.

---

# Domain Ownership

This module belongs to the **Opportunity Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Enterprise Account Manager

**Goal:** Generate a high-quality proposal draft in minutes, not days.

**Frustration:** Today, proposal preparation takes most of the AM's time before a deal closes. The work is repetitive — the same structure every time, only the details change.

## Secondary User: Solutions Engineer (in future phases)

**Goal:** Review and validate technical sections (HLD) of the proposal.

---

# User Stories

## Must Have (V2)

```
As an Account Manager,
I want to generate a proposal draft by selecting an account and opportunity,
so that I start from a complete draft instead of a blank page.

As an Account Manager,
I want the proposal to include relevant products from our catalog,
so that I don't have to manually look up specifications.

As an Account Manager,
I want to generate a Bill of Quantity automatically,
so that pricing calculations are done for me.

As an Account Manager,
I want to generate an Executive Summary tailored to the customer's context,
so that the proposal speaks directly to their business needs.

As an Account Manager,
I want to edit, refine, and download the final proposal,
so that I control the final version before sending.

As an Account Manager,
I want all proposals to be saved with version history,
so that I can track changes and revert if needed.
```

## Should Have (V2+)

```
As an Account Manager,
I want to generate a Business Case with ROI analysis,
so that I can justify the investment to the customer's finance team.

As an Account Manager,
I want to use pre-approved templates from the Knowledge Hub,
so that the proposal format is consistent with company branding standards.

As an Account Manager,
I want to see which knowledge articles were used in the proposal,
so that I can verify the accuracy of product information.
```

---

# User Flow

## Flow 1: Generate New Proposal

```
Account Manager opens Proposal Studio
        ↓
Selects: Account + Opportunity
        ↓
Proposal Employee reads:
    - Account Intelligence (company context, decision makers)
    - Opportunity data (products, value, stage)
    - Knowledge Hub Layer 2 (product specs, pricing, templates)
    - Personal Notes Layer 3 (AM's specific context for this account)
        ↓
Generates proposal sections in parallel:
    - Executive Summary Employee
    - BoQ Employee
    - Solution Design Employee
    - Business Case Employee
        ↓
ProposalDraftReady event published
        ↓
AM receives notification: "Your proposal draft is ready"
        ↓
AM opens draft in Proposal Editor:
    - Reviews each section
    - Edits where needed
    - Approves or adjusts BoQ items
    - Sets final pricing
        ↓
AM downloads PDF or exports to DOCX
        ↓
ProposalSubmitted event published (when sent to customer)
```

## Flow 2: Version Management

```
AM needs to revise a proposal
        ↓
Opens existing proposal
        ↓
Makes edits
        ↓
Saves as new version (v1 → v2)
        ↓
Both versions retained in history
        ↓
AM can compare versions side by side
```

---

# Functional Requirements

## Proposal Generation

- Select account + opportunity as context
- Generate multi-section proposal draft automatically
- Generation time target: < 3 minutes for complete draft
- Progress indicator during generation (section by section)

## Proposal Sections

Each section is independently generated and editable:

| Section | Generator | Source Knowledge |
|---|---|---|
| Cover Letter | Proposal Employee | Account name, AM name, date |
| Executive Summary | Executive Summary Employee | Account intelligence, opportunity |
| Customer Challenge | Proposal Employee | Account intelligence, industry knowledge |
| Proposed Solution | Solution Design Employee | Opportunity products, product knowledge |
| High Level Design | Solution Design Employee | Technical product knowledge (V2+) |
| Bill of Quantity | BoQ Employee | Product catalog, pricing |
| Investment Summary | Pricing Employee | BoQ output, pricing rules |
| Business Case | Business Case Employee | Account financials, product ROI data |
| Implementation Timeline | Proposal Employee | Product delivery standard timelines |

## Proposal Editor

- Rich text editor per section
- Inline AI suggestions ("Improve this paragraph")
- Table editor for BoQ
- Image insertion for diagrams (HLD)
- Comment and annotation (for internal review)

## BoQ Builder

- Line items: product name, quantity, unit price, total
- Auto-calculated subtotals
- Discount field per line or total
- Tax configuration per workspace
- Export to Excel

## Version History

- Every save creates a version snapshot
- Named versions (Draft v1, Sent to Customer, Revised v2)
- Version comparison view
- Restore previous version

## Export

- Export to PDF (branded with workspace logo)
- Export to DOCX (for further editing in Word)
- Export BoQ to XLSX

---

# How AI Helps

### Proposal Employee (Proposal Department)
- Orchestrates the proposal generation workflow
- Writes: Cover Letter, Customer Challenge, Implementation Timeline
- Reads: account intelligence, opportunity data

### Executive Summary Employee (Proposal Department)
- Writes: Executive Summary section
- Tailored to the specific customer's strategic priorities
- Uses: account intelligence, industry knowledge

### BoQ Employee (Proposal Department)
- Generates: Bill of Quantity from opportunity products
- Uses: product catalog from Knowledge Hub, pricing rules
- Validates: product codes, descriptions, and standard pricing

### Business Case Employee (Proposal Department)
- Generates: Business Case with ROI analysis
- Uses: account intelligence (company size, revenue), product ROI data
- Produces: 3-year cost-benefit analysis

### Solution Design Employee (Proposal Department)
- Generates: Proposed Solution section
- Uses: product knowledge, opportunity requirements

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `OpportunityCreated` | Opportunity Management | Make opportunity available for proposal |
| `AccountIntelligenceUpdated` | Account Intelligence | Refresh context for active proposals |
| `KnowledgeIndexed` | Knowledge Hub | Signal that new product knowledge is available |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `ProposalCreated` | `proposal.created` | proposalId, accountId, opportunityId | Opportunity Management, Audit |
| `ProposalDraftReady` | `proposal.draft_ready` | proposalId, sections, workspaceId | Digital Workforce Console, Notification |
| `ProposalSubmitted` | `proposal.submitted` | proposalId, accountId, submittedAt | Opportunity Management (stage update), Audit |
| `BoQGenerated` | `proposal.boq_generated` | proposalId, lineItemCount, totalValue | Opportunity Management |

---

# API Endpoints (High Level)

```
GET    /api/v1/proposals                    → List proposals (by account or opportunity)
POST   /api/v1/proposals                    → Create and generate new proposal
GET    /api/v1/proposals/:id                → Get proposal with all sections
PUT    /api/v1/proposals/:id                → Update proposal (saves new version)
DELETE /api/v1/proposals/:id                → Archive proposal

GET    /api/v1/proposals/:id/sections       → Get all sections
PUT    /api/v1/proposals/:id/sections/:name → Update specific section

GET    /api/v1/proposals/:id/boq            → Get BoQ
PUT    /api/v1/proposals/:id/boq            → Update BoQ items

GET    /api/v1/proposals/:id/versions       → Get version history
POST   /api/v1/proposals/:id/restore/:ver  → Restore to version

POST   /api/v1/proposals/:id/export/pdf     → Export to PDF
POST   /api/v1/proposals/:id/export/docx    → Export to DOCX
POST   /api/v1/proposals/:id/boq/export     → Export BoQ to XLSX

POST   /api/v1/proposals/:id/submit         → Mark as submitted to customer
```

---

# Data Model (High Level)

```sql
-- Proposals
proposals (
    id              UUID PRIMARY KEY,
    workspace_id    UUID NOT NULL,
    account_id      UUID NOT NULL,
    opportunity_id  UUID,
    title           VARCHAR NOT NULL,
    status          VARCHAR,           -- draft, in_review, submitted, archived
    current_version INTEGER DEFAULT 1,
    created_by      UUID,
    submitted_at    TIMESTAMP,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- Proposal Versions
proposal_versions (
    id              UUID PRIMARY KEY,
    proposal_id     UUID NOT NULL,
    version_number  INTEGER NOT NULL,
    version_label   VARCHAR,           -- "Draft v1", "Sent to Customer"
    created_by      UUID,
    created_at      TIMESTAMP
)

-- Proposal Sections
proposal_sections (
    id              UUID PRIMARY KEY,
    proposal_id     UUID NOT NULL,
    version_id      UUID NOT NULL,
    section_name    VARCHAR NOT NULL,  -- executive_summary, boq, solution, etc.
    content         TEXT,              -- rich text / HTML
    generated_by    VARCHAR,           -- Digital Employee name
    is_ai_generated BOOLEAN DEFAULT TRUE,
    last_edited_by  UUID,
    updated_at      TIMESTAMP
)

-- Bill of Quantity
proposal_boq_items (
    id              UUID PRIMARY KEY,
    proposal_id     UUID NOT NULL,
    version_id      UUID NOT NULL,
    line_number     INTEGER,
    product_name    VARCHAR NOT NULL,
    product_code    VARCHAR,
    quantity        DECIMAL(10,2),
    unit            VARCHAR,
    unit_price      DECIMAL(15,2),
    discount_pct    DECIMAL(5,2) DEFAULT 0,
    total_price     DECIMAL(15,2),
    notes           TEXT,
    is_optional     BOOLEAN DEFAULT FALSE
)
```

Files (exported PDFs, DOCX) stored in **Object Storage** per `09_DATA_ARCHITECTURE.md`.

---

# MVP Scope

## Not in MVP

This entire module is V2.

In MVP, AM can use Knowledge Hub to manually access product information for self-prepared proposals.

## In V2

- Full proposal generation workflow
- All 9 proposal sections
- BoQ builder
- PDF and DOCX export
- Version history
- Executive Summary tailored to account

## In V2+ (Future)

- Business Case with ROI calculator
- HLD diagram generation
- Solutions Engineer review workflow
- Customer portal for proposal viewing

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Proposal preparation time reduction | > 70% vs. manual | AM time tracking survey |
| Proposals generated per AM per month | Increase vs. baseline | ProposalCreated events |
| Proposal acceptance rate (customer) | Tracked over time | ProposalSubmitted + opportunity Won |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Executive Summary quality (AM rating) | > 4/5 | Post-generation rating |
| BoQ accuracy (items correct without editing) | > 80% | Edit rate tracking |
| Proposal generation time | < 3 minutes | Workflow latency |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Intelligence | Input | Customer context for tailored proposals |
| Opportunity Management | Input | Products, value, stage for BoQ |
| Knowledge Hub | Input | Product catalog, pricing, templates |
| Digital Workforce Console | Output | AM reviews generated proposal here |

---

# Anti-Goals

This module will NOT:

- Send proposals directly to customers without AM review and approval
- Guarantee legal accuracy of Terms and Conditions sections
- Replace the Solutions Engineer for complex HLD designs (MVP)
- Store customer-provided confidential specifications

---

# Final Note

> **"The proposal is where the sale is won or lost.**
>
> **Give the Account Manager more time to sell — not more time to type."**
