# FIRST_END_TO_END_GOVERNED_OPERATION_V1

## Status

`FIRST_END_TO_END_GOVERNED_OPERATION_STATUS = READY`

## Purpose

This milestone demonstrates the first complete governed AiGOL operation:

```text
Human
↓
Provider
↓
Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
Filesystem Worker
↓
Replay
```

The operation is intentionally minimal. A deterministic provider proposal is governed into an authorization artifact, transformed into an authorized worker request, and executed by one filesystem worker that creates exactly one file.

## Operation

The governed operation creates:

```text
test.txt
```

with content:

```text
FIRST_END_TO_END_GOVERNED_OPERATION_V1
```

## Runtime Components

- `aigol/provider/provider_runtime.py`
- `aigol/authorization/authorization_runtime.py`
- `aigol/workers/filesystem_worker.py`

## Worker Boundary

`FILESYSTEM_CREATE_WORKER` accepts only:

- `AUTHORIZED_WORKER_REQUEST_V1`
- `authorization_scope = FILESYSTEM_CREATE_FILE`
- `operation = CREATE_FILE`
- one relative filename
- explicit content

It rejects raw provider output, raw proposals, raw authorization artifacts, dispatch requests, orchestration requests, replay mutation, memory mutation, absolute paths, path traversal, existing target files, and invalid replay.

## Replay Reconstruction

Replay reconstructs:

- human request
- provider identity
- provider proposal envelope
- governed authorization artifact
- authorized worker request
- filesystem worker execution
- execution result

## Authority Preservation

The operation preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Provider authority remains absent. Proposal authority remains absent. Authorization originates only through governed authorization. The worker executes only after receiving an authorized worker request.

## Validation

Focused validation:

```text
python -m pytest tests/test_first_end_to_end_governed_operation_v1.py
```

Result:

```text
10 passed
```

