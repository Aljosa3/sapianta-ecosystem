# WORKER_INVOCATION_RUNTIME_FOUNDATION_V1

## Purpose

Define the governance boundary between `DISPATCHED` and `WORKER_INVOKED`.

Invocation is the replay-visible AiGOL-controlled handoff of bounded invocation parameters to an already dispatched worker. Invocation is not worker execution, completion, result persistence, or authority creation.

## Scope

This foundation defines invocation governance only.

It does not implement:

- worker execution;
- execution completion;
- worker result persistence;
- worker termination evidence;
- provider authority;
- worker self-invocation;
- automatic invocation;
- scope expansion.

## Boundary

The invocation boundary sits between:

```text
DISPATCH_ARTIFACT_V1
  -> WORKER_INVOKED
  -> Future Worker Execution
```

Dispatch proves that AiGOL has authorized the assigned worker for invocation. Invocation proves that AiGOL has delivered bounded invocation parameters to the worker. Execution remains a future boundary.

## Invocation Preconditions

Invocation may be recorded only when all of the following are true:

- dispatch artifact exists;
- dispatch artifact is well formed;
- dispatch status is `DISPATCHED`;
- dispatch was created by AiGOL;
- dispatch replay is reconstructable;
- worker assignment artifact exists;
- worker assignment status is `ASSIGNED`;
- worker identity is stable and matches dispatch evidence;
- worker capability binding matches dispatch evidence;
- readiness evidence is stable;
- execution request lineage is stable;
- invocation parameters are bounded;
- invocation parameters are hashable;
- invocation parameters match the approved request payload scope;
- no prior invocation exists for the same dispatch;
- no cancellation or expiry exists before invocation;
- no execution has occurred;
- no completion has occurred;
- provider authority is absent;
- worker self-invocation is absent;
- replay reconstruction succeeds.

If any condition fails, AiGOL must fail closed and leave the dispatch non-invoked.

## Actor Authority

Only AiGOL governance may record invocation.

The following actors may never invoke:

- Provider;
- Worker acting on itself;
- Human acting directly outside AiGOL governance;
- Replay;
- Proposal Runtime;
- Approval Runtime;
- Execution Request Runtime;
- Ready For Dispatch Runtime;
- Worker Runtime assignment artifact;
- Dispatch artifact;
- CLI transport alone;
- automatic retry logic.

Workers may receive invocation after AiGOL records it, but may not create invocation authority.

## Worker Identity Verification

AiGOL must verify worker identity from:

- worker id;
- worker type;
- worker hash;
- worker assignment reference;
- worker assignment hash;
- dispatch worker reference;
- dispatch worker hash;
- capability id;
- supported request type;
- trust boundary;
- replay-visible worker registration evidence.

Identity verification fails closed if any reference, hash, type, capability, or trust boundary is missing or inconsistent.

## Invocation Parameter Validation

Invocation parameters must be:

- explicit;
- bounded;
- JSON-serializable;
- hashable;
- derived from the approved execution request payload;
- compatible with the assigned worker capability;
- free of provider commands;
- free of authority-bearing fields;
- free of credentials or secrets;
- free of scope expansion;
- replay-visible by hash and reference.

AiGOL must reject invocation parameters that add new execution authority, mutate governance, change worker identity, or exceed approved request scope.

## Required Replay Evidence

Before invocation can be reconstructed, replay must contain:

- proposal creation evidence;
- approval evidence with `APPROVED` status;
- execution request evidence;
- ready-for-dispatch evidence;
- worker registration evidence;
- worker assignment evidence;
- dispatch evidence;
- invocation validation event;
- invocation returned event;
- stable references among dispatch, assignment, worker, readiness, and execution request artifacts;
- invocation parameter hash;
- explicit evidence that no execution or completion occurred at invocation.

## Reconstruction Rule

Replay reconstructs invocation by reading ordered evidence and verifying:

1. dispatch existed before invocation;
2. dispatch status was `DISPATCHED`;
3. worker assignment existed before dispatch;
4. assigned worker identity matches dispatch and invocation;
5. invocation parameters match the recorded parameter hash;
6. invocation references the same dispatch, assignment, worker, readiness, and execution request lineage;
7. no duplicate invocation exists;
8. no cancellation or expiry precedes invocation;
9. no execution or completion is encoded in invocation.

Any mismatch invalidates invocation reconstruction.

## Invocation States

The invocation boundary recognizes:

- `DISPATCHED`;
- `INVOKED`;
- `FAILED_INVOCATION`;
- `CANCELLED`;
- `EXPIRED`.

Only `DISPATCHED -> INVOKED` is the positive invocation transition.

## Constitutional Preservation

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Provider output remains upstream proposal evidence only. AiGOL governs invocation. Worker execution remains separate and future. Replay records the invocation decision and parameters.

## Foundation Classification

`WORKER_INVOCATION_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS`

Invocation governance is defined, but invocation runtime implementation, execution runtime, completion runtime, result persistence, and termination evidence remain future work.
