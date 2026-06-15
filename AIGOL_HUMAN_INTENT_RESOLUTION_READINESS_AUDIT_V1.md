# AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_AUDIT_V1

## Objective

Determine why `HUMAN_INTENT_RESOLUTION_READY` has not yet been achieved.

This is an audit only. No ACLI, governance, PPP, replay, Product 1, authorization, provider, or worker lifecycle behavior was modified.

## Method

Built a 100-prompt normal-human corpus across 10 categories and routed each prompt through:

```text
route_conversational_cli_intent
```

`DEFAULT_PROVIDER_ASSISTED_CONVERSATION` was classified as HIRR failure because the observed user path is:

```text
normal human prompt
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
-> provider dependency
-> FAILED_CLOSED
```

Expected behavior for unknown or underspecified normal-human intent is clarification-first routing, not provider fallback.

## Human Intent Coverage

| Category | Prompts | Success | Clarified | Failed closed | Misrouted |
|---|---:|---:|---:|---:|---:|
| Business Goals | 10 | 0 | 0 | 10 | 0 |
| Business Problems | 10 | 0 | 0 | 10 | 0 |
| Automation Requests | 10 | 0 | 0 | 10 | 0 |
| Compliance Requests | 10 | 0 | 0 | 9 | 1 |
| HR Requests | 10 | 0 | 0 | 10 | 0 |
| Decision-Making Requests | 10 | 0 | 0 | 10 | 0 |
| Operational Requests | 10 | 0 | 0 | 10 | 0 |
| AI Governance Requests | 10 | 0 | 0 | 10 | 0 |
| General Improvement Requests | 10 | 1 | 0 | 9 | 0 |
| Ambiguous Requests | 10 | 0 | 0 | 9 | 1 |

