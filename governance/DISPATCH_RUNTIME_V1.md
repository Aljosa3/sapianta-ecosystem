# DISPATCH_RUNTIME_V1

## Purpose

Implement deterministic replay-visible dispatch from worker assignment to `DISPATCHED`.

Dispatch is the AiGOL-governed boundary after worker assignment and before worker invocation. It records that an assigned worker is eligible for future invocation, but it does not invoke the worker, execute work, complete work, or persist results.

## Implemented Runtime Surface

Runtime module:

- `aigol/runtime/dispatch_runtime.py`

Runtime tests:

- `tests/test_dispatch_runtime_v1.py`

Compatibility update:

- `aigol/runtime/worker_runtime.py` accepts optional `canonical_chain_id` during assignment and carries it into assignment replay when provided.

Primary entry points:

- `dispatch_worker(...)`;
- `reconstruct_dispatch_replay(...)`.

## Supported Transition

```text
WORKER_ASSIGNMENT
  -> DISPATCHED
```

The worker assignment artifact is not mutated. Dispatch is recorded as a separate append-only artifact.

## Dispatch Artifact

The runtime emits:

```text
DISPATCH_ARTIFACT_V1
```

Required fields include:

- `dispatch_id`;
- `canonical_chain_id`;
- `worker_assignment_reference`;
- `worker_assignment_hash`;
- `worker_assignment_replay_hash`;
- `worker_reference`;
- `worker_hash`;
- `readiness_reference`;
- `readiness_hash`;
- `execution_request_reference`;
- `execution_request_hash`;
- `dispatched_by`;
- `dispatched_at`;
- `dispatch_status`;
- `request_type`;
- `capability_id`;
- `replay_reference`;
- `artifact_hash`.

## Required Inputs

Dispatch validation requires:

- valid worker assignment artifact;
- valid worker assignment replay;
- valid ready-for-dispatch artifact;
- `canonical_chain_id`;
- `dispatched_by = AIGOL`;
- dispatch timestamp;
- replay reference;
- append-only replay directory.

## Runtime Validation

AiGOL validates:

- assignment artifact exists;
- assignment artifact hash is valid;
- assignment status is `ASSIGNED`;
- assignment was created by AiGOL;
- worker was available before assignment;
- worker state after assignment is `ASSIGNED`;
- worker assignment replay matches the assignment artifact;
- readiness artifact exists;
- readiness artifact hash is valid;
- readiness status is `READY_FOR_DISPATCH`;
- readiness reference and hash match assignment evidence;
- execution request reference matches readiness and assignment evidence;
- canonical chain id matches assignment evidence;
- no provider authority exists;
- no worker self-dispatch exists;
- no worker invocation exists;
- no execution exists;
- no completion exists.

## Replay Events

The runtime persists:

```text
000_dispatch_validated.json
001_dispatch_returned.json
```

Events:

- `DISPATCH_VALIDATED`;
- `DISPATCH_RETURNED`.

Replay reconstruction verifies event order, wrapper hashes, artifact hashes, dispatch reference, dispatch hash, worker assignment reference, and canonical chain id continuity.

## Fail-Closed Behavior

The runtime fails closed on:

- missing worker assignment;
- invalid assignment artifact;
- invalid assignment status;
- worker unavailable;
- duplicate dispatch records;
- missing assignment replay;
- corrupt assignment replay;
- reference corruption;
- missing readiness evidence;
- invalid readiness evidence;
- readiness reference mismatch;
- execution request reference mismatch;
- missing canonical chain id;
- chain mismatch;
- provider authority;
- worker self-dispatch;
- worker invocation;
- execution performed;
- completion recorded;
- replay ordering corruption;
- replay hash corruption.

## Boundaries

This runtime does not implement:

- worker invocation;
- worker execution;
- execution completion;
- result persistence;
- provider authority;
- approval mutation;
- execution request mutation;
- readiness mutation;
- worker assignment mutation.

## Constitutional Preservation

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs dispatch. Workers do not self-dispatch or self-invoke. Dispatch creates no execution authority by itself. Replay records and reconstructs the dispatch decision.

## Runtime Classification

```text
DISPATCH_RUNTIME_STATUS = CERTIFIED
```
