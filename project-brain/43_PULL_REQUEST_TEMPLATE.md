---
title: Pull Request Template
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 43 — Pull Request Template

> **"A good Pull Request tells a story. What changed, why it changed, and how to prove it works. A PR without context is a PR that gets rejected."**

---

# Purpose

This document provides the mandatory template for Pull Requests (PRs). It ensures reviewers have enough context to review effectively. (This content should be placed in `.github/PULL_REQUEST_TEMPLATE.md` in the root of the repository).

---

# The Template

```markdown
## Description
<!-- Please include a clear summary of the changes and which issue is fixed. Include relevant motivation and context. -->

Fixes # (issue number)

## Type of Change
<!-- Please check the one that applies to this PR using "x". -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] ♻️ Refactor (code restructuring without changing external behavior)
- [ ] 📝 Documentation update
- [ ] 🚀 Performance improvement

## How Has This Been Tested?
<!-- Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. -->
- [ ] **Unit Tests:** (e.g., ran `pytest tests/api/test_accounts.py` - all pass)
- [ ] **Manual Verification:** (e.g., Clicked through the UI, verified the AI response time is under 3 seconds)
- [ ] **AI Evaluation Suite:** (If changing a prompt, did the Golden Dataset score drop?)

## Security & Privacy Checklist (Mandatory)
<!-- If any of these are unchecked, the PR will be blocked. -->
- [ ] 🔒 `workspace_id` tenant isolation has been explicitly verified in all new database queries.
- [ ] 🛡️ User inputs passed to the LLM are enclosed in XML tags to prevent Prompt Injection.
- [ ] 🤐 No PII, API keys, or secrets are hardcoded or printed to the logs.
- [ ] ✅ Input validation (Pydantic/Zod) is strictly applied to all new entry points.

## Screenshots / Screen Recordings
<!-- Add images or gifs here if applicable. This is highly recommended for UI changes. -->

## Definition of Done (DoD) Review
- [ ] My code follows the guidelines in `22_CODING_STANDARDS.md`.
- [ ] I have performed a self-review of my own code using `42_CODE_REVIEW_CHECKLIST.md` (or asked an AI agent to do it using Prompt #4).
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] My changes generate no new warnings (linting passes).
- [ ] If I introduced a new technology or architecture pattern, an ADR (`46_ARCHITECTURE_DECISION_RECORD.md`) has been approved.
```
