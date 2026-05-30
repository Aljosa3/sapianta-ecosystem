# Constitutional Memory Consultation Gaps V1

Status: gaps before activation implementation.

## Critical Gaps

Before implementation, AiGOL needs:

- activation record schema
- routing-to-retrieval linkage
- deterministic mapping from destination evidence to retrieval scope
- activation replay wrapper
- activation reconstruction validator
- pressure tests for routing/retrieval mismatch

## Important Gaps

Useful but not blocking for model readiness:

- operator-facing consultation summary
- governed answer presentation model
- conflict explanation format
- consultation replay summary command

## Optional Gaps

Should not drive V1 activation:

- semantic search
- vector retrieval
- memory-based answering
- correction loops
- provider-assisted retrieval

## Readiness

`CONSTITUTIONAL_MEMORY_CONSULTATION_ACTIVATION_STATUS`: `READY_WITH_CONSTRAINTS`

Activation can be implemented safely if it wraps the existing access path and does not create a new retrieval engine.

