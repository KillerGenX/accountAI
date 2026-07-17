---
title: API Guidelines
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 23 — API Guidelines

> **"An API is a contract. Make it predictable, consistent, and hard to misuse. A good API teaches the developer how to use it just by looking at the payload."**

---

# Purpose

This document defines the REST API standards for PROJECT BRAIN. All endpoints built using FastAPI must strictly adhere to these guidelines to ensure the frontend (and future external consumers) have a seamless and secure integration experience. 

Inconsistencies in API design lead to massive technical debt in frontend state management. Conformity is mandatory.

---

# 1. Base URL & Versioning

All API routes must be versioned at the URL level. We are currently on `v1`.

- **Base Path:** `/api/v1`
- **Example:** `/api/v1/accounts`

Do not introduce `v2` without a major architecture decision (ADR) and a deprecation plan for `v1`. Non-breaking changes (like adding a new field to a response) go into `v1`.

---

# 2. Resource Naming (URL Paths)

1. **Use Plural Nouns:** Always use plural nouns for resources, never verbs. The HTTP method acts as the verb.
   - ✅ `GET /api/v1/users` (Good)
   - ❌ `POST /api/v1/getUser` (Bad)
   - ❌ `GET /api/v1/user` (Bad)
2. **Kebab-case:** Use kebab-case for URLs.
   - ✅ `/api/v1/opportunity-products`
   - ❌ `/api/v1/opportunity_products`
3. **Nesting Limits:** Nest resources logically to indicate relationships, but avoid going deeper than 2 levels to prevent URL fatigue.
   - ✅ `/api/v1/accounts/{account_id}/opportunities` (Good)
   - ❌ `/api/v1/workspaces/{id}/accounts/{id}/opportunities/{id}` (Too deep. Query opportunities directly via their own endpoint or via the account).

---

# 3. Standard Response Formats (JSend Inspired)

Every endpoint must return a structured JSON response. Returning raw arrays or un-wrapped objects makes it impossible to add metadata later without breaking the contract.

## 3.1. Success Response (Single Resource)

```json
{
  "status": "success",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "PT Pertamina",
    "industry": "Energy"
  },
  "meta": {
    "timestamp": "2026-07-17T10:00:00Z",
    "request_id": "req-xyz-789"
  }
}
```

## 3.2. Collection Success Response (with Pagination)

```json
{
  "status": "success",
  "data": [
    { "id": "...", "name": "..." },
    { "id": "...", "name": "..." }
  ],
  "meta": {
    "pagination": {
      "total_count": 145,
      "current_page": 1,
      "page_size": 20,
      "total_pages": 8,
      "has_next": true
    },
    "request_id": "req-xyz-789"
  }
}
```

## 3.3. Error Response (RFC 7807 Standard)

Error responses must be actionable. The frontend needs to know exactly which field failed and why.

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The provided data is invalid.",
    "details": [
      {
        "field": "email",
        "issue": "must be a valid email address format"
      },
      {
        "field": "revenue",
        "issue": "must be greater than 0"
      }
    ]
  },
  "meta": {
    "request_id": "req-xyz-789",
    "docs_url": "https://api.project-brain.com/docs/errors#VALIDATION_FAILED"
  }
}
```

---

# 4. HTTP Status Codes

Strictly use standard status codes. Do not return `200 OK` with an error payload (the GraphQL anti-pattern).

- **200 OK:** Success for `GET`, `PUT`, `PATCH`.
- **201 Created:** Success for `POST` (when a resource is newly created). Must include the `Location` header pointing to the new resource.
- **204 No Content:** Success for `DELETE`. (No body returned).
- **400 Bad Request:** Validation failure, missing parameters, or malformed JSON.
- **401 Unauthorized:** Missing, expired, or invalid JWT. (Who are you?)
- **403 Forbidden:** Valid JWT, but the user lacks permission for this specific resource (e.g., wrong workspace, insufficient role). (I know who you are, but you can't do this).
- **404 Not Found:** Resource does not exist or has been soft-deleted.
- **409 Conflict:** Resource state conflict (e.g., trying to create an account with an email that already exists).
- **429 Too Many Requests:** Rate limit exceeded.
- **500 Internal Server Error:** Unhandled backend crash. Should trigger an immediate alert to observability tools.

---

# 5. Pagination, Filtering, and Sorting

All endpoints returning collections MUST be paginated by default. Do not allow returning the entire database table.

**Standard Query Parameters:**
- `page`: default 1
- `page_size`: default 20, max 100
- `sort_by`: field name (e.g., `created_at`)
- `sort_dir`: `asc` or `desc`

**Filtering Pattern:**
Use query parameters for exact matches and simple filters.
`/api/v1/opportunities?stage=negotiation&min_value=1000000`

For complex searches (e.g., semantic search or full-text search), use a dedicated `POST /search` endpoint to avoid URL length limits and encode complex query objects securely.

---

# 6. Idempotency

Mutating endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) should strive to be idempotent, especially when interacting with external systems or payments.

For critical `POST` actions (e.g., triggering a long-running AI workflow), require an `Idempotency-Key` header from the client.
- If a request is received with an `Idempotency-Key` that has already been processed successfully, return the cached successful response immediately without re-processing.
- This prevents duplicate records if the frontend retries a request due to a network timeout.

---

# 7. Workspace Isolation (The Prime Directive)

**Security Rule:** EVERY endpoint (except public authentication endpoints) MUST validate that the requested resource belongs to the `workspace_id` of the authenticated user.

- Do NOT rely on the frontend to pass the `workspace_id` in the URL or body payload for authorization.
- Extract the `workspace_id` directly from the JWT / Session context on the server side via a FastAPI Dependency (`Depends(get_current_workspace)`).
- Inject this `workspace_id` into every Service layer function call to ensure database queries are inherently scoped.

```python
# ✅ SECURE: workspace_id comes from the validated token, not the client request body.
@router.get("/{account_id}")
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace)
):
    return await account_service.get_account(db, workspace.id, account_id)
```
