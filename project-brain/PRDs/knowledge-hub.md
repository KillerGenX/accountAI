---
title: Knowledge Hub PRD
module: knowledge-hub
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
priority: High
mvp: true
domain: Knowledge
---

# Knowledge Hub

> **"A Digital Employee is only as good as the knowledge it has access to."**

---

# Why This Module Exists

Digital Employees need knowledge to do their work well.

Without knowledge, they produce generic output.

With the right knowledge, they produce relevant, accurate, and actionable intelligence.

The Knowledge Hub is the brain that every Digital Employee reads before doing any work.

It contains three types of knowledge:

1. **Platform-level knowledge** — available to all users
2. **Workspace-level knowledge** — unique to each company (products, pricing, playbooks)
3. **Personal knowledge** — private notes from individual Account Managers

Without the Knowledge Hub, a Research Employee cannot know what products the AM sells. A Proposal Employee cannot know the company's pricing structure. A Competitor Employee cannot know the company's competitive advantages.

This module transforms Digital Employees from generic AI into experts in the AM's specific business.

---

# Domain Ownership

This module belongs to the **Knowledge Domain** as defined in `08_DOMAIN_ARCHITECTURE.md`.

---

# Personas

## Primary User: Workspace Administrator

**Goal:** Upload and maintain the company's product knowledge, pricing, playbooks, and SOPs so that Digital Employees can use them effectively.

**Responsibility:** Keeps workspace knowledge fresh and accurate.

## Secondary User: Enterprise Account Manager

**Goal:** Add personal notes and account context that are private to them.

**Also uses:** Reads knowledge articles when preparing for meetings.

## Tertiary User: Digital Employees (AI)

**Goal:** Query the knowledge base to get relevant context before performing tasks.

**This is the most important "user" of this module.**

---

# User Stories

## Must Have (MVP)

```
As a Workspace Administrator,
I want to upload product knowledge documents,
so that Digital Employees know what products we sell.

As a Workspace Administrator,
I want to upload sales playbooks and SOPs,
so that Digital Employees follow our standard approach.

As a Workspace Administrator,
I want to organize knowledge into categories,
so that employees can find and use knowledge efficiently.

As a Digital Employee,
I want to query the knowledge base with a question,
so that I get relevant context before completing a task.

As an Account Manager,
I want to add personal notes per account,
so that I can record context that AI cannot capture from public sources.
```

## Should Have (V2)

```
As a Workspace Administrator,
I want to upload competitor battlecards,
so that Digital Employees can provide counter-positioning.

As a Workspace Administrator,
I want to add version history to knowledge articles,
so that changes are tracked over time.

As a Workspace Administrator,
I want to see which knowledge articles are most used by Digital Employees,
so that I can prioritize maintaining the most impactful ones.

As an Account Manager,
I want to search the knowledge base in natural language,
so that I can find relevant information quickly before a meeting.
```

---

# The Three Knowledge Layers

## Layer 1 — Platform Knowledge

**Owner:** Platform (managed by Founder/Admin)

**Access:** Read-only for all workspaces

**Content:**
- General market intelligence frameworks
- Best practice templates
- Standard industry classification trees
- Generic sales methodology guides (MEDDIC, Challenger Sale, etc.)

**Cannot be modified by individual tenants.**

---

## Layer 2 — Workspace Knowledge

**Owner:** Each workspace (managed by Workspace Administrator)

**Access:** All users in the workspace can read; Administrator manages content

**Content:**
- Company product catalog (names, descriptions, features, use cases)
- Pricing structure and rate cards
- Sales playbooks and SOPs
- Competitor battlecards and counter-positioning
- Case studies and success stories
- Approved proposal templates
- Company-specific industry focus areas

**This is the most important layer for Digital Employee quality.**

The better this layer is maintained, the better every Digital Employee performs.

---

## Layer 3 — Personal Knowledge

**Owner:** Each individual Account Manager

**Access:** Private — only visible to the owner

**Content:**
- Personal account notes
- Relationship context
- Private meeting observations
- Individual approach preferences

**Personal Knowledge is never used to train global AI models.**

**Personal Knowledge is never visible to other users, including administrators.**

---

# User Flow

## Flow 1: Administrator Adds Product Knowledge

