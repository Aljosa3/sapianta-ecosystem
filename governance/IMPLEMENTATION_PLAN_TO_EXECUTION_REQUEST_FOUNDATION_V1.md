# IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_FOUNDATION_V1

IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_FOUNDATION_STATUS = READY

## Purpose

Define the constitutional bridge between:

```text
Approved Implementation Plan
-> Future Execution Request creation
```

This is review only. It does not implement runtime code, create execution requests, mutate replay, mutate governance, dispatch workers, invoke workers, execute changes, or self-apply improvements.

## Context

AiGOL now has a certified governed learning lifecycle:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
-> Implementation Plan
```

The lifecycle currently terminates at:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
```

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` may describe future implementation paths but records:

```text
execution_request_created = false
implementation_performed = false
```

Therefore, execution request creation from an implementation plan requires a separate governed boundary.

## 1. When May An Implementation Plan Become Executable?

An implementation plan may become eligible for future execution request creation only when all of the following evidence exists:

- valid `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1`;
- valid upstream `IMPROVEMENT_APPROVAL_ARTIFACT_V1`;
- upstream approval decision is `APPROVED`;
- implementation plan status is `IMPLEMENTATION_PLAN_CREATED`;
- implementation plan records `implementation_authorized = true`;
- implementation plan records `execution_request_created = false`;
- implementation plan records `implementation_performed = false`;
- replay-visible plan creation and return events exist;
- canonical chain id continuity is preserved across result, evaluation, proposal, review, approval, and plan;
- future execution request payload is bounded to the approved implementation plan scope;
- AiGOL performs deterministic validation before request creation.

Eligibility is not execution.

Eligibility does not dispatch workers, invoke workers, mutate code, or mutate governance.

## 2. Who Authorizes Execution Request Creation?

Execution request creation from an implementation plan requires human authorization evidence.

The upstream improvement approval authorizes implementation planning, not automatic execution request creation. A future runtime may either:

- require a distinct human execution-request authorization artifact; or
- explicitly certify that the upstream approval artifact contains execution-request authorization scope.

Until one of those rules is implemented and certified, implementation plans may not create execution requests.

## 3. Can Implementation Plans Create Execution Requests Automatically?

No.

Implementation plans are descriptive governance artifacts. They may identify future files, steps, workers, validation commands, and execution paths, but they may not create execution requests by themselves.

Required invariant:

```text
IMPLEMENTATION_PLAN_AUTOMATIC_EXECUTION_REQUEST = FORBIDDEN
```

## 4. Replay Evidence Required

Before a future execution request may be derived from an implementation plan, replay must prove:

- result artifact creation;
- result evaluation creation;
- improvement proposal creation;
- improvement review creation;
- improvement approval creation;
- approval decision of `APPROVED`;
- improvement implementation plan creation;
- implementation plan return event;
- artifact hashes for every upstream artifact;
- wrapper hashes for relevant replay events;
- same canonical chain id across the governed learning chain;
- no rejected or superseding approval in the same chain;
- no duplicate execution request for the same implementation plan unless a future duplicate policy is certified.

Replay may prove eligibility.

Replay may not create the execution request.

## 5. Continuity Reconstruction

Continuity is reconstructed through:

```text
RESULT_ARTIFACT_V1
-> RESULT_EVALUATION_ARTIFACT_V1
-> IMPROVEMENT_PROPOSAL_ARTIFACT_V1
-> IMPROVEMENT_REVIEW_ARTIFACT_V1
-> IMPROVEMENT_APPROVAL_ARTIFACT_V1
-> IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
-> FUTURE_EXECUTION_REQUEST_ARTIFACT_V1
```

The future execution request must include:

- implementation plan reference and hash;
- improvement approval reference and hash;
- improvement proposal reference and hash;
- result or evaluation lineage references where needed;
- canonical chain id;
- human authorization reference;
- bounded request payload;
- replay reference;
- artifact hash.

## 6. Linking Approved Improvements To Future Execution Chains

An approved improvement links to a future execution chain through the implementation plan.

The implementation plan is the bridge artifact that translates:

```text
approved learning evidence
```

into:

```text
bounded future execution candidate
```

The future execution request must remain a separate artifact so that approval, planning, request derivation, readiness, dispatch, invocation, execution, completion, and result capture remain distinct.

## 7. Authority Leak Prevention

Authority leaks are prevented by requiring:

- no automatic execution request creation;
- no provider authority;
- no worker authority;
- no replay authority;
- no implementation-plan self-authority;
- no AiGOL autonomous implementation;
- explicit human authorization evidence;
- AiGOL deterministic validation;
- replay-visible derivation;
- fail-closed invalid or corrupt evidence handling.

Implementation plan content must not expand approved scope or embed command execution authority.

## 8. Constitutional Preservation

This bridge preserves:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

Mapping:

| Role | Bridge meaning |
| --- | --- |
| LLM proposes | Provider assistance may contribute non-authoritative plan language only |
| AiGOL governs | AiGOL validates plan, approval, chain, payload, and replay evidence |
| Human authorizes | Execution request creation requires explicit human authorization evidence |
| Worker executes | Worker execution remains downstream and unavailable at this bridge |
| Replay records | Replay records evidence and reconstructs continuity without mutation |

## Final Classification

```text
IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_FOUNDATION_STATUS = READY
```
