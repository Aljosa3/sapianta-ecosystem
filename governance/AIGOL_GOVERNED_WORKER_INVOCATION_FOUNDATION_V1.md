# AIGOL_GOVERNED_WORKER_INVOCATION_FOUNDATION_V1

## Status

Certified constitutional foundation.

## Final Classification

```text
AIGOL_GOVERNED_WORKER_INVOCATION_FOUNDATION_STATUS = CERTIFIED
```

## Purpose

Define the constitutional boundary by which an `EXECUTION_READY` packet may later
become eligible for governed Worker invocation.

This milestone is architecture only. It does not implement execution
authorization, dispatch, Worker invocation, Worker execution, file creation, code
generation, result persistence, or replay mutation.

## Constitutional Invariant

```text
Conversation expresses intent.
PPP produces and validates proposals.
Governance authorizes bounded execution.
AiGOL dispatches and invokes an authorized Worker.
Worker executes only the authorized scope.
Replay records but never authorizes.
```

## Worker Invocation Definition

Worker invocation is the replay-visible AiGOL-controlled delivery of a bounded,
authorized execution packet to an assigned and dispatched Worker.

Worker invocation is not:

- execution authorization;
- Worker selection;
- Worker assignment;
- dispatch;
- Worker execution;
- result acceptance;
- governance mutation;
- replay authority;
- permission for hidden continuation.

## Canonical Lifecycle

```text
EXECUTION_READY
-> EXECUTION_AUTHORIZATION
-> WORKER_INVOCATION_REQUEST
-> WORKER_ASSIGNMENT
-> DISPATCH
-> WORKER_INVOCATION
-> WORKER_RESULT
-> RESULT_VALIDATION
-> POST_EXECUTION_REPLAY_REVIEW
-> TERMINATED
```

The explicit `WORKER_ASSIGNMENT` and `DISPATCH` boundaries preserve the existing
Worker invocation constitutional rule: no Worker may be invoked merely because a
request or authorization exists.

## Who May Invoke A Worker?

Only the governed AiGOL invocation boundary may record and deliver a Worker
invocation.

The following may never invoke a Worker:

- conversation;
- cognition;
- Resource Selection;
- PPP;
- provider proposal;
- provider;
- replay;
- improvement intent;
- implementation handoff;
- execution-ready packet;
- human acting outside the governed authorization boundary;
- Worker acting on itself;
- automatic retry logic;
- CLI transport alone.

## Invocation Conditions

A Worker may be invoked only when:

- an `EXECUTION_READY` status exists;
- the execution packet is valid and hash-verifiable;
- a separate execution authorization artifact is valid and active;
- authorization scope exactly covers the execution packet;
- Worker identity and capability are registered and eligible;
- Worker assignment is deterministic and replay-visible;
- dispatch is valid, active, and bound to the same Worker;
- chain, handoff, approval, authorization, assignment, and dispatch lineage are continuous;
- no revocation, cancellation, expiry, prior invocation, or replay corruption exists;
- invocation parameters are bounded to the authorized packet;
- all pre-invocation validations pass.

## Required Artifacts

The minimum admissible lineage is:

```text
IMPLEMENTATION_HANDOFF_ARTIFACT
-> EXECUTION_CANDIDATE_ARTIFACT_V1
-> EXECUTION_PACKET_ARTIFACT_V1
-> EXECUTION_VALIDATION_ARTIFACT_V1
-> EXECUTION_READY_STATUS_ARTIFACT_V1
-> EXECUTION_AUTHORIZATION_ARTIFACT_V1
-> WORKER_INVOCATION_REQUEST_ARTIFACT_V1
-> WORKER_ASSIGNMENT_ARTIFACT
-> DISPATCH_ARTIFACT_V1
-> WORKER_INVOCATION_ARTIFACT_V1
-> WORKER_RESULT_ARTIFACT_V1
-> RESULT_VALIDATION_ARTIFACT_V1
-> POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1
```

Rejection, revocation, expiry, failure, and termination artifacts must be
preserved when applicable.

## Authority Boundary

`EXECUTION_READY` proves preparation only.

`EXECUTION_AUTHORIZATION` grants bounded permission only.

`WORKER_INVOCATION_REQUEST` requests invocation only.

`DISPATCH` binds an authorized Worker only.

`WORKER_INVOCATION` permits the separate execution boundary to begin only within
the authorized scope.

No artifact grants authority by implication or inheritance.

## Required Replay Evidence

Replay must preserve:

- original intent and proposal lineage;
- approval and implementation handoff lineage;
- execution candidate, packet, validation, and ready status;
- authorization request, decision, scope, validity window, and revocation state;
- Worker registry, capability, trust, assignment, and dispatch evidence;
- invocation request, invocation parameters, parameter hash, and invocation outcome;
- Worker result, result validation, post-execution review, and termination;
- ordered timestamps, artifact hashes, replay hashes, and chain references.

Replay records evidence. Replay does not create, renew, infer, or restore
execution authority.

## Fail-Closed Conditions

The lifecycle must fail closed when:

- authorization is missing, invalid, expired, revoked, or scope-mismatched;
- Worker identity, capability, trust, assignment, or dispatch is invalid;
- invocation parameters exceed the authorized packet;
- chain, replay, artifact, or hash continuity breaks;
- invocation is duplicated;
- cancellation or expiry precedes invocation;
- any upstream non-authoritative layer attempts invocation;
- execution attempts to begin without invocation evidence;
- result validation or replay review cannot be completed.

## Relationship To Existing Artifacts

This foundation preserves and consolidates the constitutional semantics already
defined by:

- `AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_V1`;
- `EXECUTION_AUTHORIZATION_MODEL_V1`;
- `AUTHORIZATION_AUTHORITY_MODEL_V1`;
- `WORKER_INVOCATION_RUNTIME_FOUNDATION_V1`;
- `WORKER_INVOCATION_RUNTIME_BOUNDARY_GUARANTEES_V1`;
- `AUTHORIZATION_REPLAY_MODEL_V1`.

It does not replace or weaken their authority separation, dispatch, or replay
requirements.

## Non-Goals

This milestone does not:

- authorize execution;
- invoke a Worker;
- dispatch a Worker;
- execute work;
- create files;
- generate code;
- mutate governance;
- mutate replay;
- introduce autonomous continuation.

## Certification Judgment

The constitutional foundation is sufficient to define the next governed runtime
milestones. Real Worker execution remains prohibited until authorization,
invocation, sandbox, result validation, and post-execution replay controls are
implemented and certified.
