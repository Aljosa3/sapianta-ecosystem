# MINIMAL_PROVIDER_WORKER_METADATA_V1

## Status

MINIMAL_PROVIDER_WORKER_METADATA_STATUS = READY

METADATA_AUTHORITY_IMPACT = NONE

RUNTIME_BEHAVIOR_CHANGE = NONE

## Purpose

This milestone introduces minimal descriptive metadata for providers and
workers before large-scale attachment begins.

The metadata exists only for:

- observability
- replay visibility
- future compatibility
- governance evidence

## Constitutional Invariant

LLM proposes.

AiGOL governs.

Worker executes.

Replay records.

## Metadata Model

Provider metadata:

- domain
- capability
- resource_type

Worker metadata:

- domain
- capability
- resource_type

## Authority Boundary

Metadata is descriptive only.

Metadata does not:

- grant authority
- influence authorization
- influence governance decisions
- influence execution permission
- influence worker selection
- influence provider selection
- introduce routing
- introduce orchestration
- introduce autonomous selection

## Provider Support

Provider metadata is optional.

Safe defaults:

- domain: `unspecified`
- capability: `proposal_generation`
- resource_type: `provider`

Provider metadata is recorded through provider registry metadata and surfaced in
provider replay evidence.

## Worker Support

Worker metadata is optional.

Safe defaults for the first external runtime inspection worker:

- domain: `infrastructure`
- capability: `read_only_runtime_inspection`
- resource_type: `runtime_metadata`

Worker metadata is recorded in worker identity evidence and reconstructed from
worker replay.

## Replay Visibility

Replay can reconstruct:

- provider metadata
- worker metadata

The metadata is included in deterministic artifact hashes and replay wrapper
hashes. Replay determinism is preserved because metadata is canonicalized before
persistence.

## Runtime Behavior

The runtime does not branch on metadata.

Forbidden behavior remains forbidden:

```text
IF domain == X:
    do Y

IF capability == X:
    execute Y

IF resource_type == X:
    select Y
```

No routing, execution logic, selection logic, or orchestration logic is added.

## Validation

Validation confirms:

- metadata is optional
- metadata is stored correctly
- metadata appears in replay evidence
- absent metadata uses safe defaults
- present metadata preserves runtime behavior
- metadata does not affect execution
- metadata does not affect governance decisions
- metadata does not introduce authority

## Final Classification

MINIMAL_PROVIDER_WORKER_METADATA_STATUS = READY

METADATA_AUTHORITY_IMPACT = NONE

RUNTIME_BEHAVIOR_CHANGE = NONE
