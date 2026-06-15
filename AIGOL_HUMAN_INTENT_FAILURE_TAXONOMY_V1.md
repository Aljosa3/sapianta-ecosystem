# AIGOL_HUMAN_INTENT_FAILURE_TAXONOMY_V1

## Objective

Build a complete taxonomy of human-intent failures discovered in `AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_AUDIT_V1`.

This is analysis only. No ACLI, governance, PPP, replay, provider, authorization, Product 1, or worker lifecycle behavior was modified.

## Source Evidence

The taxonomy uses the 100 observed prompt routes from `AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_AUDIT_V1`.

Observed aggregate:

```text
PROMPTS_TESTED = 100
PROMPTS_FAILED_CLOSED = 97
PROMPTS_ROUTED_CORRECTLY = 1
PROMPTS_MISROUTED = 2
```

Observed actual workflow distribution:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = 97
OCS_LLM_COGNITION = 2
REVIEW_LATEST_AUDIT = 1
```

## Human Intent Coverage Map

| Intent family | Count | Success | Clarified | Failed closed | Misrouted | Success rate | Fail rate | First failure stage | Expected workflow | Actual workflow |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Business Goal Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| Problem Statement Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| Automation Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| Compliance Intent | 10 | 0 | 0 | 9 | 1 | 0% | 90% plus 10% misroute | Workflow Selection / Intent Classification | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`, `REVIEW_LATEST_AUDIT` |
| HR-Sensitive AI Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| Decision Review Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| Operational AI Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| AI Oversight Intent | 10 | 0 | 0 | 10 | 0 | 0% | 100% | Workflow Selection | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| General Improvement Intent | 10 | 1 | 0 | 9 | 0 | 10% | 90% | Workflow Selection | `OCS_LLM_COGNITION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`, `OCS_LLM_COGNITION` |
| Ambiguous Intent | 10 | 0 | 0 | 9 | 1 | 0% | 90% plus 10% misroute | Workflow Selection / Intent Classification | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`, `OCS_LLM_COGNITION` |

## Top Failure Families

The corpus has 10 prompt families with 10 prompts each. The top failure families are therefore tied by count.

| Rank | Intent family | Failed or misrouted prompts | Percent of corpus | Primary actual workflow |
|---:|---|---:|---:|---|
| 1 | Business Goal Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | Problem Statement Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | Automation Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | HR-Sensitive AI Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | Decision Review Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | Operational AI Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | AI Oversight Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| 1 | Compliance Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`, `REVIEW_LATEST_AUDIT` |
| 1 | Ambiguous Intent | 10 | 10% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`, `OCS_LLM_COGNITION` |
| 10 | General Improvement Intent | 9 | 9% | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |

## Human Intent Failure Taxonomy

### Business Goal Intent

Observed prompts describe desired business outcomes: trust AI recommendations, check automated decisions, start using AI safely, review important AI outputs, reduce mistakes, and create an internal service for reviewing AI suggestions.

Failure pattern:

```text
business objective phrased without internal terms
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
-> FAILED_CLOSED risk
```

Expected behavior:

```text
Business Goal Intent
-> CLARIFICATION_REQUIRED
```

### Problem Statement Intent

Observed prompts describe pain points: AI contradicting policy, inconsistent chatbot use, inability to explain recommendations, unreliable review process, and missing checks.

Failure pattern:

```text
plain problem statement
-> no deterministic problem-intake route
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
Problem Statement Intent
-> CLARIFICATION_REQUIRED
```

### Automation Intent

Observed prompts ask to automate review, flag incomplete outputs, screen decisions, collect evidence, and stop bad suggestions.

Failure pattern:

```text
automation verb + AI review subject
-> no normal-human automation intake
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
Automation Intent
-> CLARIFICATION_REQUIRED
```

### Compliance Intent

Observed prompts ask for audit evidence, regulatory preparation, proof of review, records, and controlled customer-impacting AI decisions.

Failure pattern:

```text
business compliance phrase
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

One prompt containing `auditors` misrouted to:

```text
REVIEW_LATEST_AUDIT
```

Expected behavior:

```text
Compliance Intent
-> CLARIFICATION_REQUIRED
```

### HR-Sensitive AI Intent

Observed prompts mention hiring, employee evaluation, recruitment, performance feedback, promotions, and safeguards.

Failure pattern:

```text
HR-sensitive AI request
-> no HR-sensitive intake family
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
HR-Sensitive AI Intent
-> CLARIFICATION_REQUIRED
```

### Decision Review Intent

Observed prompts ask when AI recommendations should be approved, what evidence is enough, and how to review suggested decisions.

Failure pattern:

```text
decision review language
-> no normal-human decision-review route
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
Decision Review Intent
-> CLARIFICATION_REQUIRED
```

### Operational AI Intent

