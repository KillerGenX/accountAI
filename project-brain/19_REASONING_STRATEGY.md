---
title: Reasoning Strategy
version: 1.0.0
status: Approved
owner: Founder
last_updated: 2026-07-17
review_cycle: Quarterly
ai_required: false
---

# 19 — Reasoning Strategy

> **"The quality of a Digital Employee's output is determined by the quality of its thinking. Design the thinking, not just the output."**

---

# Purpose

A Digital Employee is not just a language model that produces text.

It is a worker that must **think** through a problem in a structured way before producing output.

This document defines the reasoning strategies that Digital Employees use — when to use each strategy, how to implement it, and what guarantees each strategy provides.

---

# Why Reasoning Strategy Matters

An LLM that answers immediately often answers wrongly.

An LLM that thinks step-by-step makes far fewer errors.

This is not a theoretical claim. It is a measured empirical finding across all major AI research labs.

By designing the reasoning strategy for each Digital Employee, we control the *quality of thinking* — and therefore the quality of every output.

---

# Three Reasoning Strategies

---

## Strategy 1 — Chain of Thought (CoT)

**What it is:** The employee explicitly reasons step by step before producing a final answer.

**Best for:** Analysis, scoring, classification, summarization.

**Pattern:**

```
User input → 
Employee thinks:
  "Step 1: What is being asked?"
  "Step 2: What information do I have?"
  "Step 3: What are the possible interpretations?"
  "Step 4: What is the most supported conclusion?"
→ Final answer based on reasoning chain
```

**Implementation in System Context:**

```
Before producing your final output, reason through the task explicitly.

Reasoning format:
<thinking>
Step 1: [Your observation]
Step 2: [Your analysis]
Step 3: [Your conclusion]
Confidence: [Explain why you are or are not confident]
</thinking>

Then provide your final structured output.
```

**When to use:**
- Account Scoring Employee (scoring a company)
- Buying Signal Employee (classifying a signal)
- Risk Assessment Employee (assessing deal risk)

**Guarantee:** Reduces factual errors by 30–40% on classification tasks.

---

## Strategy 2 — ReAct (Reason + Act)

**What it is:** The employee alternates between reasoning and taking tool actions until it has enough information to produce output.

**Best for:** Research tasks requiring multiple information sources.

**Pattern:**

```
Task received →
Thought: "I need to find information about X"
Action: [call web_search tool]
Observation: [web search results]

Thought: "I found Y but still need Z"
Action: [call web_search tool again]
Observation: [more results]

Thought: "I now have enough information"
Final: [Produce structured output]
```

**Implementation in System Context:**

```
You must gather information before answering.

For each step, state:
Thought: [What you need to find or do]
Action: [tool_name(input)]
Observation: [What you found]

Repeat until you have sufficient information.

Then produce your final answer.
Maximum iterations: [N] (prevents infinite loops)
```

**When to use:**
- Company Research Employee (multi-step web research)
- News Employee (monitoring multiple sources)
- Contact Intelligence Employee (finding decision makers)

**Guard:** Maximum iteration limit is mandatory. Prevents infinite loops and cost explosions.

---

## Strategy 3 — Plan and Execute

**What it is:** The employee first creates a complete plan, then executes it step by step.

**Best for:** Complex multi-section output, proposal generation, long-form analysis.

**Pattern:**

```
Task received →
PLANNING PHASE:
  "To complete this task I need to:
  1. Gather [X]
  2. Analyze [Y]
  3. Write [section A]
  4. Write [section B]
  5. Review and verify"

EXECUTION PHASE:
  Execute step 1 → result
  Execute step 2 → result
  ...
  Execute step 5 → final output
```

**Implementation:**

The Planning Phase and Execution Phase may use separate LLM calls.

Planning call: Lighter model (cost efficient) to generate the plan.
Execution call: Stronger model (per section) to execute.

**When to use:**
- Proposal Employee (generating multi-section proposal)
- Business Case Employee (structured financial analysis)
- Meeting Employee (processing long meeting notes)

---

# Confidence Scoring Standard

Every reasoning strategy must produce a confidence score.

## Scoring Rules

