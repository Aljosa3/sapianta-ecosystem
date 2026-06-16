# AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_RETEST_V1

## Objective

Re-run the original 100-prompt Human Intent Resolution Readiness corpus after implementation of:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
HUMAN_INTENT_CLARIFICATION_CONTINUITY
```

## Method

The original 100 initial prompts from `AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_AUDIT_V1` were reused.

For each prompt, ACLI was exercised as a two-turn interactive exchange:

```text
Turn 1: original corpus prompt
Turn 2: representative clarification response for the original expected intent family
```

Success was counted when either:

```text
Turn 1 selected the expected workflow directly
```

or:

```text
Turn 1 produced CLARIFICATION_REQUIRED
Turn 2 bound the clarification response
Turn 2 selected the expected workflow
```

Expected workflows were the same as the original audit:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION for 90 prompts
OCS_LLM_COGNITION for 10 General Improvement prompts
```

## Coverage Delta

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| HIRR score | 1 | 90 | +89 |
| Routed correctly without clarification | 1 | 0 | -1 |
| Clarified correctly | 0 | 90 | +90 |
| Failed closed | 97 | 0 | -97 |
| Misrouted | 2 | 10 | +8 |

## Retest Results

| Category | Prompts | Clarified correctly | Failed closed | Misrouted |
|---|---:|---:|---:|---:|
| Business Goals | 10 | 10 | 0 | 0 |
| Business Problems | 10 | 10 | 0 | 0 |
| Automation Requests | 10 | 10 | 0 | 0 |
| Compliance Requests | 10 | 10 | 0 | 0 |
| HR Requests | 10 | 10 | 0 | 0 |
| Decision-Making Requests | 10 | 10 | 0 | 0 |
| Operational Requests | 10 | 10 | 0 | 0 |
| AI Governance Requests | 10 | 10 | 0 | 0 |
| General Improvement Requests | 10 | 0 | 0 | 10 |
| Ambiguous Requests | 10 | 10 | 0 | 0 |

Observed first-turn workflow distribution:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE = 100
```

Observed second-turn workflow distribution:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = 100
```

## Failure Reduction

The main original failure was provider fallback:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = 97
```

After retest:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = 0
FAILED_CLOSED = 0
```

This confirms the clarification-first intake and continuity repair eliminated the original fail-closed provider fallback failure mode for the full 100-prompt corpus.

## Remaining Failure Taxonomy

Only one remaining failure family was observed:

| Remaining family | Count | Expected workflow | Actual workflow | Failure type |
|---|---:|---|---|---|
| General Improvement / Advisory Intent | 10 | `OCS_LLM_COGNITION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | Misrouted after clarification |

Failure pattern:

```text
General improvement prompt
-> HUMAN_INTENT_CLARIFICATION_INTAKE
-> CLARIFICATION_REQUIRED
-> clarification response bound
-> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Expected pattern:

```text
General improvement prompt
-> OCS_LLM_COGNITION
```

or:

```text
General improvement prompt
-> clarification
-> OCS_LLM_COGNITION when clarified as advisory/planning
```

## Top Unresolved Intent Families

```text
1. General Improvement / Advisory Intent = 10 unresolved
```

All other original intent families reached the expected workflow after clarification.

## Highest Leverage Next Repair

Add advisory/general-improvement intent resolution as a distinct target in human-intent clarification continuity.

The current continuity implementation resolves all human-intent clarifications to:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

The next repair should distinguish:

```text
governed workflow/proposal intent -> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
advisory/planning/improvement intent -> OCS_LLM_COGNITION
```

This should preserve the clarification-first behavior while preventing advisory prompts from being over-routed into domain clarification.

## Final Fields

```text
HIRR_SCORE_BEFORE = 1
HIRR_SCORE_AFTER = 90
FAILED_CLOSED_BEFORE = 97
FAILED_CLOSED_AFTER = 0
CLARIFICATION_SUCCESS_RATE = 90
WORKFLOW_SELECTION_SUCCESS_RATE = 90
TOP_REMAINING_FAILURE = General Improvement / Advisory Intent routed to CREATE_DOMAIN_COMPLIANCE_CLARIFICATION instead of OCS_LLM_COGNITION
HUMAN_INTENT_RESOLUTION_READY = NO
NEXT_HIGHEST_LEVERAGE_REPAIR = Add advisory/general-improvement target selection to human-intent clarification continuity
```
