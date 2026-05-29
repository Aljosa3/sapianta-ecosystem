# External Worker Replay Model V1

Status: replay model for the first external Worker attachment.

## Replay Chain

The external Worker writes a deterministic append-only replay chain:

1. `worker_identity`
2. `execution_request_reference`
3. `execution_evidence`
4. `worker_result`
5. `termination_record`

Each artifact is JSON-serialized deterministically and protected by replay hashes.

## Required Replay Fields

Replay evidence contains:

- `worker_identity`
- `execution_request_reference`
- `execution_evidence`
- `worker_result`
- `termination_record`

The execution request reference contains the AiGOL authorization evidence hash and the authorized request hash.

## Reconstruction

Replay reconstruction verifies:

- artifact ordering
- wrapper hashes
- artifact hashes
- lifecycle state continuity
- terminal state validity
- read-only boundary preservation

Successful lifecycle:

```text
WORKER_IDENTITY_CAPTURED
-> EXECUTION_REQUEST_REFERENCED
-> EXECUTION_EVIDENCE_CAPTURED
-> WORKER_RESULT_CAPTURED
-> TERMINATED
```

Failed lifecycle:

```text
FAILED
```

or a valid success prefix followed by terminal `FAILED` artifacts.

## Replay Guarantee

Replay remains append-only, reconstructable, and non-authoritative. The Worker emits evidence but cannot mutate replay authority.