Observed prompts mention supplier actions, production schedules, daily operations, service tickets, dispatch, warehouse planning, and operational managers.

Failure pattern:

```text
operational business context + AI recommendation
-> no operational AI intake family
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
Operational AI Intent
-> CLARIFICATION_REQUIRED
```

### AI Oversight Intent

Observed prompts ask for rules, supervision, controls, review enforcement, tracking, guardrails, and preventing unchecked AI work.

Failure pattern:

```text
ordinary oversight language
-> no normal-human oversight route
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Expected behavior:

```text
AI Oversight Intent
-> CLARIFICATION_REQUIRED
```

### General Improvement Intent

Observed prompts ask to improve AI use, make AI safer, reduce risk, improve AI quality, and make AI decisions easier to explain.

Failure pattern:

```text
general improvement request
-> usually DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

One prompt routed correctly:

```text
What should our first step be for safer AI use?
-> OCS_LLM_COGNITION
```

Expected behavior:

```text
General Improvement Intent
-> OCS_LLM_COGNITION
```

### Ambiguous Intent

Observed prompts are short and underspecified: help with AI, build something for my business, better decisions, make this safer, improve our process, quality problem.

Failure pattern:

```text
underspecified human request
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

One prompt misrouted:

```text
What should we do next?
-> OCS_LLM_COGNITION
```

Expected behavior:

```text
Ambiguous Intent
-> CLARIFICATION_REQUIRED
```

## Clarification-First Families

The following observed families should route to `CLARIFICATION_REQUIRED` instead of `FAILED_CLOSED` because the user has expressed a plausible governed-workflow need but has not supplied enough deterministic routing detail:

```text
Business Goal Intent
Problem Statement Intent
Automation Intent
Compliance Intent
HR-Sensitive AI Intent
Decision Review Intent
Operational AI Intent
AI Oversight Intent
Ambiguous Intent
```

`General Improvement Intent` should primarily route to `OCS_LLM_COGNITION`, with clarification only when the improvement target is too vague to safely classify.

## Intents Requiring New Routing

The observed failures requiring new deterministic normal-human routing are:

```text
Business Goal Intent
Problem Statement Intent
Automation Intent
Compliance Intent
HR-Sensitive AI Intent
Decision Review Intent
Operational AI Intent
AI Oversight Intent
General Improvement Intent
```

`Ambiguous Intent` primarily requires a deterministic clarification route, not a direct workflow route.

## Human Intent Routing Gap Analysis

1. The router recognizes internal system phrases better than normal business phrases.

   Most observed prompts do not include terms such as `domain`, `capability`, `artifact`, `milestone`, or explicit certified workflow vocabulary.

2. `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` is acting as the human-intent catch-all.

   This produced 97/100 actual workflows and is the dominant reason normal users do not reliably enter governed workflows.

3. There is no broad deterministic intake for AI decision quality, review, approval, evidence, HR sensitivity, operational impact, or business compliance.

   These are the actual normal-human families observed in the corpus.

4. Clarification is not the default response to ambiguity.

   Ambiguous prompts received 0/10 clarification outcomes.

5. Some keyword routes are too shallow for human language.

   `auditors` triggered internal audit review; `what should we do next` triggered broad cognition rather than clarification.

## Highest-Leverage Repair Candidate

Add a deterministic human-intent intake layer before `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`.

Minimum behavior:

```text
normal human AI/business request
-> intent family detection
-> CLARIFICATION_REQUIRED or certified advisory route
-> no provider fallback as first response
```

This should not grant execution authority, bypass governance, bypass PPP, modify replay, or create worker requests. It should only select a replay-visible, clarification-first intake path for normal-human language.

## Final Fields

```text
INTENT_FAMILIES_DISCOVERED = 10
TOP_FAILURE_FAMILY = TIE: Business Goal Intent, Problem Statement Intent, Automation Intent, Compliance Intent, HR-Sensitive AI Intent, Decision Review Intent, Operational AI Intent, AI Oversight Intent, Ambiguous Intent
TOP_FAILURE_PERCENT = 10
INTENTS_REQUIRING_CLARIFICATION_FIRST = 9
INTENTS_REQUIRING_NEW_ROUTING = 9
MOST_COMMON_EXPECTED_WORKFLOW = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
MOST_COMMON_ACTUAL_WORKFLOW = DEFAULT_PROVIDER_ASSISTED_CONVERSATION
ROOT_CAUSE_CONFIDENCE = HIGH
HIGHEST_LEVERAGE_REPAIR_CANDIDATE = Deterministic clarification-first human-intent intake before DEFAULT_PROVIDER_ASSISTED_CONVERSATION
HUMAN_INTENT_FAILURE_MODEL_UNDERSTOOD = YES
```
