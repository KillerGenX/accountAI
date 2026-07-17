---
title: AI Evaluation Framework
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 20 — AI Evaluation Framework

> **"You cannot improve what you cannot measure. You cannot trust what you cannot evaluate."**

---

# Purpose

Digital Employees must be evaluated continuously.

Not as a one-time launch check, but as an ongoing operational discipline.

This document defines:
- What to measure (quality dimensions)
- How to measure it (methods and data sources)
- When to measure (cadence)
- What to do with the results (action triggers)
- How to improve (optimization cycle)

---

# Evaluation Philosophy

## What We Are Evaluating

We are not evaluating the LLM.

We are evaluating the **Digital Employee as a system** — including:
- The quality of its SOP
- The quality of its context engineering
- The quality of its reasoning strategy
- The quality of its tool usage
- The quality of its output

A poor output is almost never the LLM's fault alone. It is a system design problem.

## Who Evaluates

Three evaluators work together:

| Evaluator | Role | Weight |
|---|---|---|
| Account Manager | Real-world feedback on recommendations | 50% |
| Automated metrics | Objective measurements (latency, cost, errors) | 30% |
| Periodic AI review | AI-assisted quality assessment of output samples | 20% |

---

# Quality Dimensions

Every Digital Employee is evaluated on five dimensions:

---

## Dimension 1 — Accuracy

**Definition:** Is the output factually correct?

**Measurement:**
- Primary: AM feedback (approved / rejected / corrected)
- Secondary: Spot-check by Founder (monthly, sample of 10 outputs)
- Tertiary: AI reviewer comparing output to source documents

**Metric:**
```
Accuracy Rate = (Approved + Corrected_minor) / Total_reviewed
Target: > 70% across all employees
```

**Data source:** `ai_results.am_feedback` + `recommendation_feedback`

---

## Dimension 2 — Relevance

**Definition:** Is the output relevant to what the AM actually needs?

**Measurement:**
- AM acceptance rate (accepted = relevant)
- AM rejection reason (if "not relevant" = relevance failure)
- Time AM spends reading output (low engagement = low relevance)

**Metric:**
```
Relevance Rate = Accepted / Total_shown
Target: > 60% for recommendations
        > 80% for intelligence summaries (level 1 auto-display)
```

---

## Dimension 3 — Timeliness

**Definition:** Does the output arrive when the AM needs it?

**Measurement:**
- SLA compliance: Was the overnight job complete by 08:00?
- Research completion time: < 2 minutes per account
- Response time for on-demand tasks: < 5 minutes

**Metric:**
```
SLA Compliance = tasks_completed_on_time / total_tasks
Target: > 99%
```

**Data source:** `ai_task_log.started_at` vs `ai_task_log.completed_at` vs SLA definition

---

## Dimension 4 — Cost Efficiency

**Definition:** Is the output worth what it costs?

**Measurement:**
- Cost per task (tokens × model price)
- Cost per accepted recommendation
- Cost per AM per month

**Metric:**
```
Cost per Accepted Recommendation = total_cost / accepted_recommendations
Target: Decreasing over time as prompts improve
```

**Data source:** `ai_task_log.cost_usd` + `recommendation_feedback`

---

## Dimension 5 — Improvement Trajectory

**Definition:** Is the employee getting better over time?

**Measurement:**
- Accuracy trend (improving, stable, degrading?)
- Acceptance rate trend
- AM feedback sentiment trend

**Metric:**
```
Improvement Rate = (metric_this_month - metric_last_month) / metric_last_month
Target: Positive or stable for all employees
Alert: If any metric degrades > 10% month-over-month
```

---

# Evaluation Data Sources

| Source | Data | Captured By |
|---|---|---|
| `ai_results` | Task outputs, confidence, tokens, cost | Automatic |
| `recommendation_feedback` | AM approval/rejection/feedback | AM via Console |
| `ai_task_log` | Latency, errors, success/failure | Automatic |
| Spot-check review | Qualitative output quality | Founder monthly |

---

# Evaluation Cadence

## Daily (Automated)

- Task success/failure rate per employee
- SLA compliance rate
- Cost per employee
- Error rate

Delivered as: Dashboard card in Admin view (AI Operations)

Trigger alerts if:
- Error rate > 5%
- SLA compliance < 95%
- Cost spike > 2× daily average

---

