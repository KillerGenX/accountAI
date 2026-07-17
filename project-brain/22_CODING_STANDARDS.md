---
title: Coding Standards
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 22 — Coding Standards

> **"Code is read ten times more often than it is written. Optimize for the reader, not the writer. In the era of AI coding, strict standards are the only thing separating velocity from chaos."**

---

# Purpose

This document defines the coding standards for PROJECT BRAIN. With AI capable of writing hundreds of lines of code in seconds, having strict boundaries is the only way to prevent the accumulation of fatal technical debt.

AI Coding Agents **must** check their own generated code against these guidelines before presenting it.

---

# 1. Universal Principles (Backend & Frontend)

### 1.1. No "Magic Strings" or "Magic Numbers"
Never hardcode strings or numbers that carry business meaning directly within the logic.
- ❌ `if status == "PENDING":`
- ✅ `if status == OpportunityStatus.PENDING:` (Use Enums)
- ❌ `retry_after(3)`
- ✅ `retry_after(MAX_RETRY_ATTEMPTS)`

### 1.2. Return Early (Bouncer Pattern)
Avoid deep nested `if/else` blocks. Validate at the beginning of the function and *return/raise error* as early as possible.

```python
# ❌ BAD: Nested logic
def process_data(data):
    if data:
        if data.is_valid:
            # do 50 lines of work
            return True
        else:
            raise ValidationError("Invalid")
    else:
        raise ValueError("No data")

# ✅ GOOD: Return early
def process_data(data):
    if not data:
        raise ValueError("No data")
    if not data.is_valid:
        raise ValidationError("Invalid")
    
    # do 50 lines of work here cleanly
    return True
```

### 1.3. Explicit Error Handling
Never swallow exceptions.
- ❌ `try: do_something() except Exception: pass` (STRICTLY PROHIBITED)
- ✅ Catch specific errors, log them, and either re-raise or handle them gracefully.

---

# 2. Python Backend Standards (FastAPI & AI)

We strictly follow **PEP 8** enforced through a combination of **Black**, **Ruff**, and **Mypy**.

### 2.1. Strict Type Hinting (Mandatory)
All functions, complex variables, and arguments **must** have explicit data types.
- Use Python 3.11+ features like `list[str]`, `dict[str, Any]` (avoid importing `List` or `Dict` from `typing` unless necessary).
- Use `Optional[Type]` or `Type | None` if a value can be `None`.

```python
# ✅ Mandatory format
async def fetch_account_profile(account_id: UUID, db: AsyncSession) -> AccountProfileSchema | None:
    pass
```

### 2.2. Pydantic vs SQLAlchemy Naming
Confusion between Database models and Validation models is common. We prevent this via strict naming.
- **SQLAlchemy Models:** Always use the `Model` suffix or place them in a clear namespace. (e.g., `class Account(Base):`)
- **Pydantic Schemas:** Always use the `Schema` suffix (e.g., `class AccountCreateSchema(BaseModel):` or `class AccountResponseSchema(BaseModel):`).

### 2.3. Asynchronous Purity
Do not block the event loop!
- HTTP calls (LLM API, webhooks) must use asynchronous libraries (e.g., `httpx` or `aiohttp`, NOT `requests`).
- Database access must use SQLAlchemy's *AsyncEngine*.
- If forced to use a synchronous, CPU-bound library, wrap it with `asyncio.to_thread()`.

### 2.4. Docstrings
Use **Google Docstrings** format for core functions, *services*, and *Temporal Activities*. There is no need to document API Routers as they are documented via Pydantic/FastAPI Swagger.

---

# 3. TypeScript Frontend Standards (Next.js)

### 3.1. Strict Typing & No "Any"
- The use of `any` is a standard violation.
- If the data shape is unknown, use `unknown`, then perform *type narrowing* (e.g., using a Zod schema: `parsedData = mySchema.parse(rawData)`).

### 3.2. Clean Functional Components
- A React component file must only have **one** main exported component (default or named).
- Break down a component if it exceeds 150 lines of code.
- Extract complex logic into *Custom Hooks*.

### 3.3. Naming Conventions
- **React Components:** `PascalCase.tsx` (Example: `AccountDashboard.tsx`)
- **Utility Functions/Hooks:** `camelCase.ts` (Example: `useAccountData.ts`)
- **Types/Interfaces:** `PascalCase` (Example: `interface OpportunityData { ... }`)

### 3.4. Server vs Client Components (RSC)
- Components must be **Server Components by default** (do not arbitrarily add `"use client"` at the root of a file).
- Push `"use client"` as far down the component tree as possible (leaf nodes). Only components that require *hooks* (`useState`, `useEffect`) or event listeners (`onClick`) should be Client Components.

---

# 4. Git and Commit Standards

Commit messages must adhere to **Conventional Commits** so the project history can be automatically parsed for a *changelog*.

### Format:
`<type>(<scope>): <subject>`

### Allowed Types:
- `feat`: A new feature for the user
- `fix`: A bug fix
- `docs`: Documentation only changes (like this PRD document)
- `refactor`: A code change that neither fixes a bug nor adds a feature (restructuring)
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Concrete Examples:
- ✅ `feat(account): add semantic search to account discovery`
- ✅ `fix(ui): prevent button overflow on mobile view in console`
- ❌ `added search` (Too short, no type)
- ❌ `fix bug in backend` (Not descriptive)
