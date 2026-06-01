# WORKER_INVOCATION_RUNTIME_V1

## Purpose

Implement deterministic replay-visible worker invocation from dispatch evidence.

Invocation is the AiGOL-governed boundary after dispatch and before worker execution. It records that bounded invocation parameters were delivered to the dispatched worker, but it does not execute work, complete work, or persist results.

## Implemented Runtime Surface

Runtime module:

- `aigol/runtime/worker_invocation_runtime.py`

Runtime tests:

- `tests/test_worker_invocation_runtime_v1.py`

Primary entry points:

- `invoke_worker(...)`;
- `reconstruct_worker_invocation_replay(...)`.

## Supported Transition

```text
DISPATCHED
  -> INVOKED
```

The dispatch artifact is not mutated. Invocation is recorded as a separate append-only artifact.

## Invocation Artifact

The runtime emits:

```text
WORKER_INVOCATION_ARTIFACT_V1
```

Required fields include:

- `worker_invocation_id`;
- `canonical_chain_id`;
- `dispatch_reference`;
- `dispatch_hash`;
- `dispatch_replay_hash`;
- `worker_assignment_reference`;
- `worker_assignment_hash`;
- `worker_reference`;
- `worker_hash`;
- `readiness_reference`;
- `execution_request_reference`;
- `invoked_by`;
- `invoked_at`;
- `invocation_status`;
- `request_type`;
- `capability_id`;
- `invocation_parameters`;
- `invocation_parameters_hash`;
- `replay_reference`;
- `artifact_hash`.

## Runtime Validation

AiGOL validates:

- dispatch artifact exists;
- dispatch artifact hash is valid;
- dispatch status is `DISPATCHED`;
- dispatch was created by AiGOL;
- dispatch replay matches dispatch artifact;
- worker assignment artifact exists;
- worker assignment artifact hash is valid;
- worker identity matches dispatch evidence;
- worker assignment status is `ASSIGNED`;
- worker availability lineage is valid;
- canonical chain id matches dispatch and assignment evidence;
- invocation parameters are present;
- invocation parameters match dispatch request type, capability, and execution request reference;
- invocation parameters are hashable and replay-visible;
- invocation parameters contain no authority-bearing fields;
- no provider authority exists;
- no worker self-invocation exists;
- no execution starts;
- no execution is performed;
- no completion is recorded.

## Replay Events

The runtime persists:

```text
000_worker_invocation_validated.json
001_worker_invocation_returned.json
```

Events:

- `WORKER_INVOCATION_VALIDATED`;
- `WORKER_INVOCATION_RETURNED`.

Replay reconstruction verifies event order, wrapper hashes, artifact hashes, invocation reference, invocation hash, dispatch reference, and canonical chain id continuity.

## Fail-Closed Behavior

The runtime fails closed on:

- missing dispatch;
- invalid dispatch artifact;
- invalid dispatch status;
- corrupt dispatch replay;
- worker mismatch;
- worker unavailable;
- duplicate invocation records;
- chain mismatch;
- missing invocation parameters;
- authority-bearing invocation parameters;
- invocation parameter validation failure;
- corrupt references;
- provider authority;
- worker self-invocation;
- execution started;
- execution performed;
- completion recorded;
- replay ordering corruption;
- replay hash corruption.

## Boundaries

This runtime does not implement:

- worker execution;
- execution completion;
- result persistence;
- worker termination evidence;
- provider authority;
- dispatch mutation;
- worker assignment mutation.

## Constitutional Preservation

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs invocation. Workers do not self-invoke. Invocation creates no completion or result authority. Replay records and reconstructs the invocation event.

## Runtime Classification

```text
WORKER_INVOCATION_RUNTIME_STATUS = CERTIFIED
```