| Score Range | Label | Interpretation | Action |
|---|---|---|---|
| 0.85–1.00 | Very High | Strongly supported by sources | Display to AM |
| 0.70–0.84 | High | Well supported | Display to AM |
| 0.55–0.69 | Medium | Partially supported | Display with note |
| 0.40–0.54 | Low | Weakly supported | Send to Console for review |
| 0.00–0.39 | Very Low | Insufficient evidence | Mandatory human review |

## Confidence Calculation

Confidence is not an arbitrary number. It is derived from:

```
confidence = (
    source_quality_score × 0.4 +   # How good are the sources?
    source_quantity_score × 0.3 +  # How many sources support this?
    recency_score × 0.2 +          # How recent is the information?
    internal_consistency_score × 0.1  # Does the information contradict itself?
)
```

Each component scored 0.0–1.0, weighted sum produces final confidence.

## In Practice

The System Context instructs the employee to score each output:

```
For your final output, provide:
- confidence: float (0.0 to 1.0)
- confidence_reasoning: string (brief explanation of why this score)
- low_confidence_areas: array (specific fields you are less certain about)
```

---

# Hallucination Prevention Rules

These rules apply to ALL reasoning strategies:

**Rule 1: Ground in context.**
"Only state facts that appear in the provided context, tools results, or retrieved knowledge. If you cannot find a fact, state 'Not found in available sources.'"

**Rule 2: No inference beyond evidence.**
"Do not infer or extrapolate from limited evidence to make strong claims. State your evidence and the confidence level it supports."

**Rule 3: Explicit uncertainty.**
"When uncertain, use language that reflects uncertainty: 'Based on available information, it appears...', 'One source suggests...', 'Unable to confirm...'"

**Rule 4: Source everything.**
"Every claim in your output must be accompanied by a source URL or an explicit statement that no source was found."

**Rule 5: No memory fabrication.**
"Do not reference past conversations or past tasks unless they appear explicitly in the Memory Context provided. Do not invent past results."

---

# Reasoning Trace Storage

For every task, the reasoning trace (the `<thinking>` block) is stored alongside the output.

This enables:
- Debugging: why did the employee conclude X?
- Improvement: what went wrong in the reasoning?
- Auditing: what did the employee consider before deciding?

**Storage:** `ai_results.reasoning_trace` column (TEXT, compressed)

**Retention:** Same as Episodic Memory (2 years then archive)

---

# Strategy Assignment by Employee

| Digital Employee | Strategy | Reason |
|---|---|---|
| Company Research Employee | ReAct | Multi-step web research |
| Buying Signal Employee | Chain of Thought | Signal classification |
| Account Intelligence Employee | Chain of Thought | Profile synthesis |
| Contact Intelligence Employee | ReAct | Multi-source contact lookup |
| Account Scoring Employee | Chain of Thought | Scoring formula reasoning |
| News Employee | ReAct | Multi-source news monitoring |
| Knowledge Indexing Employee | None (deterministic) | Embedding task, no reasoning needed |
| Dashboard Priority Employee | Chain of Thought | Priority ranking |
| Proposal Employee | Plan and Execute | Multi-section document |
| Executive Summary Employee | Chain of Thought | Structured writing |
| Meeting Employee | Chain of Thought | Note analysis and summarization |

---

# Anti-Patterns to Avoid

**Anti-pattern 1: Answer First, Justify Later**
Never instruct an employee to produce output and then add confidence and sources afterward. Sources must be gathered before answering.

**Anti-pattern 2: Unlimited Iterations**
ReAct strategy must always have a maximum iteration count. Without it, a poorly scoped task can run indefinitely.

**Anti-pattern 3: Mixing Strategies**
A single task should use one strategy. Mixing strategies creates unpredictable behavior.

**Anti-pattern 4: Ignoring Negative Results**
If a web search returns no results, that is information. "Company not found in public sources" is a valid, valuable output. Never fabricate results when search fails.

---

# Relationship to Other Documents

| Document | Relationship |
|---|---|
| `13_DIGITAL_EMPLOYEE_TEMPLATE.md` | Each employee's reasoning strategy is specified in its template |
| `15_STANDARD_OPERATING_PROCEDURES.md` | SOPs reference reasoning strategy in each step |
| `16_CONTEXT_ENGINEERING.md` | Reasoning strategy is configured in System Context |
| `04_AI_CONSTITUTION.md` | Confidence scoring and traceability requirements |

---

# Final Principle

> **"The output is only as good as the thinking.**
>
> **Design the thinking.**
>
> **The output will follow."**
