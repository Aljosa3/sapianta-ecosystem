# IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_ADR_V1

## Status

Accepted foundation decision.

## Decision

AiGOL will treat execution request creation from an implementation plan as a separate governed bridge.

The source artifact is:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
```

The future derived artifact is:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

Implementation plans may not automatically create execution requests.

## Context

The governed learning runtime is certified through implementation planning:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
-> Implementation Plan
```

The existing implementation plan runtime records plans only. It explicitly records:

```text
execution_request_created = false
implementation_performed = false
```

Without a distinct bridge, future execution could accidentally conflate planning with execution request authority.

## Rationale

The bridge is necessary to preserve:

- approval and execution separation;
- planning and request derivation separation;
- human authorization;
- canonical chain continuity;
- replay reconstruction;
- provider isolation;
- worker isolation;
- no automatic self-implementation.

## Decision Rules

1. Implementation plans do not create execution requests automatically.
2. Future execution request creation requires a valid implementation plan.
3. Future execution request creation requires approved upstream improvement evidence.
4. Future execution request creation requires explicit human authorization evidence.
5. AiGOL must validate plan scope, payload bounds, references, hashes, and canonical chain continuity.
6. Providers cannot create, approve, or authorize execution requests.
7. Workers cannot create, approve, self-select, or self-dispatch execution requests.
8. Replay reconstructs evidence only and cannot create or authorize requests.
9. Execution request creation does not dispatch, invoke, execute, complete, or certify results.

## Consequences

AiGOL gains a defined future bridge:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
-> EXECUTION_REQUEST_ARTIFACT_V1
```

The bridge preserves the current implementation plan runtime boundary while preparing a separate future runtime for execution request derivation from approved learning plans.

## Non-Goals

This ADR does not implement:

- runtime code;
- execution request creation;
- execution request mutation;
- worker readiness;
- dispatch;
- invocation;
- execution;
- completion;
- result capture;
- governance mutation;
- replay mutation;
- self-application.

## Final Decision

The implementation-plan-to-execution-request bridge is accepted as a foundation design.

```text
IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_FOUNDATION_STATUS = READY
```
