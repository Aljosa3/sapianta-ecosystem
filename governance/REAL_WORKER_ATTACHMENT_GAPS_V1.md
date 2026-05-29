# Real Worker Attachment Gaps V1

Status: analysis-only gap record.

## Readiness Context

The frozen baseline already preserves worker execution-only semantics.

Execution is authorized before capability invocation, replay is mandatory, and supported work is limited to read-only runtime inspection and bounded filesystem read-only inspection.

The current worker role is functionally present but not yet represented as an independently attached real worker boundary.

## Missing Before Real Worker Attachment

### Worker Identity Envelope

A real worker attachment needs deterministic worker identity fields:

- worker id
- worker type
- worker version
- capability binding id
- invocation id
- created timestamp
- attachment boundary version

### Worker Attachment Boundary

The worker boundary must explicitly separate:

- AiGOL authorization
- worker execution
- worker result evidence
- replay recording

The worker must not validate its own authority, expand capability scope, mutate governance, or create hidden continuation.

### Execution Adapter

A real worker needs an adapter that accepts only governed execution requests that already contain authorization evidence.

The adapter should reject:

- missing authorization
- unsupported capability
- boundary mismatch
- mutation request
- replay discontinuity
- worker self-authorization attempt

### Capability Binding

The first real worker attachment should bind only existing frozen capabilities:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

No new capability class is required for first attachment.

### Worker Replay Mapping

Worker replay needs deterministic stages:

- governed execution request
- authorization evidence
- worker identity envelope
- capability boundary evidence
- worker result
- worker termination state

### Isolation and Persistence Boundary

The worker must be non-persistent unless explicitly governed.

It must not leak state across invocations, cache hidden context, continue after termination, or mutate constitutional artifacts.

### Attachment Boundary Tests

Before real worker attachment is accepted, tests should pressure:

- missing authorization
- worker identity mismatch
- forbidden capability binding
- filesystem mutation attempt
- replay ordering violation
- worker self-authorization
- hidden persistence across runs
- malformed worker result

## Not Missing

The following are already present in the frozen baseline:

- authorization-before-execution
- worker execution-only role
- read-only capability enforcement
- fail-closed unsupported capability handling
- replay-visible governed result

## Real Worker Attachment Readiness

`REAL_WORKER_ATTACHMENT_READINESS`: `PARTIALLY_READY`

Reason: the execution-only role is stable, but a real worker still needs explicit identity, adapter boundary, replay mapping, isolation rules, and pressure tests before it becomes a governed attachment rather than in-process capability execution.
