---
title: Database Schema Guide
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 24 — Database Schema Guide

> **"Data outlives code. Code can be rewritten in a weekend; a bad schema will haunt you for a decade. Get the schema right."**

---

# Purpose

This document outlines the strict conventions and architectural patterns for designing the PostgreSQL database schemas in PROJECT BRAIN. Given our multi-tenant SaaS architecture and heavy reliance on AI/Vectors, adhering to these rules is non-negotiable.

---

# 1. Naming Conventions

- **Tables:** `snake_case`, plural noun (e.g., `users`, `opportunities`, `account_intelligence`).
- **Columns:** `snake_case` (e.g., `first_name`, `created_at`).
- **Primary Keys:** Always named exactly `id`. Do not use `user_id` as the primary key of the `users` table.
- **Foreign Keys:** `[singular_table_name]_id` (e.g., `account_id`, `workspace_id`).
- **Indexes:** Prefix with `idx_`, followed by table name and column(s) (e.g., `idx_accounts_workspace_id`).
- **Unique Constraints:** Prefix with `uq_` (e.g., `uq_users_email`).

---

# 2. The Universal Base Schema

EVERY table in the database MUST inherit from a declarative base that includes the following columns, unless there is a highly specific and documented reason not to (like a pure many-to-many join table):

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
workspace_id UUID NOT NULL, -- The anchor for Multi-Tenancy
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
deleted_at TIMESTAMP WITH TIME ZONE NULL
```

### Why `TIMESTAMP WITH TIME ZONE`?
Never use timestamp without timezone. Servers move, developers are in different countries. `TIMESTAMPTZ` ensures the database always stores absolute UTC time and converts it correctly to the client's timezone on read.

---

# 3. Multi-Tenancy (Row-Level Security)

PROJECT BRAIN is a multi-tenant platform. Tenant isolation is our highest security priority.

1. **`workspace_id` is mandatory** on almost every table.
2. **Denormalization for Security:** If Table C belongs to Table B, and Table B belongs to Table A (Workspace), Table C MUST ALSO have `workspace_id`. Do not force a 3-table `JOIN` just to check tenant boundaries. This trades a tiny bit of storage space for massive performance and security gains.
3. **Row-Level Security (RLS):** We enforce isolation at the database layer, not just the application layer.
   - Every table must have RLS enabled: `ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;`
   - A policy must restrict reads/writes to the current transaction's workspace setting.

---

# 4. Soft Deletes (Never DELETE)

We never execute a raw `DELETE` statement against business data. Data is too valuable for AI training, audit logs, and historical context.

1. **Soft Delete:** Set the `deleted_at` timestamp.
2. **Querying:** All standard queries (handled automatically by our SQLAlchemy Base Repository) must append `WHERE deleted_at IS NULL`.
3. **Unique Constraints with Soft Deletes:** If a table has a unique constraint (e.g., `email`), soft-deleting a record prevents a new record from using that email. To fix this, create a unique partial index:
   ```sql
   CREATE UNIQUE INDEX uq_users_email_active ON users (email) WHERE deleted_at IS NULL;
   ```

---

# 5. Data Types

- **IDs:** Always use `UUID` (specifically UUIDv4 generated via `gen_random_uuid()`). Never use auto-incrementing integers (`SERIAL` or `BIGSERIAL`). UUIDs prevent ID guessing (Insecure Direct Object Reference) and make data migration across distributed systems trivial.
- **Money/Financials:** Use `DECIMAL(15,2)` or `NUMERIC`. **NEVER use `FLOAT` or `REAL`** for money due to floating-point rounding errors.
- **Text:** Use `TEXT`. Do not use `VARCHAR(255)`. In PostgreSQL, `TEXT` and `VARCHAR` use the exact same underlying structure, but `VARCHAR(n)` requires extra CPU cycles to enforce the length limit. If you need length validation, enforce it at the application layer (Pydantic).
- **Unstructured Data:** Use `JSONB` (never standard `JSON`). `JSONB` is binary, indexable, and significantly faster for querying nested AI outputs.
- **Vector Embeddings:** Use the `VECTOR(N)` type provided by the `pgvector` extension. Our standard embedding dimension (using `text-embedding-3-small`) is 1536.
   ```sql
   embedding VECTOR(1536)
   ```

---

# 6. Indexing Strategy

1. **Foreign Keys:** PostgreSQL does *not* automatically index foreign keys. You must explicitly create an index on every foreign key column (`workspace_id`, `account_id`, etc.) to prevent massive table scans during JOINs or cascade deletes.
2. **Vector Indexes:** For `pgvector` columns, use the HNSW (Hierarchical Navigable Small World) index type instead of IVFFlat. HNSW provides vastly superior recall and performance for semantic search.
   ```sql
   CREATE INDEX idx_semantic_memory_embedding ON semantic_memory USING hnsw (embedding vector_cosine_ops);
   ```

---

# 7. Schema Migrations (Alembic)

All schema changes MUST be executed via Alembic migrations. **Never manually alter tables in the production database.**

### The Safe Migration Flow:
1. Update your SQLAlchemy models in Python.
2. Generate a revision: `alembic revision --autogenerate -m "add_industry_to_accounts"`
3. **CRITICAL:** Review the generated file. Alembic's `--autogenerate` does not catch everything (it often misses table renames or complex index changes).
4. Ensure the migration is **reversible** (the `downgrade` function must accurately undo the `upgrade` function).
5. Apply migration locally: `alembic upgrade head`.

### Zero-Downtime Rule:
We do not take the system offline for migrations.
- **Adding a column:** Safe. Make it nullable or provide a default.
- **Dropping a column:** **UNSAFE.** First, remove all code references to the column and deploy. In a subsequent release, drop the column via migration.
- **Renaming a column:** **UNSAFE.** Add the new column, dual-write to both, backfill data, switch reads to the new column, and finally drop the old column.