Observed workflow distribution:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = 97
OCS_LLM_COGNITION = 2
REVIEW_LATEST_AUDIT = 1
```

## Failure Taxonomy

| Root cause | Frequency | Evidence |
|---|---:|---|
| Missing Intent Pattern | 88 | Plain human phrases about AI quality, review, trust, approval, compliance, HR, operations, and decision safety do not match certified route predicates. |
| Missing Clarification | 9 | Ambiguous requests fall to provider-assisted conversation instead of asking clarifying questions. |
| Overly Strict Or Misweighted Routing | 2 | `audit` and broad `what should` phrasing select unrelated read-only/cognition paths. |

Cross-cutting issue:

```text
Fallback Overuse = 97/100
```

## Clarification Analysis

Ambiguous prompts tested:

```text
10
```

Ambiguous prompts that received `CLARIFICATION_REQUIRED`:

```text
0
```

Clarification-first compliance:

```text
0%
```

Current behavior:

```text
Unknown natural-human intent
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
-> provider dependency / fail-closed risk
```

Desired behavior:

```text
Unknown natural-human intent
-> deterministic clarification
-> preserve replay
-> re-enter certified workflow selection
```

## Routing Analysis

| ID | Category | Prompt | Expected Intent | Expected Workflow | Actual Workflow | Outcome | First Failure Stage |
|---:|---|---|---|---|---|---|---|
| 1 | Business Goals | I want to build a tool that helps managers trust AI recommendations. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 2 | Business Goals | We need a way to check whether automated decisions are good enough before people rely on them. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 3 | Business Goals | Our company wants to start using AI safely across departments. Where do we begin? | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 4 | Business Goals | I need a system that tells us when an AI answer should not be used. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 5 | Business Goals | Can you help us create a review process for important AI outputs? | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 6 | Business Goals | We want to reduce mistakes from AI tools used by our staff. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 7 | Business Goals | I need something that helps leadership see whether AI work is reliable. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 8 | Business Goals | Help me start a project for checking the quality of AI decisions. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 9 | Business Goals | Želim zgraditi sistem, ki bo preverjal kakovost in skladnost AI odločitev v podjetju. Kako naj začnemo? | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 10 | Business Goals | We want an internal service that reviews AI suggestions before they affect customers. | New business/product initiative | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 11 | Business Problems | Our AI sometimes gives answers that contradict company policy. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 12 | Business Problems | Teams are using chatbots differently and nobody knows which results are acceptable. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 13 | Business Problems | We cannot explain why an automated recommendation was accepted. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 14 | Business Problems | Customer support AI is making inconsistent choices and we need control. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 15 | Business Problems | Managers do not know when they should trust AI outputs. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 16 | Business Problems | We need to catch risky AI answers before they reach clients. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 17 | Business Problems | Our reports from AI tools are hard to compare and verify. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 18 | Business Problems | People are copying AI text into important documents without review. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 19 | Business Problems | We have too many manual checks around AI work and still miss problems. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 20 | Business Problems | I need help diagnosing why our AI review process is unreliable. | Business problem intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 21 | Automation Requests | Automate review of AI-generated summaries before they are sent out. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 22 | Automation Requests | Can ACLI help us check every AI answer against our internal rules? | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 23 | Automation Requests | I want the system to flag AI outputs that look incomplete. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 24 | Automation Requests | Build a workflow that reviews model answers before approval. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 25 | Automation Requests | Set up an automated check for risky AI recommendations. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 26 | Automation Requests | Help us automate quality checks for documents written with AI. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 27 | Automation Requests | Make a process that screens AI decisions before a person signs off. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 28 | Automation Requests | I want to automatically collect evidence for why an AI answer was accepted. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 29 | Automation Requests | Can we make the platform review AI outputs for missing justification? | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 30 | Automation Requests | Create a process that stops bad AI suggestions from moving forward. | Automation intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 31 | Compliance Requests | We need to show auditors how AI decisions were reviewed. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `REVIEW_LATEST_AUDIT` | MISROUTED | Intent Classification |
| 32 | Compliance Requests | Help us prepare for rules around high-risk AI use. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 33 | Compliance Requests | Can the system keep proof that AI outputs were checked? | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 34 | Compliance Requests | I need a way to demonstrate that AI recommendations followed company rules. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 35 | Compliance Requests | How do we document review of AI decisions for regulators? | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 36 | Compliance Requests | Set up checks so AI work can pass an internal audit. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 37 | Compliance Requests | We need records showing who approved an AI-assisted decision. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 38 | Compliance Requests | Help us avoid using AI results without proper review. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 39 | Compliance Requests | Can you create a process for collecting evidence about AI quality? | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 40 | Compliance Requests | We need to prove that customer-impacting AI decisions are controlled. | Compliance/evidence intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 41 | HR Requests | We want to use AI to screen job applications but need safeguards. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 42 | HR Requests | Can you help check whether AI hiring suggestions are fair? | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 43 | HR Requests | Our HR team needs review steps before using AI recommendations. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 44 | HR Requests | I need a system that flags risky employee evaluation advice from AI. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 45 | HR Requests | Help us control AI use in recruitment decisions. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 46 | HR Requests | We need proof that AI did not unfairly influence hiring choices. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 47 | HR Requests | Can the platform review AI-written performance feedback? | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 48 | HR Requests | Set up checks before managers use AI for promotion recommendations. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 49 | HR Requests | I want to make sure HR AI outputs are reviewed by a person. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 50 | HR Requests | Help us start safely with AI in employee-related decisions. | HR-sensitive AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 51 | Decision-Making Requests | How can we know whether an AI recommendation should be approved? | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 52 | Decision-Making Requests | I need a checklist for accepting or rejecting AI suggestions. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 53 | Decision-Making Requests | Help managers decide when AI output is trustworthy. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 54 | Decision-Making Requests | Can the system compare an AI answer with required evidence? | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 55 | Decision-Making Requests | We need a consistent way to review important AI decisions. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 56 | Decision-Making Requests | I want to define when an AI decision is acceptable. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 57 | Decision-Making Requests | Can ACLI help people make better calls about AI-generated advice? | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 58 | Decision-Making Requests | Set up a review flow for decisions suggested by AI. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 59 | Decision-Making Requests | Help us decide what evidence is enough before using AI output. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 60 | Decision-Making Requests | I need a process for reviewing AI recommendations before action. | Decision review intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 61 | Operational Requests | Our operations team wants AI to recommend supplier actions, but we need checks. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 62 | Operational Requests | Can we review AI suggestions before changing production schedules? | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 63 | Operational Requests | I need a process for validating AI advice in daily operations. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 64 | Operational Requests | Help us control AI recommendations for service tickets. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 65 | Operational Requests | We want AI to assist dispatch decisions but not without review. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 66 | Operational Requests | Set up a way to check AI decisions in warehouse planning. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 67 | Operational Requests | Can the system review AI alerts before staff act on them? | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 68 | Operational Requests | I need oversight for AI suggestions used by operations managers. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 69 | Operational Requests | Help us prevent bad AI recommendations in routine workflows. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 70 | Operational Requests | Create a review process for AI-assisted operational decisions. | Operational AI intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 71 | AI Governance Requests | We need rules for when staff may use AI answers. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 72 | AI Governance Requests | Can you help us supervise AI tools used inside the company? | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 73 | AI Governance Requests | I want a way to make AI use safer and easier to audit. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 74 | AI Governance Requests | Help us define controls for AI recommendations. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 75 | AI Governance Requests | We need oversight before AI outputs affect customers. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 76 | AI Governance Requests | Can the platform enforce review before risky AI use? | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 77 | AI Governance Requests | I want to track whether AI outputs were checked properly. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 78 | AI Governance Requests | Help us build guardrails for internal AI decisions. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 79 | AI Governance Requests | We need a system that prevents unchecked AI work from moving forward. | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 80 | AI Governance Requests | Can ACLI help us manage responsible AI use? | AI oversight intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 81 | General Improvement Requests | Help improve how our company uses AI. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 82 | General Improvement Requests | Make our AI processes safer. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 83 | General Improvement Requests | I want to improve trust in AI work. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 84 | General Improvement Requests | Can you suggest how to make our AI reviews better? | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 85 | General Improvement Requests | Help us reduce risk from AI tools. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 86 | General Improvement Requests | Where should we start improving AI quality? | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 87 | General Improvement Requests | What should our first step be for safer AI use? | General improvement / advisory | `OCS_LLM_COGNITION` | `OCS_LLM_COGNITION` | SUCCESS | None |
| 88 | General Improvement Requests | Help me plan a better review process for AI work. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 89 | General Improvement Requests | Can you recommend improvements for how staff use AI? | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 90 | General Improvement Requests | We need to make AI decisions easier to explain. | General improvement / advisory | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 91 | Ambiguous Requests | I need help with AI. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 92 | Ambiguous Requests | Can you build something for my business? | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 93 | Ambiguous Requests | We need better decisions. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 94 | Ambiguous Requests | Make this safer. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 95 | Ambiguous Requests | Help us get started. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 96 | Ambiguous Requests | I want an intelligent system. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 97 | Ambiguous Requests | Can you improve our process? | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 98 | Ambiguous Requests | We have a quality problem. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |
| 99 | Ambiguous Requests | What should we do next? | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `OCS_LLM_COGNITION` | MISROUTED | Intent Classification |
| 100 | Ambiguous Requests | I need a system that checks things. | Ambiguous intake | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | FAILED_CLOSED | Workflow Selection |

## Root Cause Analysis

`HUMAN_INTENT_RESOLUTION_READY` is not achieved because ACLI routing still primarily recognizes internal or certified-system language rather than normal human intent.

The main gaps are:

1. Normal-human AI quality, trust, review, approval, compliance, HR, and operational-safety phrases are not represented as first-class intent families.
2. Unknown intent does not reliably enter a deterministic clarification workflow.
3. The provider-assisted fallback is still used as the broad catch-all for normal human language.
4. Keyword-only routes can misclassify ordinary business phrases, such as `auditors` causing `REVIEW_LATEST_AUDIT`.
5. Multilingual normal-human intent has no evident coverage; the Slovenian prompt fell to provider fallback.

## Recommended Repair Order

1. Introduce a deterministic human-intent resolver before provider fallback.
   - Impact: highest.
   - It should classify plain business, compliance, HR, operations, decision-review, and AI-safety requests without requiring internal terms.

2. Make unknown human intent clarification-first.
   - Impact: highest for ambiguous prompts.
   - Unknown intent should produce replay-visible clarification instead of `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`.

3. Add normal-human synonym families for AI Decision Validator intake.
   - Impact: high.
   - Examples: `check AI decisions`, `trust AI answers`, `review AI recommendations`, `prove AI outputs were checked`, `AI used in hiring`, `AI affects customers`.

4. Separate business-audit language from internal audit-review commands.
   - Impact: targeted.
   - Prevent words like `auditors` or `audit` from routing to `REVIEW_LATEST_AUDIT` unless the user asks to review an existing ACLI audit artifact.

5. Add multilingual clarification fallback for high-signal non-English prompts.
   - Impact: targeted but important.
   - At minimum, non-English prompts mentioning AI decisions, quality, compliance, checking, or business should clarify rather than provider-fallback.

## Final Fields

```text
PROMPTS_TESTED = 100
HIRR_SCORE = 1
PROMPTS_ROUTED_CORRECTLY = 1
PROMPTS_CLARIFIED_CORRECTLY = 0
PROMPTS_FAILED_CLOSED = 97
PROMPTS_MISROUTED = 2
FIRST_FAILURE_STAGE = Workflow Selection
MOST_COMMON_FAILURE = Missing Intent Pattern
CLARIFICATION_FIRST_COMPLIANCE_PERCENT = 0
ROOT_CAUSE = ACLI lacks a deterministic normal-human intent resolver and overuses provider-assisted fallback for unknown natural language.
HIGHEST_LEVERAGE_REPAIR = Add clarification-first human intent resolution before DEFAULT_PROVIDER_ASSISTED_CONVERSATION.
HUMAN_INTENT_RESOLUTION_READY = NO
```
