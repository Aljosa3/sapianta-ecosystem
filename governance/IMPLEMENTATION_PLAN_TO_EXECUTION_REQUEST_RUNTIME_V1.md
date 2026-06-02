# IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1

IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_STATUS = CERTIFIED

## Purpose

`IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1` implements the governed bridge:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
-> EXECUTION_REQUEST_ARTIFACT_V1
```

It creates:

```text
IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1
```

and a source-aware:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

The runtime creates an execution request only through explicit governance validation and explicit human execution-request authorization. Implementation plans do not create execution requests automatically.

## Runtime Boundary

The implemented boundary is:

```text
Implementation Plan
-> Governed Bridge Link
-> Execution Request.CREATED
```

Creation requires:

- valid `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1`;
- valid `IMPROVEMENT_APPROVAL_ARTIFACT_V1`;
- approval decision and status of `APPROVED`;
- implementation plan status of `IMPLEMENTATION_PLAN_CREATED`;
- canonical chain id continuity;
- explicit human execution-request authorization reference;
- bounded request payload;
- AiGOL as requester;
- replay-visible creation and link events.

The bridge rejects reuse of the implementation-plan approval reference as execution-request authorization. Planning authorization is not execution request authorization.

## Replay Events

The runtime persists append-only replay events:

```text
000_implementation_plan_execution_request_created.json
001_implementation_plan_execution_request_linked.json
```

Replay reconstruction validates event ordering, replay wrapper hashes, execution request hash, bridge link hash, implementation plan reference, implementation plan hash, improvement approval reference, canonical chain id continuity, authorization continuity, and non-dispatch/non-execution flags.

## Fail-Closed Behavior

The runtime fails closed on:

- missing implementation plan;
- invalid implementation plan;
- invalid improvement approval;
- rejected approval;
- missing explicit human authorization;
- reuse of planning approval as execution-request authorization;
- duplicate bridge replay;
- canonical chain mismatch;
- approval reference mismatch;
- approval hash mismatch;
- corrupt plan references;
- corrupt approval references;
- replay wrapper corruption;
- replay ordering mismatch;
- replay chain mismatch;
- authority-bearing request payload;
- automatic execution request markers;
- provider, worker, replay, or self-authority markers.

## Explicit Non-Goals

`IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1` does not implement:

- readiness validation;
- worker assignment;
- dispatch;
- invocation;
- worker execution;
- completion;
- result capture;
- code mutation;
- governance mutation;
- replay mutation;
- self-approval;
- self-authorization;
- self-implementation;
- self-application.

## Downstream Compatibility Note

Existing `READY_FOR_DISPATCH_RUNTIME_V1` validates proposal-derived execution requests.

This bridge creates implementation-plan-derived execution requests with explicit source lineage. Future readiness integration should add a certified source-aware validation path rather than silently treating implementation plans as proposal approvals.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_implementation_plan_to_execution_request_runtime_v1.py
```

Result:

```text
18 passed
```

Broader regression validation passed:

```bash
python -m pytest tests/test_improvement_implementation_runtime_v1.py tests/test_improvement_approval_runtime_v1.py tests/test_execution_request_runtime_v1.py tests/test_implementation_plan_to_execution_request_runtime_v1.py
```

Result:

```text
68 passed
```

## Final Classification

```text
IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_STATUS = CERTIFIED
```
