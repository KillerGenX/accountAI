---
title: Bug Report Template
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 45 — Bug Report Template

> **"A bug report without reproduction steps is just a complaint. Help the engineer (or the AI) help you."**

---

# Purpose

This document provides the mandatory template for reporting bugs in PROJECT BRAIN. A well-written bug report allows a human engineer (or an AI Debugging Agent) to quickly identify the root cause without having to ask a dozen follow-up questions.

(This content should be placed in `.github/ISSUE_TEMPLATE/bug_report.md`).

---

# The Template

```markdown
## 🐞 Bug Description
<!-- Provide a clear and concise description of what the bug is. Is the AI hallucinating? Did the UI crash? Did a database save fail? -->

## 🔄 Reproduction Steps
<!-- Steps to reproduce the behavior: -->
1. Log in as '...' (Workspace ID: ...)
2. Go to '...'
3. Click on '....'
4. Enter the following text: '...'
5. See error / unexpected behavior.

## 🎯 Expected Behavior
<!-- A clear and concise description of what you expected to happen. -->

## 💥 Actual Behavior
<!-- What actually happened. Include explicit error messages if applicable. -->

## 📸 Screenshots / Screen Recordings
<!-- If applicable, add screenshots or videos to help explain your problem. Visual context is invaluable for frontend bugs. -->

## 🖥️ Environment Information
- **OS:** [e.g. Windows 11, macOS Sonoma]
- **Browser:** [e.g. Chrome 120, Safari 17]
- **Environment:** [e.g. Local, Staging, Production]

## 🔍 Additional Context (Logs/Traces)
<!-- Add any other context about the problem here. -->
- **Trace ID / Request ID:** [If visible in the UI error toast, paste it here. This is critical for backend debugging.]
- **Timestamp:** [When did this happen? (UTC preferred)]
- **Console Errors:** [Paste any red errors from the browser's Developer Tools Console]
```
