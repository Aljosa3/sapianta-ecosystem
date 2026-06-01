# WORKER_RUNTIME_V1

## Purpose

Implement minimal replay-visible Worker Runtime for registration and assignment.

This runtime creates:

- `WORKER_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`.

It supports worker registration and AiGOL-governed assignment from a `READY_FOR_DISPATCH` readiness artifact.

## Implemented Runtime Surface

Runtime module:

- `aigol/runtime/worker_runtime.py`

Runtime tests:

- `tests/test_worker_runtime_v1.py`

Primary entry points:

- `register_worker(...)`;
- `assign_worker(...)`;
- `reconstruct_worker_registration_replay(...)`;
- `reconstruct_worker_assignment_replay(...)`.

## Supported Worker States

```text
AVAILABLE
ASSIGNED
UNAVAILABLE
```

Only `AVAILABLE` workers may be assigned.

Assignment records:

```text
worker_state_before = AVAILABLE
worker_state_after = ASSIGNED
assignment_status = ASSIGNED
```

The worker artifact is not mutated in place. Assignment is recorded as append-only replay evidence.

## Assignment Eligibility

Worker assignment requires:

- valid `WORKER_ARTIFACT_V1`;
- worker state `AVAILABLE`;
- valid `READY_FOR_DISPATCH_ARTIFACT_V1`;
- readiness status `READY_FOR_DISPATCH`;
- matching readiness replay evidence;
- supported request type;
- `assigned_by = AIGOL`;
- no provider authority;
- no worker self-assignment;
- no dispatch;
- no worker invocation;
- no execution;
- no completion.

## Replay Events

Registration persists:

```text
000_worker_registered.json
001_worker_registration_returned.json
```

Assignment persists:

```text
000_worker_assigned.json
001_worker_assignment_returned.json
```

Events:

- `WORKER_REGISTERED`;
- `WORKER_REGISTRATION_RETURNED`;
- `WORKER_ASSIGNED`;
- `WORKER_ASSIGNMENT_RETURNED`.

Replay reconstruction verifies event order, wrapper hashes, artifact hashes, worker references, readiness references, and assignment references.

## Fail-Closed Behavior

The runtime fails closed on:

- missing worker;
- invalid worker artifact;
- invalid worker state;
- worker unavailable;
- duplicate assignment records;
- missing readiness artifact;
- invalid readiness artifact;
- non-ready readiness state;
- corrupt readiness replay;
- readiness reference mismatch;
- unsupported request type;
- provider authority;
- worker self-authorization;
- worker dispatch;
- worker invocation;
- execution performed;
- completion recorded;
- corrupt replay ordering;
- corrupt replay hashes.

## Boundaries

This runtime does not implement:

- dispatch;
- worker invocation;
- execution;
- execution completion;
- result persistence;
- provider authority;
- approval mutation;
- execution request mutation;
- readiness mutation.

## Constitutional Preservation

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs worker assignment. Workers do not self-authorize or execute in this runtime. Replay records registration and assignment evidence.

## Runtime Classification

`WORKER_RUNTIME_STATUS = CERTIFIED`
