---
title: Architecture Decision Record (ADR)
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 46 — Architecture Decision Record (ADR)

> **"Code tells you how the system works. An ADR tells you why the system works that way. Without the 'Why', future developers (and AI agents) will unknowingly dismantle your careful design."**

---

# Purpose

An Architecture Decision Record (ADR) is a short markdown document that captures an important architectural decision made along with its context and consequences. We store these in a `docs/adrs/` folder within the codebase.

Whenever we decide to introduce a new major technology, change a core pattern, or deviate from the guidelines established in Layer 5 (e.g., deciding to use a NoSQL database for a specific module instead of PostgreSQL), an ADR MUST be written and approved by the Chief Architect.

---

# The Importance of ADRs for AI Coding Agents

AI Coding Agents have limited context windows. They cannot read every Slack message, email thread, or meeting transcript to understand *why* we chose PostgreSQL over MongoDB, or *why* we use Temporal instead of Celery. 

By documenting the *Why* in an ADR, we provide the AI with the exact historical and logical context for the system's design. This prevents the AI from accidentally refactoring our code into an anti-pattern just because that anti-pattern happens to be common on StackOverflow.

---

# ADR Template

```markdown
# ADR [Number]: [Short Noun Phrase Describing the Decision]

**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Rejected | Superseded by ADR-XXX]

## 1. Context
<!-- What is the issue that we're seeing that is motivating this decision or change? Describe the technological, business, and project context. -->
*Example: We need to store high-dimensional embeddings for our semantic search feature. Currently, we are using PostgreSQL for relational data.*

## 2. Decision
<!-- What is the change that we're proposing and/or doing? -->
*Example: We will use the `pgvector` extension inside our existing PostgreSQL database instead of provisioning a separate vector database like Pinecone or Milvus.*

## 3. Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
### Positive
- [Benefit 1] *Example: Reduces operational overhead; no new infrastructure to manage.*
- [Benefit 2] *Example: Allows us to perform JOINs between relational tenant data and vector data in a single query, ensuring strict RLS security.*

### Negative
- [Drawback 1] *Example: PostgreSQL might consume more RAM/CPU as the vector index grows compared to a specialized vector database.*
- [Drawback 2] *Example: `pgvector` index building locks the table temporarily.*

## 4. Alternatives Considered
- [Alternative 1]: *Pinecone.* Rejected because it adds a third-party dependency, increases cost, and complicates tenant isolation (data sync issues between Postgres and Pinecone).
- [Alternative 2]: *Milvus.* Rejected because it requires standing up additional complex infrastructure (etcd, MinIO) which is overkill for our current scale.
```
