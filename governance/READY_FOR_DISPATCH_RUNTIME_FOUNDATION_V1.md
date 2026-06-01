# READY_FOR_DISPATCH_RUNTIME_FOUNDATION_V1

## Purpose

Define the minimal readiness boundary between an Execution Request and future Worker Assignment.

`READY_FOR_DISPATCH` is not dispatch. It is the replay-visible governance conclusion that an approved execution request has passed deterministic readiness validation and may later be considered by Worker Runtime.

## Scope

This foundation defines readiness governance only.

It does not implement:

- dispatch;
- worker assignment;
- worker execution;
- execution completion;
- provider authority;
- automatic approval;
- proposal mutation;
- execution request mutation outside readiness state.

## Boundary

The readiness boundary sits between:

```text
APPROVED Proposal
  -> Execution Request (CREATED)
  -> READY_FOR_DISPATCH
  -> Future Worker Assignment
```

The current execution request runtime creates `EXECUTION_REQUEST_ARTIFACT_V1` in `CREATED` state only. Such requests are not worker-eligible until a readiness transition has been validated and recorded.

## Readiness Conditions

An execution request may become `READY_FOR_DISPATCH` only when all of the following are true:

- the execution request artifact exists;
- the execution request artifact is well formed;
- the execution request status is `CREATED`;
- the execution request id is unique;
- the execution request replay reference is valid;
- the referenced proposal exists;
- the referenced proposal is replay-reconstructable;
- the referenced proposal has an `APPROVED` approval record;
- the approval record is replay-reconstructable;
- the execution request references the same approved proposal lineage;
- the request type is recognized by AiGOL governance;
- the request payload is bounded and hashable;
- the request payload hash matches the readiness evidence;
- the request has not been cancelled or expired;
- no previous readiness event exists for the same execution request;
- no worker has already been assigned;
- no dispatch has occurred;
- no execution has occurred;
- provider output is not treated as readiness authority;
- replay reconstruction succeeds before readiness is recorded.

If any condition fails, AiGOL must fail closed and leave the request out of worker eligibility.

## Actor Authority

Only AiGOL governance may mark an execution request `READY_FOR_DISPATCH`.

The following actors may never mark readiness:

- Human;
- Provider;
- Worker;
- Replay;
- Proposal Runtime;
- Approval Runtime;
- Execution Request artifact itself;
- CLI transport alone;
- automatic retry logic.

Human approval is already captured at the proposal approval boundary. Readiness is an AiGOL validation boundary, not a second approval ceremony and not a worker invocation.

## Required Replay Evidence

Before readiness can be reconstructed, replay must contain:

- proposal creation event;
- approval decision event with `APPROVED` status;
- execution request creation event;
- execution request returned event;
- readiness validation event;
- readiness returned event;
- stable references among proposal, approval, execution request, and readiness artifact;
- artifact hashes or equivalent deterministic integrity markers;
- validation result set;
- explicit evidence that no dispatch or execution was performed by the readiness step.

## Reconstruction Rule

Replay reconstructs readiness by reading the ordered event stream and verifying:

1. the proposal was created before approval;
2. approval reached `APPROVED` before execution request creation;
3. execution request creation reached `CREATED` before readiness;
4. readiness references the same execution request and proposal lineage;
5. readiness validation succeeded;
6. no duplicate readiness record exists;
7. no cancellation or expiry precedes readiness;
8. no worker assignment, dispatch, or execution is encoded in readiness.

Any mismatch invalidates readiness reconstruction.

## Runtime States

The readiness boundary recognizes these execution request states:

- `CREATED`;
- `READY_FOR_DISPATCH`;
- `CANCELLED`;
- `EXPIRED`.

Only `CREATED -> READY_FOR_DISPATCH` is the positive readiness transition.

## Constitutional Preservation

The boundary preserves the constitutional invariant:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Provider or LLM output may contribute to the proposal text or conversational context, but it cannot approve, validate readiness, assign workers, or execute. AiGOL alone validates readiness. Workers remain inactive until a future dispatch boundary. Replay records every readiness decision.

## Foundation Classification

`READY_FOR_DISPATCH_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS`

The governance boundary is defined, but runtime implementation, worker capability registry, readiness tests, and dispatch integration remain future work.