```
Administrator opens Knowledge Hub
        ↓
Navigates to Workspace Knowledge → Products
        ↓
Clicks "Add Article"
        ↓
Fills in:
    - Title
    - Category (Product / Pricing / Playbook / Competitor / Case Study)
    - Content (rich text or file upload)
    - Tags for better searchability
        ↓
Saves article
        ↓
KnowledgeArticleAdded event published
        ↓
Knowledge Indexing Employee:
    - Processes the article
    - Creates embeddings (pgvector)
    - Makes available for semantic search
        ↓
Digital Employees can now use this knowledge
```

## Flow 2: Digital Employee Queries Knowledge

```
Research Employee is building a company profile
        ↓
Needs: "What products do we sell that solve connectivity challenges?"
        ↓
Queries Knowledge Hub via internal API:
    search(query="connectivity solutions", layer=[workspace], workspaceId=X)
        ↓
Semantic search returns top 3 relevant articles
        ↓
Research Employee uses articles as context for company profiling
        ↓
Response includes: which knowledge articles were used (for traceability)
```

## Flow 3: Account Manager Adds Personal Note

```
Account Manager finishes a meeting
        ↓
Opens account profile → Personal Notes tab
        ↓
Types: "CTO prefers concise decks. No more than 8 slides.
        Preferred meeting time: Tuesday mornings."
        ↓
Note saved as Layer 3 knowledge
        ↓
Proposal Employee can access this note when generating proposal
        ↓
Only this Account Manager can see this note
```

---

# Functional Requirements

## Knowledge Article Management

- Create, edit, archive knowledge articles
- Rich text editor for content
- File upload support (PDF, DOCX, XLSX) — extracted and indexed
- Category tagging
- Version history per article
- Active / archived / draft status

## Knowledge Search

- Semantic search (vector-based, powered by pgvector)
- Keyword search fallback
- Layer-aware search (Digital Employees only search layers they have access to)
- Returns: top K results with relevance score and source

## Knowledge Indexing

- Automatic indexing after article creation or update
- File content extraction (PDF, DOCX → text → embedding)
- Re-indexing triggered by KnowledgeArticleUpdated event

## Personal Notes

- Free-text notes per account per user
- Visible only to the author
- Never indexed for workspace-wide search
- Available to Digital Employees only for tasks on that specific account by that specific user

## Knowledge Health Dashboard (Admin)

- Articles by category count
- Last updated per article
- Most-accessed articles by Digital Employees
- Articles not updated in 90+ days (flagged for review)

---

# How AI Helps

### Knowledge Indexing Employee (Knowledge Department)
- Triggered by: KnowledgeArticleAdded, KnowledgeArticleUpdated
- Extracts text from uploaded files
- Creates semantic embeddings
- Indexes for vector search

### Documentation Employee (Knowledge Department)
- Triggered by: OpportunityWon, OpportunityLost
- Suggests what new knowledge should be added based on won/lost patterns
- Produces: "Knowledge Gap Report" for Administrator

---

# Events

## Subscribes To

| Event | Source | Purpose |
|---|---|---|
| `OpportunityWon` | Opportunity Management | Trigger knowledge gap analysis |
| `OpportunityLost` | Opportunity Management | Trigger knowledge gap analysis |
| `FeedbackSubmitted` | Digital Workforce Console | Identify where knowledge is insufficient |

## Publishes

| Event | NATS Subject | Payload | Consumers |
|---|---|---|---|
| `KnowledgeArticleAdded` | `knowledge.article_added` | articleId, category, workspaceId | Indexing Worker |
| `KnowledgeArticleUpdated` | `knowledge.article_updated` | articleId, workspaceId | Indexing Worker |
| `KnowledgeIndexed` | `knowledge.indexed` | articleId, embeddingCount, workspaceId | All AI Workers (ready signal) |
| `KnowledgeGapDetected` | `knowledge.gap_detected` | gapType, description, workspaceId | Notification (to Admin) |

---

# API Endpoints (High Level)

```
# Knowledge Articles
GET    /api/v1/knowledge/articles           → List articles (filterable by layer, category)
POST   /api/v1/knowledge/articles           → Create article (Workspace layer)
GET    /api/v1/knowledge/articles/:id       → Get article detail
PUT    /api/v1/knowledge/articles/:id       → Update article
DELETE /api/v1/knowledge/articles/:id       → Archive article

POST   /api/v1/knowledge/articles/:id/upload → Upload file (PDF, DOCX)

# Search
POST   /api/v1/knowledge/search             → Semantic search
                                              Body: { query, layers, limit, workspaceId }

# Personal Notes (Layer 3)
GET    /api/v1/accounts/:id/notes           → Get personal notes for account
POST   /api/v1/accounts/:id/notes           → Add personal note
PUT    /api/v1/accounts/:id/notes/:noteId   → Update note
DELETE /api/v1/accounts/:id/notes/:noteId   → Delete note

# Admin
GET    /api/v1/knowledge/health             → Knowledge base health metrics
GET    /api/v1/knowledge/gaps               → Knowledge gap report
```

