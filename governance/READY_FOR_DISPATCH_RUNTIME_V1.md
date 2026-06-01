# READY_FOR_DISPATCH_RUNTIME_V1

## Purpose

Implement deterministic readiness validation for AiGOL execution requests.

This runtime creates replay-visible `READY_FOR_DISPATCH_ARTIFACT_V1` evidence for execution requests that are valid, replay-continuous, and tied to matching approved proposal lineage.

## Implemented Runtime Surface

Runtime module:

- `aigol/runtime/ready_for_dispatch_runtime.py`

Runtime tests:

- `tests/test_ready_for_dispatch_runtime_v1.py`

Primary entry points:

- `mark_ready_for_dispatch(...)`
- `reconstruct_ready_for_dispatch_replay(...)`

## Supported Transition

```text
EXECUTION_REQUEST.CREATED
  -> READY_FOR_DISPATCH
```

The execution request artifact is not mutated. Readiness is recorded as a separate append-only artifact that references the execution request, approval, proposal lineage, and replay evidence.

## Required Inputs

Readiness validation requires:

- `readiness_id`;
- `execution_request_artifact`;
- `execution_request_replay`;
- `approval_artifact`;
- `validated_at`;
- `replay_reference`;
- `replay_dir`;
- `validated_by = AIGOL`.

## Required Evidence

AiGOL validates:

- execution request artifact exists;
- execution request artifact hash is valid;
- execution request status is `CREATED`;
- execution request replay is present;
- execution request replay hash is valid;
- execution request replay references the same request;
- approval artifact exists;
- approval artifact hash is valid;
- approval status is `APPROVED`;
- approval id and hash match the execution request;
- proposal reference and hash match across approval, execution request, and replay;
- provider authority is absent;
- worker assignment is absent;
- worker dispatch is absent;
- worker invocation is absent;
- execution is absent;
- automatic authorization is absent.

## Replay Events

The runtime persists:

```text
000_ready_for_dispatch_validated.json
001_ready_for_dispatch_returned.json
```

Events:

- `READY_FOR_DISPATCH_VALIDATED`;
- `READY_FOR_DISPATCH_RETURNED`.

Replay reconstruction verifies event order, wrapper hashes, artifact hashes, readiness reference, readiness hash, execution request reference, and approval reference.

## Fail-Closed Behavior

The runtime fails closed on:

- missing execution request;
- invalid execution request artifact;
- invalid execution request status;
- corrupt execution request artifact;
- missing execution request replay;
- corrupt execution request replay;
- invalid replay reference;
- missing approval;
- corrupt approval artifact;
- non-approved approval;
- approval mismatch;
- proposal reference mismatch;
- duplicate readiness records;
- provider authority introduction;
- worker assignment;
- worker dispatch;
- worker invocation;
- execution performed;
- replay ordering corruption;
- replay hash corruption.

## Boundaries

This runtime does not implement:

- worker assignment;
- dispatch;
- worker execution;
- execution completion;
- provider authority;
- approval mutation;
- execution request mutation.

## Constitutional Preservation

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs readiness. Workers remain inactive. Providers have no readiness authority. Replay records and reconstructs the readiness decision.

## Runtime Classification

`READY_FOR_DISPATCH_RUNTIME_STATUS = CERTIFIED`
