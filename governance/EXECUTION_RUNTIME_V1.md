# EXECUTION_RUNTIME_V1

EXECUTION_RUNTIME_STATUS = CERTIFIED

## Purpose

`EXECUTION_RUNTIME_V1` implements the deterministic transition:

```text
INVOKED
↓
EXECUTING
```

The runtime records that an invoked worker has entered the execution-start boundary. It does not complete work, certify results, mutate governance, mutate replay, or perform self-improvement.

## Runtime Artifact

The runtime creates:

```text
EXECUTION_ARTIFACT_V1
```

Required evidence includes:

- `execution_id`;
- `canonical_chain_id`;
- `worker_invocation_reference`;
- `dispatch_reference`;
- `worker_assignment_reference`;
- `worker_reference`;
- `execution_request_reference`;
- `execution_status`;
- `execution_metadata`;
- `execution_context`;
- `execution_timestamps`;
- `started_by`;
- `started_at`;
- `replay_reference`.

The only valid V1 execution state is:

```text
EXECUTING
```

## Required Validation

Execution start requires:

- a valid `WORKER_INVOCATION_ARTIFACT_V1`;
- invocation status `INVOKED`;
- worker invocation replay continuity;
- matching dispatch artifact reference and hash;
- matching worker assignment reference and hash;
- matching worker identity and worker hash;
- canonical chain continuity;
- valid execution metadata;
- valid execution context.

## Replay Events

The runtime persists append-only replay events:

```text
000_execution_started.json
001_execution_returned.json
```

Replay reconstruction validates wrapper hashes, artifact hashes, replay ordering, reference continuity, chain continuity, and valid execution state.

## Fail-Closed Guarantees

The runtime fails closed on:

- invalid invocation artifact;
- invalid invocation state;
- worker mismatch;
- assignment mismatch;
- dispatch mismatch;
- chain mismatch;
- duplicate execution replay;
- corrupt references;
- replay corruption;
- invalid execution state;
- authority-bearing metadata or context.

## Explicit Non-Goals

`EXECUTION_RUNTIME_V1` does not implement:

- completion runtime;
- result runtime;
- failure runtime;
- reflection runtime;
- self-improvement runtime;
- governance mutation;
- replay mutation;
- provider authority;
- worker self-start authority.

## Constitutional Invariant

The runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

In V1, AiGOL governs the transition into execution by validating invocation, dispatch, assignment, worker identity, and chain continuity. Replay records the execution-start evidence. Completion and result semantics remain out of scope.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_execution_runtime_v1.py
```

Result:

```text
16 passed
```

Execution-chain validation passed:

```bash
python -m pytest tests/test_execution_runtime_v1.py tests/test_worker_invocation_runtime_v1.py tests/test_dispatch_runtime_v1.py tests/test_worker_runtime_v1.py
```

Result:

```text
68 passed
```

Final classification:

```text
EXECUTION_RUNTIME_STATUS = CERTIFIED
```
