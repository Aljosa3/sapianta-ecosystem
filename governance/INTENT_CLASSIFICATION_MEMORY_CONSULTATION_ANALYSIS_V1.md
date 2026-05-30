# Intent Classification Memory Consultation Analysis V1

Status: Constitutional Memory consultation analysis for future intent classification.

## Current Position

Constitutional Memory Consultation is currently defined as reference-only access.

It is supported by:

- `CONSTITUTIONAL_MEMORY_RETRIEVAL_MODEL_V1`
- `CONSTITUTIONAL_MEMORY_CITATION_MODEL_V1`
- `CONSTITUTIONAL_MEMORY_ACCESS_PATH_V1`
- `CONSTITUTIONAL_MEMORY_ACCESS_BOUNDARY_V1`
- `CONSTITUTIONAL_MEMORY_ACCESS_REPLAY_MODEL_V1`

## Existing Flow

```text
Operator or governance-scoped request
-> retrieval request
-> explicit catalog lookup
-> citation bundle
-> replay-visible retrieval result
```

## Authority Boundary

Memory Consultation returns `REFERENCE_RESULT` only.

It does not return:

- authorization
- governance decision
- execution request
- proposal
- worker command
- provider command
- correction instruction

## Intent Classification Readiness

Memory Consultation is a plausible future intent destination.

The missing element is not memory access; it is the classifier that can decide:

```text
this Human Prompt requests constitutional reference evidence
```

and then create a replay-visible retrieval request.

## Classification

`MEMORY_CONSULTATION_INTENT_POSITION`: `DEFINED`

`MEMORY_CONSULTATION_ROUTING_READINESS`: `READY_WITH_GAPS`

Gap: no intent classifier currently maps Human Prompt to memory retrieval scope.