---

# Data Model (High Level)

```sql
-- Knowledge Articles
knowledge_articles (
    id              UUID PRIMARY KEY,
    workspace_id    UUID,               -- NULL for Layer 1 (platform-wide)
    user_id         UUID,               -- NULL for Layer 1 and 2; set for Layer 3
    layer           INTEGER NOT NULL,   -- 1, 2, or 3
    title           VARCHAR NOT NULL,
    content         TEXT,               -- extracted text content
    category        VARCHAR,            -- product, pricing, playbook, competitor, case_study
    tags            JSONB,
    status          VARCHAR,            -- draft, active, archived
    version         INTEGER DEFAULT 1,
    created_by      UUID,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
)

-- Knowledge Embeddings (pgvector)
knowledge_embeddings (
    id              UUID PRIMARY KEY,
    article_id      UUID NOT NULL,
    workspace_id    UUID,
    layer           INTEGER NOT NULL,
    chunk_index     INTEGER,            -- for large articles split into chunks
    chunk_text      TEXT,
    embedding       VECTOR(1536),       -- OpenAI/Gemini embedding dimension
    created_at      TIMESTAMP
)

-- Uploaded Files
knowledge_files (
    id              UUID PRIMARY KEY,
    article_id      UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    file_name       VARCHAR NOT NULL,
    file_type       VARCHAR,            -- pdf, docx, xlsx
    storage_path    VARCHAR NOT NULL,   -- Object Storage path
    extracted_text  TEXT,
    file_size_bytes INTEGER,
    uploaded_by     UUID,
    uploaded_at     TIMESTAMP
)
```

Storage mapping per `09_DATA_ARCHITECTURE.md`:
- Article metadata → **PostgreSQL**
- Embeddings → **pgvector**
- Uploaded files → **Object Storage**

---

# Multi-Tenancy Rules

Layer 1: Shared across all workspaces. Managed by platform.

Layer 2: `workspace_id` is mandatory. Queries are always scoped to `workspace_id`.

Layer 3: `workspace_id` + `user_id` are mandatory. Queries are scoped to both.

**No cross-tenant knowledge access is permitted under any circumstance.**

---

# MVP Scope

## In MVP

- Workspace Knowledge (Layer 2): articles with rich text editor
- Layer 3: personal notes per account
- Basic semantic search for Digital Employees (internal API)
- Knowledge indexing after upload
- File upload: PDF support only in MVP

## Not in MVP

- Layer 1 (Platform Knowledge): platform-wide articles — V2
- Knowledge health dashboard
- Knowledge gap detection
- Version history per article
- DOCX, XLSX file support
- AM-facing search UI (AM can browse but not semantic search in MVP)
- Knowledge usage analytics

---

# KPIs

## Business KPIs

| KPI | Target | Measurement |
|---|---|---|
| Workspace knowledge articles created | > 20 in first month | Article count |
| Digital Employee knowledge queries answered | > 80% with relevant result | Search relevance score |
| Time for new knowledge to become searchable | < 5 minutes | Article created → indexed timestamp |

## AI KPIs

| KPI | Target | Measurement |
|---|---|---|
| Semantic search relevance (AM feedback) | > 4/5 | Feedback on AI outputs citing knowledge |
| Knowledge retrieval accuracy | > 75% | Proportion of retrieved articles used in final AI output |

---

# Dependencies

| Module | Type | Reason |
|---|---|---|
| Account Intelligence | Consumer | Research Employee queries workspace knowledge |
| Account Discovery | Consumer | Research Employee uses knowledge for company profiling |
| Proposal Studio | Consumer | Proposal Employee uses product knowledge and templates |
| Opportunity Management | Consumer | Competitor Employee uses battlecards |
| Settings | Configuration | Administrator manages knowledge from settings |

---

# Anti-Goals

This module will NOT:

- Store customer confidential data uploaded by mistake
- Train global AI models using workspace-private knowledge
- Share Layer 2 knowledge between different workspaces
- Make personal notes (Layer 3) visible to anyone other than the author
- Guarantee real-time updates for external data sources

---

# Final Note

> **"A Digital Employee without knowledge is just a language model.**
>
> **A Digital Employee with knowledge is an expert in your business."**