## Weekly (Automated + Human)

- Acceptance rate per employee (7-day rolling)
- Accuracy rate per employee (7-day rolling)
- Cost trend vs. previous week
- Top 3 rejected recommendations + reason analysis

Delivered as: Email summary to workspace administrator

---

## Monthly (Human-Assisted)

- Full performance review per employee
- Sample 10 random outputs per employee → quality review
- Compare against previous month trends
- Identify employees requiring SOP updates
- Review and update confidence thresholds if needed

Delivered as: Monthly AI Performance Report document

---

## Quarterly (Strategic)

- Employee version review — which employees need major update?
- Compare AI forecast vs actual outcomes (deal scoring accuracy)
- Review employee roadmap vs V2 plan alignment
- Evaluate new capabilities or tools to add

---

# Scoring Dashboard

Each Digital Employee has a scorecard:

```
Employee: Company Research Employee
Version: 1.0.0
Review Period: July 2026

┌─────────────────────────────────────────────────┐
│ DIMENSION          SCORE    TARGET    TREND      │
├─────────────────────────────────────────────────┤
│ Accuracy           74%      >70%      ↑ +4%     │
│ Relevance          68%      >60%      → stable   │
│ Timeliness         99.1%    >99%      ✅         │
│ Cost/Task          $0.031   Tracked   ↓ -12%    │
│ Improvement        ↑        Positive  ✅         │
├─────────────────────────────────────────────────┤
│ OVERALL STATUS: ✅ PERFORMING WELL               │
│ ACTION REQUIRED: None                            │
└─────────────────────────────────────────────────┘
```

---

# Performance Alert Thresholds

| Condition | Severity | Action |
|---|---|---|
| Accuracy < 50% for 7 days | Critical | Disable employee, investigate SOP |
| Acceptance rate < 30% for 7 days | High | Review context engineering |
| SLA compliance < 90% | High | Review tool failures and infrastructure |
| Cost spike > 3× average | Medium | Review prompt efficiency |
| Error rate > 10% | High | Investigate tool failures |
| Confidence score average < 0.5 | Medium | Review knowledge quality |

---

# Improvement Cycle

When an employee underperforms, follow this cycle:

```
Step 1: Identify the failure mode
    What type of task is failing?
    Is it accuracy, relevance, or timeliness?

Step 2: Sample failing outputs
    Get 5 examples of poor outputs
    Read the reasoning trace

Step 3: Identify root cause
    Bad context? → Fix context engineering
    Bad reasoning? → Fix SOP steps or reasoning strategy
    Bad knowledge? → Update Knowledge Hub
    Bad tool? → Fix tool implementation
    Wrong model? → Try different model for this task

Step 4: Fix and test
    Make one change at a time
    Test in staging
    Measure improvement

Step 5: Deploy new version
    Increment employee version
    Document in changelog
    Monitor for 7 days after deployment
```

---

# A/B Testing Framework

For significant changes to employee behavior, use A/B testing:

```
Version A: Current production employee (70% of tasks)
Version B: New experimental employee (30% of tasks)

Measure for: 14 days minimum
Compare: Accuracy, acceptance rate, cost

Decision:
  If B outperforms A on all dimensions: promote B to production
  If B underperforms: discard B, document findings
  If mixed: iterate on B
```

**Implementation:** Task routing randomly assigns versions based on workspace configuration.

---

# Employee Retirement Policy

An employee is retired when:

1. It is replaced by a better version (V2 employee)
2. Its accuracy degrades below 40% and cannot be recovered
3. Its function is merged into another employee
4. The product module it serves is deprecated

Retirement process:
1. Set status to `deprecated` in employee definition
2. Route all new tasks to replacement employee
3. Allow in-flight tasks to complete
4. Archive employee definition (never delete)
5. Retain all episodic memory (historical record)

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `13_DIGITAL_EMPLOYEE_TEMPLATE.md` | Section 11 (Evaluation) uses this framework |
| `04_AI_CONSTITUTION.md` | All measurement must respect privacy and traceability rules |
| `PRDs/digital-workforce-console.md` | AM feedback is collected here |
| `29_OBSERVABILITY.md` | Technical metrics collected via observability stack |

---

# Final Principle

> **"An employee that is never evaluated is never trusted.**
>
> **An employee that is continuously evaluated and improved**
>
> **becomes irreplaceable."**
