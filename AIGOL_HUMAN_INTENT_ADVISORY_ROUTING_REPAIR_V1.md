# AIGOL_HUMAN_INTENT_ADVISORY_ROUTING_REPAIR_V1

Status: implemented and validated.

## Objective

Resolve the remaining Human Intent Resolution routing gap for advisory and general-improvement prompts.

## Scope

This repair only changes human-intent intake target selection and clarification-continuity workflow selection.

Preserved boundaries:

- governance behavior unchanged;
- replay-visible clarification artifacts preserved;
- authorization behavior unchanged;
- worker behavior unchanged;
- provider behavior unchanged;
- fail-closed behavior preserved for malformed or unsupported continuation state.

## Before Behavior

HIRR retest after clarification continuity produced:

```text
HIRR_SCORE_AFTER = 90
FAILED_CLOSED_AFTER = 0
GENERAL_IMPROVEMENT_REQUESTS = 10 misrouted
```

Advisory/general-improvement prompts were clarified correctly, but their continuation state targeted:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Expected workflow:

```text
OCS_LLM_COGNITION
```

## Root Cause

The intake runtime had no dedicated advisory/general-improvement intent family.

Clarification-continuity selection also assumed that every human-intent clarification should resolve to:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

This preserved continuity but collapsed advisory prompts into the compliance/domain clarification path.

## Repair

Implemented minimum deterministic routing support:

- added `GENERAL_IMPROVEMENT_INTENT`;
- added advisory signal predicates for normal human general-improvement prompts;
- mapped `GENERAL_IMPROVEMENT_INTENT` to `OCS_LLM_COGNITION`;
- kept workflow/control prompts out of advisory routing so governed workflow requests continue to target `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- updated clarification-continuity selection to use the replay-visible `expected_workflow_targets` recorded by intake;
- retained fail-closed validation for missing or unsupported target workflows.

## Routing Predicates

Advisory prompts require an AI term and at least one advisory/general-improvement signal, including:

```text
improve how
processes safer
improve trust
suggest how
reduce risk
where should we start
first step
plan a better
recommend improvements
easier to explain
```

Prompts containing workflow/control signals remain outside advisory routing:

```text
human approval
collect evidence
before staff use
before action
workflow
controlled
audit evidence
```

## Validation

Focused regression:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py
105 passed
```

HIRR 100-prompt corpus retest:

```text
PROMPTS_TESTED = 100
HIRR_SCORE_AFTER_REPAIR = 100
PROMPTS_ROUTED_CORRECTLY = 100
PROMPTS_FAILED_CLOSED = 0
PROMPTS_MISROUTED = 0
PROMPTS_CLARIFICATION_REQUIRED_ONLY = 0
```

Category coverage:

```text
AI Governance Requests = 10/10 success
Ambiguous Requests = 10/10 success
Automation Requests = 10/10 success
Business Goals = 10/10 success
Business Problems = 10/10 success
Compliance Requests = 10/10 success
Decision-Making Requests = 10/10 success
General Improvement Requests = 10/10 success
HR Requests = 10/10 success
Operational Requests = 10/10 success
```

## Before / After

Representative advisory prompt:

```text
Help improve how our company uses AI.
```

Before:

```text
CLARIFICATION_REQUIRED
Clarification response bound
Selected workflow: CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
Outcome: MISROUTED
```

After:

```text
CLARIFICATION_REQUIRED
Clarification response bound
Selected workflow: OCS_LLM_COGNITION
Outcome: SUCCESS
```

## Final Fields

```text
ADVISORY_INTENT_SUPPORTED = YES
ADVISORY_TARGET_SELECTION_CORRECT = YES
HIRR_SCORE_AFTER_REPAIR = 100
WORKFLOW_SELECTION_ACCURACY = 100
FAILED_CLOSED_AFTER_REPAIR = 0
HUMAN_INTENT_RESOLUTION_READY = YES
```
