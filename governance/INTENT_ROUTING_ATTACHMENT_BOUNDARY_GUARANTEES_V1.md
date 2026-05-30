# Intent Routing Attachment Boundary Guarantees V1

Status: boundary guarantees for Intent Routing Attachment V1.

## Core Guarantee

The routing attachment creates routing evidence only.

It does not:

- invoke destination
- call provider
- call worker
- execute
- retrieve memory
- generate conversation
- authorize
- govern

## Supported Destinations

Only the following destination labels are accepted:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

No custom destination is accepted.

## Input Boundary

Only `CLASSIFIED` intent artifacts may route.

Failed, ambiguous, corrupted, multiple-destination, or authority-bearing artifacts fail closed.

## Authority Status

`INTENT_ROUTING_ATTACHMENT_AUTHORITY_STATUS`: `PRESERVED`

Routing evidence is not routing authority.

Destination activation remains out of scope.

## Invariant Preservation

The implementation preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

