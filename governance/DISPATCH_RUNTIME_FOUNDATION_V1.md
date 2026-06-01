# DISPATCH_RUNTIME_FOUNDATION_V1

## Purpose

Define the minimal dispatch governance boundary between Worker Assignment and Worker Invocation.

Dispatch is the replay-visible AiGOL decision that an assigned worker may be invoked by a future invocation runtime. Dispatch is not invocation, execution, completion, or result persistence.

## Scope

This foundation defines dispatch governance only.

It does not implement:

- worker invocation;
- worker execution;
- execution completion;
- worker result persistence;
- provider authority;
- automatic dispatch;
- worker self-dispatch;
- worker self-execution.

## Boundary

The dispatch boundary sits between:

```text
WORKER_ASSIGNMENT_ARTIFACT_V1
  -> DISPATCHED
  -> Future Worker Invocation
```

Current Worker Runtime records registration and assignment only. Assigned workers remain non-invoked until a future dispatch runtime records dispatch eligibility.

## Dispatch Preconditions

Dispatch may be recorded only when all of the following are true:

- worker assignment artifact exists;
- worker assignment artifact is well formed;
- assignment status is `ASSIGNED`;
- worker state after assignment is `ASSIGNED`;
- assignment was created by AiGOL;
- assignment replay is reconstructable;
- worker artifact reference is stable;
- readiness artifact reference is stable;
- readiness status is `READY_FOR_DISPATCH`;
- execution request reference is stable;
- request type is supported by the assigned worker capability;
- no prior dispatch exists for the same assignment;
- no cancellation or expiry exists before dispatch;
- no worker invocation has occurred;
- no execution has occurred;
- no completion has occurred;
- provider authority is absent;
- worker self-dispatch is absent;
- replay reconstruction succeeds.

If any condition fails, AiGOL must fail closed and leave the assignment non-dispatchable.

## Actor Authority

Only AiGOL governance may dispatch.

The following actors may never dispatch:

- Provider;
- Worker;
- Human acting directly outside AiGOL governance;
- Replay;
- Proposal Runtime;
- Approval Runtime;
- Execution Request Runtime;
- Ready For Dispatch Runtime;
- Worker Assignment artifact;
- CLI transport alone;
- automatic retry logic.

Workers may later execute only after future invocation evidence exists. They may not dispatch themselves.

## Required Replay Evidence

Before dispatch can be reconstructed, replay must contain:

- proposal creation evidence;
- approval evidence with `APPROVED` status;
- execution request evidence;
- ready-for-dispatch evidence;
- worker registration evidence;
- worker assignment evidence;
- dispatch validation event;
- dispatch returned event;
- stable references among assignment, worker, readiness, and execution request artifacts;
- artifact hashes or equivalent deterministic integrity markers;
- explicit evidence that no invocation, execution, or completion occurred at dispatch.

## Reconstruction Rule

Replay reconstructs dispatch by reading the ordered event stream and verifying:

1. readiness existed before worker assignment;
2. worker assignment existed before dispatch;
3. assignment status was `ASSIGNED`;
4. assigned worker identity is stable;
5. dispatch references the same assignment, worker, readiness, and execution request lineage;
6. no duplicate dispatch exists;
7. no cancellation or expiry precedes dispatch;
8. no invocation, execution, or completion is encoded in dispatch.

Any mismatch invalidates dispatch reconstruction.

## Dispatch States

The dispatch boundary recognizes these states:

- `ASSIGNED`;
- `DISPATCHED`;
- `CANCELLED`;
- `EXPIRED`.

Only `ASSIGNED -> DISPATCHED` is the positive dispatch transition.

## Constitutional Preservation

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Provider output remains upstream proposal evidence only. AiGOL governs dispatch. Workers remain non-invoked until a future invocation boundary. Replay records the dispatch decision.

## Foundation Classification

`DISPATCH_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS`

Dispatch governance is defined, but dispatch runtime implementation, invocation runtime, execution runtime, completion runtime, and result persistence remain future work.
