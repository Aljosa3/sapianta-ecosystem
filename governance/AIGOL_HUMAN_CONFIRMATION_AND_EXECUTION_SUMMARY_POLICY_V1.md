# AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_V1

## Status

Constitutional policy certification.

## Final Classification

```text
AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_STATUS = CERTIFIED
```

## Purpose

This policy defines the mandatory human confirmation boundary before any execution-capable AiGOL action.

It applies to:

- deterministic routing;
- cognition-assisted routing;
- replay-derived improvements;
- domain operations;
- capability operations;
- worker execution requests.

The policy does not implement a new runtime and does not authorize execution. It defines the mandatory boundary that execution-capable runtimes must satisfy before execution can proceed.

## Architectural Principle

The following transition is prohibited:

```text
Deterministic Intent
-> Automatic Execution
```

The required model is:

```text
Intent Resolution
-> Execution Summary
-> Human Review
-> Human Confirmation
-> Execution Authorization
-> Execution
```

Intent resolution is not confirmed human intent.

## Canonical Invariant

```text
INTENT_RESOLUTION != HUMAN_CONFIRMATION
```

Successful classification may classify, route, prepare, or summarize. It must not authorize execution.

## Execution Summary Requirement

Before any execution-capable transition, AiGOL must create and present:

```text
EXECUTION_SUMMARY_ARTIFACT_V1
```

Execution may not continue until a valid human response is received and replay-visible confirmation evidence exists.

Existing narrower summaries, including `IMPLEMENTATION_SUMMARY_ARTIFACT_V1`, may satisfy a specialized portion of this policy only when they include or are wrapped by the complete execution summary contract.

## Minimum Execution Summary Fields

`EXECUTION_SUMMARY_ARTIFACT_V1` must include:

1. Original Human Request
2. Interpreted Intent
3. Selected Route
4. Planned Actions
5. Expected Outputs
6. Risk Classification
7. Assumptions
8. Constraints
9. Execution Scope
10. Authorization Required
11. Replay References

The summary must be human-readable and replay-visible.

## Human Response Options

AiGOL must support the following human response options:

- `APPROVE`
- `MODIFY`
- `CLARIFY`
- `EXPAND`
- `REDUCE_SCOPE`
- `REJECT`
- `CONTINUE_CONVERSATION`

The human must not be forced into a binary approve/reject workflow.

## Approval Model

`APPROVE` creates:

```text
EXECUTION_AUTHORIZATION_ARTIFACT_V1
```

Only after that authorization may execution proceed through the governed execution lifecycle.

## Modification Model

`MODIFY`, `EXPAND`, or `REDUCE_SCOPE` must create an intent update and a new execution summary.

Execution remains blocked until the updated summary is reviewed and confirmed.

## Clarification Model

`CLARIFY` enters conversation and intent refinement.

Execution remains blocked until a refined intent produces a new execution summary and that summary is confirmed.

## Rejection Model

`REJECT` blocks execution and records replay-visible rejection evidence.

## Continue Conversation Model

`CONTINUE_CONVERSATION` continues conversation without execution, authorization, worker invocation, provider authority escalation, governance mutation, or replay mutation.

## Deterministic Routing Policy

Deterministic routing may:

- classify;
- route;
- prepare;
- summarize.

Deterministic routing may not:

- authorize;
- execute;
- bypass human confirmation.

Therefore:

```text
Deterministic Route
-> Execution Summary
```

never:

```text
Deterministic Route
-> Execute
```

## LLM Policy

LLMs may:

- propose intent;
- propose assumptions;
- propose scope;
- propose actions.

LLMs may not:

- authorize execution;
- approve summaries;
- confirm intent;
- bypass human review.

## Replay Policy

Replay must record:

- original intent;
- execution summary;
- human response;
- authorization state;
- execution outcome;
- validation outcome;
- replay review.

## Fail-Closed Requirement

Execution must not occur if:

- summary generation fails;
- summary is incomplete;
- human response is missing;
- authorization state is invalid.

System behavior:

```text
FAIL_CLOSED
```

## Certification Cases

| Case | Input State | Required Boundary | Execution State |
| --- | --- | --- | --- |
| 1 | Deterministic development intent | Summary generated and human approval required | Blocked until confirmation |
| 2 | OCS cognition intent | Summary generated and human approval required | Blocked until confirmation |
| 3 | Replay-derived improvement | Summary generated and human approval required | Blocked until confirmation |
| 4 | Human modifies scope | Updated summary required | Blocked until reconfirmed |
| 5 | Human requests clarification | Conversation continues | No execution |
| 6 | Missing human response | `FAIL_CLOSED` | No execution |

## Non-Goals

This policy does not:

- redesign ACLI;
- redesign OCS;
- redesign PPP;
- redesign worker lifecycle;
- redesign replay;
- add providers;
- authorize any execution;
- implement automatic domain or capability operations.

## Governance Impact Statement

This policy strengthens the existing AiGOL boundary model:

```text
LLM proposes.
AiGOL governs.
AiGOL summarizes.
Human confirms.
Worker executes.
Replay records.
```

It preserves governance authority, human authority, replay auditability, fail-closed behavior, and provider non-authority.

## Final Fields

```text
EXECUTION_SUMMARY_REQUIRED = YES
HUMAN_CONFIRMATION_REQUIRED = YES
DETERMINISTIC_AUTO_EXECUTION_PROHIBITED = YES
LLM_AUTO_EXECUTION_PROHIBITED = YES
REPLAY_AUDITABILITY_PRESERVED = YES
FAIL_CLOSED_PRESERVED = YES
POLICY_CERTIFIED = YES
```
