# REPLAY_INSPECTOR_WORKER_V1

REPLAY_INSPECTOR_WORKER_STATUS = CERTIFIED

## Purpose

`REPLAY_INSPECTOR_WORKER_V1` implements AiGOL's first real worker as a bounded read-only replay inspector.

The worker accepts explicit replay references, reads replay artifacts, validates replay and artifact hashes, checks canonical chain continuity where chain evidence is present, and emits a replay-visible inspection report.

## Runtime Artifact

The worker produces:

```text
REPLAY_INSPECTION_REPORT_V1
```

Required report fields include:

- `worker_id`;
- `worker_type`;
- `inspection_id`;
- `canonical_chain_id`;
- `inspection_scope`;
- `inspection_status`;
- `inspected_replay_references`;
- `artifact_count`;
- `artifact_types`;
- `chain_continuity_status`;
- `missing_references`;
- `corrupt_references`;
- `authority_leak_detected`;
- `mutation_detected`;
- `failure_reason`;
- `created_at`;
- `artifact_hash`.

## Valid Statuses

```text
INSPECTION_COMPLETED
FAILED_CLOSED
```

## Replay Events

The worker persists append-only replay events:

```text
000_replay_inspection_recorded.json
001_replay_inspection_returned.json
```

Replay reconstruction validates wrapper hashes, artifact hashes, replay ordering, report-to-return reference continuity, and canonical chain continuity.

## Read-Only Boundary

The worker may read only explicit file references or one-level JSON replay files inside explicit directory references.

The worker rejects report output paths that would write inside an inspected replay location.

The worker does not modify:

- replay artifacts;
- governance artifacts;
- filesystem inputs;
- runtime state;
- execution history.

## Fail-Closed Behavior

The worker fails closed on:

- missing replay references;
- invalid replay references;
- corrupt replay wrappers;
- corrupt replay artifacts;
- canonical chain mismatch;
- missing artifacts;
- authority-bearing replay input;
- duplicate worker replay records;
- invalid replay reconstruction.

## Explicit Non-Goals

`REPLAY_INSPECTOR_WORKER_V1` does not:

- repair replay;
- modify replay;
- certify results;
- evaluate result quality;
- create governance decisions;
- call providers;
- execute shell commands;
- mutate filesystem inputs;
- mutate execution history.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_replay_inspector_worker_v1.py
```

Result:

```text
11 passed
```

Worker lifecycle validation passed:

```bash
python -m pytest tests/test_replay_inspector_worker_v1.py tests/test_completion_runtime_v1.py tests/test_execution_runtime_v1.py tests/test_worker_invocation_runtime_v1.py tests/test_dispatch_runtime_v1.py tests/test_worker_runtime_v1.py
```

Result:

```text
95 passed
```

## Final Classification

```text
REPLAY_INSPECTOR_WORKER_STATUS = CERTIFIED
```
