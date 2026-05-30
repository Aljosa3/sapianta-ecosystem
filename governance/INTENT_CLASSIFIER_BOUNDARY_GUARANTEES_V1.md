# Intent Classifier Boundary Guarantees V1

Status: boundary guarantees for implemented Intent Classifier V1.

## Core Guarantee

The Intent Classifier classifies only.

It does not:

- route
- invoke providers
- invoke workers
- execute
- retrieve memory
- authorize
- govern
- mutate replay

## Authority Status

`INTENT_CLASSIFIER_AUTHORITY_STATUS`: `PRESERVED`

The classifier remains non-authoritative.

## Runtime Boundary

The runtime returns:

- classification artifact
- classification replay evidence

The runtime does not return:

- authorization decision
- governance decision
- execution request
- provider command
- worker command
- memory retrieval result
- proposal artifact
- correction instruction

## Destination Boundary

The classifier may emit a destination label.

The label does not perform the destination action.

## Invariant Preservation

The implementation preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

