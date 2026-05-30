# Provider Attachment Architecture Review ADR V1

Status: accepted review decision record.

## Decision

Certify provider attachment architecture as:

```text
PROVIDER_ATTACHMENT_STATUS = READY_FOR_IMPLEMENTATION
```

## Context

The Governed Cognition Foundation is frozen as `READY_FOR_PROVIDER_ATTACHMENT`.

The next constitutional question is whether external providers can attach while remaining completely non-authoritative.

## Accepted Finding

Providers can attach if they remain:

```text
external proposal producers
```

and if implementation preserves identity, lifecycle, replay visibility, isolation, substitutability, fail-closed behavior, and proposal-only boundaries.

## Rejected Scope

This milestone rejects:

- provider runtime implementation
- provider execution
- provider dispatch
- orchestration
- planning
- reflection
- autonomous behavior
- worker changes
- governance activation
- runtime mutation

## Consequence

The Provider Attachment Epoch may proceed to implementation of a bounded provider attachment adapter.

The implementation must not alter the frozen invariant:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
